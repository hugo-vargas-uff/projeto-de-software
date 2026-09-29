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

Mudei o comportamento do salvar() para ele procurar o voo no banco antes de fazer qualquer coisa. Se o voo já existir ele faz um update e se não existir ele cria um novo. Tive que fazer isso porque o voo muda depois de salvo, o status muda ao cancelar ou realizar, e os assentos diminuem a cada alocação. Se o repositório só soubesse fazer insert, o banco nunca ia receber essas mudanças e ia dar erro de chave primária duplicada na hora de salvar.


### Voo não pode ser criado incompleto
2026-09-27

Agora não dá para criar um voo sem rota, sem aeronave ou sem capacidade. A capacidade zero como padrão também foi alterada, porque criava um voo que já nascia lotado.

## Entrega da Fase 1 - Voo

Arquivos: src/airline/service_layer/services.py, src/airline/domain/exception.py, src/airline/entrypoints/flask_app.py, tests/unit/service_layer/test_voo_service.py, tests/e2e/test_api_voo.py, tests/conftest.py

Commits:
- 57db2de - 29/09 - test: agendar voo copia a capacidade da aeronave
- 738f24e - 29/09 - feat: cria vooService com agendar_voo
- 088be94 - 29/09 - test: agendar voo recusa numero repetido e aeronave indisponivel
- 7c3595c - 29/09 - feat: valida numero repetido e disponibilidade da aeronave
- 9fbe23a - 29/09 - test: cancelar voo pelo servico
- ce8e2d5 - 29/09 - feat: cancelar_voo no service
- 53f6258 - 29/09 - test: realizar e consultar voo pelo servico
- 57adc44 - 29/09 - feat: realizar e consultar voo no service
- b3bb806 - 29/09 - test: adiciona conftest para o flask
- 6af90be - 29/09 - test: agendar e consultar voo pela API
- e13fa2c - 29/09 - conteudo do test_api_voo
- e5ef788 - 29/09 - feat: rotas de agendar e consultar voo
- 9766150 - 29/09 - test: cancelar voo pela api
- 475920c - 29/09 - feat: rotas de cancelar e realizar voo
- abc20da - 29/09 - test: fix

### Agendar um voo consulta a aeronave
2026-09-29

A regra de manutenção da Aeronave passou a valer no sistema, porque até então nada impedia de marcar um voo com um avião em manutenção. Os dois agregados continuam separados, o Voo só guarda o prefixo, e quem conversa com a Aeronave é o serviço.

### O commit fica no serviço
2026-09-29

O repositório do Voo nunca fez commit, então quem confirma a operação depois que tudo deu certo é o serviço. Nos testes uso uma sessão falsa que só anota se o commit foi chamado, e confiro que ele não acontece quando o caso de uso termina em erro.

### A data de hoje entra como parâmetro
2026-09-29

O agendar recebe a data em vez de consultar o relógio do computador, pois o teste precisa dar o mesmo resultado em qualquer dia. Quem passa a data real é a rota do Flask.

### O fake de voo passou a guardar por número
2026-09-29

O repositório falso guardava os voos numa lista, então salvar de novo um voo cancelado deixava duas entradas. Troquei por um dicionário com o número do voo como chave, para ele se comportar como o repositório real, que atualiza em vez de duplicar.

### 404 quando não existe, 400 quando uma regra impede
2026-09-29

Para quem usa a API saber se errou o identificador ou se esbarrou numa regra do negócio.

### Fixtures de teste ponta a ponta no conftest
2026-09-29

Como o app do Flask que o Filipe fez já conecta num banco SQLite fixo, criei duas fixtures no conftest pra compartilhar com o grupo o client da API e a sessão do banco. A do client limpa as tabelas antes de cada teste, pra um teste não ver os dados do outro. A da sessão eu uso pra colocar uma aeronave direto no banco antes de testar o agendamento, já que ainda não temos rota pra cadastrar aeronave.

### Limitação, cancelar um voo não cancela as reservas
2026-09-29

