# 🌿 Happy Green

**Suas finanças, com mais leveza.** Gestão financeira pessoal com Python, Streamlit,
Programação Orientada a Objetos e PostgreSQL no Supabase.

> **Link público:** será registrado aqui depois de uma publicação efetivamente verificada.
> A aplicação exige uma conexão real com o Supabase. Sem configuração, apresenta uma
> tela de configuração inicial; não simula que os dados foram persistidos.

## Objetivo e escopo

Projeto acadêmico de POO para controlar contas, receitas, despesas e orçamentos mensais.
A versão inicial é uma **demonstração pública com dados fictícios compartilhados**:
todos os visitantes veem e podem modificar a mesma carteira. Não inserir dados pessoais.
Não inclui autenticação, integração bancária, transferências, pagamentos ou investimentos.

## Funcionalidades

- Contas financeiras: cadastro, edição, consulta de saldo e exclusão quando sem vínculos.
- Categorias de receitas e despesas, com validação dos relacionamentos.
- Lançamentos: cadastro, edição, exclusão e filtros combinados.
- Painel: saldo acumulado, receitas, despesas e resultado do mês.
- Orçamento por categoria e mês, com consumo e alerta de limite ultrapassado.
- Resumo mensal por categoria e gráfico das despesas.
- Dados demonstrativos carregados explicitamente, apenas com o banco vazio.
- Persistência PostgreSQL, sem dependência de arquivos temporários da hospedagem.

## Tecnologias

Python **3.12**, Streamlit, Psycopg 3, Pandas (apresentação), PostgreSQL/Supabase e pytest.
O arquivo `requirements.txt` fixa as versões principais; `requirements-lock.txt`
registra o ambiente completo utilizado nas verificações locais.

O servidor Python do Streamlit faz a conexão com o Supabase. O navegador nunca recebe
a senha do banco. A hospedagem proposta é Streamlit Community Cloud.

## Execução local

Requisitos: Python 3.12 e um projeto Supabase configurado.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edite `.streamlit/secrets.toml` com os dados do seu Supabase. Esse arquivo é ignorado
pelo Git. Não use as chaves de API `anon` ou `service_role` como senha PostgreSQL.

```toml
[database]
host = "host copiado de Connect > Session pooler"
port = 5432
dbname = "postgres"
user = "usuario copiado de Connect > Session pooler"
password = "sua senha PostgreSQL"
```

Execute `migrations/001_initial.sql` no SQL Editor do Supabase antes do primeiro uso.
Então inicie:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

No Linux/macOS, use `python3 -m venv .venv` e `.venv/bin/python` nos comandos.
Também são aceitas as variáveis `HAPPY_GREEN_DB_HOST`, `HAPPY_GREEN_DB_PORT`,
`HAPPY_GREEN_DB_DBNAME`, `HAPPY_GREEN_DB_USER` e `HAPPY_GREEN_DB_PASSWORD`.
Variáveis definidas substituem os respectivos valores do arquivo de segredos.
Um arquivo `.env` não é carregado automaticamente.

Na primeira abertura, cadastre conta/categorias ou clique em **Carregar demonstração**.
A carga cria uma receita de R$ 1.500,00, despesas de R$ 300,00 e R$ 120,00,
orçamento de alimentação de R$ 250,00 e saldo de R$ 1.080,00, no mês atual.

## Publicação

Siga [o guia completo de publicação](docs/PUBLICACAO.md). Resumo:

1. Publique este diretório como raiz de um repositório GitHub.
2. Configure o banco Supabase e aplique a migração SQL.
3. Em Streamlit Community Cloud, selecione repositório, branch `main` e
   arquivo de entrada `streamlit_app.py`.
4. Nas configurações avançadas, escolha Python 3.12 e informe a seção `[database]`
   no painel protegido de Secrets.
5. Publique e execute o roteiro de verificação pela URL HTTPS gerada.

A URL deve funcionar com o computador de desenvolvimento desligado.
O banco permanece no Supabase mesmo quando a hospedagem reinicia.

## POO e arquitetura

