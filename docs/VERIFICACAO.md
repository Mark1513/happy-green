# Verificação

Resultados observados em **10/11/2026**, durante o desenvolvimento assistido.

- Python 3.12.14; Streamlit 1.67.0; Psycopg 3.3.8; pytest 9.2.0.
- `python -m pytest -q`: **51 testes aprovados**, incluindo domínio, serviços e
  navegação/formulários pelo AppTest. Última execução após ajuste visual: 3,86 s.
- A verificação ampliada reproduziu a mudança indesejada de seleção após editar
  um lançamento; chaves estáveis corrigiram a seleção em contas, categorias,
  lançamentos e orçamento. O teste de edição/exclusão confirma o registro correto.
- Migração inicial aplicada ao projeto **Happy Green 1** no Supabase.
- Script SQL transacional: **12 verificações aprovadas**, incluindo saldos de 1.080,
  1.050 e 1.350, consumo acima do orçamento, unicidade de
  orçamento, tipos de categorias, vínculos, valores inválidos e datas futuras.
  Os registros de teste foram revertidos.
- Segunda migração aplicada: índices compostos cobrindo as chaves estrangeiras.
  A revisão de desempenho deixou apenas o aviso informativo de índice de período
  ainda não utilizado, esperado em uma demonstração recém-criada:
  https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index
- RLS habilitado nas cinco tabelas; schema privado, sem grants para anon/authenticated.
- O aviso informativo RLS sem políticas é intencional: o acesso pela Data API é
  negado; o servidor acessa pelo papel PostgreSQL proprietário. Referência:
  https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy
- **Aplicação publicada:** https://happy-green-mark1513.streamlit.app/
- Streamlit Community Cloud com Secrets preenchidos diretamente pelo titular.
- Conexão real com o Supabase confirmada pela leitura da carteira vazia e pela
  carga de demonstração acionada na interface publicada.
- Após a carga: 1 conta, 4 categorias, 3 lançamentos, 1 orçamento; saldo R$ 1.080,00,
  receitas R$ 1.500,00, despesas R$ 420,00 e alerta de excesso de R$ 50,00.
- Compartilhamento: opção **Make this app public** observada como habilitada.
- Reabertura da página confirmada: os três lançamentos e o saldo de R$ 1.080,00
  continuaram disponíveis, sem repetir a carga de demonstração.

Resultados esperados estão em APRESENTACAO.md e não representam, por si só, evidências
de execução em produção.
