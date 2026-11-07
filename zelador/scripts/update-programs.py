#!/usr/bin/env python3
"""
Zelador Worker — Deterministic CLI binary updater for SDD ecosystem.

Version: 0.1.0

Usage:
    python update-programs.py --check-only [--program NAME] [--json]
    python update-programs.py --update [--program NAME] [--json] [--dry-run]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import hashlib
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

# ─── Config ──────────────────────────────────────────────────────────────
SKILLS_DIR = Path(__file__).parent.parent.parent
ROOT_DIR = SKILLS_DIR.parent
PROGRAMAS_DIR = ROOT_DIR / "programas"
CONFIG_FILE = SKILLS_DIR / "updater.json"

# Skills que NÃO são programas CLI (ignoradas)
SKIP_SKILLS = {
    "architect",
    "design-operator",
    "design-planner",
    "pittaya-indesign-scripts",
}

# Defaults (overridden by config)
DEFAULT_CONFIG = {
    "asset_patterns": {
        "darwin": [r"macos-universal\.zip$", r"-macos\.zip$", r"-darwin\.zip$"],
        "linux": [r"linux-x86_64\.tar\.gz$", r"-linux\.tar\.gz$", r"-linux\.tgz$"],
        "win32": [r"windows-x86_64\.zip$", r"-windows\.zip$", r"\.exe$"],
        "cygwin": [r"windows-x86_64\.zip$", r"-windows\.zip$", r"\.exe$"],
    },
    "timeouts": {"api": 30, "download": 300},
    "parallel_downloads": 4,
    "retry": {"max_attempts": 3, "backoff_base": 2, "backoff_max": 60},
    "checksum": {
        "enabled": True,
        "fallback_to_local": True,
        "checksum_asset_names": ["SHA256SUMS", "SHA256SUMS.txt", "checksums.txt", "checksums.sha256", "sha256sums.txt"],
    },
    "cleanup": {"remove_old_assets": True, "remove_failed_downloads": True},
}


def load_config() -> Dict[str, Any]:
    """Carrega configuração do updater.json com fallback para defaults."""
    config = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            # Deep merge
            for key, value in user_config.items():
                if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                    config[key].update(value)
                else:
                    config[key] = value
        except Exception as e:
            print(f"⚠ Failed to load config {CONFIG_FILE}: {e}", file=sys.stderr)
    return config


CONFIG = load_config()


# ─── Data Classes ────────────────────────────────────────────────────────
@dataclass
class SkillInfo:
    name: str
    path: Path
    project_url: str
    cli_binary: str
    version_cmd: str
    owner: str
    repo: str


@dataclass
class VersionInfo:
    skill: str
    current: str
    latest: str
    asset_name: str
    asset_url: str
    asset_sha256: Optional[str]


@dataclass
class UpdateResult:
    skill: str
    old_version: str
    new_version: str
    asset_downloaded: str
    binary_path: str
    dist_path: str
    status: str  # "updated" | "skipped" | "error"


@dataclass
class ScriptOutput:
    status: str  # "success" | "partial" | "error"
    platform: str
    updated: List[Dict[str, Any]]
    skipped: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    would_update: List[Dict[str, Any]]


# ─── Utilitários ─────────────────────────────────────────────────────────
def log(msg: str, level: str = "INFO", quiet: bool = False, json_mode: bool = False):
    """Log para stderr (não polui stdout em modo JSON)."""
    if not quiet:
        prefix = {"INFO": "→", "WARN": "⚠", "ERROR": "✗", "OK": "✓", "PROGRESS": "⟳"}.get(level, "•")
        print(f"  {prefix} {msg}", flush=True, file=sys.stderr)


def run_cmd(
    cmd: List[str],
    cwd: Path = None,
    capture: bool = True,
    timeout: int = None,
    json_mode: bool = False,
) -> subprocess.CompletedProcess:
    """Executa comando com timeout configurável."""
    if timeout is None:
        timeout = CONFIG["timeouts"].get("api", 30)
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        if json_mode:
            raise
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(cmd)}") from e


def parse_frontmatter(skill_md: Path) -> Dict[str, str]:
    """Extrai frontmatter YAML do SKILL.md"""
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        import yaml
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        # Fallback regex para campos simples
        fm = {}
        for line in parts[1].splitlines():
            m = re.match(r'^(\w+):\s*["\']?([^"\']+)["\']?$', line.strip())
            if m:
                fm[m.group(1)] = m.group(2)
        return fm


def extract_repo_info(project_url: str) -> Optional[tuple]:
    """Extrai owner/repo de URL GitHub"""
    m = re.search(r'github\.com/([^/]+)/([^/]+?)(?:\.git)?$', project_url)
    if m:
        return m.group(1), m.group(2)
    return None


def clean_version(version_str: str) -> str:
    """Extrai apenas a versão semântica (X.Y.Z) de string ruidosa"""
    if not version_str:
        return "0.0.0"
    m = re.search(r'(\d+\.\d+\.\d+)', version_str)
    return m.group(1) if m else version_str.strip()


def get_current_version(skill: SkillInfo) -> str:
    """Detecta versão atual em cascata — SÓ conta se binário existe e roda."""
    # 1. version.txt
    version_file = skill.path / "version.txt"
    if version_file.exists():
        return clean_version(version_file.read_text())

    # 2. binário local (precisa existir E executar)
    binary = skill.path / "bin" / skill.cli_binary
    if binary.exists() and binary.is_file():
        try:
            result = run_cmd([str(binary), skill.version_cmd], timeout=10)
            if result.returncode == 0:
                return clean_version(result.stdout)
        except Exception:
            pass

    # 3. NÃO usar programas/ como fallback — só reflete downloads, não instalação real
    return "0.0.0"


def get_latest_release(owner: str, repo: str, json_mode: bool = False) -> Optional[Dict]:
    """Busca release latest via gh api"""
    try:
        result = run_cmd(
            ["gh", "api", f"repos/{owner}/{repo}/releases/latest"],
            timeout=CONFIG["timeouts"]["api"],
            json_mode=json_mode,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return None


def fetch_checksums_from_release(release: Dict, json_mode: bool = False) -> Dict[str, str]:
    """Busca arquivo de checksums do release (se existir) usando release já obtido."""
    checksum_assets = CONFIG["checksum"]["checksum_asset_names"]
    for asset in release.get("assets", []):
        if asset.get("name") in checksum_assets:
            url = asset.get("browser_download_url")
            if url:
                try:
                    cs_result = run_cmd(
                        ["curl", "-sL", url],
                        timeout=CONFIG["timeouts"]["download"],
                        capture=True,
                        json_mode=json_mode,
                    )
                    if cs_result.returncode == 0:
                        return parse_checksum_file(cs_result.stdout)
                except Exception:
                    continue
    return {}


def parse_checksum_file(content: str) -> Dict[str, str]:
    """Parseia arquivo de checksums (formato: sha256  filename)."""
    checksums = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            sha = parts[0].lower()
            filename = parts[1].lstrip("*")
            checksums[filename] = sha
    return checksums


def find_matching_asset(release: Dict, platform: str, skill_name: str) -> Optional[Dict]:
    """Encontra asset compatível com o OS atual."""
    assets = release.get("assets", [])
    if not assets:
        return None

    patterns = CONFIG["asset_patterns"].get(platform, [])
    if not patterns:
        return None

    # Tenta match exato primeiro
    for asset in assets:
        name = asset.get("name", "")
        for pattern in patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return asset

    # Fallback: primeiro asset que NÃO seja "Source code" (GitHub auto-generated)
    for asset in assets:
        name = asset.get("name", "").lower()
        # Skip GitHub's auto-generated source archives
        if "source code" in name or name.startswith("src"):
            continue
        # This is likely the binary
        return asset

    return None


def verify_checksum(filepath: Path, expected_sha256: str) -> bool:
    """Verifica SHA256 do arquivo."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest().lower() == expected_sha256.lower()


