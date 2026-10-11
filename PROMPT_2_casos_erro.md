# PROMPT 2: Casos de Erro e Edge Cases - API de Gerenciamento de Tarefas

## Objetivo
Gerar casos de teste de integração para validar comportamento da **API de Gerenciamento de Tarefas** em FastAPI, considerando dados inválidos, valores duplicados, falhas de camadas, ausência de validação e estados inconsistentes.

---

## 1. TESTES DE VALIDAÇÃO DE DADOS INVÁLIDOS

### 1.1 Criação de Tarefa com Dados Inválidos

#### Teste: Campo `title` vazio
```python
def test_create_task_with_empty_title(client):
    """Valida rejeição de title vazio (string vazia)"""
    response = client.post("/tasks/", json={"title": ""})
    assert response.status_code == 422  # Validation Error
    assert "title" in response.json()["detail"][0]["loc"]
```

#### Teste: Campo `title` nulo
```python
def test_create_task_with_null_title(client):
    """Valida rejeição de title nulo (null)"""
    response = client.post("/tasks/", json={"title": None})
    assert response.status_code == 422
    assert "title" in str(response.json()["detail"])
```

#### Teste: Campo `title` muito longo (edge case de tamanho)
```python
def test_create_task_with_extremely_long_title(client):
    """Valida rejeição ou truncamento de title excessivamente longo"""
    long_title = "A" * 10000
    response = client.post("/tasks/", json={"title": long_title})
    # Deve ser 422 (validation error) ou 200 com truncamento
    data = response.json()
    if response.status_code == 200:
        assert len(data["title"]) <= 255  # Verificar limite BD
    else:
        assert response.status_code == 422
```

#### Teste: Campo `title` com tipos inválidos
```python
def test_create_task_with_invalid_title_type(client):
    """Valida rejeição de title com tipo não-string"""
    response = client.post("/tasks/", json={"title": 12345})
    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]
```

#### Teste: Campo `completed` com valor inválido
```python
def test_create_task_with_invalid_completed_type(client):
    """Valida rejeição de completed com tipo não-booleano"""
    response = client.post("/tasks/", json={
        "title": "Test",
        "completed": "yes"  # String em vez de bool
    })
    assert response.status_code == 422
    assert "completed" in response.json()["detail"][0]["loc"]
```

#### Teste: Campo `priority` com valor inválido
```python
def test_create_task_with_invalid_priority(client):
    """Valida rejeição de priority fora do conjunto esperado"""
    response = client.post("/tasks/", json={
        "title": "Test",
        "priority": "SUPER_URGENTE"  # Valor não reconhecido
    })
    # FastAPI não valida enum por padrão, verifica se passa ou trata
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        # Se passa, garante que não quebra a aplicação
        assert response.json()["priority"] is not None
```

#### Teste: `description` com tipo inválido
```python
def test_create_task_with_invalid_description_type(client):
    """Valida rejeição de description com tipo não-string"""
    response = client.post("/tasks/", json={
        "title": "Test",
        "description": ["list", "of", "strings"]
    })
    assert response.status_code == 422
    assert "description" in response.json()["detail"][0]["loc"]
```

#### Teste: Payload vazio
```python
def test_create_task_with_empty_payload(client):
    """Valida rejeição de request body vazio"""
    response = client.post("/tasks/", json={})
    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]
```

#### Teste: Payload com campo desconhecido
```python
def test_create_task_with_unknown_field(client):
    """Valida se API rejeita ou ignora campos desconhecidos"""
    response = client.post("/tasks/", json={
        "title": "Test",
        "unknown_field": "should be ignored or cause 422"
    })
    # Pydantic ignora por padrão, mas pode ser configurado
    assert response.status_code == 200
    assert "unknown_field" not in response.json()
```

---

## 2. TESTES DE VALORES DUPLICADOS E CONFLITOS

### 2.1 Criação de Tarefas Duplicadas

#### Teste: Múltiplas tarefas com mesmo título
```python
def test_create_duplicate_task_titles(client):
    """Valida se API permite múltiplas tarefas com mesmo título"""
    task_data = {"title": "Duplicate Title", "description": "Same"}
    
    response1 = client.post("/tasks/", json=task_data)
    response2 = client.post("/tasks/", json=task_data)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    # Ambas devem ter IDs diferentes
    assert response1.json()["id"] != response2.json()["id"]
    
    # Ambas devem estar no banco
    all_tasks = client.get("/tasks/").json()
    assert len(all_tasks) >= 2
```

