BEGIN;
CREATE INDEX IF NOT EXISTS lancamentos_categoria_tipo
    ON happy_green.lancamentos(categoria_id,tipo);
CREATE INDEX IF NOT EXISTS orcamentos_categoria_tipo
    ON happy_green.orcamentos(categoria_id,tipo);
-- O índice composto cobre também consultas somente por categoria.
DROP INDEX IF EXISTS happy_green.lancamentos_categoria;
INSERT INTO happy_green.schema_migrations(version) VALUES (2) ON CONFLICT DO NOTHING;
COMMIT;
