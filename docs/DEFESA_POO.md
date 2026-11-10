# Happy Green: guia de apresentação e defesa de POO

Roteiro para aproximadamente 10 minutos, com 11 slides e demonstração ao vivo. Os tempos são uma proposta e podem ser ajustados ao limite da disciplina.

Aplicação: https://happy-green-mark1513.streamlit.app/

Repositório: https://github.com/Mark1513/happy-green

Base do mapeamento: código do commit 4c116986b262f1c33cef5affdcfda4e4885e43de. As falas abaixo são sugestões para ensaio. Preencham os nomes dos integrantes e relatem apenas contribuições reais.

## Mapa dos conceitos no código

| Conceito | Onde aparece | Como explicar |
| --- | --- | --- |
| Classes | [ContaFinanceira, Categoria, Lancamento, Receita, Despesa e OrcamentoMensal](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L68) | A classe reúne dados e comportamentos de um tipo do domínio. |
| Objetos | [Instâncias criadas na carga de demonstração](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/demo.py#L12) | Minha carteira é um objeto de ContaFinanceira. |
| Atributos e métodos | [_nome, _saldo_inicial e calcular_saldo](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L69) | Atributos guardam estado e métodos representam comportamentos. |
| Inicialização | [__init__ e super().__init__(id)](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L69) | __init__ inicializa a instância e as funções de validação protegem os dados. |
| Encapsulamento | [Atributos com _ e propriedades sem setters](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L74) | O acesso público usa propriedades. O sublinhado indica uma convenção de API interna. |
| Abstração | [Lancamento com ABC e abstractmethod](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L107) | A classe abstrata define o contrato comum para lançamentos. |
| Herança | [Receita(Lancamento) e Despesa(Lancamento)](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L155) | As especializações aproveitam estado e validações definidos na classe base. |
| Sobrescrita | [Implementações de calcular_impacto_no_saldo](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L160) | Receita retorna valor e Despesa retorna -valor. |
| Polimorfismo | [ContaFinanceira.calcular_saldo](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L82) | A mesma chamada executa o comportamento da classe real do objeto. |
| Associação | [Lancamento recebe conta e categoria](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L108) | Os objetos mantêm referências entre si. |
| Agregação | [Carteira agrupa referências em tuplas](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/ports.py#L11) | As entidades existem independentemente dessa fotografia. |
| Contrato de persistência | [RepositorioFinanceiro e RepositorioPostgres](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/ports.py#L18) | O serviço utiliza uma abstração e o adaptador fornece a implementação. |
| Injeção de dependência | [ServicoFinanceiro recebe repositorio](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/services.py#L30) | A implementação é fornecida ao inicializar o serviço. |
| Exceções | [ValidationError e HappyGreenError](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/errors.py#L1) | O domínio comunica um erro e a interface apresenta a mensagem. |
| Métodos estáticos | [filtrar e resumir](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/services.py#L91) | São operações que não dependem do estado de uma instância do serviço. |
| Persistência | [Reconstrução de Receita e Despesa na leitura](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/repository.py#L63) | As linhas do banco voltam a ser objetos com comportamento. |

## Distinção importante sobre composição

O relacionamento de Carteira com as entidades representa agregação de referências. Não defendam posse exclusiva ou destruição em cascata de objetos, pois isso não é o que o código implementa. O diagrama atualizado usa losangos vazios. O enunciado pede relacionamentos e colaboração entre objetos, que aparecem nas associações de Lancamento e no agrupamento Carteira.

## A explicação central em uma frase

A conta solicita o impacto de cada lançamento, e cada objeto responde conforme sua classe: Receita devolve um valor positivo e Despesa devolve um valor negativo. Essa colaboração aplica polimorfismo ao cálculo do saldo.

## Slide 1: Happy Green

Tempo sugerido: 20 s.

**Fala para ensaiar**

O Happy Green é um sistema de gestão financeira pessoal. O projeto aplica orientação a objetos nas regras de contas, receitas, despesas e orçamentos. Vamos mostrar o sistema funcionando e depois localizar esses conceitos no código. A interface usa Streamlit e os dados ficam no PostgreSQL do Supabase.

**O que mostrar**

Apresente o nome do projeto e abra o link público em uma aba separada.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/README.md).

## Slide 2: O sistema em funcionamento

Tempo sugerido: 30 s.

**Fala para ensaiar**

A pessoa cadastra suas contas e categorias, registra entradas e saídas e acompanha seu resultado mensal. O painel mostra tanto o saldo acumulado quanto o resultado do mês. Orçamentos permitem comparar o gasto de uma categoria com um limite. A versão publicada é uma demonstração com dados fictícios compartilhados entre visitantes. O endereço público permite apresentar a aplicação sem instalar programas no computador do professor.

**O que mostrar**

Mostre rapidamente o painel e a navegação, sem percorrer todos os formulários.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/README.md).

## Slide 3: Classes, objetos, atributos e métodos

Tempo sugerido: 45 s.

**Fala para ensaiar**

Classe é a definição de um tipo de objeto. ContaFinanceira define os dados e comportamentos de uma conta. Quando executamos ContaFinanceira com o nome Minha carteira e saldo inicial zero, criamos uma instância concreta. O nome e o saldo inicial são atributos dessa instância. calcular_saldo é um método, porque representa um comportamento da conta. Outras classes importantes são Categoria, Receita, Despesa e OrcamentoMensal. Os objetos colaboram para representar uma situação financeira real.

**O que mostrar**

Abra domain.py na classe ContaFinanceira e demo.py na linha que cria Minha carteira.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L68).

## Slide 4: Inicialização e encapsulamento

Tempo sugerido: 50 s.

**Fala para ensaiar**

Em Python, __init__ inicializa a instância. Nosso inicializador chama super para inicializar o identificador herdado, valida o nome e converte o saldo inicial para Decimal. Os atributos internos usam um sublinhado por convenção. As propriedades permitem consultar os valores sem oferecer setters públicos. Atribuir diretamente a conta.saldo_inicial gera AttributeError. O sublinhado não cria privacidade absoluta em Python. Nas edições, o serviço constrói um novo objeto validado com o mesmo identificador, preservando a identidade do registro.

**O que mostrar**

Aponte __init__, super(), _saldo_inicial e @property. Relacione ao teste de encapsulamento.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L69).

## Slide 5: Abstração e herança

Tempo sugerido: 55 s.

**Fala para ensaiar**

Lancamento representa o que receitas e despesas têm em comum: conta, categoria, descrição, valor e data. Ele herda a identidade de Entidade e usa ABC para declarar um contrato abstrato. O método calcular_impacto_no_saldo é abstrato, assim como a propriedade tipo. As subclasses Receita e Despesa completam esse contrato. A classe abstrata não pode ser instanciada diretamente. Essa organização centraliza as validações compartilhadas e permite especializar o comportamento financeiro.

**O que mostrar**

Mostre Lancamento, o decorador abstractmethod e as declarações Receita(Lancamento) e Despesa(Lancamento).

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L107).

## Slide 6: Polimorfismo no cálculo do saldo

Tempo sugerido: 75 s.

**Fala para ensaiar**

Aqui está o principal exemplo de polimorfismo do projeto. Receita devolve o valor positivo e Despesa devolve o valor negativo ao implementar o mesmo método. A conta percorre os lançamentos associados e chama calcular_impacto_no_saldo em cada objeto. O comportamento escolhido depende da classe real daquele objeto. O filtro pelo identificador seleciona a conta, enquanto cada lançamento determina o sinal do seu impacto. Com saldo inicial zero, receita de 1.500 e despesas de 300 e 120, o resultado é 1.080 reais. Sobrescrita é a implementação específica nas subclasses. Polimorfismo é o uso dessas implementações pela mesma chamada.

**O que mostrar**

Aponte os dois retornos e depois a chamada feita dentro de calcular_saldo. Explique o percurso de um objeto de cada tipo.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L82).

## Slide 7: Associação e agregação

Tempo sugerido: 40 s.

**Fala para ensaiar**

Cada lançamento se associa a uma conta e a uma categoria. Esses objetos são recebidos no inicializador e mantidos como referências. Carteira agrupa contas, categorias, lançamentos e orçamentos em tuplas para representar uma fotografia consistente dos dados. Esse agrupamento é uma agregação: as entidades continuam existindo no banco quando a fotografia é descartada. O projeto não modela uma composição UML forte com posse exclusiva e ciclo de vida dependente. A montagem de dependências no bootstrap é outro uso da palavra composição.

**O que mostrar**

Mostre _conta e _categoria no lançamento, depois as tuplas de Carteira em ports.py.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L108).