def download_with_retry(
    url: str,
    dest: Path,
    quiet: bool = False,
    json_mode: bool = False,
) -> bool:
    """Baixa com retry exponencial e resume (curl -C -)."""
    max_attempts = CONFIG["retry"]["max_attempts"]
    backoff_base = CONFIG["retry"]["backoff_base"]
    backoff_max = CONFIG["retry"]["backoff_max"]
    download_timeout = CONFIG["timeouts"]["download"]

    for attempt in range(1, max_attempts + 1):
        try:
            if not quiet:
                log(f"Baixando {dest.name} (tentativa {attempt}/{max_attempts})...", "PROGRESS", quiet, json_mode)

            # Resume se arquivo parcial existe
            resume_flag = ["-C", "-"] if dest.exists() and dest.stat().st_size > 0 else []

            cmd = ["curl", "-L"] + resume_flag + ["-#", "-o", str(dest), url, "--max-time", str(download_timeout)]
            result = run_cmd(cmd, capture=False, timeout=download_timeout + 30, json_mode=json_mode)

            if result.returncode == 0 and dest.exists() and dest.stat().st_size > 0:
                if not quiet:
                    log(f"Download completo: {dest.name}", "OK", quiet, json_mode)
                return True

            # Falha — limpa arquivo parcial se configurado
            if CONFIG["cleanup"]["remove_failed_downloads"] and dest.exists():
                dest.unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            if not quiet:
                log(f"Timeout no download (tentativa {attempt}/{max_attempts})", "WARN", quiet, json_mode)
        except Exception as e:
            if not quiet:
                log(f"Erro no download: {e} (tentativa {attempt}/{max_attempts})", "WARN", quiet, json_mode)

        # Backoff exponencial antes da próxima tentativa
        if attempt < max_attempts:
            wait_time = min(backoff_base ** attempt, backoff_max)
            if not quiet:
                log(f"Aguardando {wait_time}s antes de retry...", "INFO", quiet, json_mode)
            time.sleep(wait_time)

    return False


