# Frameworks

## 1. Papel de cada framework

### Flask

### SQLAlchemy

### pytest

## 2. Pontos de inversão de controle

A diferença entre uma biblioteca e um framework está em quem controla o fluxo do programa. O nosso código chama a biblioteca quando precisa dela, enquanto o framework assume esse fluxo e chama o nosso código nos pontos que deixa abertos para isso. No projeto, essa inversão de controle aparece em três lugares, um em cada framework que usamos.

**Rotas do Flask.** Em `src/airline/entrypoints/flask_app.py`, a função `cancelar_voo` recebe o decorador `@app.route("/voos/<numero_voo>/cancelar", methods=["POST"])` e não é chamada em nenhum outro lugar do nosso código. O decorador registra a função no `app`, e o Flask a chama quando chega um `POST` nesse endereço, passando o `numero_voo` tirado da URL e transformando o retorno numa resposta JSON.

**Fixtures do pytest.** Em `tests/conftest.py`, as fixtures `client` e `session_factory` preparam um banco limpo e o cliente de teste da API. Os testes só declaram esses nomes como parâmetros, como em `test_cancelar_voo_cancela_as_reservas_pela_api(client, session_factory)`, e o pytest executa a fixture de mesmo nome e entrega o resultado ao teste.

**Mapeamento do SQLAlchemy.** Em `src/airline/adapters/orm.py`, a classe `VooModel` herda de `Base` e só declara o `__tablename__` e as colunas, que o SQLAlchemy lê para registrar a tabela `voos` e criá-la no banco quando o `flask_app.py` chama `Base.metadata.create_all(engine)`. O mesmo SQLAlchemy aparece como biblioteca no `VooService.cancelar_voo`, onde somos nós que chamamos `self.session.commit()` para gravar o cancelamento.


## 3. Padrões de projeto dentro dos frameworks

## 4. E se fosse Django?
