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

## Reserva e Passageiro, Hugo Vargas

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