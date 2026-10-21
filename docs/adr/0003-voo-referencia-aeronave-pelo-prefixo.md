# 0003 — O Voo referencia a Aeronave pelo prefixo e copia a capacidade

- **Status:** aceito (Fase 1), registrado no checkpoint 1 da Fase 2
- **Autor:** Matheus Verdan (@verdanmatheus)
- **Data do registro:** 21/10/2026

## Contexto

O Voo precisa saber quantos assentos tem para proteger a regra de lotação, e só pode ser agendado com uma aeronave disponível. A capacidade e a disponibilidade pertencem ao agregado Aeronave, que é mantido por outro integrante e muda por outros motivos, como abrir e concluir ordens de manutenção.

## Decisão

O Voo guarda apenas o prefixo da aeronave (`aeronave_id`). Ao agendar, o `VooService` busca a aeronave pelo repositório, pergunta se ela está disponível na data (`esta_disponivel`) e copia a capacidade para o próprio Voo. Depois disso, o Voo controla os assentos sozinho, com `alocar_assento()`.

## Alternativas consideradas

- **Guardar o objeto Aeronave dentro do Voo.** Daria acesso direto à capacidade, mas juntaria dois agregados numa mesma gravação e acoplaria as regras de manutenção às de lotação.
- **Consultar a capacidade da aeronave a cada alocação de assento.** A capacidade estaria sempre atualizada, mas cada alocação passaria a depender de outro agregado e de mais uma leitura no banco.
- **Voo e Aeronave num agregado só.** Simplificaria a consulta, mas uma aeronave faz centenas de voos e seria bloqueada a cada operação em qualquer um deles.

## Consequências

- (+) Voo e Aeronave evoluem e são testados separadamente; o teste do serviço usa um repositório falso de aeronave.
- (+) A regra de manutenção da Aeronave passa a valer no agendamento, porque o serviço pergunta à própria Aeronave.
- (−) A disponibilidade da aeronave só é conferida no agendamento e, se ela entrar em manutenção depois, os voos já agendados continuam agendados e podem ser realizados.
- (−) É preciso uma camada de serviço para coordenar os dois agregados.

## Riscos e evolução

- Para o voo reagir a uma aeronave que entra em manutenção, seria preciso um aviso da Aeronave para os voos que a usam, ou uma nova verificação ao realizar o voo.
- Não existe caso de uso para trocar a aeronave de um voo já agendado. Se a companhia precisar disso, o novo caso de uso terá de perguntar de novo à Aeronave se ela está disponível e copiar a nova capacidade, levando em conta os assentos já alocados.

## Evidências

- `1b54eff` — feat: add aeronave_id e capacidade de assentos em voo
- `025311c` — feat: implementa metodo alocar_assento com invariante de lotacao em voo
- `57db2de` — test: agendar voo copia a capacidade da aeronave
- `738f24e` — feat: cria vooService com agendar_voo
- `7c3595c` — feat: valida numero repetido e disponibilidade da aeronave