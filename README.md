# Sistema de Operações de Companhia Aérea

Trabalho em grupo da disciplina de Projeto de Software.


## Quem faz o quê

| Integrante | GitHub | Responsabilidade |
|---|---|---|
| Matheus Verdan | [verdanmatheus](https://github.com/verdanmatheus) | Agregado Voo (Voo, Trecho) |
| Hugo Vargas | [hugo-vargas-uff](https://github.com/hugo-vargas-uff) | Agregados Reserva e Passageiro |
| Filipe Moreira | [Filipe-Moreira-sb](https://github.com/Filipe-Moreira-sb) | Agregados Escala e Tripulante |
| Matheus Andrade | [MatheusFSD](https://github.com/MatheusFSD) | Agregado Aeronave (Aeronave, OrdemManutencao) |
| Vinicius Duarte | [DEVinicius-jpeg](https://github.com/DEVinicius-jpeg) | Agregado Despacho (Despacho, Volume) |

A divisão começou com 4 agregados e foi ajustada para 7 na Semana 3.

## Agregados

| Agregado (raiz) | Objetos internos | Papel e regra principal |
|---|---|---|
| Voo | Trecho (objeto de valor) | Não aloca mais assentos que a capacidade. Voo cancelado ou realizado não muda mais de status. |
| Reserva | StatusReserva (enum: CONFIRMADA, CANCELADA) | Liga um passageiro a um voo pelos IDs dos dois. Pode ser cancelada, alterando o status para CANCELADA. |
| Passageiro | | Existe independente dos voos, o que permite ter um histórico de reservas. |
| Tripulante | CargoTripulante (enum: PILOTO, COPILOTO, COMISSARIO) | A soma de horas de voo no período não pode passar do teto regulamentar (padrão: 85 h). |
| Escala | | Monta a tripulação de um voo, referenciando os tripulantes por ID. Não permite adicionar o mesmo tripulante duas vezes. |
| Aeronave | OrdemManutencao | Com manutenção pendente ou vistoria vencida, fica indisponível para voos. |
| Despacho | Volume (objeto de valor) | O peso total dos volumes não pode passar da carga máxima. |

## Como rodar os testes

```bash
pip install -r requirements.txt
cd tests
python -m pytest -v
```