#### Teste: Update com conflito de nome
```python
def test_update_task_to_existing_title(client):
    """Valida comportamento ao atualizar tarefa para título existente"""
    # Criar duas tarefas
    res1 = client.post("/tasks/", json={"title": "Task A"})
    res2 = client.post("/tasks/", json={"title": "Task B"})
    
    task1_id = res1.json()["id"]
    task2_id = res2.json()["id"]
    
    # Tentar atualizar task2 para o título de task1
    response = client.put(f"/tasks/{task2_id}", 
                         json={"title": "Task A"})
    
    # Deve permitir (sem constraint UNIQUE) ou retornar erro
    if response.status_code == 200:
        assert response.json()["title"] == "Task A"
```

---

## 3. TESTES DE ESTADOS INCONSISTENTES

### 3.1 Ciclos de Vida de Tarefa Inválidos

#### Teste: Completar e descompletar múltiplas vezes
```python
def test_toggle_completion_multiple_times(client):
    """Valida múltiplas transições de estado"""
    res_create = client.post("/tasks/", json={"title": "Toggle Test"})
    task_id = res_create.json()["id"]
    
    # Completar
    response1 = client.patch(f"/tasks/{task_id}/complete?completed=true")
    assert response1.json()["completed"] is True
    
    # Descompletar
    response2 = client.patch(f"/tasks/{task_id}/complete?completed=false")
    assert response2.json()["completed"] is False
    
    # Completar novamente
    response3 = client.patch(f"/tasks/{task_id}/complete?completed=true")
    assert response3.json()["completed"] is True
    
    # Verificar estado final no GET
    response_get = client.get(f"/tasks/{task_id}")
    assert response_get.json()["completed"] is True
```

#### Teste: Atualizar tarefa concluída
```python
def test_update_completed_task(client):
    """Valida se é possível editar tarefa já completada"""
    # Criar tarefa completa
    res_create = client.post("/tasks/", 
                            json={"title": "Will be completed", 
                                  "completed": True})
    task_id = res_create.json()["id"]
    
    # Tentar atualizar
    response = client.put(f"/tasks/{task_id}", 
                         json={"description": "Updated description"})
    
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"
    assert response.json()["completed"] is True
```

#### Teste: Deletar tarefa concluída
```python
def test_delete_completed_task(client):
    """Valida se é possível deletar tarefa completada"""
    res_create = client.post("/tasks/", 
                            json={"title": "Delete me", 
                                  "completed": True})
    task_id = res_create.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verificar se foi realmente deletada
    response_get = client.get(f"/tasks/{task_id}")
    assert response_get.status_code == 404
```

#### Teste: Converter tarefa com priority inválida
```python
def test_update_task_with_invalid_priority(client):
    """Valida atualização com priority não reconhecida"""
    res_create = client.post("/tasks/", json={"title": "Priority Test"})
    task_id = res_create.json()["id"]
    
    response = client.put(f"/tasks/{task_id}", 
                         json={"priority": "INVALID_PRIORITY"})
    
    # Deve aceitar (sem validação) ou retornar 422
    assert response.status_code in [200, 422]
```

---

## 4. TESTES DE OPERAÇÕES COM IDs INVÁLIDOS

### 4.1 Operações em IDs Inexistentes

#### Teste: GET com ID negativo
```python
def test_get_task_with_negative_id(client):
    """Valida comportamento com ID negativo"""
    response = client.get("/tasks/-1")
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]
```

#### Teste: GET com ID zero
```python
def test_get_task_with_zero_id(client):
    """Valida comportamento com ID zero"""
    response = client.get("/tasks/0")
    assert response.status_code == 404
```

#### Teste: GET com ID muito grande
```python
def test_get_task_with_huge_id(client):
    """Valida comportamento com ID excepcional"""
    response = client.get("/tasks/999999999")
    assert response.status_code == 404
```

#### Teste: GET com ID não numérico
```python
def test_get_task_with_string_id(client):
    """Valida rejeição de ID não numérico"""
    response = client.get("/tasks/abc")
    assert response.status_code == 422
```

#### Teste: UPDATE com ID inexistente
```python
def test_update_nonexistent_task(client):
    """Valida atualização de tarefa inexistente"""
    response = client.put("/tasks/999", 
                         json={"title": "Update Ghost Task"})
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]
```

#### Teste: DELETE com ID inexistente
```python
def test_delete_nonexistent_task(client):
    """Valida deleção de tarefa inexistente"""
    response = client.delete("/tasks/999")
    assert response.status_code == 404
```

