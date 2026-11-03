# Refatorações SOLID

## Voo, Matheus Verdan

### Princípio violado: Aberto/Fechado

Código antes, em `src/airline/domain/model.py`, dos commits `3911707` (20/09) e `78c3ae0` (29/09):

```python
    def cancelar(self):
        if self.status == StatusVoo.REALIZADO:
            raise ErroRegraVoo("voo realizado, nao pode ser cancelado")
        if self.status == StatusVoo.CANCELADO:
            raise ErroRegraVoo("Voo ja estava cancelado")

        self.status = StatusVoo.CANCELADO

    def realizar(self):
        if self.status != StatusVoo.AGENDADO:
            raise ErroRegraVoo("So pode realizar voos que estao agendados")
        self.status=StatusVoo.REALIZADO

    def alocar_assento(self):
        #so voo agendado aceita passageiro novo
        if self.status != StatusVoo.AGENDADO:
            raise ErroRegraVoo("So pode alocar assento em voo agendado")
        if self.assentos_disponiveis <= 0:
            raise ErroRegraVoo("lotado, sem assentos livres.")
        self.assentos_disponiveis -= 1
```

### O problema

As regras de status do voo estavam espalhadas em ifs dentro do `cancelar`, do `realizar` e do `alocar_assento`, o que dificultava mudar essas regras depois. Se a companhia passasse a registrar atrasos, por exemplo, com um status ATRASADO em que o voo ainda pudesse ser realizado e receber passageiros, seria preciso revisar o `cancelar` e mudar o `realizar` e o `alocar_assento`, que só aceitavam voo agendado. Um status novo obrigava a mexer em métodos que já funcionavam e estavam testados, o que o princípio Aberto/Fechado pede para evitar.

### A refatoração

No commit afe1aad, as regras saíram de dentro dos métodos e foram para duas estruturas no model.py, a TRANSICOES_VOO, que diz quais mudanças cada status permite, e o STATUS_QUE_ACEITAM_ASSENTO, que diz em quais status o voo recebe passageiro. O cancelar e o realizar agora só chamam o `mudar_status`, que consulta a tabela.

```python
# mudancas de status que cada status permite
TRANSICOES_VOO = {
    StatusVoo.AGENDADO: {StatusVoo.CANCELADO, StatusVoo.REALIZADO},
    StatusVoo.CANCELADO: set(),
    StatusVoo.REALIZADO: set(),
}

# status em que o voo ainda aceita passageiro novo
STATUS_QUE_ACEITAM_ASSENTO = {StatusVoo.AGENDADO}

    def cancelar(self):
        self.mudar_status(StatusVoo.CANCELADO)

    def realizar(self):
        self.mudar_status(StatusVoo.REALIZADO)

    def mudar_status(self, novo_status):
        if novo_status not in TRANSICOES_VOO[self.status]:
            raise ErroRegraVoo(f"voo {self.status.value.lower()} nao pode passar para {novo_status.value.lower()}")
        self.status = novo_status
```

Com isso, criar o ATRASADO exigiria acrescentar o valor no `StatusVoo`, ajustar a tabela e o conjunto e criar um método `atrasar()`, sem alterar os métodos que já existiam.

### Testes

Antes de mexer no código, acrescentei dois testes para os casos que faltavam, cancelar um voo já cancelado e realizar um voo já realizado `90560b6`. Os 132 testes passaram antes e depois da refatoração. Para conferir, liberei de propósito na tabela o cancelamento de um voo já cancelado, e só o teste novo acusou o erro.

### Custo

A refatoração trouxe uma tabela, um conjunto e um método a mais, e quem lê o `cancelar` agora precisa olhar a tabela para saber quando ele dá erro. As mensagens de erro também ficaram mais genéricas, mas a API continua respondendo 400 e nenhum teste depende do texto. Compensa porque as regras ficam num lugar só e um status novo não exige mudar métodos já testados.

Considerei criar uma classe por status, mas preferi a tabela porque os status do voo não têm comportamento próprio, só definem quais mudanças são permitidas, e as classes deixariam o código maior sem ganho. Se algum status passar a ter comportamento próprio, vale rever essa escolha.

## Aeronave, Matheus Andrade

### Princípio violado: Substituição de Liskov (LSP)

