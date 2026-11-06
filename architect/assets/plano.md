# Plano — <slug>

Pertence ao planejador. O usuário aprova antes de gerar o pacote (gate único).

aprovado: não

| id | skill | ação | entrada | saída | check | custo | depende |
|----|-------|------|---------|-------|-------|-------|---------|
| T1 | <programa> | <verbo + objeto> | <arquivo> | work/<arquivo> | <check objetivo> | baixo | — |

Regras:
- Uma ação por tarefa; a saída é sempre um arquivo.
- Check objetivo e, se possível, executável por script.
- Custo: baixo | médio | alto (estimativa). Cortar ou justificar em uma linha os altos antes de aprovar.
- Agrupar na mesma rodada as tarefas que já podem rodar. (cada rodada recarrega contexto; menos rodadas, menos tokens)
- Tarefa que depende de pergunta em aberto fica para a rodada seguinte.
- Pedido trivial dispensa brief e plano (caminho rápido): vai direto à skill do programa.
