-- Execute uma vez pelo SQL Editor do Supabase. Não expor happy_green na Data API.
BEGIN;

CREATE SCHEMA IF NOT EXISTS happy_green;
CREATE TABLE IF NOT EXISTS happy_green.schema_migrations (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS happy_green.contas (
    id uuid PRIMARY KEY,
    nome varchar(80) NOT NULL CHECK (length(btrim(nome)) > 0),
    saldo_inicial numeric(14,2) NOT NULL DEFAULT 0
        CHECK (abs(saldo_inicial) <= 999999999999.99),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS contas_nome_unique
    ON happy_green.contas (lower(btrim(nome)));

CREATE TABLE IF NOT EXISTS happy_green.categorias (
    id uuid PRIMARY KEY,
    nome varchar(80) NOT NULL CHECK (length(btrim(nome)) > 0),
    tipo text NOT NULL CHECK (tipo IN ('RECEITA','DESPESA')),
    UNIQUE (id,tipo)
);
CREATE UNIQUE INDEX IF NOT EXISTS categorias_nome_tipo_unique
    ON happy_green.categorias (lower(btrim(nome)),tipo);

CREATE TABLE IF NOT EXISTS happy_green.lancamentos (
    id uuid PRIMARY KEY,
    conta_id uuid NOT NULL REFERENCES happy_green.contas(id) ON DELETE RESTRICT,
    categoria_id uuid NOT NULL,
    tipo text NOT NULL CHECK (tipo IN ('RECEITA','DESPESA')),
    descricao varchar(160) NOT NULL CHECK (length(btrim(descricao)) > 0),
    valor numeric(14,2) NOT NULL CHECK (valor > 0 AND valor <= 999999999999.99),
    data date NOT NULL CHECK (data BETWEEN DATE '1900-01-01' AND DATE '2100-12-31'
        AND data <= CURRENT_DATE),
    FOREIGN KEY (categoria_id,tipo) REFERENCES happy_green.categorias(id,tipo)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS lancamentos_periodo ON happy_green.lancamentos(data);
CREATE INDEX IF NOT EXISTS lancamentos_conta ON happy_green.lancamentos(conta_id);
CREATE INDEX IF NOT EXISTS lancamentos_categoria ON happy_green.lancamentos(categoria_id);

CREATE TABLE IF NOT EXISTS happy_green.orcamentos (
    id uuid PRIMARY KEY,
    categoria_id uuid NOT NULL,
    tipo text NOT NULL DEFAULT 'DESPESA' CHECK (tipo = 'DESPESA'),
    mes date NOT NULL CHECK (EXTRACT(DAY FROM mes) = 1
        AND mes BETWEEN DATE '1900-01-01' AND DATE '2100-12-31'),
    limite numeric(14,2) NOT NULL CHECK (limite > 0 AND limite <= 999999999999.99),
    FOREIGN KEY (categoria_id,tipo) REFERENCES happy_green.categorias(id,tipo)
        ON DELETE RESTRICT ON UPDATE RESTRICT,
    UNIQUE (categoria_id,mes)
);

-- Browser/anon/authenticated não acessam o schema; o servidor usa a conexão PG.
REVOKE ALL ON SCHEMA happy_green FROM PUBLIC, anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA happy_green FROM PUBLIC, anon, authenticated;

-- Defesa adicional: acesso por Data API permanece negado, inclusive se houver
-- exposição acidental do schema. O servidor usa a conexão PG com papel proprietário.
ALTER TABLE happy_green.contas ENABLE ROW LEVEL SECURITY;
ALTER TABLE happy_green.categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE happy_green.lancamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE happy_green.orcamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE happy_green.schema_migrations ENABLE ROW LEVEL SECURITY;

INSERT INTO happy_green.schema_migrations(version) VALUES (1) ON CONFLICT DO NOTHING;
COMMIT;