Código antes, dos commits `05ca3a9` (26/09) e `51ca19a` (26/09). O contrato `AeronaveRepository` tem duas implementações, e o `salvar` de cada uma faz uma coisa diferente:

```python
# adapters/repository.py, SqlAlchemyAeronaveRepository (05ca3a9)
    def salvar(self, aeronave: Aeronave) -> None:
        aeronave_model = AeronaveModel(
            prefixo=aeronave.prefixo,
            modelo=aeronave.modelo,
            capacidade=aeronave.capacidade,
            validade_vistoria=aeronave.validade_vistoria
        )

        for ordem in aeronave.ordens_manutencao:
            ordem_model = OrdemManutencaoModel(
                descricao=ordem.descricao,
                status=ordem.status
            )

            aeronave_model.ordens_manutencao.append(ordem_model)

        self.session.add(aeronave_model)
        self.session.commit()
```

```python
# tests/unit/service_layer/test_aeronave_service.py, FakeAeronaveRepository (51ca19a)
    def salvar(self, aeronave):
        self.aeronaves[aeronave.prefixo] = aeronave
```

### O problema

O `AeronaveService` só conhece o contrato `AeronaveRepository` e parte do princípio de que dá para salvar a mesma aeronave mais de uma vez: o `abrir_ordem_manutencao` busca a aeronave, abre a ordem e salva de novo. O fake aceita isso, porque sobrescreve no dicionário. O repositório real não aceita, porque o `salvar` sempre insere, e falha com `IntegrityError` (`UNIQUE constraint failed: aeronaves.prefixo`). Trocar o fake pelo repositório real quebrava um código que só dependia do contrato, e é isso que o princípio de Liskov proíbe.

Na prática, os testes do serviço passavam e o mesmo caso de uso falhava com o banco real. Foi por isso que as rotas de abrir e concluir ordem de manutenção nunca foram expostas na API (ADR 0004 e seção 4.3 do `arquitetura.md`). Os repositórios de Voo e de Despacho já atualizavam quando o registro existia, e o da Aeronave era o que destoava.

### A refatoração

No commit `0353d3e`, o `salvar` do `SqlAlchemyAeronaveRepository` passou a buscar a aeronave pelo prefixo. Se ela não existe, insere. Se existe, atualiza os campos e substitui as ordens de manutenção: faz o `clear()` e regrava as atuais, e o `delete-orphan` apaga as antigas, porque a ordem ainda não tem identidade no domínio. A conversão entre domínio e ORM saiu do repositório e foi para o `from_domain` e o `to_domain` dos models, como já estava no resto do grupo. O `to_domain` continua remontando as ordens pelos métodos da própria aeronave (ADR 0004).

```python
    def salvar(self, aeronave: Aeronave) -> None:
        model = self.session.query(AeronaveModel).filter_by(prefixo=aeronave.prefixo).first()
        if model is None:
            model = AeronaveModel.from_domain(aeronave)
            self.session.add(model)
        else:
            model.modelo = aeronave.modelo
            model.capacidade = aeronave.capacidade
            model.validade_vistoria = aeronave.validade_vistoria
            model.ordens_manutencao.clear()
            for ordem in aeronave.ordens_manutencao:
                model.ordens_manutencao.append(OrdemManutencaoModel.from_domain(ordem))
        self.session.commit()
```

Considerei fazer o contrário: deixar o fake recusar o `salvar` de uma aeronave que já existe, como o repositório real fazia. Descartei porque o contrato correto de `salvar` é persistir o estado atual, como fazem os repositórios de Voo e de Despacho, e porque o próprio `AeronaveService` precisa salvar uma aeronave existente para abrir uma ordem.

### Testes

Antes de mexer no código, escrevi um teste de contrato (`e98040c`, 02/11) que roda o mesmo cenário nas duas implementações, com uma fixture parametrizada (`fake` e `sqlalchemy`). São 4 cenários, então 8 execuções. Antes da refatoração, 6 passavam e 2 falhavam, as duas no SQLAlchemy e com `IntegrityError`: salvar uma aeronave que já existe e concluir uma ordem e salvar. Depois, as 8 passam, e a suíte inteira foi de 146 passando e 2 falhando para 148 passando. O commit da refatoração não alterou nenhum teste que já existia, e os e2e da API de aeronave continuaram passando.

