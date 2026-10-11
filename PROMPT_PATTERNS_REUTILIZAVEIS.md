# 🎯 Padrões de Prompt Reutilizáveis para Testes de API

## 📋 Introdução

Este documento fornece padrões de prompt que funcionaram bem durante a geração de testes para a API de Gerenciamento de Tarefas. Podem ser adaptados para outras APIs e contextos.

---

## 🏗️ Padrão 1: Testes de Happy Path

### Quando Usar
- Testar fluxos bem-sucedidos
- Validar integração entre camadas
- Verificar comportamento esperado

### Template

```
Você é especialista em testes de integração para APIs REST.

CONTEXTO:
- Framework: [FastAPI/Django/Flask]
- ORM: [SQLAlchemy/Django ORM]
- Banco de dados: [SQLite/PostgreSQL]
- Tecnologia de teste: [Pytest/Jest/Mocha]

ESTRUTURA DA APLICAÇÃO:
[Copiar estrutura de pastas com descrição]
- app/routes/ → Endpoints da API
- app/services/ → Lógica de negócio
- app/models/ → Modelos ORM
- app/schemas/ → Validação Pydantic

ENDPOINTS A TESTAR:
1. POST /[resource]/ → Criar [resource]
   Input: [campos obrigatórios]
   Output: [campos esperados]
   
2. GET /[resource]/ → Listar [resource]
   Query: [parâmetros opcionais]
   Output: [array de resources]

[... listar todos os endpoints]

FLUXOS PARA TESTAR:
1. CREATE → READ → verificar BD
2. CREATE → UPDATE → READ → verificar BD
3. CREATE → DELETE → GET 404

PARA CADA FLUXO:
- Usar TestClient para chamar endpoint
- Verificar status code
- Verificar response tem todos campos
- Verificar dados foram salvos no BD
- Verificar filtros funcionam

FORMATO:
```python
class TestHappyPath:
    def test_[endpoint]_workflow(client, db):
        # Arrange: preparar dados
        
        # Act: chamar endpoint
        response = client.[METHOD]("/endpoint/", json={...})
        
        # Assert: verificar response
        assert response.status_code == 200
        
        # Assert: verificar BD
        db_item = db.query(Model).filter(...).first()
        assert db_item is not None
```

GERE N testes covering todos os happy paths listados.
```

### Exemplo de Resultado Esperado

```python
class TestHappyPath:
    def test_create_task_and_verify_in_database(self, client, db):
        """Criar tarefa via API e verificar no BD"""
        # Act
        response = client.post("/tasks/", json={"title": "Test Task"})
        
        # Assert response
        assert response.status_code == 200
        task_data = response.json()
        task_id = task_data["id"]
        
        # Assert database
        db_task = db.query(Task).filter(Task.id == task_id).first()
        assert db_task is not None
        assert db_task.title == "Test Task"
```

---

## 🏗️ Padrão 2: Testes de Validação de Entrada

### Quando Usar
- Testar rejeição de dados inválidos
- Validar constraints Pydantic
- Verificar mensagens de erro

### Template

```
Você é especialista em testes de validação de dados.

CONTEXTO:
- Framework: [FastAPI/Django]
- Validação: [Pydantic/Marshmallow]

ANÁLISE NECESSÁRIA:
1. Leia app/schemas/[schema].py
2. Identifique para cada campo:
   - Tipo de dado (str, int, bool, datetime)
   - Obrigatório? (required/optional)
   - Validações (min_length, max_length, regex, enum)
   - Default value

CAMPOS A TESTAR:
[Listar cada campo com suas validações]

Field: title
- Tipo: string
- Obrigatório: Sim
- Validações: (nenhuma mencionada, testar vazio/null)
- Default: Nenhum

Field: completed
- Tipo: boolean
- Obrigatório: Não
- Validações: Nenhuma
- Default: False

[... listar todos]

TESTES A GERAR:
Para CADA CAMPO, teste:
1. Valor válido → 200 + aceito
2. Tipo incorreto (string para int) → 422 + erro
3. Null (se obrigatório) → 422 + erro
4. Vazio/default (se optional) → 200 + usar default
5. Extremo (muito longo, números grandes) → [aceitar ou 422]

FORMATO:
```python
class TestValidacao:
    def test_[field]_[case](client):
        """Valida [behavior] para campo [field]"""
        response = client.post("/endpoint/", json={
            "required_field": "value",
            "[field]": [test_value]
        })
        assert response.status_code == [expected_code]
        if expected_code == 422:
            assert "[field]" in str(response.json()["detail"])
```

GERE testes para TODOS os campos + TODOS os casos.
```

### Exemplo de Resultado Esperado

```python
class TestValidacao:
    def test_title_null_rejected(self, client):
        """Rejeita title nulo"""
        response = client.post("/tasks/", json={"title": None})
        assert response.status_code == 422
        assert "title" in str(response.json()["detail"])
    
    def test_title_empty_string(self, client):
        """Comportamento com title vazio"""
        response = client.post("/tasks/", json={"title": ""})
        # FastAPI aceita string vazia por padrão
        if response.status_code == 200:
            assert response.json()["title"] == ""
```

