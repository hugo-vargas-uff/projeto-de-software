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

## Aeronave, Matheus Andrade

## Reserva e Passageiro, Hugo Vargas

## Tripulante e Escala, Filipe Moreira

## Despacho, Vinicius Duarte