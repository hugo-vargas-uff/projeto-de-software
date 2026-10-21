# ADR-002 — Identidade e cadastro de Passageiro

## Contexto

Era necessário definir como identificar passageiros e impedir cadastros duplicados com o mesmo CPF, mantendo a
identidade da entidade independente de seus dados pessoais.

## Decisão

A entidade `Passageiro` terá um UUID como identificador interno e o CPF como atributo único.
O `PassageiroService` consulta o repositório para verificar se o CPF já está cadastrado
e lança `CpfJaCadastradoException` em caso de duplicidade. A restrição de unicidade também é definida no banco de dados.

## Alternativa considerada

Utilizar o CPF como identificador principal do passageiro, eliminando a necessidade de um UUID.
Essa opção simplificaria a identificação pelo CPF, mas vincularia a identidade técnica da entidade a um dado pessoal
e exigiria seu uso como identificador nas relações com outras entidades.

## Consequências

O UUID separa a identidade interna do passageiro do CPF, enquanto a validação no serviço fornece uma mensagem de
erro específica para cadastros duplicados. A restrição no banco reforça a unicidade, inclusive em situações de
concorrência. Em contrapartida, o sistema precisa manter o UUID e o CPF como informações distintas.