Hoje, cancelar um voo só muda o status dele, e as reservas daquele voo continuam confirmadas. Avisar a Reserva de dentro do Voo misturaria os dois agregados.


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



# Agregados Tripulante e Escala — Filipe Moreira

## Checkpoint 1 — Domínio da Tripulação e Escala

Arquivos: `src/airline/domain/model.py`, `tests/unit/domain/test_tripulante.py`, `tests/unit/domain/test_escala.py`, `DECISIONS.md`

Commits:
- 761b2b4 — 19/09 — test: cria testes unitarios para criacao e invariante de horas do Tripulante
- 8f4b87e — 19/09 — feat: implementa entidade Tripulante com controle de teto de horas
- bd87044 — 20/09 — test: adiciona testes de alocacao de tripulantes na Escala
- d402dac  — 20/09 — feat: implementa agregado Escala com protecao contra tripulante duplicado

### 1. O que eu fiz neste checkpoint

Neste checkpoint implementei as classes de domínio `Tripulante` e `Escala`, responsáveis pelo gerenciamento da tripulação e escalonamento dos voos da companhia aérea. Antes de implementar cada entidade, criei os testes unitários cobrindo criação, invariantes e regras de negócio no estilo TDD.

### 2. Decisão: Tripulante é entidade com identidade própria

Decidi tratar `Tripulante` como uma entidade (com `id` via `uuid.uuid4()`) porque cada profissional possui uma identidade própria que persiste ao longo do tempo, independentemente de mudanças em seu cargo ou acúmulo de horas voadas. Usei `Enum` (`CargoTripulante`) para padronizar os papéis a bordo (Piloto, Copiloto, Comissário).

### 3. Decisão: Invariante do teto regulamentar de horas no Tripulante

A regra de negócio central da tripulação é que a soma de horas de voo de um tripulante não pode ultrapassar o teto regulamentar do período (definido por padrão como 85h, em conformidade com as normas da aviação civil).
Decidi encapsular essa verificação no método `registrar_horas_de_voo(horas)` da própria entidade `Tripulante`. Caso o acréscimo exceda o teto permitido, a entidade lança a exceção de domínio `ErroRegraTripulacao`, garantindo que o objeto nunca fique em estado inválido. Também adicionei o método `pode_voar(duracao_horas)` para pré-validação antes da alocação.

### 4. Decisão: Escala como agregado desacoplado referenciando IDs

A `Escala` representa a tripulação montada para atender a um voo específico. Seguindo as boas práticas de Domain-Driven Design (DDD) sobre limites de agregados, a `Escala` referencia tanto o voo (`voo_id`) quanto os tripulantes (`tripulantes_ids`) apenas por seus identificadores, sem carregar instâncias completas.
A raiz do agregado `Escala` protege a invariante de não permitir tripulantes duplicados no mesmo voo, lançando `ErroRegraTripulacao` caso alguém tente adicionar o mesmo `tripulante_id` duas vezes.

### 5. Uso de IA

Conforme a Seção 2.5 da especificação, usei IA generativa apenas para tirar dúvidas conceituais sobre design de agregados em DDD e para revisar a estruturação das invariantes. O código implementado e testado no projeto foi escrito por mim.


## Checkpoint 2 — Repositórios e Persistência da Tripulação e Escala

Arquivos: `src/airline/domain/repositories.py`, `tests/unit/service_layer/test_tripulacao_service.py`, `src/airline/adapters/orm.py`, `src/airline/adapters/repository.py`, `tests/integration/adapter/test_SqlAlchemyTripulanteRepository.py`, `DECISIONS.md`

Commits:
- f4a5acd — 25/09 — feat: adiciona contratos abstratos TripulanteRepository e EscalaRepository
- d3ccfcd — 25/09 — test: implementa FakeTripulanteRepository e FakeEscalaRepository com testes
- 73a6c7f — 26/09 — feat: adiciona mapeamento ORM para tabelas de tripulantes e escalas
- 2ee494a — 27/09 — test: adiciona testes de integracao para repositorios de tripulacao

