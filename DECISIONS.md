# Agregado Voo

## Trecho como objeto de valor
2026-09-18

Um trecho tem só origem e destino, então não vi necessidade de dar um ID a ele. GRU -> GIG sempre representa o mesmo trecho, e o que importa é o valor, não uma identidade própria. Por isso tratei Trecho como Objeto de Valor.

Também não faz sentido alterar um trecho depois de criado (se a rota mudar, basta criar um novo), então usei frozen=True para deixar o objeto imutável.

## StatusVoo como Enum
2026-09-18

Usei Enum para os status do Voo (AGENDADO, CANCELADO, REALIZADO) para padronizar os valores e evitar erros de digitação.