```text
streamlit_app.py          entrada
happy_green/
  domain.py              entidades e regras financeiras
  errors.py              exceções de aplicação
  ports.py               contrato de repositório e fotografia da carteira
  services.py            casos de uso e resumos
  repository.py          persistência PostgreSQL
  bootstrap.py           configuração e composição das dependências
  presentation.py        leitura e formatação monetária
  demo.py                criação explícita dos exemplos
  ui.py                  interface gráfica
migrations/              estrutura do banco versionada
tests/                   testes de domínio, serviços e interface
docs/                    documentação e roteiro de apresentação
```

`Lancamento` é abstrato. `Receita` retorna impacto positivo e `Despesa` retorna
impacto negativo ao sobrescrever `calcular_impacto_no_saldo()`. `ContaFinanceira`
calcula seu saldo chamando esse mesmo método em todos os lançamentos associados.
O cálculo não consulta o subtipo com `isinstance` nem troca o polimorfismo por `if`.

O repositório reconstrói objetos das subclasses ao ler o banco. Propriedades sem
setters protegem atributos validados nos construtores, conforme as convenções de
encapsulamento de Python. Serviços coordenam os casos de uso e as referências.

Veja o [diagrama e decisões](docs/ARQUITETURA.md) e o
[mapa dos critérios de avaliação](docs/AVALIACAO.md).

## Regras financeiras

- Moeda única: **BRL**. Entrada por texto, aceitando `1500,00`, `1.500,00` e `1500.00`.
- Cálculos: `Decimal`, duas casas, `ROUND_HALF_UP`; banco: `NUMERIC(14,2)`.
- Float é rejeitado no domínio; conversão para float só ocorre ao desenhar gráficos.
- Receitas/despesas estritamente positivas; sinal definido pelo método polimórfico.
- Saldo inicial pode ser negativo. Saldo atual = inicial + todos os impactos.
- Resultado mensal = receitas menos despesas do mês, sem incluir saldo inicial.
- Somente movimentações realizadas: datas futuras não são aceitas pela aplicação.
- Categoria tem tipo fixo enquanto houver lançamentos ou orçamentos vinculados.
- Exclusão de contas e categorias vinculadas é bloqueada também por chaves estrangeiras.
- Categoria/mês tem um único orçamento; salvar novamente atualiza o limite.
- Cada escrita usa transação. A carga demonstrativa inteira é atômica e serializada.
- Leituras da carteira usam uma fotografia consistente (`REPEATABLE READ`).

## Testes

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes de domínio e serviços não precisam de Supabase. Os testes de interface
usam o `AppTest` oficial do Streamlit e um repositório exclusivamente de teste,
definido em `tests/fakes.py`. A aplicação real sempre usa PostgreSQL.

Resultados realmente executados e limites de verificação ficam em
[docs/VERIFICACAO.md](docs/VERIFICACAO.md). O roteiro manual está em
[docs/APRESENTACAO.md](docs/APRESENTACAO.md).

## Desenvolvimento e integrantes

As 16 etapas em [docs/MISSOES.md](docs/MISSOES.md) são uma proposta de evolução;
os enunciados individuais oficiais das missões não foram fornecidos.

Responsável pelo repositório: conta GitHub que hospeda o projeto.
Integrantes, turma e contribuições individuais devem ser preenchidos pelo grupo em
[docs/INTEGRANTES.md](docs/INTEGRANTES.md). Desenvolvimento com assistência de IA;
o grupo deve revisar o código e compreender os conceitos antes da apresentação.

O exemplo didático de referência é a
[oficina mecânica do professor](https://github.com/cdpudi/oficina-mecanica).

## Limitações conhecidas

- Demonstração pública compartilhada, sem isolamento por visitante.
- Edições concorrentes do mesmo registro usam a última gravação bem-sucedida.
- Atualização entre visitantes é manual pelo botão **Atualizar dados**.
- A carteira inteira é carregada por sessão/interação: adequado ao escopo acadêmico,
  sem promessa de escala para grandes volumes.
- Disponibilidade e suspensão por inatividade dependem dos planos dos provedores.

