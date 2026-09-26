# Agregado Voo

## Trecho como objeto de valor
2026-09-18

Um trecho tem só origem e destino, então não vi necessidade de dar um ID a ele. GRU -> GIG sempre representa o mesmo trecho, e o que importa é o valor, não uma identidade própria. Por isso tratei Trecho como Objeto de Valor.

Também não faz sentido alterar um trecho depois de criado (se a rota mudar, basta criar um novo), então usei frozen=True para deixar o objeto imutável.

## StatusVoo como Enum
2026-09-18

Usei Enum para os status do Voo (AGENDADO, CANCELADO, REALIZADO) para padronizar os valores e evitar erros de digitação.

## Trocas de Status
2026-09-20

Em vez de deixar o status do voo ser alterado livremente de fora da classe, decidi criar métodos específicos (cancelar() e realizar()). Dessa forma, o próprio agregado consegue proteger suas regras de negócio antes da mudança ocorrer. Por exemplo, o método lança um ErroRegraVoo caso alguém tente cancelar um voo que já foi realizado.

## Sem metodo para reagendar()
2026-09-20

Inicialmente pensei em criar um método para voltar o status de CANCELADO para AGENDADO. Mas, olhando para a situação real, um voo cancelado envolve mudanças que vão além do próprio status. Se a companhia precisar daquela rota novamente, o correto é instanciar um Voo novo. Por isso, decidi que um voo cancelado (ou realizado) não pode mais mudar de status.

## Invariante de lotação movida para o Voo
2026-09-24
Percebi que no modelo original, a regra de não exceder a capacidade do voo estava atribuída ao agregado Reserva. Isso não funcionaria na prática porque a Reserva não tem acesso ao número total de assentos nem sabe quantas outras reservas existem. Movi essa responsabilidade para o Voo, que agora recebe a capacidade da aeronave no momento da criação e controla a alocação de
assentos internamente com o método alocar_assento().


# Agregado Aeronave — Matheus Andrade

## 1. O que eu fiz neste checkpoint

Neste checkpoint criei a classe Aeronave, que representa uma aeronave dentro do domínio do sistema. Antes de criar a classe, escrevi os testes para criação, igualdade, diferença entre aeronaves e disponibilidade inicial.

## 2. Arquivos e commits

- tests/unit/domain/test_aeronave.py, 
- src/airline/domain/model.py, bloco Aeronave

## 3. Decisão: Aeronave é entidade, não objeto de valor
2026-09-20

Decidi tratar Aeronave como uma entidade porque ela possui uma identidade própria, representada pelo prefixo. Duas aeronaves com o mesmo prefixo representam a mesma aeronave, mesmo que outros dados, como modelo ou capacidade, estejam diferentes. Isso é diferente do Trecho criado pelo Verdan, que é um objeto de valor e depende dos seus atributos para definir igualdade. Também não usei frozen=True, porque a aeronave vai precisar mudar de estado no futuro, por exemplo quando entrar ou sair de manutenção.

## 4. Decisão: disponivel como atributo
2026-09-20

Por enquanto decidi guardar disponivel como um atributo da aeronave, iniciando com o valor True. Fiz assim porque ainda não existe a OrdemManutencao no código e essa foi a forma mais simples de atender os testes atuais.

Essa solução tem uma limitação: o atributo pode ser alterado diretamente por qualquer parte do código, sem passar por uma regra do domínio. Quando a OrdemManutencao for criada, pretendo revisar isso para que a disponibilidade dependa das regras de manutenção e não apenas de uma alteração manual no atributo.

## 5. Próximos passos

Os próximos passos são avaliar o uso de `__hash__`, implementar a regra de vistoria vencida, criar a OrdemManutencao e garantir a regra de que uma aeronave com manutenção pendente não esteja disponível.

## 6. Uso de IA

Usei IA para tirar dúvidas sobre entidade e objeto de valor, entender melhor `__eq__` e `__hash__`, ajudar a interpretar erros de ambiente e revisar o código que eu escrevi. O código utilizado no projeto foi escrito por mim.

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