def download_asset(asset: Dict, dest: Path, quiet: bool = False, json_mode: bool = False) -> bool:
    """Baixa asset via curl com retry/resume."""
    url = asset.get("browser_download_url")
    if not url:
        return False
    return download_with_retry(url, dest, quiet, json_mode)


def extract_asset(asset_path: Path, dest_dir: Path, binary_name: str, quiet: bool = False) -> Optional[Path]:
    """Extrai binário do asset (zip ou tar.gz)."""
    try:
        if asset_path.suffix == ".zip":
            import zipfile
            with zipfile.ZipFile(asset_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith(binary_name) or name == binary_name:
                        zf.extract(name, dest_dir)
                        extracted = dest_dir / name
                        if extracted != dest_dir / binary_name:
                            extracted.rename(dest_dir / binary_name)
                        return dest_dir / binary_name
        elif asset_path.suffix in {".gz", ".tgz"} or ".tar." in asset_path.name:
            import tarfile
            with tarfile.open(asset_path, 'r:*') as tf:
                for member in tf.getmembers():
                    if member.name.endswith(binary_name) or os.path.basename(member.name) == binary_name:
                        tf.extract(member, dest_dir)
                        extracted = dest_dir / member.name
                        if extracted != dest_dir / binary_name:
                            extracted.rename(dest_dir / binary_name)
                        return dest_dir / binary_name
        if not quiet:
            log(f"Binário '{binary_name}' não encontrado no asset", "WARN", quiet, False)
    except Exception as e:
        if not quiet:
            log(f"Falha na extração: {e}", "ERROR", quiet, False)
    return None


def process_skill(skill: SkillInfo, args, release: Dict, checksums: Dict[str, str]) -> Dict[str, Any]:
    """Processa uma skill: checa release, compara, baixa se necessário."""
    quiet = getattr(args, 'quiet', False)
    json_mode = getattr(args, 'json', False)
    dry_run = getattr(args, 'dry_run', False)

    # Versão atual
    current_version = get_current_version(skill)

    latest_tag = release.get("tag_name", "").lstrip("v")
    if not latest_tag:
        return {"skill": skill.name, "status": "error", "error": "no_tag", "details": "Release sem tag"}

    # Asset compatível
    platform = sys.platform
    asset = find_matching_asset(release, platform, skill.name)
    if not asset:
        return {"skill": skill.name, "status": "error", "error": "no_matching_asset",
                "details": f"Nenhum asset para {platform} no release {latest_tag}"}

    # Compara versões
    if current_version == latest_tag:
        return {"skill": skill.name, "status": "skipped", "version": current_version, "reason": "already_latest"}

    # Modo check-only
    if args.check_only:
        return {"skill": skill.name, "status": "update_available",
                "old_version": current_version, "new_version": latest_tag,
                "asset": asset.get("name")}

    # Modo dry-run: simula sem baixar
    if dry_run:
        return {"skill": skill.name, "status": "would_update",
                "old_version": current_version, "new_version": latest_tag,
                "asset": asset.get("name"), "asset_url": asset.get("browser_download_url")}

    # Baixa asset
    dist_dir = PROGRAMAS_DIR / skill.name
    dist_dir.mkdir(parents=True, exist_ok=True)
    asset_path = dist_dir / asset["name"]

    if not download_asset(asset, asset_path, quiet, json_mode):
        return {"skill": skill.name, "status": "error", "error": "download_failed"}

    # Checksum verification
    asset_sha256 = None
    if CONFIG["checksum"]["enabled"]:
        # 1. Tenta do arquivo de checksums baixado
        asset_name = asset.get("name", "")
        if asset_name in checksums:
            asset_sha256 = checksums[asset_name]
        # 2. Tenta do release asset metadata (raro)
        elif asset.get("sha256") or asset.get("digest"):
            asset_sha256 = asset.get("sha256") or asset.get("digest")
            if asset_sha256 and asset_sha256.startswith("sha256:"):
                asset_sha256 = asset_sha256[7:]

        if asset_sha256:
            if not verify_checksum(asset_path, asset_sha256):
                if not quiet:
                    log(f"Checksum falhou para {asset['name']}", "ERROR", quiet, json_mode)
                if CONFIG["cleanup"]["remove_failed_downloads"]:
                    asset_path.unlink(missing_ok=True)
                return {"skill": skill.name, "status": "error", "error": "checksum_mismatch"}
            elif not quiet:
                log(f"Checksum OK: {asset['name']}", "OK", quiet, json_mode)
        elif not quiet:
            log(f"Checksum não disponível para {asset['name']} — pulando verificação", "WARN", quiet, json_mode)

    # Extrai binário para skills/<skill>/bin/
    bin_dir = skill.path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    binary_path = bin_dir / skill.cli_binary

    extracted = extract_asset(asset_path, bin_dir, skill.cli_binary, quiet)
    if not extracted or not extracted.exists():
        if CONFIG["cleanup"]["remove_failed_downloads"]:
            asset_path.unlink(missing_ok=True)
        return {"skill": skill.name, "status": "error", "error": "binary_not_found",
                "details": f"Binário {skill.cli_binary} não extraído do asset"}

    # Torna executável
    extracted.chmod(0o755)

    # Verifica se binário roda
    test_result = run_cmd([str(extracted), skill.version_cmd], timeout=10, json_mode=json_mode)
    if test_result.returncode != 0:
        if not quiet:
            log(f"Binário extraído não executa: {test_result.stderr}", "WARN", quiet, json_mode)

    # Remove assets antigos (após sucesso)
    if CONFIG["cleanup"]["remove_old_assets"]:
        old_assets = list(dist_dir.glob("*"))
        for old in old_assets:
            if old != asset_path:
                old.unlink(missing_ok=True)
                if not quiet:
                    log(f"Removido antigo: {old.name}", "OK", quiet, json_mode)

    # Grava version.txt
    (skill.path / "version.txt").write_text(latest_tag + "\n")

    if not quiet:
        log(f"{skill.name}: {current_version} → {latest_tag} ✓", "OK", quiet, json_mode)

    return {
        "skill": skill.name,
        "status": "updated",
        "old_version": current_version,
        "new_version": latest_tag,
        "asset_downloaded": asset["name"],
        "binary_path": str(binary_path.relative_to(ROOT_DIR)),
        "dist_path": str(asset_path.relative_to(ROOT_DIR))
    }


# ─── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Update programs CLI binaries")
    parser.add_argument("--check-only", action="store_true", help="Só verifica, não atualiza")
    parser.add_argument("--update", action="store_true", help="Baixa e atualiza (padrão se nem --check-only)")
    parser.add_argument("--program", help="Filtrar só uma skill")
    parser.add_argument("--json", action="store_true", help="Output JSON limpo no stdout")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem baixar")
    parser.add_argument("--quiet", action="store_true", help="Menos output visual (progresso em stderr)")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    args = parser.parse_args()

    if not args.check_only and not args.update:
        args.update = True

    # Carrega skills
    skills: List[SkillInfo] = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name in SKIP_SKILLS:
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_frontmatter(skill_md)
        project_url = fm.get("project_url", "").strip()
        if not project_url:
            continue
        repo_info = extract_repo_info(project_url)
        if not repo_info:
            continue
        owner, repo = repo_info
        skills.append(SkillInfo(
            name=skill_dir.name,
            path=skill_dir,
            project_url=project_url,
            cli_binary=fm.get("cli_binary", f"{skill_dir.name}-cli"),
            version_cmd=fm.get("version_cmd", "--version"),
            owner=owner,
            repo=repo,
        ))

    if args.program:
        skills = [s for s in skills if s.name == args.program]
        if not skills:
            print(json.dumps({"status": "error", "errors": [{"skill": args.program, "error": "not_found"}]}))
            return 1

    if not skills:
        print(json.dumps({"status": "success", "updated": [], "skipped": [], "errors": [], "warnings": []}))
        return 0

    # Pré-busca releases e checksums (uma vez por skill)
    releases = {}
    all_checksums = {}
    for skill in skills:
        release = get_latest_release(skill.owner, skill.repo, args.json)
        if release:
            releases[skill.name] = release
            checksums = fetch_checksums_from_release(release, args.json)
            if checksums:
                all_checksums[skill.name] = checksums

    # Processa em paralelo
    updated = []
    skipped = []
    errors = []
    warnings = []
    would_update = []  # para dry-run

    max_workers = min(CONFIG["parallel_downloads"], len(skills))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_skill, s, args, releases.get(s.name, {}), all_checksums.get(s.name, {})): s
            for s in skills
        }
        for future in as_completed(futures):
            result = future.result()
            if result["status"] == "updated":
                updated.append(result)
            elif result["status"] == "skipped":
                skipped.append(result)
            elif result["status"] in ("update_available",):
                updated.append(result)
            elif result["status"] == "would_update":
                would_update.append(result)
            elif result["status"] == "error":
                errors.append(result)
            else:
                warnings.append(result)

    # Warnings para skills sem project_url
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and skill_dir.name in SKIP_SKILLS:
            warnings.append({"skill": skill_dir.name, "reason": "no_project_url"})

    output = ScriptOutput(
        status="success" if not errors else ("partial" if (updated or would_update) else "error"),
        platform=sys.platform,
        updated=updated,
        skipped=skipped,
        errors=errors,
        warnings=warnings,
        would_update=would_update
    )

    # JSON output: APENAS JSON no stdout
    if args.json:
        print(json.dumps(asdict(output), indent=2, ensure_ascii=False))
    else:
        # Output humano (vai para stdout)
        print(f"\nPlatform: {sys.platform}")
        print(f"Updated: {len(updated)} | Skipped: {len(skipped)} | Errors: {len(errors)}")
        for u in updated:
            print(f"  ✓ {u['skill']}: {u.get('old_version', '?')} → {u.get('new_version', u.get('new_version', '?'))}")
        for s in skipped:
            print(f"  ○ {s['skill']}: {s.get('version')} ({s.get('reason')})")
        for e in errors:
            print(f"  ✗ {e['skill']}: {e.get('error')} - {e.get('details')}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())