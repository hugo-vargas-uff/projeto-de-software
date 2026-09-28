# Agregado Voo - Matheus Verdan
## Checkpoint 1 - Domínio do Voo

Arquivos: src/airline/domain/model.py, tests/unit/domain/test_voo.py, .github/workflows/ci.yml, DECISIONS.md

Commits:
- 40949ed - 18/09 - Adicionando DECISIONS.md
- 7d27fcb - 18/09 - test: cria teste de criação de Voo com status agendado
- 60601b4 - 18/09 - feat: implementa classe Voo com StatusVoo
- 20fb31b - 18/09 - test: cria teste de criacao de Trecho
- 3530400 - 19/09 - feat: implementa Trecho como objeto de valor
- 5f7bf61 - 19/09 - docs: registra decisoes do agregado Voo
- 42a4d6b - 20/09 - test: att voo com trecho e add teste de igualdade de rota
- feef938 - 20/09 - feat: construtor de voo agora tem trecho
- c5c5dc5 - 20/09 - test: add teste de cancelamento de voo
- 86f2b21 - 20/09 - feat: add funcionalidade para cancelar voo
- 8ca9a20 - 20/09 - test: add realizacao de voo
- 42c2b09 - 20/09 - feat:add funcionalidade para realizar voo
- 37a106d - 20/09 - test: add testes de regras de negocio para mudancas de status
- 3911707 - 20/09 - feat: aplica validacoes de status no Voo
- 06a4c1a - 20/09 - docs: novas decisoes sobre os status
- ee4cca4 - 20/09 - configura testes automaticos no github

### Trecho como objeto de valor
2026-09-18

Um trecho tem só origem e destino, então não vi necessidade de dar um ID a ele. GRU -> GIG sempre representa o mesmo trecho, e o que importa é o valor, não uma identidade própria. Por isso tratei Trecho como Objeto de Valor.

Também não faz sentido alterar um trecho depois de criado (se a rota mudar, basta criar um novo), então usei frozen=True para deixar o objeto imutável.

### StatusVoo como Enum
2026-09-18

Usei Enum para os status do Voo (AGENDADO, CANCELADO, REALIZADO) para padronizar os valores e evitar erros de digitação.

### Trocas de Status
2026-09-20

Em vez de deixar o status do voo ser alterado livremente de fora da classe, decidi criar métodos específicos (cancelar() e realizar()). Dessa forma, o próprio agregado consegue proteger suas regras de negócio antes da mudança ocorrer. Por exemplo, o método lança um ErroRegraVoo caso alguém tente cancelar um voo que já foi realizado.

### Sem metodo para reagendar()
2026-09-20

Inicialmente pensei em criar um método para voltar o status de CANCELADO para AGENDADO. Mas, olhando para a situação real, um voo cancelado envolve mudanças que vão além do próprio status. Se a companhia precisar daquela rota novamente, o correto é instanciar um Voo novo. Por isso, decidi que um voo cancelado (ou realizado) não pode mais mudar de status.

## Checkpoint 2 - Repositório do Voo

Arquivos: src/airline/domain/model.py, src/airline/domain/repositories.py, src/airline/adapters/orm.py, src/airline/adapters/repository.py, tests/unit/domain/test_voo.py, tests/integration/adapter/test_SqlAlchemyVooRepository.py, tests/unit/service_layer/test_voo_service.py

Commits:
- d8331d5 - 24/09 - test: adiciona aeronave_id e capacidade nos testes
- 1b54eff - 24/09 - feat: add aeronave_id e capacidade de assentos em voo
- 368e1b6 - 24/09 - test: add teste de alocacao de assentos
- 025311c - 24/09 - feat: implementa metodo alocar_assento com invariante de lotacao em voo
- 1feb052 - 25/09 - docs: add a decisao sobre a invariante de lotacao
- 6c1ae4e - 26/09 - feat: add rep abstrato de voo
- 4d18dde - 26/09 - feat: cria modelo de voo
- 453e524 - 26/09 - test: add teste de integracao do repo de voo
- d0cd57f - 26/09 - feat: implementa SqlAlchemyVooRepository
- 4831301 - 26/09 - test: implementa repositorio fake de voo
- 30e3fc2 - 27/09 - test: salvar voo existente deve atualizar o status
- 33f4529 - 27/09 - fix: repositorio att voo existente em vez de inserir de novo
- a61afe5 - 27/09 - refactor: trecho, aeronave e capacidade passam a ser obrigatorios

