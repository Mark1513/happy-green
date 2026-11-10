# Critérios de avaliação e evidências

| Critério | Onde observar |
| --- | --- |
| Execução de ponta a ponta | README, publicação e roteiro em APRESENTACAO.md |
| Funcionalidades principais | ui.py, services.py, tests/test_services.py e test_ui.py |
| Validações e consistência | domain.py, errors.py, restrições em migrations/001_initial.sql |
| Cenários reais | carga explícita demo.py e cenário de R$ 1.080 → 1.050 → 1.350 |
| Classes, atributos e métodos | ContaFinanceira, Categoria, Lancamento e OrcamentoMensal em domain.py |
| Construtores | __init__ com validação e propriedades sem setters |
| Relacionamentos | associação dos lançamentos a conta/categoria e fotografia Carteira |
| Herança e sobrescrita | Lancamento → Receita/Despesa |
| Polimorfismo | ContaFinanceira.calcular_saldo e ServicoFinanceiro.resumir |
| Abstração | ABC/abstractmethod em domínio e contrato do repositório |
| Separação de responsabilidades | domain/services/repository/ui/bootstrap/presentation |
| Exceções | ValidationError, ConflictError, NotFoundError, PersistenceError |
| Persistência Supabase | repository.py, migração e Secrets da hospedagem |
| GitHub e commits | histórico real do repositório; nomes do grupo em INTEGRANTES.md |
| README e reprodução | README.md e PUBLICACAO.md |
| Testes e evidências | tests/ e VERIFICACAO.md |
| Diagrama coerente | ARQUITETURA.md |

As evidências de execução devem ser distinguidas de verificações ainda pendentes.
O enunciado integral das 16 missões não foi disponibilizado: a lista de etapas é
uma proposta de organização, sem alegação de equivalência às missões oficiais.
