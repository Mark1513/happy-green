# Publicação do Happy Green

## 1. Supabase

Crie um projeto no plano adequado à demonstração. Salve a senha PostgreSQL em local
protegido. Se a plataforma pedir criação ou troca de senha, o titular deve fazer isso
diretamente no painel; não é necessário enviá-la pelo chat.

Abra SQL Editor, cole e execute `migrations/001_initial.sql` e depois
`migrations/20261110040438_finance_foreign_key_indexes.sql`. A primeira é uma migração
transacional identificada por versão. `CREATE IF NOT EXISTS` permite reaplicar a
criação inicial sem apagar os dados; isso não substitui novas migrações quando o
modelo for alterado. Para mudanças futuras, gere o arquivo com
`supabase migration new nome_descritivo`, confira o SQL e mantenha a ordem de aplicação.

O schema `happy_green` não deve estar na lista de schemas expostos pela Data API.
A aplicação usa uma conexão PostgreSQL no servidor. A migração revoga acesso de
`PUBLIC`, `anon` e `authenticated` ao schema/tabelas. Uma credencial de aplicação
dedicada pode receber apenas os privilégios necessários; a carga de demonstração
usa bloqueios de tabelas e exige permissão para essas operações.

Em **Connect → Session pooler**, copie exatamente host, porta e usuário. O usuário
do pooler normalmente contém a referência do projeto. Não derive host/região
manualmente. A conexão tem `sslmode=require` e tempo limite de 10 segundos.

## 2. GitHub

Use a raiz deste projeto como raiz do repositório. Antes do envio:

```powershell
git status --short
git check-ignore .streamlit/secrets.toml
```

Nunca adicione o arquivo real de segredos. O arquivo `.example` é intencionalmente
versionado e contém apenas instruções. O `.venv` também fica fora do repositório.

## 3. Streamlit Community Cloud

1. Entre em https://share.streamlit.io/ e selecione criação de aplicativo a partir
   de um repositório existente.
2. Selecione o repositório Happy Green e a branch `main`.
3. Informe `streamlit_app.py` como arquivo de entrada.
4. Escolha Python **3.12** nas opções avançadas.
5. No painel **Secrets**, preencha:

```toml
[database]
host = "HOST_REAL_DO_SESSION_POOLER"
port = 5432
dbname = "postgres"
user = "USUARIO_REAL_DO_POOLER"
password = "SENHA_POSTGRESQL"
```

6. Publique. Use o subdomínio disponível que a plataforma aceitar. Somente depois
   de confirmar o resultado, registre a URL real no README.
7. Verifique que o compartilhamento permite o acesso público solicitado.

Não é necessário Docker ou servidor Java. O Streamlit Community Cloud executa o
Python com as dependências de `requirements.txt`. Atualizações publicadas na branch
selecionada são utilizadas pela hospedagem.

## 4. Primeira verificação

Abra a URL gerada. Se aparecer configuração pendente, a publicação da interface
ocorreu, mas o sistema ainda não está operacional. Confira os Secrets e a migração.

Com o banco conectado, carregue explicitamente a demonstração. Verifique saldo,
orçamentos, edição e exclusão conforme `APRESENTACAO.md`. Reabra em outro dispositivo
e confirme que os dados permanecem disponíveis com o computador local desligado.

## 5. Diagnóstico

| Sintoma | Verificação |
| --- | --- |
| Tela de configuração | Seção `[database]`, nomes das propriedades e Secrets salvos |
| Falha de conexão | Host/usuário exatos do Session Pooler, senha PG e projeto ativo |
| Estrutura não criada | Migração 001 executada no projeto correto |
| Nome duplicado | Nomes são únicos sem diferenciar maiúsculas/minúsculas |
| Exclusão bloqueada | A conta/categoria ainda possui vínculos |
| Demonstração recusada | O banco já contém registros; nenhuma carga automática é feita |
| Outro visitante não vê alteração | Use Atualizar dados |
| Demora na primeira abertura | Confira estado e limites de inatividade da hospedagem |

Consulte os logs pelo painel administrativo da aplicação no Streamlit Cloud.
A aplicação registra a classe do erro PostgreSQL sem imprimir senha ou parâmetros
financeiros. Não publique capturas de logs ou painéis que revelem credenciais.

## 6. Planos e disponibilidade

Confirme no painel as condições atuais de cada serviço antes de contratar ou mudar
de plano. Não há contratação paga prevista neste projeto. Planos gratuitos podem
ter suspensão por inatividade e limites de recursos; abra e confira a aplicação
antes da apresentação. Isso não deve ser contornado por mecanismos artificiais
de tráfego. O armazenamento permanente fica no Supabase.

Referências oficiais: [deploy Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy),
[Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management),
[conexão Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres).
