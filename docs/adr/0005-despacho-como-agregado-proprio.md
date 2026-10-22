# 0005 — Despacho como agregado próprio, separado da Aeronave

- **Status:** aceito (Fase 1), registrado no checkpoint 1 da Fase 2
- **Autor:** Vinicius Duarte (@DEVinicius-jpeg)
- **Data do registro:** 21/10/2026

## Contexto

Na proposta do projeto (`PROPOSTA.md`, commit `4fe1bdd`), o despacho de bagagem fazia parte do agregado Aeronave, junto com a `OrdemManutencao`, e a invariante era: "o peso total dos volumes despachados não pode exceder a carga máxima da aeronave".

Quando fui implementar, apareceram três problemas:

- Um despacho existe para **um voo**, não para a aeronave. A mesma aeronave faz vários voos e cada voo tem a sua carga. Dentro da Aeronave, a lista de despachos cresceria a cada voo e seria carregada inteira toda vez que alguém consultasse a disponibilidade.
- O agregado Aeronave é mantido pelo Matheus Andrade e muda por motivos de manutenção. Colocar o despacho dentro dele faria duas pessoas editarem a mesma raiz, e cada volume despachado regravaria a aeronave.
- O campo `capacidade` da Aeronave é número de assentos, não peso. Não existia "carga máxima" na Aeronave.

## Decisão

O `Despacho` é a raiz de um agregado próprio, e o `Volume` é um objeto de valor interno.

- O `Despacho` é entidade: tem `id` (uuid4), e igualdade e hash usam esse `id`.
- O `Volume` é `dataclass(frozen=True)` só com `peso`. Dois volumes de 150 kg são iguais.
- O `Despacho` referencia o voo só pelo `voo_id` (o número do voo), como a `Escala` faz.
- A `carga_maxima` é informada quando o despacho é aberto, e não lida da Aeronave.
- A invariante fica num único lugar: `Despacho.adicionar_volume` lança `ErroRegraDespacho` se o novo peso total passar da `carga_maxima`. O cálculo do peso livre também é do domínio (`peso_disponivel`).
- A regra "um despacho por voo" é verificada no `DespachoService.abrir_despacho`, consultando `buscar_por_voo`.
- No banco são duas tabelas (`despachos` e `despacho_volumes`) com `cascade="all, delete-orphan"`. Como o `Volume` não tem identidade, no update os volumes são apagados e gravados de novo.

## Alternativas consideradas

- **Manter o Despacho dentro do agregado Aeronave (proposta original).** A carga máxima poderia vir da própria aeronave, mas a aeronave acumularia despachos de todos os voos, misturaria manutenção com bagagem e seria regravada a cada volume. Também obrigaria criar um campo de peso na Aeronave, que é de outro integrante.
- **Colocar o Despacho dentro do agregado Voo.** O voo é a coisa a que o despacho realmente pertence, mas o Voo seria regravado e carregaria todos os volumes a cada assento alocado, e juntaria a regra de lotação com a de carga num agregado de outro autor.
- **Ler a carga máxima da Aeronave no serviço** (Despacho → Voo → Aeronave). Deixaria o limite sempre coerente com o avião, mas o `DespachoService` passaria a depender de dois repositórios de outros agregados e seria preciso alterar o domínio da Aeronave. Optei por receber o valor ao abrir o despacho e deixar essa ligação para quando a Aeronave tiver um campo de peso.
- **Volume como entidade com `id`.** Permitiria remover ou corrigir um volume específico e fazer update linha a linha no banco, mas nenhum caso de uso precisa disso hoje e o domínio ganharia uma identidade que não usa.

## Consequências

- (+) O agregado Despacho foi incluído sem alterar o domínio de nenhum outro agregado (commits `cb5c9c5` a `3f4e4fd` só mexem na seção do Despacho em cada arquivo).
- (+) A invariante de carga está num método só e é testada sem banco: o `FakeDespachoRepository` tem 20 linhas e os testes de serviço não precisam de SQLite.
- (+) Cada despacho é pequeno: carregar e salvar envolve só os volumes daquele voo.
- (−) O `DespachoService` não confere se o voo existe. É possível abrir um despacho para um `voo_id` que não está cadastrado, ou para um voo já cancelado.
- (−) A `carga_maxima` é um número digitado, sem relação com a aeronave do voo. Nada impede um despacho de 50 toneladas num avião pequeno.
- (−) "Um despacho por voo" só é garantido no serviço. A coluna `voo_id` da tabela `despachos` não é única, então duas requisições simultâneas podem criar dois despachos para o mesmo voo.
- (−) Apagar e regravar todos os volumes a cada `salvar` é simples, mas gera mais escrita no banco à medida que o despacho cresce.

## Riscos e evolução

- Para fechar a brecha do voo inexistente, o `abrir_despacho` pode receber o `VooRepository` e recusar voos que não existem ou que não estão agendados, do mesmo jeito que o `VooService` consulta a Aeronave (ADR 0003).
- Se a Aeronave ganhar um campo de carga máxima em peso, a `carga_maxima` pode ser copiada dela na abertura do despacho, como o Voo copia a capacidade de assentos.
- Uma restrição `unique` em `despachos.voo_id` levaria a regra "um despacho por voo" também para o banco.
- O despacho não tem estado (aberto/fechado). Se for preciso impedir volumes depois do embarque, um ciclo de vida para o despacho é candidato a padrão State no checkpoint 3.

## Evidências

- `4fe1bdd` — PROPOSTA.md com o Despacho dentro do agregado Aeronave
- `3ba0d15` — README atualiza a divisão para 7 agregados, com o Despacho separado
- `cb5c9c5` — test: adiciona testes de id, voo_id, limite de carga e restaurar do despacho
- `18d4c48` — feat: adiciona id, voo_id, peso_disponivel e restaurar no despacho
- `42c1615` — feat: adiciona contrato DespachoRepository
- `60dd88d` — feat: adiciona mapeamento ORM do despacho e seus volumes
- `0fe7760` — feat: implementa SqlAlchemyDespachoRepository
- `3a1b43c` — feat: implementa DespachoService com abrir, adicionar volume e consultas
- `3f4e4fd` — feat: adiciona rotas flask de despacho