## Slide 8: Responsabilidades e contrato de persistência

Tempo sugerido: 45 s.

**Fala para ensaiar**

A interface recolhe os dados e chama os serviços. As classes de domínio protegem as regras financeiras. Os serviços coordenam os casos de uso e utilizam o contrato RepositorioFinanceiro. RepositorioPostgres implementa esse contrato e realiza as operações no Supabase. Nos testes, RepositorioEmMemoria implementa a mesma interface de métodos. Isso permite testar os serviços sem conectar ao banco. A aplicação publicada usa o repositório PostgreSQL. O inicializador do serviço recebe o repositório como dependência, o que é uma forma simples de injeção de dependência.

**O que mostrar**

Abra ports.py e services.py. Mostre a construção das dependências em bootstrap.py, sem abrir arquivos de segredos.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/ports.py#L18).

## Slide 9: Validações, exceções e precisão

Tempo sugerido: 40 s.

**Fala para ensaiar**

Um lançamento exige valor maior que zero e uma categoria compatível. Quando os dados violam uma regra, o domínio lança ValidationError. Essa exceção deriva de HappyGreenError, que a interface captura para apresentar uma mensagem legível. Essa hierarquia também demonstra herança. Nos valores monetários usamos Decimal e, no banco, NUMERIC com duas casas. O arredondamento segue ROUND_HALF_UP. A persistência mantém os dados no Supabase e o repositório reconstrói objetos Receita e Despesa quando faz a leitura.