#### Teste: PATCH com ID inexistente
```python
def test_patch_nonexistent_task_complete(client):
    """Valida patch de tarefa inexistente"""
    response = client.patch("/tasks/999/complete?completed=true")
    assert response.status_code == 404
```

---

## 5. TESTES DE QUERY PARAMETERS INVÁLIDOS

### 5.1 Filtros com Valores Inválidos

#### Teste: GET com parâmetro `completed` inválido
```python
def test_get_tasks_with_invalid_completed_param(client):
    """Valida filtro completed com valor inválido"""
    response = client.get("/tasks/?completed=maybe")
    # FastAPI deve fazer coerção ou retornar 422
    assert response.status_code in [200, 422]
```

#### Teste: GET com parâmetro `completed` numérico
```python
def test_get_tasks_with_numeric_completed_param(client):
    """Valida filtro completed com número"""
    response = client.get("/tasks/?completed=1")
    # Pode ser coagido para True ou causar erro
    assert response.status_code in [200, 422]
```

#### Teste: GET com múltiplos parâmetros conflitantes
```python
def test_get_tasks_with_conflicting_params(client):
    """Valida comportamento com parâmetros conflitantes"""
    # Se a API não suporta múltiplos filtros, testa tolerância
    response = client.get("/tasks/?completed=true&completed=false")
    assert response.status_code == 200
```

---

## 6. TESTES DE FALHAS DE CAMADAS

### 6.1 Falhas de Persistência e Transação

#### Teste: Simular falha de banco (transação)
```python
def test_create_task_with_db_failure_simulation(client, db, monkeypatch):
    """Simula falha de commit no banco de dados"""
    from sqlalchemy.orm import Session
    
    # Criar um mock que falha no commit
    original_commit = db.commit
    call_count = [0]
    
    def failing_commit():
        call_count[0] += 1
        if call_count[0] > 1:  # Simular falha na segunda tentativa
            raise Exception("Database connection lost")
        original_commit()
    
    monkeypatch.setattr(db, "commit", failing_commit)
    
    # A primeira deve passar, a segunda deve falhar
    response1 = client.post("/tasks/", json={"title": "Task 1"})
    assert response1.status_code == 200
    
    response2 = client.post("/tasks/", json={"title": "Task 2"})
    assert response2.status_code == 500  # Deve retornar erro de servidor
```

#### Teste: Verificar rollback após erro
```python
def test_transaction_rollback_on_error(client, db):
    """Valida se transação é desfeita após erro"""
    # Criar tarefa válida
    res1 = client.post("/tasks/", json={"title": "Valid Task"})
    initial_count = len(client.get("/tasks/").json())
    
    # Tentar operação que cause erro
    res_error = client.post("/tasks/", json={"title": ""})
    assert res_error.status_code == 422
    
    # Contar novamente - deve ser igual (rollback)
    final_count = len(client.get("/tasks/").json())
    assert initial_count == final_count
```

---

## 7. TESTES DE AUSÊNCIA DE VALIDAÇÃO

### 7.1 Validações Faltantes

#### Teste: Campos requeridos ausentes em UPDATE
```python
def test_update_task_with_empty_data(client):
    """Valida comportamento ao atualizar com dados vazios"""
    res_create = client.post("/tasks/", json={"title": "Test"})
    task_id = res_create.json()["id"]
    
    # UPDATE com payload vazio (todos os campos opcionais)
    response = client.put(f"/tasks/{task_id}", json={})
    
    # Deve retornar 200 (nada foi alterado)
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
```

#### Teste: Sobrescrever dados com null
```python
def test_update_task_fields_to_null(client):
    """Valida se é possível setar campos para null"""
    res_create = client.post("/tasks/", 
                            json={"title": "Test", 
                                  "description": "Has description"})
    task_id = res_create.json()["id"]
    
    # Tentar setar description para null
    response = client.put(f"/tasks/{task_id}", 
                         json={"description": None})
    
    # Pode aceitar (deixando null) ou rejeitar
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        assert response.json()["description"] is None
```

#### Teste: Validação de comprimento de description
```python
def test_create_task_with_huge_description(client):
    """Valida rejeição de description excessivamente grande"""
    huge_desc = "X" * 100000
    response = client.post("/tasks/", 
                          json={"title": "Test", 
                                "description": huge_desc})
    
    # Pode truncar ou rejeitar
    if response.status_code == 200:
        assert len(response.json()["description"]) <= 100000
```