### 1. O que eu fiz neste checkpoint

Neste checkpoint criei os contratos abstratos dos repositórios para os agregados `Tripulante` e `Escala`, uma implementação Fake em memória para testes rápidos da camada de serviço, o mapeamento relacional via SQLAlchemy ORM e a implementação real persistindo em SQLite com testes de integração.

### 2. Decisão: Repositórios Abstratos (DIP - Dependency Inversion Principle)

Defini as interfaces abstratas `TripulanteRepository` e `EscalaRepository` no domínio (`repositories.py`) usando `ABC`. Isso desacopla totalmente a camada de negócio de qualquer framework ou banco de dados, permitindo que a camada de aplicação use tanto implementações reais quanto fakes sem saber a diferença.

### 3. Decisão: Fake Repositories para testes unitários isolados

Implementei `FakeTripulanteRepository` e `FakeEscalaRepository` utilizando dicionários em memória no arquivo de testes. Isso viabiliza testes de unidade instantâneos para a camada de serviço, sem o overhead de inicializar banco de dados SQLite a cada execução de teste.

### 4. Decisão: Modelagem relacional da Escala e Tripulantes

Para persistir a `Escala` e os tripulantes a ela associados, criei as tabelas `escalas` e `escala_tripulantes` ligadas por chave estrangeira e `relationship` com `cascade="all, delete-orphan"`.
Dessa forma, a integridade da escala é mantida pelo SQLAlchemy: se a escala for atualizada ou removida, a relação de tripulantes daquele voo é sincronizada de forma limpa.

### 5. Decisão: Atualização inteligente no método salvar()

Seguindo a mesma decisão arquitetural adotada pelo Verdan no agregado Voo, fiz com que o método `salvar()` do `SqlAlchemyTripulanteRepository` e do `SqlAlchemyEscalaRepository` consulte primeiro se o registro já existe no banco antes de persistir. Caso já exista, atualiza os campos; caso contrário, realiza o `insert`. Isso evita erros de integridade e garante que alterações no acúmulo de horas e na lista de tripulantes sejam salvas com sucesso.

### 6. Uso de IA

Utilizei IA para tirar dúvidas conceituais sobre cascade e relationship no SQLAlchemy ORM ao modelar a tabela intermediária de tripulantes da escala e para revisar mensagens de erro de importação. Todo o código commitado foi escrito por mim.

## Entrega da Fase 1 — Camada de Serviço, API Flask e Testes E2E

Arquivos: `src/airline/service_layer/services.py`, `tests/unit/service_layer/test_tripulacao_service.py`, `src/airline/entrypoints/flask_app.py`, `tests/e2e/test_api.py`, `tests/conftest.py`, `requirements.txt`, `DECISIONS.md`

Commits:
- 6c53dd6 — 28/09 — test: adiciona testes de servico para cadastro e escalonamento de tripulantes
- afb9fef — 28/09 — feat: implementa servicos de tripulacao e escala na camada de servico
- 8f6c569 — 28/09 — feat: adiciona entrypoints Flask com rotas para tripulacao e escala
- 5edf237 — 28/09 — test: cria testes e2e para a API Flask

### 1. O que eu fiz neste fechamento de Fase

Nesta etapa final da Fase 1, conectei todas as pontas da aplicação: implementei a Camada de Serviço (`service_layer`), a API HTTP utilizando Flask (`entrypoints`) e os testes ponta a ponta (`tests/e2e/`) cobrindo todas as rotas e fluxos de tripulação e escala.

### 2. Decisão: Orquestração e transações na Service Layer

Criei `TripulanteService` e `EscalaService` na camada de serviço. A operação de escalonar um tripulante (`escalar_tripulante`) é um caso de uso que orquestra a lógica entre os agregados:
1. Localiza o tripulante pelo ID via repositório;
2. Verifica e atualiza o acúmulo de horas de voo no domínio;
3. Recupera ou instancia a escala do voo e aloca o tripulante;
4. Persiste as duas entidades garantindo a consistência das operações.
A camada de serviço não contém regras de negócio de domínio (como cálculo de horas ou validação de duplicidade), ela apenas orquestra as chamadas aos métodos de domínio e repositórios.

