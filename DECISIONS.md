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
