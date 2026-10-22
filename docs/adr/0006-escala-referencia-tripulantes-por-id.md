# 0006 — A Escala referencia Tripulantes e Voo apenas por ID

- **Status:** aceito (Fase 1), registrado no checkpoint 1 da Fase 2
- **Autor:** Filipe Moreira (@Filipe-Moreira-sb)
- **Data do registro:** 21/10/2026

## Contexto

A montagem da tripulação de um voo exige associar múltiplos tripulantes (pilotos, copilotos e comissários) a um voo específico. Cada tripulante possui ciclo de vida e invariantes próprios (como o teto regulamentar de horas de voo), enquanto o voo possui sua própria dinâmica de agendamento e assentos. Se a `Escala` contivesse instâncias completas de `Tripulante` ou de `Voo`, carregar ou salvar uma escala exigiria carregar grafos inteiros de objetos, gerando acoplamento transacional indesejado e risco de concorrência.

## Decisão

A `Escala` é um agregado independente cuja raiz referencia o voo (`voo_id`) e os tripulantes (`tripulantes_ids`) exclusivamente por seus identificadores primitivos (`UUID` ou string).
- A raiz da `Escala` protege sua própria invariante: impede que o mesmo tripulante seja alocado mais de uma vez no mesmo voo (`ErroRegraTripulacao`).
- A invariante de horas do tripulante (`registrar_horas_de_voo`) permanece dentro do agregado `Tripulante`.
- A coordenação entre verificar horas do tripulante e adicioná-lo na escala é de responsabilidade da camada de serviço (`TripulacaoService.escalar_tripulante`).
- No banco de dados, a persistência utiliza a tabela `escalas` e a tabela associativa `escala_tripulantes` com `cascade="all, delete-orphan"`, sem criar chaves estrangeiras rígidas no nível de domínio.

## Alternativas consideradas

- **Guardar objetos Tripulante dentro da Escala:** Daria acesso direto aos métodos do tripulante, mas forçaria a persistência de ambos na mesma transação, aumentando conflitos e violando a diretriz de DDD de manter agregados pequenos.
- **A Escala pertencer ao agregado Voo:** Centralizaria todas as informações do voo num único agregado, mas tornaria a entidade `Voo` excessivamente inflada e sujeita a concorrência entre reservas, despacho e escalas.
- **Não ter agregado Escala e guardar o `voo_id` dentro do Tripulante:** Dificultaria a visão consolidada da tripulação escalada para um voo e impediria consultas eficientes por voo.

## Consequências

- (+) Os agregados `Tripulante`, `Voo` e `Escala` evoluem de forma desacoplada e possuem testes unitários completamente isolados.
- (+) Reduz o risco de locks no banco durante gravações concorrentes.
- (−) Exige que a camada de serviço orquestre a operação com dois repositórios (`TripulanteRepository` e `EscalaRepository`).
- (−) A consistência entre tripulantes alocados e horas debitadas não é garantida por uma única transação no domínio, dependendo da coordenação do serviço.

## Riscos e evolução

- Se uma escala for cancelada ou um tripulante removido, a restituição de horas de voo precisará ser explicitamente orquestrada pelo serviço.
- Não há validação em tempo real se o voo associado ainda está ativo/agendado no momento em que a escala é montada, ponto que poderá ser aprimorado com eventos de domínio no futuro.

## Evidências

- `761b2b4` — test: cria testes unitarios para criacao e invariante de horas do Tripulante
- `8f4b87e` — feat: implementa entidade Tripulante com controle de teto de horas
- `bd87044` — test: adiciona testes de alocacao de tripulantes na Escala
- `d402dac` — feat: implementa agregado Escala com protecao contra tripulante duplicado
- `afb9fef` — feat: implementa servicos de tripulacao e escala na camada de servico
