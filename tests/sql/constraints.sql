-- Verificação de integração: todos os registros criados aqui são revertidos.
BEGIN;
SET LOCAL TIME ZONE 'America/Sao_Paulo';
DO $test$
DECLARE
    conta uuid := gen_random_uuid();
    renda uuid := gen_random_uuid();
    comida uuid := gen_random_uuid();
    transporte uuid := gen_random_uuid();
    receita uuid := gen_random_uuid();
    despesa_comida uuid := gen_random_uuid();
    despesa_transporte uuid := gen_random_uuid();
    resultado numeric;
BEGIN
    INSERT INTO happy_green.contas(id,nome,saldo_inicial)
        VALUES (conta,'__verificacao_' || conta::text,0);
    INSERT INTO happy_green.categorias(id,nome,tipo) VALUES
        (renda,'__renda_' || renda::text,'RECEITA'),
        (comida,'__comida_' || comida::text,'DESPESA'),
        (transporte,'__transporte_' || transporte::text,'DESPESA');
    INSERT INTO happy_green.lancamentos(id,conta_id,categoria_id,tipo,descricao,valor,data) VALUES
        (receita,conta,renda,'RECEITA','Receita de teste',1500,CURRENT_DATE),
        (despesa_comida,conta,comida,'DESPESA','Comida de teste',300,CURRENT_DATE),
        (despesa_transporte,conta,transporte,'DESPESA','Transporte de teste',120,CURRENT_DATE);
    SELECT sum(CASE tipo WHEN 'RECEITA' THEN valor ELSE -valor END) INTO resultado
        FROM happy_green.lancamentos WHERE conta_id=conta;
    ASSERT resultado=1080, 'Saldo inicial incorreto';
    UPDATE happy_green.lancamentos SET valor=150 WHERE id=despesa_transporte;
    SELECT sum(CASE tipo WHEN 'RECEITA' THEN valor ELSE -valor END) INTO resultado
        FROM happy_green.lancamentos WHERE conta_id=conta;
    ASSERT resultado=1050, 'Saldo apos edicao incorreto';
    INSERT INTO happy_green.orcamentos(id,categoria_id,mes,limite)
        VALUES (gen_random_uuid(),comida,date_trunc('month',CURRENT_DATE)::date,250);
    SELECT sum(valor) INTO resultado FROM happy_green.lancamentos
        WHERE categoria_id=comida AND tipo='DESPESA';
    ASSERT resultado > (SELECT limite FROM happy_green.orcamentos WHERE categoria_id=comida),
        'Consumo deveria ultrapassar o limite';
    BEGIN
        INSERT INTO happy_green.orcamentos(id,categoria_id,mes,limite)
            VALUES (gen_random_uuid(),comida,date_trunc('month',CURRENT_DATE)::date,500);
        RAISE EXCEPTION 'Orcamento duplicado foi aceito';
    EXCEPTION WHEN unique_violation THEN NULL; END;
    BEGIN
        UPDATE happy_green.lancamentos SET valor=0 WHERE id=despesa_comida;
        RAISE EXCEPTION 'Valor zero foi aceito';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        UPDATE happy_green.lancamentos SET valor='NaN'::numeric WHERE id=despesa_comida;
        RAISE EXCEPTION 'NaN foi aceito';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        UPDATE happy_green.contas SET saldo_inicial='NaN'::numeric WHERE id=conta;
        RAISE EXCEPTION 'Saldo NaN foi aceito';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
        UPDATE happy_green.lancamentos SET categoria_id=renda WHERE id=despesa_comida;
        RAISE EXCEPTION 'Categoria de tipo incompativel foi aceita';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    BEGIN
        DELETE FROM happy_green.contas WHERE id=conta;
        RAISE EXCEPTION 'Conta vinculada foi excluida';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    BEGIN
        UPDATE happy_green.categorias SET tipo='RECEITA' WHERE id=comida;
        RAISE EXCEPTION 'Tipo de categoria vinculada foi alterado';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    BEGIN
        UPDATE happy_green.lancamentos SET data=CURRENT_DATE+1 WHERE id=receita;
        RAISE EXCEPTION 'Data futura foi aceita';
    EXCEPTION WHEN check_violation THEN NULL; END;
    DELETE FROM happy_green.lancamentos WHERE id=despesa_comida;
    SELECT sum(CASE tipo WHEN 'RECEITA' THEN valor ELSE -valor END) INTO resultado
        FROM happy_green.lancamentos WHERE conta_id=conta;
    ASSERT resultado=1350, 'Saldo apos exclusao incorreto';
END;
$test$;
SELECT '12 verificacoes de integridade aprovadas; dados de teste revertidos ao final' AS resultado;
ROLLBACK;
