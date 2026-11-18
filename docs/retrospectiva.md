# Retrospectiva da Arquitetura

Depois de conviver com esta arquitetura ao longo de duas fases completas — modelando sete agregados, implementando persistência relacional, refatorando violações de SOLID e introduzindo cinco padrões de projeto GoF distintos —, esta retrospectiva responde à pergunta central da disciplina: **nós escolheríamos essa arquitetura de novo?**

---

## 1. As previsões do checkpoint 1

No Checkpoint 1, documentamos no `docs/arquitetura.md` os três atributos de qualidade priorizados (Corretude, Modificabilidade e Testabilidade) e seus trade-offs associados. A vivência prática da Fase 2 permitiu confrontar essas previsões teóricas com a realidade do código.

### Os cenários de qualidade

- **Corretude das regras de negócio:** **Confirmada no nível de cada agregado, mas com limites na coordenação entre eles.** A decisão de encapsular rigorosamente as invariantes no domínio puro comprovou seu valor: o padrão GoF State na `Escala` impediu alocação em escalas confirmadas ou realizadas, o Composite no `Despacho` isolou o cálculo de tara e capacidade, e o Strategy na `Aeronave` desacoplou regras de vistoria, sem depender de banco de dados ou requisições HTTP. Por outro lado, a corretude entre agregados diferentes depende da coordenação na camada de serviços ou de observadores: embora o cancelamento de um voo dispare o cancelamento das reservas existentes via Observer, a API ainda aceita criar uma reserva nova apontando para um voo previamente cancelado, pois o caso de uso de criação de reserva não valida o status do voo antes de persistir.
- **Modificabilidade:** **Confirmada com ressalvas de atrito.** A modificabilidade comportou-se exatamente como previsto: a adição de novos comportamentos foi isolada nas camadas certas. Por exemplo, a refatoração de Responsabilidade Única (SRP) no `Tripulante` (extraindo a classe `ControleJornada`) e a transição de status do `Voo` ocorreram sem tocar em nenhuma linha da camada de entrada (`flask_app.py`). Por outro lado, o custo de modificar operações que atravessam o sistema revelou-se alto: quando um novo campo ou relacionamento precisa ser persistido, o desenvolvedor é obrigado a alterar o modelo de domínio, o contrato abstrato, a implementação concreta do SQLAlchemy, o modelo ORM e os repositórios Fake de teste.
- **Testabilidade:** **Amplamente confirmada.** A suíte de testes unitários (`tests/unit/`) possui 134 testes e roda localmente em apenas **0.27 segundos**, atendendo com folga à medida de resposta do cenário do Checkpoint 1 (tempo estritamente abaixo de 1 segundo). A ausência de I/O no domínio e o uso de repositórios Fake na camada de serviço foram determinantes para essa agilidade. No total geral, a suíte saltou de 130 para **203 testes** (somando testes unitários, testes de integração de contrato e testes ponta a ponta na API), permitindo aplicar refatorações agressivas e padrões GoF com total segurança e feedback imediato.

### Os trade-offs

- **Testabilidade × Simplicidade:** Este foi o trade-off que mais pesou no dia a dia. Para manter o domínio livre de SQL, foi necessário sustentar uma "dupla representação" de cada entidade: as classes de negócio em `domain/model.py` e as classes relacionais em `adapters/orm.py`, interligadas manualmente pelos métodos `from_domain()` e `to_domain()`. O volume de código dos adaptadores (`orm.py` e `repository.py`) ultrapassou 500 linhas de código puramente mecânico de infraestrutura e sincronização.
- **Repositórios Falsos × Realidade do Banco (O risco que virou evidência):** O risco apontado no Checkpoint 1 sobre a divergência entre fakes e o SQLAlchemy concretizou-se na prática. O repositório falso da `Aeronave` permitia atualizações que falhavam com `IntegrityError` no banco real. A equipe precisou investir esforço adicional criando testes de contrato (`tests/integration/adapter/test_contrato_aeronave_repository.py`, commit `e98040c`) para garantir que o fake e o repositório real se comportassem de forma idêntica. Antes do teste de contrato, o cenário de salvar uma aeronave já existente passava no fake e falhava no SQLAlchemy. A correção (`0353d3e`) mudou só `orm.py` e `repository.py`, sem tocar no domínio nem no serviço, o que mostra a camada de adaptadores absorvendo o problema que ela mesma criou.

---

## 2. O que a Fase 2 mostrou sobre as camadas

A convivência prática durante as refatorações SOLID (Checkpoint 2) e a implementação dos padrões GoF (Checkpoint 3) trouxe lições claras sobre o impacto da arquitetura em camadas e Ports & Adapters:

### Onde as camadas ajudaram:
1. **Isolamento de padrões de domínio:** A aplicação de padrões como **State** (no ciclo de vida da `Escala`), **Strategy** (na verificação de disponibilidade da `Aeronave`) e **Composite** (na hierarquia de volumes e contêineres de carga do `Despacho`) foi extremamente natural. Como o domínio é orientado a objetos puro (POPO - Plain Old Python Objects), pudemos desenhar hierarquias polimórficas limpas com herança e composição, sem nos preocuparmos com restrições de tabelas ou limitações do ORM. O Strategy da `Aeronave` é a medida mais direta disso: o commit `4606a68` mudou um único arquivo (`domain/model.py`, 27 linhas acrescentadas e 9 removidas), sem alterar o serviço, o ORM ou a API, e os 8 casos do teste de caracterização escrito antes (`9a9f6c5`) passaram sem nenhuma mudança.
2. **Rede de segurança refatoração/testes:** Quando refatoramos classes existentes para respeitar o SRP (extração de `ControleJornada`) e Aberto/Fechado (tabela de transições no `Voo`), os testes unitários garantiram em frações de segundo que nenhuma regressão de negócio foi introduzida antes mesmo de realizarmos o commit.

### Onde as camadas atrapalharam ou geraram atrito:
1. **Persistência de padrões estruturais e comportamentais:** Persistir o padrão State ou Composite revelou o atrito clássico do impedimento objeto-relacional (Object-Relational Impedance Mismatch). O banco SQLite precisava armazenar strings simples (`"ABERTA"`, `"CONFIRMADA"`), enquanto a entidade em memória manipulava objetos de estado polimórficos (`EstadoEscalaAberta`). Mapear essa transição nos conversores do ORM exigiu código extra e cuidados manuais de reconstrução através de métodos como `Escala.restaurar(...)`. Na `Aeronave`, o atrito apareceu de outra forma: as regras de disponibilidade não são gravadas no banco, e o `AeronaveModel.to_domain` sempre reconstrói a aeronave com as regras padrão. Hoje isso não muda o resultado, porque todas as aeronaves usam as mesmas regras, mas regras diferentes por aeronave exigiriam uma tabela nova e mais código de conversão.
2. **Orquestração sem transações distribuídas:** Como a regra de limites de agregados em DDD estabelece que um agregado só referencia outro por identificador primitivo (UUID/prefixo), operações compostas — como o cancelamento de um voo que dispara o cancelamento das reservas via Observer, ou a escala de um tripulante que debita horas — dependem exclusivamente da orquestração na camada de serviço (`services.py`). Sem um padrão como Unit of Work transacional unificado, garantir a atomicidade total entre múltiplos repositórios em caso de falha no meio do processo exigiu atenção redobrada.

---

## 3. Decisão final

**Depois de conviver com essa arquitetura, nós a escolheríamos de novo?**

A resposta do grupo é: **Sim, mas com uma abordagem híbrida e mais pragmática.**

Para um sistema de pequeno porte ou no início de desenvolvimento (MVP), a arquitetura adotada introduz uma burocracia desproporcional. A necessidade de criar interfaces abstratas, repositórios fakes em dicionário, modelos ORM duplicados e conversores manuais consome tempo que, em um cenário de mercado real, postergaria a entrega de valor. Se o objetivo fosse puramente velocidade inicial, um framework full-stack com Active Record (como Django) ou rotas diretas no Flask com SQLAlchemy acoplado permitiria entregar os mesmos casos de uso na metade do tempo.

Contudo, para o domínio de **operações de companhia aérea**, que envolve regras regulatórias estritas (limites de horas de voo da ANAC, controle de vistoria de aeronaves, homologação de tripulação e despacho de carga), o isolamento do domínio mostrou-se insubstituível. Em um framework Active Record como Django, os modelos rapidamente se tornariam "classes monstro" (fat models), repletas de chamadas a `.save()`, queries de banco e regras de negócio misturadas, tornando a aplicação de padrões como State ou Strategy artificial e os testes unitários lentos e dependentes de banco.

### O que faríamos diferente:
Se fôssemos reiniciar o projeto hoje com o conhecimento adquirido na Fase 2, escolheríamos uma **solução híbrida moderna**:
1. **SQLAlchemy 2.0 com Mapeamento Declarativo Integrado:** Em vez de manter `model.py` e `orm.py` como arquivos e classes completamente separados que exigem métodos de conversão manual, utilizaríamos o recurso moderno de *Mapped As Dataclass* do SQLAlchemy. Isso permite que a entidade de domínio continue sendo uma dataclass pura para efeitos de regras e testes, enquanto os metadados de coluna são anexados sem poluir a lógica de negócio, eliminando mais de 200 linhas de boilerplate de conversão.
2. **Repositórios com SQLite em memória em vez de Fakes manuais:** Como o SQLite roda em memória em milissegundos, poderíamos ter evitado a manutenção manual de repositórios fake baseados em dicionários (e os riscos de divergência de comportamento comprovados no projeto), rodando os testes rápidos de integração diretamente com um banco leve em memória.
3. **Manutenção da Service Layer e do Domínio Puro:** Manteríamos sem qualquer dúvida a camada de serviços (`service_layer/`) desacoplada do Flask e o domínio com proteção rigorosa de invariantes, pois foi essa separação que permitiu ao sistema incorporar com facilidade regras de negócio e padrões de projeto sem desestruturar a aplicação.