**O que mostrar**

Mostre o raise no domínio e o except na interface. Demonstre uma tentativa com valor zero.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/happy_green/domain.py#L118).

## Slide 10: Demonstração prática

Tempo sugerido: 110 s.

**Fala para ensaiar**

Vamos acompanhar uma alteração real. Na base demonstrativa original, o saldo é 1.080 reais. Em Lançamentos, selecionamos Passe de transporte e alteramos o valor de 120 para 150. A despesa aumenta em 30 e o saldo deve cair para 1.050. Depois restauramos o valor de 120 para deixar a base pronta para outra demonstração. No orçamento, alimentação de 300 diante de um limite de 250 gera excesso de 50. Uma tentativa de registrar valor zero deve apresentar uma validação. Por fim, atualizamos a página para observar que os dados permanecem disponíveis no banco.

**O que mostrar**

Confira os dados antes de começar. Se a base pública tiver mudado, prepare o cenário previamente e explique os novos valores esperados.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/docs/APRESENTACAO.md).

## Slide 11: Verificação e acesso ao projeto

Tempo sugerido: 40 s.

**Fala para ensaiar**

O desenvolvimento registrou 51 testes Python e 12 verificações de integridade executadas no PostgreSQL. Os testes cobrem abstração, polimorfismo, precisão, validações e efeitos de edição e exclusão. A interface também possui testes com o AppTest do Streamlit. A publicação e a persistência após reabrir a página foram verificadas. Esses resultados estão documentados no repositório. O projeto mostra POO em comportamentos utilizados pelo sistema, especialmente no cálculo do saldo e na colaboração entre domínio, serviços e repositório.

**O que mostrar**

Mostre VERIFICACAO.md e a lista de testes. Termine com o link público e abra espaço para perguntas.