### 3. Decisão: API Flask enxuta e orientada a casos de uso

Na camada de entrada (`entrypoints/flask_app.py`), implementei rotas RESTful para cadastro de tripulantes (`POST /tripulantes`), busca (`GET /tripulantes/<id>`) e alocação de escalas (`POST /escalas`, `GET /escalas/<voo_id>`).
A API não contém lógica de negócio: ela apenas extrai o JSON da requisição, chama a camada de serviço correspondente e converte o retorno para JSON, mapeando exceções de domínio (`ErroRegraTripulacao`) para status HTTP `400 Bad Request` e buscas vazias para `404 Not Found`.

### 4. Decisão: Testes E2E com client nativo do Flask

Nos testes ponta a ponta (`tests/e2e/test_api.py`), utilizei a fixture `client` do Flask com `app.test_client()`, testando os fluxos reais de requisições HTTP, envio de payloads JSON e validação dos códigos de status HTTP e das respostas recebidas.

### 5. Uso de IA

Utilizei IA para revisar as boas práticas de estrutura de fixtures com pytest para o test_client do Flask e para consultar o padrão do Apêndice B do livro no desacoplamento entre entrypoints e service layer. Todo o código do projeto foi implementado e testado por mim.


# Agregado Despacho — Vinicius Duarte

## Checkpoint 1 — Domínio do Despacho
Neste checkpoint implementei o domínio `Despacho`. Antes de implementar a entidade, criei os testes unitários cobrindo criação, invariantes e regras de negócio no estilo TDD.

### 2. Arquivos e commits

- src/airline/domain/model.py
- tests/unit/domain/test_despacho.py

- cb5c9c5754e0198bba313553cb3e0e08409a6c53 — 28/09 — test: adiciona testes de id, voo_id, limite de carga e restaurar do despacho
- 18d4c48a1003ee222d28add484436ed416fa688f — 28/09 — feat: adiciona id, voo_id, peso_disponivel e restaurar no despacho

### 3. Decisão: Despacho é entidade e Volume é objeto de valor

2026-09-29

O Despacho tem id (uuid4) e muda de estado quando recebe volumes, então é entidade. Igualdade e hash usam o id, como no Tripulante e na Escala. O Volume só tem peso e não tem identidade: dois volumes de 150 kg são iguais. Por isso ele continua como dataclass frozen.

### 3. Decisão: Despacho referencia o Voo só pelo voo_id

2026-09-29

O Despacho guarda apenas o voo_id (o numero_voo, ex. "MV-3000"), não a instância do Voo. Voo e Despacho são agregados diferentes, e um não deve alterar o outro. Segui o mesmo formato de voo_id da Escala.

### 3. Decisão: carga_maxima informada na criação do despacho

2026-09-29

Verifiquei se dava para pegar a carga máxima da Aeronave, mas o campo capacidade dela é número de assentos, não peso. Usar a aeronave exigiria criar um campo novo no agregado Aeronave e fazer o serviço passar por Voo e Aeronave. Por isso a carga_maxima é informada quando o despacho é aberto. Troquei a mensagem de erro de "carga maxima da aeronave" para "carga maxima do despacho".

### 3. Decisão: peso_disponivel no domínio

2026-09-29

O cálculo carga_maxima - peso_total ficou num método do próprio Despacho. Assim o serviço só consulta e não faz conta de regra de negócio.

### 3. Decisão: restaurar para reconstruir vindo do banco

2026-09-29

Criei restaurar(id, voo_id, carga_maxima, volumes), igual ao do Passageiro e da Tripulante. Ele recria o despacho com o id que já existe, sem gerar um uuid novo.

## Checkpoint 2 — Repositório do Despacho