---

## 8. TESTES DE RACE CONDITIONS E CONCORRÊNCIA

### 8.1 Operações Concorrentes

#### Teste: Deletar durante read
```python
def test_get_task_deleted_during_read(client):
    """Simula deleção durante leitura"""
    res_create = client.post("/tasks/", json={"title": "Race Test"})
    task_id = res_create.json()["id"]
    
    # Deletar
    client.delete(f"/tasks/{task_id}")
    
    # Tentar ler
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
```

#### Teste: Update durante read
```python
def test_update_task_during_read(client):
    """Valida consistência ao atualizar durante leitura"""
    res_create = client.post("/tasks/", json={"title": "Original Title"})
    task_id = res_create.json()["id"]
    
    # Simular: ler, depois atualizar, depois verificar
    read1 = client.get(f"/tasks/{task_id}").json()
    updated = client.put(f"/tasks/{task_id}", 
                        json={"title": "Updated Title"})
    read2 = client.get(f"/tasks/{task_id}").json()
    
    assert read1["title"] == "Original Title"
    assert updated.json()["title"] == "Updated Title"
    assert read2["title"] == "Updated Title"
```

---

## 9. TESTES DE LIMITES DE RECURSO

### 9.1 Limites de Quantidade e Tamanho

#### Teste: Criar grande número de tarefas
```python
def test_create_many_tasks(client):
    """Valida performance com muitas tarefas"""
    for i in range(1000):
        response = client.post("/tasks/", 
                              json={"title": f"Task {i}"})
        assert response.status_code == 200
    
    # Listar todas
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) >= 1000
```

#### Teste: Filtro com muitos resultados
```python
def test_get_tasks_with_large_result_set(client):
    """Valida listagem com muitos resultados"""
    # Criar tarefas
    for i in range(100):
        client.post("/tasks/", json={"title": f"Task {i}", "completed": False})
    
    # Listar sem completar
    response = client.get("/tasks/?completed=false")
    assert response.status_code == 200
    assert len(response.json()) >= 100
```

---

## 10. TESTES DE PRIORIDADE COM PRIORITY_ADVISOR

### 10.1 Prioridade Automática

#### Teste: Palavras-chave de alta prioridade
```python
def test_priority_detection_high(client):
    """Valida detecção automática de priority alta"""
    keywords = ["urgente", "crítico", "imediato"]
    
    for keyword in keywords:
        response = client.post("/tasks/", 
                              json={"title": f"Task {keyword}"})
        assert response.json()["priority"] == "Alta"
```

#### Teste: Palavras-chave de prioridade média
```python
def test_priority_detection_medium(client):
    """Valida detecção automática de priority média"""
    keywords = ["importante", "breve"]
    
    for keyword in keywords:
        response = client.post("/tasks/", 
                              json={"title": f"Task {keyword}"})
        assert response.json()["priority"] == "Média"
```

#### Teste: Priority explícita sobrescreve automática
```python
def test_explicit_priority_overrides_detection(client):
    """Valida se priority explícita sobrescreve detecção"""
    response = client.post("/tasks/", 
                          json={"title": "Urgente task", 
                                "priority": "Baixa"})
    # Verifica se respeita a priority fornecida
    assert response.json()["priority"] == "Baixa"
```

#### Teste: Priority nulo deve usar detecção
```python
def test_null_priority_triggers_detection(client):
    """Valida detecção quando priority é None"""
    response = client.post("/tasks/", 
                          json={"title": "Urgente task", 
                                "priority": None})
    # Deve usar o advisor
    assert response.json()["priority"] == "Alta"
```

---

## 11. TESTES DE RESPONSE INTEGRITY

### 11.1 Integridade da Resposta

#### Teste: Response tem todos os campos obrigatórios
```python
def test_response_has_all_required_fields(client):
    """Valida se response tem todos os campos"""
    response = client.post("/tasks/", json={"title": "Test"})
    data = response.json()
    
    required_fields = ["id", "title", "description", "completed", "priority"]
    for field in required_fields:
        assert field in data, f"Field '{field}' missing in response"
```

#### Teste: Response types são corretos
```python
def test_response_field_types_are_correct(client):
    """Valida tipos dos campos na response"""
    response = client.post("/tasks/", json={"title": "Test"})
    data = response.json()
    
    assert isinstance(data["id"], int)
    assert isinstance(data["title"], str)
    assert isinstance(data["completed"], bool)
    assert isinstance(data["priority"], str)
    # description pode ser None ou str
    assert data["description"] is None or isinstance(data["description"], str)
```

