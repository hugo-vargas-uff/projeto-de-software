# Arquitetura do Sistema de Operações de Companhia Aérea

## 1. Escopo

## 2. Requisitos arquiteturais

## 3. Arquitetura atual

O sistema aéreo adota uma arquitetura organizada em camadas, combinando conceitos de *Ports & Adapters*
(Arquitetura Hexagonal) com os padrões Repository e Service Layer.
Essa organização busca separar as regras de negócio dos detalhes de infraestrutura,
como persistência de dados e comunicação HTTP.

### Camadas e componentes

**1. Camada de entrada — Entrypoints**

Localizada em `src/airline/entrypoints/`, contém o arquivo `flask_app.py`, responsável por expor os endpoints HTTP da
aplicação. Essa camada recebe as requisições, instancia os serviços e seus repositórios, converte os resultados em
respostas JSON e traduz exceções em códigos HTTP.

**2. Camada de serviços — Service Layer**

Localizada em `src/airline/service_layer/`, contém `services.py`, que coordena os casos de uso da aplicação.
Serviços como `ReservaService`, `PassageiroService` e `VooService` organizam as operações, consultam repositórios e
acionam as regras de negócio do domínio. Essa camada evita concentrar toda a lógica de aplicação nos endpoints.

**3. Camada de domínio — Domain**

Localizada em `src/airline/domain/`, contém `model.py`, `repositories.py` e os módulos de exceções de domínio.
O arquivo `model.py` reúne as entidades, os objetos de valor, os estados e as regras de negócio. Já `repositories.py`
define os contratos que os repositórios devem implementar.

O domínio não precisa conhecer o Flask nem os detalhes de persistência do SQLAlchemy. 
Dessa forma, suas regras podem ser testadas independentemente da infraestrutura.

**4. Camada de adaptadores — Adapters**

Localizada em `src/airline/adapters/`, contém `repository.py` e `orm.py`. O primeiro implementa os contratos de
repositório utilizando SQLAlchemy; o segundo define os modelos ORM utilizados para persistir os dados.
Os repositórios fazem a conversão entre os objetos de domínio e os modelos de persistência.

### Padrões arquiteturais adotados

- **Arquitetura em camadas:** separa entrada HTTP, coordenação dos casos de uso, regras de negócio e infraestrutura.
- **Ports & Adapters:** os contratos de repositório representam portas de acesso à persistência, enquanto os repositórios SQLAlchemy funcionam como adaptadores concretos.
- **Repository:** encapsula as operações de consulta e gravação, evitando que os serviços precisem manipular diretamente as consultas SQLAlchemy.
- **Service Layer:** centraliza a coordenação dos casos de uso, incluindo verificações de existência e a interação entre diferentes repositórios.

### Direção das dependências

- Os serviços dependem do domínio e dos contratos de repositório.
- Os adaptadores de persistência dependem dos modelos de domínio e implementam esses contratos.
- A camada de entrada utiliza os serviços e instancia os adaptadores concretos para conectar os componentes.

### Diagrama de componentes

```mermaid
flowchart TB
    API["flask_app.py"]
    S["services.py"]
    D["domain/model.py"]
    R["domain/repositories.py"]
    A["adapters/repository.py"]
    ORM["adapters/orm.py"]
    DB[("Banco de dados")]

    API --> S
    S --> D
    S --> R
    A -.-> R
    A --> ORM
    ORM --> DB
```

### Mapeamento para as pastas de `src/`

| Componente | Localização | Responsabilidade |
| :--- | :--- | :--- |
| **Entrypoints** | `src/airline/entrypoints/` | Endpoints HTTP e respostas da API |
| **Service Layer** | `src/airline/service_layer/` | Coordenação dos casos de uso |
| **Modelos de domínio** | `src/airline/domain/model.py` | Entidades e regras de negócio |
| **Contratos de repositório** | `src/airline/domain/repositories.py` | Interfaces de persistência |
| **Exceções de domínio** | `src/airline/domain/exception.py` | Erros relacionados às regras e operações do domínio |
| **Adaptadores de repositório** | `src/airline/adapters/repository.py` | Consultas e gravações via SQLAlchemy |
| **Modelos ORM** | `src/airline/adapters/orm.py` | Mapeamento entre objetos Python e tabelas |

## 4. Análise de trade-offs

## 5. Alternativa

## 6. Evidências
