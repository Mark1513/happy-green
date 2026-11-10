# Roteiro de apresentação (8 a 12 minutos)

Use apenas dados fictícios. Para repetir a carga inicial, utilize um projeto de
demonstração separado e vazio; a aplicação não oferece reset global automático.

1. **Objetivo (1 min):** apresentar Happy Green e os problemas resolvidos.
2. **Link público (1 min):** abrir a aplicação pelo navegador de outro dispositivo.
3. **Contas/categorias (1 min):** explicar composição da carteira e tipos.
4. **Movimentações (2 min):** mostrar os dados demonstrativos e filtros.
5. **Orçamento (1 min):** alimentação de 300 diante de limite de 250 gera alerta.
6. **Editar/excluir (1 min):** executar o cenário abaixo e observar os resultados.
7. **POO (2 min):** mostrar Lancamento abstrato, Receita/Despesa, métodos e cálculo do saldo.
8. **Persistência/testes (1 a 2 min):** reabrir a página, mostrar testes e diagrama.

## Cenário e resultados esperados

| Operação | Resultado esperado |
| --- | --- |
| Conta inicial zero + receita 1.500 | saldo 1.500 |
| Alimentação 300 + transporte 120 | saldo 1.080 |
| Orçamento alimentação 250 | alerta de excesso de 50 |
| Editar transporte de 120 para 150 | saldo 1.050 |
| Excluir alimentação de 300 | saldo 1.350 e orçamento sem excesso |
| Atualizar página e reabrir em outra sessão | manter registros e saldo 1.350 |
| Registrar valor zero/negativo | validação compreensível, sem gravar |
| Excluir conta com lançamentos | operação bloqueada, dados preservados |
| Trocar tipo de categoria vinculada | operação bloqueada pelo relacionamento |
| Reabrir após reinício da aplicação | dados permanecem no Supabase |

## Perguntas que o grupo deve saber responder

- Onde o saldo é calculado e por que não é uma coluna atualizada manualmente?
- Como o mesmo método produz comportamentos diferentes em Receita e Despesa?
- Por que Decimal foi escolhido?
- O que acontece se a interface for substituída?
- Que regras também são protegidas pelo banco?
- Qual a diferença entre saldo acumulado e resultado mensal?
- Como os dados sobrevivem à reexecução do Streamlit?
- Qual a diferença entre código preparado e publicação verificada?
