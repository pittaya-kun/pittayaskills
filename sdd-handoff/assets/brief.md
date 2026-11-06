# Brief — <slug>

Uma página no máximo. Descreve o quê e o porquê; nunca o como.

```
objetivo: <1–2 linhas>
entregáveis:
  - arquivo: <nome.ext> | formato: <PDF se omitido> | dimensões/páginas: <...>
restrições: <marca, fontes, cores, sangria, prazo>
fora_de_escopo: <...>
aceite:        # checks objetivos; preferir os que um script consegue verificar
  - [ ] <...>
abertas:       # perguntas sem resposta; nunca supor
  - <...>
```

Regras:
- Valores exatos em vez de adjetivos: "A5, sangria 3 mm, 300 dpi", não "bom e limpo". (só o que é mensurável pode ser conferido)
- Cada item de `aceite` deve ter resposta sim ou não.
- Dúvida sem resposta vai para `abertas`, não para o texto do objetivo.