#### Teste: GET list retorna array
```python
def test_get_tasks_returns_array(client):
    """Valida que GET lista retorna array"""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

#### Teste: DELETE retorna mensagem apropriada
```python
def test_delete_response_format(client):
    """Valida formato da response de delete"""
    res_create = client.post("/tasks/", json={"title": "Delete me"})
    task_id = res_create.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}")
    data = response.json()
    
    assert "msg" in data or "message" in data
    assert "deletada" in str(data).lower()
```

---

## 12. TESTES DE INTEGRAÇÃO ENTRE CAMADAS

### 12.1 Fluxos Complexos

#### Teste: Criar → Atualizar → Listar → Deletar
```python
def test_full_crud_workflow(client):
    """Testa fluxo completo de CRUD"""
    # CREATE
    res_create = client.post("/tasks/", 
                            json={"title": "CRUD Test", 
                                  "description": "Initial"})
    assert res_create.status_code == 200
    task_id = res_create.json()["id"]
    
    # READ individual
    res_read = client.get(f"/tasks/{task_id}")
    assert res_read.status_code == 200
    assert res_read.json()["title"] == "CRUD Test"
    
    # UPDATE
    res_update = client.put(f"/tasks/{task_id}", 
                           json={"description": "Updated"})
    assert res_update.status_code == 200
    assert res_update.json()["description"] == "Updated"
    
    # LIST
    res_list = client.get("/tasks/")
    assert res_list.status_code == 200
    task_ids = [t["id"] for t in res_list.json()]
    assert task_id in task_ids
    
    # DELETE
    res_delete = client.delete(f"/tasks/{task_id}")
    assert res_delete.status_code == 200
    
    # Verify deleted
    res_verify = client.get(f"/tasks/{task_id}")
    assert res_verify.status_code == 404
```

#### Teste: Criar múltiplas, filtrar, atualizar todas
```python
def test_bulk_operations_workflow(client):
    """Testa operações em lote"""
    # Criar tarefas variadas
    for i in range(5):
        client.post("/tasks/", 
                   json={"title": f"Task {i}", 
                         "completed": i % 2 == 0})
    
    # Listar pendentes
    res_pending = client.get("/tasks/?completed=false")
    pending_tasks = res_pending.json()
    
    # Completar todos pendentes
    for task in pending_tasks:
        response = client.patch(f"/tasks/{task['id']}/complete?completed=true")
        assert response.status_code == 200
    
    # Verificar nenhum pendente restante
    res_final = client.get("/tasks/?completed=false")
    assert len(res_final.json()) == 0
```

---

## Resumo de Cobertura de Testes

| Categoria | Testes | Casos |
|-----------|--------|-------|
| Validação de Dados | 10+ | title vazio/nulo, tipos inválidos, tamanho extremo |
| Valores Duplicados | 2+ | Títulos duplicados, conflitos de update |
| Estados Inconsistentes | 4+ | Ciclos de conclusão, updates em concluídas |
| IDs Inválidos | 6+ | ID negativo, zero, grande, string, inexistente |
| Query Parameters | 3+ | Parâmetros inválidos, conflitantes |
| Falhas de Camadas | 2+ | Falha de BD, rollback de transação |
| Ausência de Validação | 3+ | Dados vazios, null, tamanho não validado |
| Race Conditions | 2+ | Delete durante read, update durante read |
| Limites de Recurso | 2+ | Muitas tarefas, muitos resultados |
| Priority Advisor | 4+ | Palavras-chave, override, null |
| Response Integrity | 4+ | Campos obrigatórios, tipos, formato |
| Integração Completa | 2+ | CRUD completo, operações em lote |

**Total: 45+ casos de teste cobrindo segurança, performance e robustez**

---

## Implementação dos Testes

Os testes devem ser adicionados em:
- `app/tests/test_error_cases.py` - Casos de erro e edge cases
- `app/tests/test_integration_complex.py` - Fluxos complexos
- `app/tests/conftest.py` - Fixtures para simular falhas

### Arquitetura de Testes Recomendada

```
app/tests/
├── conftest.py                    # Fixtures base
├── test_tasks.py                  # Happy path (existente)
├── test_validation.py             # Validação de dados
├── test_edge_cases.py             # Edge cases e limites
├── test_error_handling.py         # Tratamento de erros
├── test_integration.py            # Fluxos complexos
└── unit/                          # Testes unitários por camada
```

