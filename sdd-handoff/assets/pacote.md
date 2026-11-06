# Pacote de operação — <slug> · rodada <n>

Contém dados, não regras. O comportamento do operador vive na skill `design-operator` e na constituição, instaladas e idênticas entre rodadas; não colar regras aqui. (prefixo estável aproveita cache; só o pacote muda)

```
<pacote slug="<slug>" rodada="<n>">
  <objetivo><1–2 linhas, vindas do brief></objetivo>
  <entregaveis><arquivo, formato, dimensões></entregaveis>
  <tarefas>
    T1 | <skill> | <ação> | in: <...> | out: <...> | check: <...> | custo: <...>
  </tarefas>
  <orcamento><teto total estimado; ao estourar, tratar como N2></orcamento>
  <excecoes_desvio><tarefas em que N1 é proibido, ou "nenhuma"></excecoes_desvio>
  <autorizacoes><programas que o usuário já autorizou, ex.: photocraft, designcraft; ou "nenhuma"></autorizacoes>
  <acao>Execute as tarefas na ordem, conforme a skill design-operator, e grave o resultado em projetos/<slug>/retorno.md.</acao>
</pacote>
```

Regras:
- Só as tarefas desta rodada, com os ids do plano preservados.
- A instrução de ação fica por último, depois dos dados.
- `autorizacoes` lista só os programas que o usuário aprovou ao aprovar o plano. O operador não pergunta de novo por eles e trata qualquer outro como N2.
