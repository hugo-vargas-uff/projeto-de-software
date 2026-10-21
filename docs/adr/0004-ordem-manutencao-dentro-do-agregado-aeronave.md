# 0004 — A OrdemManutencao faz parte do agregado Aeronave

- **Status:** aceito (Fase 1), registrado no checkpoint 1 da Fase 2
- **Autor:** Matheus Andrade (@MatheusFSD)
- **Data do registro:** 21/10/2026

## Contexto

A regra principal do agregado Aeronave é que uma aeronave com vistoria vencida ou com manutenção pendente fica indisponível para voos. O `VooService` depende dessa resposta para agendar um voo, chamando `esta_disponivel(hoje)`.

Para essa regra valer, alguém precisa garantir que a disponibilidade sempre reflita o estado real das ordens de manutenção. Se as ordens puderem ser criadas ou concluídas sem passar pela aeronave, uma aeronave com manutenção pendente pode continuar aparecendo como disponível.

## Decisão

A `OrdemManutencao` é uma entidade interna do agregado Aeronave, e a `Aeronave` é a raiz.

- A aeronave guarda a lista `ordens_manutencao`, e as ordens só são abertas e concluídas pelos métodos da raiz: `abrir_ordem_manutencao` e `concluir_ordem_manutencao`.
- A disponibilidade não é guardada: `esta_disponivel(hoje)` é calculada na hora, olhando a validade da vistoria e se existe alguma ordem pendente.
- A data de referência (`hoje`) é recebida como parâmetro, em vez de usar `date.today()` dentro da classe, para que os testes sejam determinísticos.
- No banco, são duas tabelas (`aeronaves` e `ordens_manutencao`), ligadas por chave estrangeira e por um `relationship` com `cascade="all, delete-orphan"`. Não existe repositório próprio para a ordem: ela é salva e carregada junto com a aeronave pelo `SqlAlchemyAeronaveRepository`.
- Ao carregar do banco, o `buscar` reconstrói as ordens usando os próprios métodos da aeronave, em vez de preencher a lista por fora.

## Alternativas consideradas

- **OrdemManutencao como agregado separado, referenciando a aeronave pelo prefixo.** Foi a primeira versão que escrevi, antes do commit. A ordem teria vida própria e poderia ter seu próprio repositório, mas a `Aeronave` não teria como enxergar as ordens pendentes, e qualquer parte do código poderia concluir uma ordem sem passar por ela. A invariante deixaria de ser protegida pela raiz.
- **Guardar `disponivel` como atributo da aeronave.** Foi a solução da primeira versão (commit `4c752e8`). Era simples, mas qualquer código podia fazer `aeronave.disponivel = True` e liberar uma aeronave com manutenção pendente. Troquei por um cálculo quando a ordem de manutenção passou a existir.
- **Guardar as ordens numa coluna da tabela de aeronaves.** Evitaria a segunda tabela, mas uma aeronave tem várias ordens, e cada ordem tem descrição e status próprios. Seria preciso serializar a lista, perdendo a possibilidade de consultar as ordens pelo banco.

## Consequências

- (+) A invariante fica num lugar só. Ninguém consegue deixar a aeronave disponível com manutenção pendente, porque a disponibilidade é sempre calculada a partir das ordens.
- (+) O `cascade` faz o banco seguir a mesma regra do domínio: apagar a aeronave apaga as ordens, e uma ordem não existe sem a aeronave.
- (+) O `VooService` só precisa perguntar `esta_disponivel` à aeronave. Ele não conhece as ordens nem as regras de vistoria.
- (−) A `OrdemManutencao` não tem identidade própria no domínio. O `id` existe só no banco. Por isso, o `AeronaveService` localiza a ordem a concluir pela descrição, o que falha se houver duas ordens com o mesmo texto.
- (−) O `salvar` do repositório sempre insere. Salvar de novo uma aeronave que já existe, depois de abrir ou concluir uma ordem, gera conflito de chave primária. Por isso as rotas de abrir e concluir ordem não foram expostas na API.
- (−) Toda leitura da aeronave carrega também todas as ordens dela, inclusive as antigas e concluídas.

## Riscos e evolução

- Para expor as rotas de manutenção na API, a ordem precisa de um identificador no domínio, e o `salvar` precisa atualizar a aeronave em vez de sempre inserir (por exemplo, com `session.merge`).
- Se uma aeronave acumular muitas ordens ao longo dos anos, carregar todas a cada consulta de disponibilidade pode ficar lento. Uma saída seria consultar só as ordens pendentes.
- Os voos já agendados não são avisados quando a aeronave entra em manutenção depois do agendamento. Esse risco também aparece no ADR 0003.

## Evidências

- `3567978` — feat: adiciona regra de vistoria vencida na Aeronave
- `fbde803` — feat: Adiciona OrdemManutencao e bloqueio por manutenção
- `08a13bd` — feat: adiciona mapeamento ORM da Aeronave e OrdemManutencao
- `05ca3a9` — feat: adiciona SqlAlchemyAeronaveRepository
- `f9bc17b` — test: add teste de integracao do SqlAlchemyAeronaveRepository