---

## 🏗️ Padrão 3: Testes de Edge Cases

### Quando Usar
- Testar limites e extremos
- Verificar race conditions
- Testar com dados muito grandes

### Template

```
Você é especialista em edge cases.

DEFINIR EDGE CASES:
Para cada recurso/campo, identifique extremos:

TIPO: String
- Casos: vazio "", muito longo (10k chars), unicode, emoji, null

TIPO: Inteiro
- Casos: 0, -1, 999999999, muito grande, string

TIPO: Boolean
- Casos: null, string "true"/"false", número 0/1

TIPO: Array
- Casos: vazio [], muito grande (1000 items), estrutura inválida

ID de Recurso
- Casos: negativo, zero, muito grande, string, float, inexistente

OPERAÇÕES SEQUENCIAIS
- Criar → Deletar → Acessar (404?)
- Criar → Update → Delete → Verificar não existe
- Complete → Uncomplete → Complete (toggle múltiplas)

FORMATO:
```python
class TestEdgeCases:
    def test_[case_name](client):
        """[Descrição do edge case]"""
        response = client.[METHOD]("/endpoint/", json={...})
        # Verificar aceita/rejeita gracefully
        assert response.status_code in [200, 400, 404, 422]
```

GERE testes para TODAS os edge cases identificados.
```

### Exemplo de Resultado Esperado

```python
class TestEdgeCases:
    def test_get_task_with_negative_id(self, client):
        """GET com ID negativo retorna 404"""
        response = client.get("/tasks/-1")
        assert response.status_code == 404
    
    def test_create_task_with_extremely_long_title(self, client):
        """Criar com title muito longo (10k chars)"""
        long_title = "A" * 10000
        response = client.post("/tasks/", json={"title": long_title})
        # Aceita ou rejeita, mas não quebra
        assert response.status_code in [200, 422]
```

---

## 🏗️ Padrão 4: Testes de Performance

### Quando Usar
- Verificar performance com muitos dados
- Testar filtros com resultado grande
- Validar sem timeout

### Template

```
Você é especialista em testes de performance.

CENÁRIOS DE PERFORMANCE:
1. Criar muitos recursos (100, 1000)
   - Cada um deve ser criável sem timeout
   - Listagem deve retornar todos rápido

2. Filtros com muitos resultados
   - Filtrar 50+ items deve ser rápido
   - Sem n+1 queries

3. Update em lote
   - Update 10 items sequencialmente
   - Cada um deve suceder

FORMATO:
```python
class TestPerformance:
    def test_create_many_resources(client):
        """Criar N recursos"""
        count = 100
        for i in range(count):
            response = client.post("/endpoint/", json={...})
            assert response.status_code == 200
        
        # Listar todos
        response = client.get("/endpoint/")
        assert len(response.json()) >= count
```

GERE testes para TODOS os cenários listados.
Não testar tempo exato, apenas que executa sem erro.
```

---

## 🏗️ Padrão 5: Testes de Integração Complexa

### Quando Usar
- Testar fluxos com múltiplos passos
- Verificar consistência entre operações
- Validar comportamentos especiais

### Template

```
Você é especialista em testes de integração complexa.

FLUXOS COMPLEXOS A TESTAR:
1. [Fluxo 1]: Describe o que testa
   Passos:
   - Passo 1
   - Passo 2
   - Passo 3
   Verificações:
   - Verificar resultado após passo 1
   - Verificar resultado após passo 2
   - Verificar resultado final
   - Verificar BD está consistente

2. [Fluxo 2]: ...

COMPORTAMENTOS ESPECIAIS:
- [Behavior 1]: Descrever
- [Behavior 2]: Descrever

FORMATO:
```python
class TestIntegracaoComplexa:
    def test_[fluxo_name]_workflow(client, db):
        """[Descrição do fluxo complexo]"""
        
        # Step 1
        res1 = client.post(...)
        assert res1.status_code == 200
        item_id = res1.json()["id"]
        
        # Step 2
        res2 = client.put(f"/{item_id}", json={...})
        assert res2.status_code == 200
        
        # Verificar consistência
        db_item = db.query(Model).filter(...).first()
        assert db_item.field == expected_value
```

GERE testes para TODOS os fluxos + comportamentos.
```

---

## 🔄 Padrão 6: Iteração Incremental

### Quando Usar
- Expandir cobertura existente
- Refinar testes baseado em feedback
- Adicionar novas categorias

### Processo

```
Iteração 1: Base
- Testes happy path (CRUD básico)
- Status: ✅ Pronto

Iteração 2: Validação
- Testes validação de entrada
- Testes rejeição de dados inválidos
- Status: ✅ Pronto

Iteração 3: Edge Cases
- Testes com dados extremos
- Testes IDs inválidos
- Status: ✅ Pronto

Iteração 4: Integração
- Testes fluxos múltiplos passos
- Testes consistência
- Status: ✅ Pronto

Iteração 5: Performance
- Testes com muitos dados
- Testes velocidade de filtros
- Status: ✅ Pronto

Total: 5 arquivos = ~70 testes bem organizados
```