### Custo

A conversão ganhou `from_domain` e `to_domain` em dois models, e o `orm.py` cresceu de 219 para 250 linhas. O repositório encolheu, então o saldo do commit foi de +9 linhas, mas o código de mapeamento agora está em dois lugares, e um campo novo na Aeronave exige mudar o `from_domain`, o `to_domain` e a parte de atualização do `salvar`. O `salvar` também ficou com dois caminhos, inserir e atualizar. Compensa porque os dois repositórios passam a obedecer ao mesmo contrato, o fake volta a ser confiável nos testes do serviço e as rotas de manutenção podem ser expostas na API sem outra mudança de persistência.

## Reserva e Passageiro, Hugo Vargas

### Princípio Violado: Princípio da Responsabilidade Única

### Agregado: Passageiro

### 1. Violação identificada

**Commit anterior:** `81f49f1`

Antes da refatoração, o CPF era representado diretamente como uma string na entidade `Passageiro`:

```python
class Passageiro:
    def __init__(self, nome, cpf):
        self.id = uuid.uuid4()
        self.nome = nome
        self.cpf = cpf
```

A entidade recebia o CPF sem uma abstração específica para representar e centralizar as regras relacionadas a esse dado.

**Problema concreto:**

A entidade `Passageiro` utilizava uma string para representar o CPF, sem uma abstração responsável por garantir sua normalização e validade. Isso fazia com que as regras específicas desse dado não tivessem um local próprio no domínio. Caso essas regras precisassem ser ampliadas ou modificadas, sua implementação poderia acabar distribuída entre diferentes componentes, aumentando o acoplamento e dificultando a manutenção.

### 2. Refatoração realizada

**Commit posterior:** `f1184e0`

Foi criado o Value Object `CPF`, responsável por centralizar as regras de representação, normalização e validação do CPF.

A implementação contempla:

- Normalização do valor, removendo caracteres que não sejam dígitos.
- Validação da quantidade de dígitos.
- Rejeição de sequências com todos os dígitos iguais.

A entidade `Passageiro` passou a exigir uma instância de `CPF` em seu construtor e no método `restaurar()`, impedindo que uma string seja utilizada diretamente como CPF.

Também foram criadas duas exceções específicas de domínio:

- `CpfInvalidoException`: lançada pelo Value Object `CPF` quando o valor não atende às regras de validação.
- `TipoCpfInvalidoException`: lançada pela entidade `Passageiro` quando recebe um objeto que não é uma instância de `CPF`.

O `PassageiroService` recebe o Value Object já construído pelo Controller e permanece responsável pelas regras do caso de uso, como verificar a existência de cadastros com CPF duplicado.

O `PassageiroModel` realiza as conversões entre o Value Object e a representação textual armazenada no banco de dados, sem exigir alterações na estrutura de persistência.

### 3. Garantia de comportamento por meio de testes

Foram implementados e executados testes para verificar:

- Criação e normalização do Value Object `CPF`.
- Rejeição de CPFs com quantidade incorreta de dígitos.
- Rejeição de CPFs com todos os dígitos iguais.
- Impedimento da criação de passageiros com CPF representado diretamente como string.
- Prevenção de cadastros com CPF duplicado.
- Retorno HTTP 400 nos endpoints para requisições com CPFs inválidos.

Os testes automatizados verificaram que as funcionalidades existentes de cadastro e identificação de passageiros continuaram funcionando após a refatoração. Também foram adicionados testes para as novas regras do Value Object `CPF`, garantindo a normalização dos valores, a rejeição de CPFs inválidos e o tratamento adequado das exceções nos endpoints.

Dessa forma, foi possível preservar os comportamentos anteriores, como a unicidade do CPF, enquanto novas garantias foram incorporadas ao domínio.

### 4. Custo

A principal desvantagem da alteração foi o aumento da quantidade de classes e da indireção no código, com a introdução do Value Object `CPF` e de exceções específicas de domínio.

Também foi necessário adaptar os pontos de entrada da aplicação, os serviços e as conversões da camada de persistência para trabalhar com o novo objeto.

Apesar desse custo, a alteração compensa por centralizar as regras relacionadas ao CPF, evitar a duplicação de validações e tornar o domínio mais consistente e fácil de manter e testar.
## Tripulante e Escala, Filipe Moreira

