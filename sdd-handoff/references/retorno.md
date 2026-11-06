# Retorno — <slug> · rodada <n>

Preenchido pelo operador. Máximo de uma página; só o que mudou ou falhou merece texto.

```
<retorno slug="<slug>" rodada="<n>">
  <resumo><1 linha></resumo>
  <tarefas>
    T1 | ok | arquivos: <caminhos> | checks: <resultado objetivo> | custo: <baixo|médio|alto>
    T2 | ajustado | arquivos: <...> | checks: <...> | desvio: <N1: o quê e por quê> | custo: <...>
    T3 | bloqueado | causa: <...> | custo: <...>
  </tarefas>
  <pendencias><o que falta ou depende de decisão do usuário, em perguntas objetivas></pendencias>
  <entrega><arquivos finais em entrega/, quando concluído></entrega>
</retorno>
```

Regras:
- Status: `ok`, `ajustado` (houve N1) ou `bloqueado` (N2 ou falha após a nova tentativa).
- O campo `desvio` só aparece quando houve desvio; omitir blocos vazios.
- Checks em resultado observável (ex.: "2 páginas, 320 dpi, fontes embutidas"), não em "conferido".
