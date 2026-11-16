# Frameworks

## 1. Papel de cada framework

## Flask

O Flask é utilizado como framework da camada de entrada da aplicação, permitindo disponibilizar as funcionalidades do sistema por meio de uma API REST. Sua responsabilidade é receber as requisições dos clientes, encaminhar as operações para os serviços da aplicação e devolver as respostas correspondentes.

### Papel do framework na solução

O Flask fornece os recursos necessários para:

- **Definição de endpoints:** os decorators `@app.get`, `@app.post` e `@app.route` associam funções Python a rotas e métodos HTTP, disponibilizando as operações do sistema.
- **Recebimento de requisições:** o recurso `request.get_json()` permite recuperar os dados enviados pelo cliente no corpo da requisição, enquanto os parâmetros das rotas recebem valores informados na URL.
- **Integração com a aplicação:** as funções das rotas instanciam os serviços e repositórios necessários e encaminham as operações para a camada de aplicação. Por exemplo, a criação de uma reserva utiliza o `ReservaService`, que coordena a operação e suas validações.
- **Tratamento de respostas:** os resultados são convertidos em respostas JSON, utilizando `jsonify()` ou dicionários Python, acompanhados dos respectivos códigos HTTP, como 200, 201, 400 e 404.
- **Tratamento de exceções:** exceções lançadas pelos serviços e pelo domínio são capturadas nas rotas e traduzidas em respostas HTTP adequadas. Por exemplo, uma exceção de recurso não encontrado pode resultar em uma resposta 404.
- **Gerenciamento de sessões:** as rotas criam sessões SQLAlchemy para utilização dos repositórios e realizam seu encerramento ao final das operações.

Além disso, a camada de entrada realiza conversões necessárias para integrar os dados recebidos aos componentes internos, como a conversão de strings em UUIDs e a construção do Value Object `CPF`.

### Camada em que aparece

O Flask está presente na camada de entrada (`src/airline/entrypoints/`), especificamente no arquivo `flask_app.py`. Essa camada funciona como uma fronteira entre os clientes HTTP e os componentes internos da aplicação.

### Por que o domínio não depende do Flask?

O domínio não precisa conhecer conceitos específicos de comunicação HTTP, como rotas, requisições, respostas JSON ou códigos de status. Ele contém as entidades, os Value Objects, as exceções e as regras de negócio, que podem ser executados independentemente do framework utilizado para disponibilizar o sistema.

Essa separação permite que as regras de negócio sejam reutilizadas por diferentes mecanismos de entrada, sem exigir alterações no domínio caso o Flask seja substituído por outro framework ou a aplicação passe a oferecer uma interface diferente da API REST.

Assim, o Flask é um detalhe externo de infraestrutura, responsável por disponibilizar e integrar as funcionalidades do sistema, enquanto as regras de negócio permanecem independentes dele.

## SQLAlchemy

O SQLAlchemy é utilizado para realizar a persistência dos dados no banco de dados, permitindo mapear objetos Python para tabelas e executar operações de consulta, inserção e atualização.

### Papel do framework na solução

O SQLAlchemy é utilizado para:

- **Mapeamento objeto-relacional (ORM):** classes como `PassageiroModel`, `ReservaModel` e `VooModel` representam as tabelas do banco de dados, definindo suas colunas e relacionamentos.
- **Conversão de objetos:** métodos `from_domain()` e `to_domain()`, implementados no projeto, convertem objetos do domínio em modelos de persistência e vice-versa.
- **Implementação dos repositórios:** classes como `SqlAlchemyPassageiroRepository` e `SqlAlchemyReservaRepository` implementam os contratos definidos pelo domínio, utilizando o SQLAlchemy para salvar e consultar dados.
- **Gerenciamento de sessões:** sessões criadas com `sessionmaker()` permitem executar consultas e operações no banco, utilizando métodos como `query()`, `filter_by()`, `add()` e `commit()`.

### Camada em que aparece

O SQLAlchemy aparece na camada de adaptadores (`src/airline/adapters/`):

- **`orm.py`:** define os modelos de persistência e as conversões entre esses modelos e os objetos do domínio.
- **`repository.py`:** implementa os repositórios utilizando as operações do SQLAlchemy.

### Por que o domínio não depende do SQLAlchemy?

O domínio não precisa conhecer tabelas, colunas, sessões, consultas ou modelos do ORM. Ele trabalha com suas próprias entidades, Value Objects, regras de negócio e contratos de repositório.