### Princípio violado: Responsabilidade Única (SRP)

Código antes, em `src/airline/domain/model.py`, do commit `8f4b87e` (19/09):

```python
class Tripulante:
    def __init__(self, nome: str, cargo: CargoTripulante, teto_horas: float = 85.0):
        self.id = uuid.uuid4()
        self.nome = nome
        self.cargo = cargo
        self.teto_horas = teto_horas
        self.horas_de_voo = 0.0

    def registrar_horas_de_voo(self, horas: float):
        if self.horas_de_voo + horas > self.teto_horas:
            raise ErroRegraTripulacao("Teto regulamentar de horas ultrapassado")
        self.horas_de_voo += horas

    def pode_voar(self, duracao_horas: float) -> bool:
        return (self.horas_de_voo + duracao_horas) <= self.teto_horas
```

### O problema

A classe `Tripulante` acumulava duas responsabilidades com motivos diferentes para mudar:
1. **Identidade e cadastro do profissional:** gerenciar atributos cadastrais como identificador único (`id`), `nome` e `cargo`.
2. **Controle de regras regulamentares de jornada de voo:** rastrear `horas_de_voo`, verificar o limite regulamentar (`teto_horas`), validar disponibilidade de jornada (`pode_voar`) e lançar exceções de extrapolação (`ErroRegraTripulacao`).

Se a regulamentação aeronáutica (como a Lei do Aeronauta nº 13.475/2017) mudasse as regras de jornada — como cálculo de saldo residual, tetos diferenciados por período ou descanso obrigatório —, éramos forçados a modificar a classe de cadastro `Tripulante`. Além disso, a lógica de jornada não podia ser testada ou reutilizada de forma isolada sem instanciar uma entidade completa de domínio com UUID e cargo.

### A refatoração

No commit `17e4cc7`, extraí toda a responsabilidade de jornada e limites regulamentares para uma classe/Objeto de Valor dedicado, `ControleJornada`. A entidade `Tripulante` passou a compor essa jornada e a delegar as operações, mantendo o foco exclusivo na identidade do aeronauta:

```python
class ControleJornada:
    """Responsabilidade única: controle de horas voadas e aplicação de limites regulamentares."""

    def __init__(self, teto_horas: float = 85.0, horas_acumuladas: float = 0.0):
        self.teto_horas = teto_horas
        self.horas_de_voo = horas_acumuladas

    def registrar_horas(self, horas: float):
        if self.horas_de_voo + horas > self.teto_horas:
            raise ErroRegraTripulacao("Teto regulamentar de horas ultrapassado")
        self.horas_de_voo += horas

    def pode_voar(self, duracao_horas: float) -> bool:
        return (self.horas_de_voo + duracao_horas) <= self.teto_horas

    @property
    def horas_disponiveis(self) -> float:
        return max(0.0, self.teto_horas - self.horas_de_voo)
```

Na classe `Tripulante`, o construtor instancia `self.jornada = ControleJornada(teto_horas, 0.0)` e expõe propriedades e métodos delegados (`teto_horas`, `horas_de_voo`, `registrar_horas_de_voo`, `pode_voar`). Isso manteve a interface pública idêntica, preservando total compatibilidade com a camada de serviço (`TripulacaoService`), os adaptadores do SQLAlchemy (`TripulanteModel`) e os entrypoints da API.

### Testes

Antes de refatorar, adicionei testes de unidade em `tests/unit/domain/test_tripulante.py` (commit `f94553c`) para cobrir o método `pode_voar` e o caso de borda de atingir exatamente o teto de 85h. Em seguida, após a refatoração, acrescentei um teste específico exercitando `ControleJornada` de forma totalmente isolada. A suíte completa (135 testes) passou sem nenhuma regressão.

### Custo

A refatoração introduziu uma classe adicional (`ControleJornada`) e um nível de indireção através de properties delegadas em `Tripulante`. O custo é pequeno diante do ganho: as regras de jornada agora podem evoluir de forma independente das informações de cadastro, e a verificação de limites regulamentares pode ser testada isoladamente em memória sem a necessidade de instanciar entidades complexas.

## Despacho, Vinicius Duarte