Código/fonte: [abrir referência](https://github.com/Mark1513/happy-green/blob/4c116986b262f1c33cef5affdcfda4e4885e43de/docs/VERIFICACAO.md).

## Exemplo numérico para explicar no quadro

Com saldo inicial zero: receita de R$ 1.500,00, alimentação de R$ 300,00 e transporte de R$ 120,00 produzem saldo de R$ 1.080,00. O valor armazenado na despesa é positivo. O método calcular_impacto_no_saldo() fornece o sinal negativo durante o cálculo.

A seleção do construtor no serviço e no repositório é uma fábrica simples. O cálculo utiliza o objeto já construído e chama seu método. O filtro por conta em calcular_saldo compara identificadores e não escolhe o sinal do lançamento.

## Perguntas prováveis do professor

**Qual a diferença entre classe e objeto?**

ContaFinanceira é a definição do tipo. A instância criada como Minha carteira é um objeto desse tipo, com estado próprio.

**O que é self?**

É a referência à instância que recebe a chamada do método. Em conta.calcular_saldo(...), self corresponde àquela conta.

**__init__ é o construtor?**

Na linguagem da disciplina, costuma ser apresentado como construtor. Tecnicamente, em Python ele inicializa a instância depois da criação, responsabilidade associada a __new__. Nossa implementação usa __init__ para configurar estado e validar dados.

**Para que serve super()?**

Permite chamar uma implementação da classe base conforme a resolução de métodos. Em ContaFinanceira, inicializa o identificador definido em Entidade.

**Por que criar uma classe abstrata?**

Para expressar um contrato comum. Lancamento centraliza dados e validações e exige que subclasses concretas implementem o comportamento financeiro.

**Por que Receita e Despesa são classes diferentes?**

Neste projeto, o impacto positivo ou negativo é um comportamento especializado. As classes permitem demonstrar herança, sobrescrita e polimorfismo com uma regra do domínio.

**Onde está o polimorfismo?**

No método calcular_saldo, que chama item.calcular_impacto_no_saldo() para cada lançamento. A implementação executada corresponde ao objeto Receita ou Despesa. Também existe substituição de repositórios nos testes.

**Sobrescrita é igual a sobrecarga?**

Sobrescrita fornece uma implementação específica de um método herdado. O projeto usa sobrescrita. Ele não implementa sobrecarga por múltiplas assinaturas como em Java. Parâmetros opcionais, por si só, não são esse tipo de sobrecarga.

**O sublinhado torna o atributo privado?**

É uma convenção de membro interno. As propriedades sem setter protegem o uso normal da API pública, mas Python permite acesso deliberado ao atributo interno.

**O objeto inteiro é imutável?**

As propriedades das entidades não oferecem setters, mas seus atributos internos continuam acessíveis por convenção. Carteira e ResumoMensal usam dataclass(frozen=True), que impede reatribuir campos normalmente, sem tornar recursivamente imutáveis todos os objetos referenciados.

**Existe composição no diagrama?**

A Carteira representa agregação de referências. As entidades continuam no banco após descartar a fotografia. O sistema não modela composição UML forte entre essas entidades. Montar dependências no bootstrap é uma atividade distinta.

**Por que usar Decimal?**

Permite representar os valores decimais usados nos cálculos financeiros sem introduzir a aproximação binária típica de float. O domínio define duas casas e arredondamento ROUND_HALF_UP.

**O saldo fica gravado em uma coluna?**

A conta guarda o saldo inicial. O saldo atual é derivado dos impactos dos lançamentos. Assim, uma edição ou exclusão reflete no cálculo seguinte.

**Saldo acumulado e resultado mensal são iguais?**

O saldo acumulado inclui saldo inicial e todas as movimentações. O resultado mensal considera apenas receitas menos despesas do mês selecionado. Eles podem ter valores diferentes.

**O que mantém os dados depois de atualizar a página?**

O PostgreSQL hospedado no Supabase. O Streamlit reexecuta a interface, e o repositório faz uma nova leitura do banco. st.session_state guarda apenas informações temporárias da interface.

**Por que não há SQL nas telas?**

A interface deve cuidar da interação. O repositório concentra o acesso ao banco, enquanto domínio e serviços cuidam das regras e dos casos de uso.

**Como foram feitos os testes?**

pytest verifica domínio e serviços. AppTest exercita a interface com um repositório de teste. Um script SQL verifica restrições no PostgreSQL e reverte seus registros ao final. Os resultados registrados são 51 testes Python e 12 verificações SQL.

**A aplicação tem login e separa usuários?**

A versão atual é uma demonstração pública compartilhada com dados fictícios. Autenticação e isolamento por usuário são possibilidades de evolução, fora do escopo inicial.

**Qual foi a contribuição da IA?**

O desenvolvimento recebeu assistência de IA. O grupo deve declarar essa assistência conforme as regras da disciplina e explicar o que revisou, testou e compreendeu, sem inventar contribuições individuais.

## Preparação e ensaio

1. Confiram o tempo permitido e dividam as falas por blocos, sem inventar a contribuição de cada integrante.
2. Abram a aplicação e o repositório antes de começar. A base pública é compartilhada e pode mudar.
3. Confiram se a demonstração tem saldo 1.080, receita 1.500 e despesas 300 e 120 antes de usar os resultados deste roteiro.
4. Deixem abertas as referências ContaFinanceira, Lancamento, Receita, Despesa, RepositorioFinanceiro e os testes.
5. Ensaiem a alteração do transporte e restaurem seu valor original ao final.
6. Preparem uma captura do painel como apoio se a conexão estiver indisponível. Identifiquem a captura como imagem de apoio, sem apresentá-la como uma demonstração ao vivo.
7. Apresentem o teste de encapsulamento e o de abstração/polimorfismo. A evidência registrada está em docs/VERIFICACAO.md.
8. Mantenham os arquivos de segredos e os painéis de credenciais fora da apresentação.

## Referências para estudar os conceitos

- [Classes e objetos em Python 3.12](https://docs.python.org/3.12/tutorial/classes.html).
- [Convenções de atributos internos](https://docs.python.org/3.12/tutorial/classes.html#private-variables).
- [Classes abstratas e abstractmethod](https://docs.python.org/3.12/library/abc.html).
- [Inicialização de objetos](https://docs.python.org/3.12/reference/datamodel.html#object.__init__).

O guia não afirma que todas as verificações foram realizadas novamente nesta preparação. Ele usa as evidências já registradas no desenvolvimento, além da inspeção do código atual.
