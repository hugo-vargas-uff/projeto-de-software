# Proposta de Projeto: Sistema de Operações de Companhia Aérea

## Integrantes do grupo

- Matheus Verdan ( https://github.com/verdanmatheus ): agregado Voo
- Hugo Vargas ( https://github.com/hugo-vargas-uff ): agregado Reserva
- Felipe Moreira ( https://github.com/Filipe-Moreira-sb ): agregado Tripulação
- Matheus Andrade ( https://github.com/MatheusFSD ): agregado Aeronave, parte de manutenção
- Vinicius Duarte( https://github.com/DEVinicius-jpeg ): agregado Aeronave, parte de despacho de bagagem

## Domínio

Operação de uma companhia aérea: agendamento de voos, reservas de passageiros,
escalonamento de tripulação e controle da frota, incluindo manutenção e despacho
de bagagem.

## Entidades e agregados

O domínio tem 10 entidades de negócio, organizadas em 4 agregados.

### Voo
- Entidades: Voo(raiz), Trecho
- Invariante: um voo já realizado não pode ser cancelado, e um voo cancelado
  não pode voltar a ficar agendado.

### Reserva
- Entidades: Reserva(raiz), Passageiro
- Invariante: o número de reservas confirmadas não pode exceder a capacidade
  do voo.

### Tripulação
- Entidades: Escala(raiz), Tripulante
- Invariante: a soma de horas de voo de um tripulante não pode ultrapassar o
  teto regulamentar do período.

### Aeronave
- Entidades: Aeronave(raiz), OrdemManutencao, Despacho, Volume (objeto de valor)
- Invariante de manutenção: aeronave com manutenção pendente ou vistoria vencida
  fica indisponível para voos.
- Invariante de despacho: o peso total dos volumes despachados não pode exceder
  a carga máxima da aeronave.