Por exemplo, `PassageiroRepository` define as operações necessárias para salvar e recuperar passageiros, mas não determina como essas operações serão executadas. A classe `SqlAlchemyPassageiroRepository`, localizada na camada de adaptadores, implementa esse contrato utilizando o SQLAlchemy.

Essa separação permite substituir a tecnologia de persistência sem exigir alterações nas regras de negócio. Outra implementação de repositório poderia utilizar outro ORM, comandos SQL diretamente ou até mesmo uma estrutura em memória, desde que respeitasse os contratos definidos pelo domínio.

Assim, o SQLAlchemy é um detalhe de infraestrutura responsável pela comunicação com o banco de dados, enquanto o domínio permanece independente da tecnologia utilizada para armazenar os dados.

## Pytest

O pytest é utilizado como framework de testes automatizados, permitindo executar e organizar testes unitários, de integração e E2E. No projeto, os testes verificam o comportamento das regras de negócio, a interação entre componentes e o funcionamento dos fluxos disponibilizados pela API.

### Papel do framework na solução

O pytest é utilizado para:

- **Testes unitários:** verifica comportamentos isolados do domínio, como a criação e a igualdade entre aeronaves, sem depender de banco de dados ou API.
- **Testes de integração:** verifica a interação entre componentes reais. Um exemplo é o teste do `SqlAlchemyDespachoRepository`, que salva um despacho no SQLite em memória e consulta os registros persistidos.
- **Testes E2E:** verifica fluxos completos pela API. Um exemplo é o teste que cadastra uma aeronave, agenda um voo pela rota HTTP e consulta o voo em seguida, verificando as respostas.
- **Fixtures:** permite preparar recursos compartilhados pelos testes. No projeto, o `conftest.py` define fixtures como `client` e `session_factory`, responsáveis por disponibilizar o cliente de testes do Flask e a fábrica de sessões do banco.
- **Testes de serviços com repositórios Fake:** permite verificar os serviços utilizando implementações em memória dos contratos de repositório, criadas no próprio projeto, sem precisar acessar o banco de dados.

### Camada em que aparece

O pytest é utilizado na camada de testes, organizada no diretório `tests/`, que contém testes de domínio, serviços, integração e API.

O arquivo `conftest.py` centraliza fixtures compartilhadas, evitando a repetição da preparação de recursos entre diferentes testes.

### Por que o domínio não depende do pytest?

O domínio não precisa conhecer ferramentas de testes automatizados. Suas entidades e regras de negócio funcionam independentemente do framework utilizado para verificá-las.

O pytest é uma ferramenta externa utilizada durante o desenvolvimento para validar o comportamento do sistema, sem participar da execução normal das regras de negócio.

## 2. Pontos de inversão de controle

A diferença entre uma biblioteca e um framework está em quem controla o fluxo do programa. O nosso código chama a biblioteca quando precisa dela, enquanto o framework assume esse fluxo e chama o nosso código nos pontos que deixa abertos para isso. No projeto, essa inversão de controle aparece em três lugares, um em cada framework que usamos.

**Rotas do Flask.** Em `src/airline/entrypoints/flask_app.py`, a função `cancelar_voo` recebe o decorador `@app.route("/voos/<numero_voo>/cancelar", methods=["POST"])` e não é chamada em nenhum outro lugar do nosso código. O decorador registra a função no `app`, e o Flask a chama quando chega um `POST` nesse endereço, passando o `numero_voo` tirado da URL e transformando o retorno numa resposta JSON.

**Fixtures do pytest.** Em `tests/conftest.py`, as fixtures `client` e `session_factory` preparam um banco limpo e o cliente de teste da API. Os testes só declaram esses nomes como parâmetros, como em `test_cancelar_voo_cancela_as_reservas_pela_api(client, session_factory)`, e o pytest executa a fixture de mesmo nome e entrega o resultado ao teste.

**Mapeamento do SQLAlchemy.** Em `src/airline/adapters/orm.py`, a classe `VooModel` herda de `Base` e só declara o `__tablename__` e as colunas, que o SQLAlchemy lê para registrar a tabela `voos` e criá-la no banco quando o `flask_app.py` chama `Base.metadata.create_all(engine)`. O mesmo SQLAlchemy aparece como biblioteca no `VooService.cancelar_voo`, onde somos nós que chamamos `self.session.commit()` para gravar o cancelamento.


## 3. Padrões de projeto dentro dos frameworks

Os frameworks que utilizamos não são apenas coleções de funções; internamente, eles são construídos sobre padrões consolidados de projeto de software (GoF e padrões de arquitetura corporativa de Martin Fowler). No nosso projeto, podemos apontar claramente onde pelo menos três desses padrões operam no código real:

### Padrão 1: Decorator (GoF Estrutural) — Flask

- **Onde aparece no nosso código:** Em `src/airline/entrypoints/flask_app.py`, em todas as definições de rotas da API, como:
  ```python
  @app.route("/voos/<numero_voo>/cancelar", methods=["POST"])
  def cancelar_voo(numero_voo):
  ...
  @app.post("/tripulantes")
  def cadastrar_tripulante():
  ...
  @app.get("/escalas/<voo_id>")
  def buscar_escala(voo_id):
  ```
- **Como o framework usa internamente:** O Flask utiliza o padrão estrutural Decorator para interceptar a função manipuladora de requisição (`view function`). Em vez de exigir que a nossa função herde de uma classe base de endpoint ou registre rotas manualmente em coleções externas, o decorator `@app.route` "embrulha" a função, extrai seus metadados, registra a regra no mapa de URLs (`url_map`) do Flask e a devolve intacta. Quando uma requisição HTTP chega, o framework executa comportamentos antes e depois da chamada da função (como parsing de parâmetros da URL e formatação da resposta), exemplificando a extensão de comportamento dinâmico sem alterar a estrutura da função decorada.

### Padrão 2: Data Mapper (Fowler / Padrão de Persistência) — SQLAlchemy

- **Onde aparece no nosso código:** Na separação estrita entre as entidades puras em `src/airline/domain/model.py` (`Tripulante`, `Escala`, `Voo`, `Aeronave`) e as classes de persistência em `src/airline/adapters/orm.py` (`TripulanteModel`, `EscalaModel`, `VooModel`, `AeronaveModel`), integradas através dos métodos `from_domain()` e `to_domain()`:
  ```python
  class TripulanteModel(Base):
      __tablename__ = "tripulantes"
      id = Column(String, primary_key=True)
      ...
      @classmethod
      def from_domain(cls, tripulante: Tripulante): ...

      def to_domain(self): ...
  ```
- **Como o framework usa internamente:** Ao contrário do padrão Active Record (onde a entidade de negócio herda do ORM e sabe salvar a si mesma no banco), o SQLAlchemy adota o padrão Data Mapper. O framework mantém uma camada de mapeamento independente responsável por transferir dados entre os objetos em memória e o esquema relacional do banco. Dessa forma, as nossas classes de domínio permanecem completamente desvinculadas de SQL, tipos de colunas, chaves primárias de banco ou chamadas de I/O, garantindo que o domínio permaneça puro e focado apenas nas regras de negócio.

### Padrão 3: Proxy / Lazy Loading (GoF Estrutural) — SQLAlchemy

- **Onde aparece no nosso código:** Nas definições de relacionamentos entre tabelas em `src/airline/adapters/orm.py`, como nas relações de `EscalaModel` com `EscalaTripulanteModel` e de `AeronaveModel` com `OrdemManutencaoModel`:
  ```python
  tripulantes = relationship(
      "EscalaTripulanteModel",
      back_populates="escala",
      cascade="all, delete-orphan"
  )
  ```
- **Como o framework usa internamente:** O SQLAlchemy utiliza objetos Proxy para intermediar o acesso a coleções e objetos relacionados. Quando uma `Escala` ou `Aeronave` é consultada no banco, o SQLAlchemy não executa imediatamente junções complexas com todas as tabelas filhas. Em vez disso, ele instancia uma coleção especial instrumentada que funciona como um Proxy Virtual (Lazy Loading). A leitura dos registros relacionados só é disparada quando o código de fato itera ou acessa o atributo, economizando memória e transferências desnecessárias de dados.

### Padrão 4: Factory / Dependency Injection (GoF Criacional) — pytest

- **Onde aparece no nosso código:** Em `tests/conftest.py`, nas definições das fixtures `@pytest.fixture def client(session_factory)` e `@pytest.fixture def session_factory()`, e em todos os testes e2e que recebem `client` como argumento:
  ```python
  def test_cadastrar_tripulante_sucesso(client):
      ...
  ```
- **Como o framework usa internamente:** O pytest funciona como um contêiner de injeção de dependências baseado em funções de fábrica (Factory). A anotação `@pytest.fixture` transforma a função em uma fábrica gerenciada, com ciclo de vida controlado (criação, execução com `yield` e finalização/limpeza). Em tempo de execução, o pytest inspeciona a lista de argumentos de cada função de teste e injeta automaticamente as dependências solicitadas, sem que o teste precise instanciar objetos manualmente ou gerenciar conexões.