### Invariante de lotação movida para o Voo
2026-09-24
Percebi que no modelo original, a regra de não exceder a capacidade do voo estava atribuída ao agregado Reserva. Isso não funcionaria na prática porque a Reserva não tem acesso ao número total de assentos nem sabe quantas outras reservas existem. Movi essa responsabilidade para o Voo, que agora recebe a capacidade da aeronave no momento da criação e controla a alocação de
assentos internamente com o método alocar_assento().

### Trecho sem tabela própria
2026-09-25

Como o Trecho não tem identidade, criar uma tabela para ele me obrigaria a inventar um ID que o domínio nunca usaria. Guardei origem e destino como duas colunas da tabela voos, e no buscar monto um Trecho novo com esses dois valores.

### testes de integração sem usar o repositório para conferir ele mesmo
2026-09-25

Fiz os testes de integração usando comandos SQL puro para não usar o próprio repositório para testar ele mesmo. Se eu chamasse o buscar() pra validar o salvar() e houvesse um erro de mapeamento de colunas nos dois, um erro esconderia o outro e o teste daria um falso positivo.

### Atualização de voos no método salvar
2026-09-27

Mudei o comportamento do salvar() para ele procurar o voo no banco antes de fazer qualquer coisa. Se o voo já existir ele faz um update e se não existir ele cria um novo. Tive que fazer isso porque as informações do voo mudam bastante, principalmente a quantidade de assentos que cai toda vez que uma reserva é feita. Se o repositório só soubesse fazer insert, o banco nunca ia receber a atualização dos assentos e ia dar erro de chave primária duplicada na hora de salvar a mudança.

### Voo não pode ser criado incompleto
2026-09-27

Agora não dá para criar um voo sem rota, sem aeronave ou sem capacidade. A capacidade zero como padrão também foi alterada, porque criava um voo que já nascia lotado.


# Agregado Aeronave — Matheus Andrade

## Checkpoint 1 — Domínio da Aeronave

### 1. O que eu fiz neste checkpoint

Neste checkpoint criei a classe Aeronave, que representa uma aeronave dentro do domínio do sistema. Antes de criar a classe, escrevi os testes para criação, igualdade, diferença entre aeronaves, hash, vistoria e manutenção.

### 2. Arquivos e commits

- 5cfc168 — 20/09 — test: add testes de criacao e identidade da Aeronave
- 4c752e8 — 20/09 — feat: implementa Aeronave com identidade por prefixo
- beb9bd3 — 21/09 — docs: Decisoes do agregado Aeronave
- 1afb0af — 21/09 — test: add teste de hash da Aeronave
- 4c4d0bd — 21/09 — feat: implementando `__hash__` da Aeronave
- 3567978 — 21/09 — feat: adiciona regra de vistoria vencida na Aeronave
- fbde803 — 21/09 — feat: Adiciona OrdemManutencao e bloqueio por manutenção

Os principais arquivos alterados foram:

- tests/unit/domain/test_aeronave.py
- src/airline/domain/model.py

### 3. Decisão: Aeronave é entidade, não objeto de valor

2026-09-20

Decidi tratar Aeronave como uma entidade porque ela possui uma identidade própria, representada pelo prefixo. Duas aeronaves com o mesmo prefixo representam a mesma aeronave, mesmo que outros dados, como modelo ou capacidade, estejam diferentes. Isso é diferente do Trecho criado pelo Verdan, que é um objeto de valor e depende dos seus atributos para definir igualdade. Também não usei frozen=True, porque a aeronave precisa mudar de estado, por exemplo quando entra ou sai de manutenção.

A igualdade e o hash da Aeronave usam o prefixo, pois ele representa sua identidade.

### 4. Decisão: disponibilidade calculada

2026-09-21