### Template

```
Você é especialista em testes incrementais.

ITERAÇÕES PLANEJADAS:
[Listar cada iteração]

ITERAÇÃO ATUAL: [número]
OBJETIVOS: [listar]
DEPENDÊNCIAS: [listar]

GERE [número] testes para esta iteração.
Cada teste deve:
1. Ser independente
2. Usar fixtures do conftest.py
3. Ter docstring clara
4. Ser organizado em classe apropriada

Depois gere resumo de cobertura:
Iteração X: Y testes
- Z testes de [categoria 1]
- Z testes de [categoria 2]
Total: N testes nesta iteração
Cobertura cumulativa: M testes
```

---

## 🎓 Padrão 7: Análise de Gaps de Cobertura

### Quando Usar
- Identificar o que falta testar
- Priorizar próximos testes
- Validar cobertura

### Template

```
Você é especialista em cobertura de testes.

ANÁLISE NECESSÁRIA:
1. Listar todos os endpoints da API
2. Para cada endpoint, listar:
   - Método HTTP (GET, POST, etc)
   - Caminho
   - Parâmetros
   - Response esperada (200, 404, etc)

ENDPOINTS:
- [Endpoint 1]
- [Endpoint 2]
...

TESTES EXISTENTES:
[Listar testes que já existem]

GAPS IDENTIFICADOS:
Para cada endpoint, verificar:
- Há teste de happy path? Sim/Não
- Há teste de validação? Sim/Não
- Há teste de edge case? Sim/Não
- Há teste de erro? Sim/Não

GENERATE:
Uma matriz de cobertura mostrando:
- Endpoint | Happy Path | Validação | Edge Case | Erro
- [endpoint 1] | ✅ | ❌ | ✅ | ❌
- [endpoint 2] | ✅ | ✅ | ✅ | ✅

Depois gere testes para os GAPS identificados (❌).
```

---

## 💡 Padrões Compostos

### Padrão: Teste Completo (Validação + Integração)

```
def test_[endpoint]_complete_workflow(client, db):
    """Testa happy path + validação + integração"""
    
    # Happy path
    response = client.post("/endpoint/", json={
        "field1": "valid_value",
        "field2": "valid_value"
    })
    assert response.status_code == 200
    
    # Verificar BD
    db_item = db.query(Model).filter(...).first()
    assert db_item is not None
    
    # Validação de entrada
    response = client.post("/endpoint/", json={
        "field1": None  # Invalid
    })
    assert response.status_code == 422
```

### Padrão: Teste com Setup e Teardown

```
@pytest.fixture
def setup_tasks(client):
    """Criar tarefas para teste"""
    tasks = []
    for i in range(3):
        res = client.post("/tasks/", json={"title": f"Task {i}"})
        tasks.append(res.json()["id"])
    yield tasks
    # Cleanup: deletar tarefas
    for task_id in tasks:
        client.delete(f"/tasks/{task_id}")

def test_[algo](client, setup_tasks):
    """Usar setup_tasks"""
    ...
```

---

## 🚀 Como Usar Estes Padrões

### Passo 1: Escolher Padrão
Qual tipo de teste você precisa?
- Happy path? → Padrão 1
- Validação? → Padrão 2
- Edge cases? → Padrão 3
- Performance? → Padrão 4
- Complexo? → Padrão 5

### Passo 2: Adaptar Contexto
- Substituir [nome do framework] pelo seu
- Substituir [estrutura] pela sua
- Substituir [endpoints] pelos seus

### Passo 3: Copiar para Prompt
- Copiar template adaptado
- Adicionar informações específicas
- Pedir para gerar testes

### Passo 4: Verificar Resultado
- Testes cobrem casos esperados?
- Código segue seu estilo?
- Testes estão bem organizados?

---

## ✅ Checklist de Padrão Completo

- ✅ Contexto claro (tecnologias, estrutura)
- ✅ Análise necessária (quais arquivos ler)
- ✅ Casos definidos (listar cada caso)
- ✅ Formato especificado (template de código)
- ✅ Exemplo concreto (mostra esperado)
- ✅ Critérios de sucesso (como validar)

---

## 📊 Resumo de Padrões

| Padrão | Quando Usar | Casos | Tempo |
|--------|-----------|-------|-------|
| 1: Happy Path | Validar fluxo normal | 5-10 | 30min |
| 2: Validação | Testar input | 20-40 | 1h |
| 3: Edge Cases | Extremos | 15-30 | 1h |
| 4: Performance | Muitos dados | 3-5 | 30min |
| 5: Integração | Fluxos complexos | 5-10 | 1h |
| 6: Incremental | Expandir | N/A | N/A |
| 7: Gaps | Análise | 1 | 30min |

---

## 🎯 Conclusão

Estes padrões funcionaram bem para a API de Gerenciamento de Tarefas e podem ser reutilizados em:
- Outras APIs FastAPI
- APIs em outros frameworks
- Projetos com estruturas similares
- Equipes que querem padronizar testes

**Adapt, use, melhore, compartilhe!**

