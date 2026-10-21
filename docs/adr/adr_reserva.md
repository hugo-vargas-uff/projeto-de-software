# ADR-001 — Identidade e criação de Reserva

## Contexto

Era necessário definir como identificar uma reserva e como representar sua relação com um passageiro e um voo.
No domínio do sistema, um passageiro pode possuir apenas uma reserva para determinado voo, e a reserva possui um
ciclo de vida, podendo ser confirmada ou cancelada.

## Decisão

A `Reserva` não terá um UUID próprio. Sua identidade será composta por `voo_id` e `passageiro_id`, que juntos
identificam unicamente uma reserva. Toda nova reserva será criada com o status `CONFIRMADA`, podendo posteriormente 
ser cancelada.

A criação será coordenada pelo `ReservaService`, que verifica se o passageiro e o voo existem antes de criar e
persistir a reserva.

## Alternativa considerada

Utilizar um UUID próprio para cada reserva, mantendo `voo_id` e `passageiro_id` como chaves estrangeiras. Essa abordagem
permitiria referenciar a reserva por um único identificador, mas exigiria uma restrição adicional de unicidade para
impedir mais de uma reserva do mesmo passageiro para o mesmo voo.

## Consequências

A identidade composta representa diretamente a regra de negócio e impede duplicações da mesma combinação quando aplicada
como chave primária no banco. Por outro lado, operações que identificam uma reserva precisam utilizar os dois
identificadores, em vez de apenas um UUID.