---

## 4. E se fosse Django?

A escolha por uma arquitetura em camadas com microframeworks (Flask, SQLAlchemy puro e pytest) traz contrastes fundamentais quando comparada ao uso de um framework full-stack e opinativo como o **Django**:

### O que mudaria na arquitetura e no código:

1. **Adoção compulsória do padrão Active Record:**
   * No Django, todas as entidades de negócio herdam obrigatoriamente de `django.db.models.Model` (ex.: `class Tripulante(models.Model): ...`).
   * Não existiria o isolamento entre o domínio (`src/airline/domain/model.py`) e a persistência (`src/airline/adapters/orm.py`). Cada classe de negócio seria simultaneamente a representação da tabela no banco de dados, misturando regras operacionais da aviação com métodos de persistência como `.save()`, `.delete()` e consultas diretas como `Tripulante.objects.filter(...)`.

2. **Extinção dos Repositórios e Fakes:**
   * A camada de repositórios abstratos (`domain/repositories.py`) e suas implementações concretas (`adapters/repository.py`) deixariam de fazer sentido na mentalidade idiomática do Django, pois o `Manager` nativo (`Model.objects`) já atua como um repositório acoplado.
   * Não utilizaríamos `FakeTripulanteRepository` ou `FakeEscalaRepository`. Os testes de serviços seriam forçados a interagir diretamente com o banco de dados do Django (geralmente SQLite em memória ou transações revertidas via `TestCase`).

3. **Roteamento Centralizado vs Decoradores:**
   * O Flask utiliza roteamento distribuído e flexível via decoradores (`@app.route`, `@app.post`). No Django, o roteamento é obrigatoriamente centralizado em arquivos `urls.py`, mapeando rotas para Class-Based Views (CBVs), ViewSets ou funções controladoras, desacoplando a URL da função, mas aumentando a cerimônia de configuração.

4. **Camada de Serviço no Django:**
   * O padrão arquitetural tradicional do Django tende a concentrar a lógica de negócio ou nas Views (fat views) ou nos Models (fat models). Para mantermos uma `service_layer` organizada como a atual, precisaríamos adotar um padrão de arquitetura externa (como o Django Services Pattern), lutando contra a convenção padrão do framework que empurra a lógica para dentro dos modelos Active Record.

### Ganhos que o Django traria:
- **Painel Administrativo nativo (Django Admin):** Criaria automaticamente interfaces visuais completas para cadastrar tripulantes, inspecionar voos, gerenciar aeronaves e visualizar despachos sem necessidade de implementar telas ou rotas manuais.
- **Migrações automáticas:** Comandos nativos como `makemigrations` e `migrate` detectariam alterações nas classes de modelo e gerariam scripts de migração do banco automaticamente, dispensando scripts manuais de criação de schema.
- **Validação e serialização consolidadas:** O ecossistema Django REST Framework (DRF) forneceria serializadores robustos com validações declarativas, paginação e autenticação integradas.

### Perdas que o Django causaria:
- **Perda total da pureza do Domínio:** As entidades de negócio passariam a carregar dezenas de métodos e atributos de infraestrutura do Django, ferindo o princípio de que o domínio deve desconhecer detalhes de banco de dados.
- **Lentidão e dependência nos testes de unidade:** No projeto atual, a suíte unitária de domínio roda em frações de segundo porque não depende de nenhum módulo externo, I/O ou banco. No Django, instanciar ou testar um `Model` normalmente exige inicializar o ambiente do framework (`django.setup()`) e o schema de banco de dados, tornando a suíte consideravelmente mais pesada.
- **Dificuldade de aplicação de padrões GoF puros:** Padrões como **State** (aplicado na `Escala`) ou Value Objects puros (como `ControleJornada` e `CPF`) exigem adaptações não triviais quando encapsulados dentro de campos gerenciados pelo ORM do Django.

### Conclusão:
Se o objetivo do projeto fosse entregar rapidamente um produto web tradicional com formulários administrativos e CRUDs padrão, o **Django** seria muito mais produtivo. Porém, para um sistema com regras de negócio críticas e regulamentadas (como aviação civil), onde a testabilidade instantânea, a independência de infraestrutura e a modelagem rica em DDD são prioridades, a combinação adotada de **Flask + SQLAlchemy (Data Mapper) + Pytest** foi a decisão arquitetural correta, permitindo isolar o coração do sistema da tecnologia de armazenamento.
