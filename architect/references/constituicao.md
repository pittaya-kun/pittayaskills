# Constituição de design

Regras fixas, lidas por planejador e operador. Manter abaixo de 50 linhas. O motivo de cada regra vem entre parênteses: ele ajuda a decidir casos que a regra não previu.

<entrega>
- Formato padrão: PDF, salvo indicação no brief. (evita perguntar de novo)
- Devolver somente os arquivos pedidos: sem prévias, sem lista de scripts, sem extras. (cada extra custa leitura e atenção)
- Intermediários em `work/`; apenas o pedido em `entrega/`.
</entrega>

<estrutura_projeto>
projetos/<slug>/
  brief.md · plano.md · pacote.md · retorno.md · log.md
  work/ · entrega/
log.md: só anexar, uma linha por evento (ex.: `R1 T1 ok baixo`).
</estrutura_projeto>

<economia_tokens>
- Tarefa determinística (converter, redimensionar, aplicar template) vira comando ou script. (o modelo gasta tokens; o script não)
- Verificar por script (dimensões, páginas, fontes embutidas, DPI, texto estourando caixa) antes de olhar qualquer imagem. (imagem custa muito mais que texto)
- Inspeção visual: um render por vez, em baixa resolução, só no final ou quando um check falhar.
- Ler só o trecho necessário; não reler o que já está no plano ou no log.
- Ajuste = edição pontual, nunca reescrever o arquivo inteiro.
- Estado em arquivos, não na conversa.
- Operador: responder somente com o retorno, sem narração e sem recapitular o pacote.
- No máximo uma nova tentativa por tarefa; depois marcar `bloqueado` com a causa. (evita laços caros)
</economia_tokens>

<politica_desvio>
- N0: executar exatamente como escrito.
- N1: ajuste menor dentro do objetivo (parâmetro, caminho, nome). Fazer e registrar no retorno.
- N2: muda entregável, escopo, ferramenta ou custo relevante. Parar essa tarefa e devolver a pergunta objetiva em `pendencias`.
- Em dúvida entre N1 e N2, tratar como N2. (desvio silencioso custa mais que uma pergunta)
</politica_desvio>

<marca_estilo>
(preencher por projeto ou cliente: fontes, cores, margens, sangria)
</marca_estilo>

<limites>
- Pergunta em aberto no brief: não executar a tarefa afetada e devolvê-la em `pendencias`; nunca supor a resposta.
- Entregar sempre no formato e na pasta combinados.
- Antes de fechar a rodada, conferir cada `check` do pacote e relatar só o resultado.
</limites>