Inicialmente disponivel era um atributo da Aeronave. Depois da implementação da vistoria e da OrdemManutencao, decidi calcular a disponibilidade pelo método esta_disponivel.

A aeronave fica disponível quando a vistoria está válida e não existe nenhuma ordem de manutenção pendente. A data de hoje é passada como parâmetro para deixar os testes previsíveis e não depender da data do computador.

A OrdemManutencao também passou a fazer parte do agregado Aeronave, já que uma manutenção pendente interfere diretamente na disponibilidade.

### 5. Próximos passos

Depois das regras do domínio, o próximo passo foi criar a persistência da Aeronave e das suas ordens de manutenção através de repositórios e ORM.

### 6. Uso de IA

Usei IA para tirar dúvidas sobre entidade e objeto de valor, entender melhor `__eq__` e `__hash__`, discutir a forma de testar datas, ajudar a interpretar erros e revisar o código que eu escrevi. O código utilizado no projeto foi escrito por mim.

## Checkpoint 2 — Repositório da Aeronave

### 1. O que eu fiz neste checkpoint

Neste checkpoint criei o contrato do repositório da Aeronave, uma implementação falsa para os testes e a implementação real com SQLAlchemy. Também criei o mapeamento da Aeronave e das ordens de manutenção no banco e escrevi testes de integração.

### 2. Arquivos e commits

- e917250 — 25/09 — feat: adiciona contrato AeronaveRepository
- 51ca19a — 26/09 — test: adiciona FakeAeronaveRepository e testes de salvar e buscar
- 08a13bd — 26/09 — feat: adiciona mapeamento ORM da Aeronave e OrdemManutencao
- 05ca3a9 — 26/09 — feat: adiciona SqlAlchemyAeronaveRepository
- f9bc17b — 27/09 — test: add teste de integracao do SqlAlchemyAeronaveRepository

Os principais arquivos alterados foram:

- src/airline/domain/repositories.py
- src/airline/adapters/orm.py
- src/airline/adapters/repository.py
- tests/unit/
- tests/integration/adapter/test_SqlAlchemyAeronaveRepository.py

### 3. Decisão: duas tabelas para Aeronave e OrdemManutencao

2026-09-27

Decidi usar uma tabela para Aeronave e outra para OrdemManutencao porque uma aeronave pode ter várias ordens de manutenção.

As duas tabelas são ligadas por chave estrangeira e relationship. Também usei cascade porque a ordem pertence ao agregado Aeronave e não deve existir sem ela.

Isso é diferente do Voo, que apenas guarda uma referência para a aeronave, pois Voo e Aeronave são agregados separados.

### 4. Decisão: reconstrução da Aeronave no buscar

2026-09-27

No método buscar, preferi reconstruir as ordens usando abrir_ordem_manutencao e concluir_ordem_manutencao, em vez de alterar diretamente a lista de ordens.

Decidi fazer assim para que o repositório use os métodos da própria Aeronave e não altere diretamente seu estado interno.

### 5. Limitações técnicas

Atualmente o método salvar sempre cria um novo registro. Por isso, salvar novamente uma aeronave que já existe pode gerar conflito.

A OrdemManutencao também possui um ID no banco, mas ainda não possui uma identidade própria no domínio.

### 6. Uso de IA

Usei IA para tirar dúvidas sobre relationship e cascade no SQLAlchemy, revisar o código e ajudar na resolução de um conflito de rebase no repository.py. O código utilizado no projeto foi escrito por mim.





# Agregado Reserva

## Entidade Reserva
2026-09-21

Reserva é entidade pois possui um identificador unico para diferenciar de outras reservas.

Reserva possui um identificador unico(UUID), voo_id(Voo para qual foi feita a reserva), passageiro_id(identificador do passageiro que fez a reserva) e um ENUM StatusReserva.

### Metodo cancelar
Metodo usado para cancelar uma reserva feita por um passageiro

## StatusReserva
2026-09-21

Criei StatusReserva("CONFIRMADA", "CANCELADA") para padronizar valores.

# Agregado Passageiro

## Entidade Passageiro

Passageiro possui um identificador unico(UUID), nome e CPF.
adicionei cpf para servir como um identificador externo para facilitar futuras buscas por passageiros.