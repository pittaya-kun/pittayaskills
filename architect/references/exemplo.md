# Exemplo ilustrativo (não carregar nas skills)

Convite A5 de lançamento de livro, em duas rodadas. Mostra como os documentos se encadeiam.

## brief.md
```
objetivo: convite A5 frente e verso para lançamento de livro, impressão em gráfica
entregáveis:
  - arquivo: convite.pdf | formato: PDF/X-4 | dimensões/páginas: A5, 2 páginas, sangria 3 mm
restrições: fontes Playfair Display e Inter; paleta azul-marinho e creme; foto da capa fornecida (capa.jpg)
fora_de_escopo: versão para redes sociais
aceite:
  - [ ] 2 páginas A5 com sangria de 3 mm
  - [ ] fontes embutidas
  - [ ] imagens com 300 dpi ou mais
  - [ ] nenhum texto estourando caixa
abertas:
  - data e local do evento (aguardar texto final)
```

## plano.md
aprovado: sim

| id | skill | ação | entrada | saída | check | custo | depende |
|----|-------|------|---------|-------|-------|-------|---------|
| T1 | photocraft | tratar capa (recorte e cor leve) | capa.jpg | work/capa-tratada.jpg | ≥ 300 dpi no tamanho final | baixo | — |
| T2 | designcraft | montar frente e verso A5 | brief + capa-tratada.jpg + texto final | work/convite.idml | 2 páginas, sem overflow | médio | T1, texto |
| T3 | designcraft | exportar PDF/X-4 | work/convite.idml | entrega/convite.pdf | fontes embutidas, sangria 3 mm | baixo | T2 |

## pacote.md — rodada 1
```
<pacote slug="convite" rodada="1">
  <objetivo>convite A5 frente e verso para lançamento de livro</objetivo>
  <entregaveis>convite.pdf, PDF/X-4, A5, 2 páginas, sangria 3 mm</entregaveis>
  <tarefas>
    T1 | photocraft | tratar capa | in: capa.jpg | out: work/capa-tratada.jpg | check: >= 300 dpi no tamanho final | custo: baixo
  </tarefas>
  <orcamento>baixo</orcamento>
  <excecoes_desvio>nenhuma</excecoes_desvio>
  <autorizacoes>photocraft, designcraft</autorizacoes>
  <acao>Execute as tarefas na ordem, conforme a skill design-operator, e grave o resultado em projetos/convite/retorno.md.</acao>
</pacote>
```
T2 e T3 ficam de fora: dependem do texto final (pergunta em aberto).

## retorno.md — rodada 1
```
<retorno slug="convite" rodada="1">
  <resumo>capa tratada</resumo>
  <tarefas>
    T1 | ok | arquivos: work/capa-tratada.jpg | checks: 320 dpi no tamanho final | custo: baixo
  </tarefas>
  <pendencias>Qual é o texto final (data e local) para liberar T2?</pendencias>
</retorno>
```
Na rodada 2, o planejador recebe o texto, gera um novo pacote com T2 e T3 e o ciclo se repete até a entrega.