### 1. O que eu fiz neste checkpoint

Criei o contrato DespachoRepository em domain/repositories.py, com salvar, buscar_por_id e buscar_por_voo.

### 2. Arquivos e commits

- src/airline/domain/repositories.py

- 42c16150731d7fa11c5c8631866851d846a81896 — 29/09 — feat: adiciona contrato DespachoRepository

### 3. Decisão: contrato abstrato no domínio

2026-09-29

O DespachoRepository fica no domínio, como classe abstrata (ABC). O serviço depende só dele, então nos testes de serviço posso usar um fake com dicionário e na aplicação o repositório com SQLAlchemy.

### 3. Decisão: buscar_por_voo devolve um único despacho

2026-09-29

Considerei que cada voo tem um despacho de carga, igual à Escala, que também é buscada pelo voo_id e devolve uma só. Se não existir, o método retorna None.


### 3. Decisão: duas tabelas para Despacho e Volume

2026-09-29

Um despacho tem vários volumes, então usei a tabela despachos e a tabela filha despacho_volumes, ligadas por ForeignKey e relationship com cascade="all, delete-orphan", como na Aeronave/OrdemManutencao e na Escala. O volume não existe fora do despacho. O id da tabela de volumes é só técnico (Integer autoincrement): no domínio o Volume continua sem identidade, e no to_domain eu recrio Volume(peso=...).

### 3. Decisão: to_domain usa restaurar

2026-09-29

Na leitura, o DespachoModel monta o despacho com Despacho.restaurar(...), passando o id salvo, em vez de chamar adicionar_volume volume a volume. Os dados do banco já passaram pela regra de carga quando foram salvos.

### 3. Decisão: salvar faz insert ou update

2026-09-29

Segui o salvar() que o Verdan fez no Voo e o Filipe na Escala: primeiro consulto o despacho pelo id; se não existir, insiro; se existir, atualizo. Sem isso, adicionar um volume num despacho já salvo daria erro de chave primária duplicada. O commit fica dentro do salvar, como nos outros repositórios.

### 3. Decisão: no update os volumes são apagados e gravados de novo

2026-09-29

Como o Volume não tem identidade, não dá para saber qual linha do banco corresponde a qual volume. No update eu limpo a lista de volumes do model e recrio a partir do domínio; o cascade delete-orphan apaga as linhas antigas.

### 3. Decisão: teste de integração com SQL puro

2026-09-29

Nos testes de integração confiro o banco com text() e insiro dados com INSERT direto, sem usar o próprio repositório para validar ele mesmo, seguindo o que o Verdan fez nos testes do Voo. Também testei que salvar um despacho existente não duplica o despacho nem os volumes.


### 3. Decisão: casos de uso do DespachoService

2026-09-29

Criei o DespachoService com abrir_despacho, adicionar_volume, consultar_despacho e consultar_peso_disponivel. O serviço só busca no repositório, chama o domínio e salva. A regra do peso fica no Despacho.adicionar_volume e o cálculo do peso livre no Despacho.peso_disponivel.

### 3. Decisão: um despacho por voo

2026-09-29

O abrir_despacho recusa um segundo despacho para o mesmo voo com ErroRegraDespacho. Fiz a verificação no serviço consultando buscar_por_voo, do mesmo jeito que o criar_passageiro confere se o CPF já existe antes de criar.

### 3. Decisão: DespachoNaoEncontrado em vez de retornar None

2026-09-29

Quando o despacho não existe, o serviço lança DespachoNaoEncontrado (em domain/exception.py, como o PassageiroNaoEncontrado), em vez de retornar None. Assim a API consegue transformar isso em 404 e o volume não é adicionado em algo que não existe.

### 3. Decisão: fake repository no próprio arquivo de teste

2026-09-29

O FakeDespachoRepository guarda os despachos num dicionário pelo id e fica dentro do test_despacho_service.py, como o FakeAeronaveRepository. Assim os testes do serviço rodam sem banco.

