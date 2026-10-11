"""
Testes de Integração - Casos de Erro e Edge Cases
API de Gerenciamento de Tarefas em FastAPI

Cobre cenários de falha, validação e estados inconsistentes:
- Dados inválidos
- Recursos não encontrados
- Valores duplicados
- Estados inconsistentes
- Falhas de validação Pydantic

Usa fixtures do conftest.py

Arquivo: app/tests/test_integration_error_cases.py
"""

import pytest


# ============================================================================
# TESTE 1: Validação de Entrada (Pydantic)
# ============================================================================

class TestInputValidation:
    """Validações Pydantic no endpoint POST /tasks/"""
    
    def test_create_task_missing_title_required_field(self, integration_client):
        """
        Cenário: Tentar criar tarefa sem 'title' (campo obrigatório)
        Esperado: 422 Unprocessable Entity (Pydantic validation error)
        
        Camada testada: Route → Pydantic validation
        """
        response = integration_client.post(
            "/tasks/",
            json={"description": "Sem título"}
        )
        
        assert response.status_code == 422
        assert "detail" in response.json()
        # Validar que erro menciona o campo 'title'
        error_detail = str(response.json()["detail"])
        assert "title" in error_detail.lower()
    
    def test_create_task_empty_title_string(self, integration_client):
        """
        Cenário: Criar tarefa com título vazio
        Esperado: Aceita (Pydantic permite str vazio por padrão)
        Nota: Esta é uma lacuna de validação que pode ser melhorada
        """
        response = integration_client.post(
            "/tasks/",
            json={"title": "", "description": "Título vazio"}
        )
        
        # Comportamento atual: aceita
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == ""
        
        # TODO: Adicionar validação `title: str = Field(..., min_length=1)`
    
    def test_create_task_invalid_json_format(self, integration_client):
        """
        Cenário: Enviar JSON inválido
        Esperado: 422 JSON decode error
        """
        response = integration_client.post(
            "/tasks/",
            data="invalid json {]",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_create_task_invalid_field_type(self, integration_client):
        """
        Cenário: Fornecer tipo incorreto para campo
        Esperado: 422 Validation error do Pydantic
        """
        response = integration_client.post(
            "/tasks/",
            json={
                "title": "Task",
                "completed": "não"  # String ao invés de boolean
            }
        )
        
        assert response.status_code == 422
        error = response.json()["detail"][0]
        assert "completed" in str(error) or "type" in str(error).lower()


# ============================================================================
# TESTE 2: Recursos Não Encontrados (404)
# ============================================================================

class TestNotFoundErrors:
    """Testa cenários 404"""
    
    def test_get_task_non_existent_id(self, integration_client):
        """
        Cenário: Recuperar tarefa com ID que não existe
        Esperado: 404 Not Found
        
        Camada testada: Route → Service.get_task() → DB (query retorna None)
        """
        response = integration_client.get("/tasks/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Tarefa não encontrada"
    
    def test_get_task_invalid_id_format(self, integration_client):
        """
        Cenário: ID com formato inválido (não é inteiro)
        Esperado: 422 Validation error
        """
        response = integration_client.get("/tasks/abc")
        
        assert response.status_code == 422
        error = response.json()
        assert "detail" in error
    
    def test_get_task_negative_id(self, integration_client):
        """
        Cenário: ID negativo (válido para FastAPI, inválido para DB)
        Esperado: 404 (query não encontra ID negativo)
        """
        response = integration_client.get("/tasks/-1")
        
        assert response.status_code == 404
    
    def test_update_non_existent_task(self, integration_client):
        """
        Cenário: Tentar atualizar tarefa que não existe
        Esperado: 404 Not Found
        
        Camada testada: Route → Service.update_task() → (DB query retorna None)
        """
        response = integration_client.put(
            "/tasks/999",
            json={"title": "New Title"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Tarefa não encontrada"
    
    def test_patch_non_existent_task(self, integration_client):
        """
        Cenário: Tentar marcar como completo tarefa inexistente
        Esperado: 404 Not Found
        """
        response = integration_client.patch("/tasks/999/complete?completed=true")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Tarefa não encontrada"
    
    def test_delete_non_existent_task(self, integration_client):
        """
        Cenário: Tentar deletar tarefa que não existe
        Esperado: 404 Not Found
        
        Camada testada: Route → Service.delete_task() → (DB query retorna None)
        """
        response = integration_client.delete("/tasks/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Tarefa não encontrada"


# ============================================================================
# TESTE 3: Estados Inconsistentes
# ============================================================================

class TestInconsistentStates:
    """Testa estados contraditórios"""
    
    def test_task_cannot_be_created_and_completed_simultaneously(self, integration_client):
        """
        Cenário: Criar tarefa já marcada como completada
        Esperado: Task é criada com completed=True (sem contradição no fluxo)
        Observação: Logicamente pode ser inconsistente (criar = não fazer)
        """
        response = integration_client.post(
            "/tasks/",
            json={
                "title": "Completed on creation",
                "completed": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        # Verificar que foi realmente persistido
        get_response = integration_client.get(f"/tasks/{data['id']}")
        assert get_response.json()["completed"] is True
    
    def test_task_priority_advisor_overrides_baixa(self, integration_client):
        """
        Cenário: Criar tarefa com priority="Baixa" explicitamente
        Esperado: Service ainda aplica PriorityAdvisor se detectar palavras-chave
        
        Fluxo validado:
        - Route recebe priority="Baixa"
        - Service verifica: if not priority or priority == "Baixa"
        - Service chama PriorityAdvisor mesmo para "Baixa" explícito
        """
        response = integration_client.post(
            "/tasks/",
            json={
                "title": "urgente problema crítico",
                "priority": "Baixa"  # Explicitamente baixa, mas título sugere alta
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Service sobrescreve "Baixa" com PriorityAdvisor
        assert data["priority"] == "Alta"
    
    def test_task_priority_explicitly_set_not_overridden(self, integration_client):
        """
        Cenário: Criar tarefa com priority="Média" (não é None ou "Baixa")
        Esperado: PriorityAdvisor NÃO é chamado, mantém "Média"
        
        Fluxo:
        - Service verifica: if not priority or priority == "Baixa"
        - Condição é False para "Média"
        - Priority não é sobrescrita
        """
        response = integration_client.post(
            "/tasks/",
            json={
                "title": "urgente problema crítico",
                "priority": "Média"  # Explicitamente Média
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # Priority não é sobrescrita
        assert data["priority"] == "Média"


# ============================================================================
# TESTE 4: Valores Duplicados e Limites
# ============================================================================

class TestDuplicatesAndLimits:
    """Testa comportamento com valores duplicados"""
    
    def test_create_multiple_tasks_with_same_title(self, integration_client):
        """
        Cenário: Criar duas tarefas com título idêntico
        Esperado: Ambas são criadas com IDs diferentes
        Observação: Não há constraint UNIQUE em 'title'
        
        Camada testada: Service → ORM → DB (sem validação de unicidade)
        """
        title = "Mesma Tarefa"
        
        response1 = integration_client.post("/tasks/", json={"title": title})
        response2 = integration_client.post("/tasks/", json={"title": title})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        
        # IDs são diferentes
        assert id1 != id2
        
        # Ambas existem no DB
        assert integration_client.get(f"/tasks/{id1}").status_code == 200
        assert integration_client.get(f"/tasks/{id2}").status_code == 200
        
        # GET /tasks/ retorna 2 tarefas
        all_tasks = integration_client.get("/tasks/").json()
        assert len(all_tasks) == 2
    
    def test_create_task_very_long_title(self, integration_client):
        """
        Cenário: Criar tarefa com título muito longo
        Esperado: Aceita (SQLite String pode ser bem longo)
        """
        long_title = "X" * 10000  # 10k characters
        
        response = integration_client.post(
            "/tasks/",
            json={"title": long_title}
        )
        
        # Deve aceitar (SQLite String não tem limite fixo)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == long_title
        assert len(data["title"]) == 10000
    
    def test_create_task_very_long_description(self, integration_client):
        """
        Cenário: Descrição muito longa
        Esperado: Aceita
        """
        long_description = "Y" * 50000  # 50k characters
        
        response = integration_client.post(
            "/tasks/",
            json={"title": "Task", "description": long_description}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["description"]) == 50000
    
    def test_create_task_special_characters_title(self, integration_client):
        """
        Cenário: Título com caracteres especiais
        Esperado: Persiste corretamente
        """
        special_title = "Task @#$%^&*()[]{}\\|;:'\",.<>?/ 日本語 العربية"
        
        response = integration_client.post(
            "/tasks/",
            json={"title": special_title}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == special_title
        
        # Verificar que foi persistido
        get_response = integration_client.get(f"/tasks/{data['id']}")
        assert get_response.json()["title"] == special_title


# ============================================================================
# TESTE 5: Operações Concorrentes (Simuladas)
# ============================================================================

class TestConcurrentOperations:
    """Simula operações concorrentes"""
    
    def test_read_during_update_consistency(self, integration_client):
        """
        Cenário: Ler tarefa enquanto está sendo atualizada
        Esperado: Sem race conditions (SQLite tem locking)
        
        Nota: Teste sequencial simula concorrência
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "Original", "description": "Orig desc"}
        )
        task_id = create_response.json()["id"]
        
        # Update (em tempo real seria concorrente)
        integration_client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated"}
        )
        
        # Read
        get_response = integration_client.get(f"/tasks/{task_id}")
        data = get_response.json()
        
        # Deve ter valor consistente (updated ou original, não inconsistente)
        assert data["title"] in ["Updated", "Original"]
    
    def test_multiple_updates_sequence(self, integration_client):
        """
        Cenário: Múltiplas atualizações sequenciais
        Esperado: Última atualização prevalece
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "V1"}
        )
        task_id = create_response.json()["id"]
        
        # Sequência de updates
        updates = ["V2", "V3", "V4", "V5"]
        for version in updates:
            integration_client.put(f"/tasks/{task_id}", json={"title": version})
        
        # Verificar última versão
        final_response = integration_client.get(f"/tasks/{task_id}")
        assert final_response.json()["title"] == "V5"
    
    def test_delete_and_recreate(self, integration_client):
        """
        Cenário: Deletar tarefa e criar nova com mesmo ID (impossível)
        Esperado: Nova tarefa recebe novo ID
        """
        # Create and get ID
        create1 = integration_client.post("/tasks/", json={"title": "First"})
        id1 = create1.json()["id"]
        
        # Delete
        integration_client.delete(f"/tasks/{id1}")
        
        # Create new
        create2 = integration_client.post("/tasks/", json={"title": "Second"})
        id2 = create2.json()["id"]
        
        # IDs são diferentes (no SQLite, ID não é reutilizado)
        assert id1 != id2
        assert id2 > id1  # Novo ID é maior
        
        # Original não existe
        assert integration_client.get(f"/tasks/{id1}").status_code == 404
        # Nova existe
        assert integration_client.get(f"/tasks/{id2}").status_code == 200


# ============================================================================
# TESTE 6: Filtros com Edge Cases
# ============================================================================

class TestFilterEdgeCases:
    """Testa filtros com valores extremos"""
    
    def test_filter_completed_with_no_tasks(self, integration_client):
        """
        Cenário: Filtrar tarefas completadas quando nenhuma existe
        Esperado: Lista vazia, status 200
        """
        response = integration_client.get("/tasks/?completed=true")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_filter_completed_true_and_false_mixed(self, integration_client):
        """
        Cenário: DB tem mix de True e False
        Esperado: Filtro retorna apenas requisitado
        """
        # Setup
        for i in range(5):
            integration_client.post(
                "/tasks/",
                json={"title": f"Task {i}", "completed": i % 2 == 0}
            )
        
        # Filter true
        response_true = integration_client.get("/tasks/?completed=true")
        data_true = response_true.json()
        assert len(data_true) == 3
        assert all(t["completed"] is True for t in data_true)
        
        # Filter false
        response_false = integration_client.get("/tasks/?completed=false")
        data_false = response_false.json()
        assert len(data_false) == 2
        assert all(t["completed"] is False for t in data_false)
    
    def test_filter_completed_invalid_value(self, integration_client):
        """
        Cenário: Query param ?completed=maybe (valor inválido)
        Esperado: Pydantic tenta converter para bool, falha, 422
        """
        response = integration_client.get("/tasks/?completed=maybe")
        
        assert response.status_code == 422


# ============================================================================
# TESTE 7: Transações e Integridade
# ============================================================================

class TestTransactionIntegrity:
    """Testa transações e integridade de dados"""
    
    def test_update_partial_then_full_consistency(self, integration_client):
        """
        Cenário: Atualizar parcialmente (alguns campos) e depois full
        Esperado: Estados intermediários não conflitam
        """
        # Create
        create_response = integration_client.post(
            "/tasks/",
            json={
                "title": "Original Title",
                "description": "Original Desc",
                "priority": "Baixa",
                "completed": False
            }
        )
        task_id = create_response.json()["id"]
        
        # Partial update - apenas title
        integration_client.put(f"/tasks/{task_id}", json={"title": "Updated Title"})
        
        # Full update - todos os campos
        full_update = integration_client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Final Title",
                "description": "Final Desc",
                "priority": "Alta",
                "completed": True
            }
        )
        
        final_data = full_update.json()
        
        # Verificar estado final consistente
        assert final_data["title"] == "Final Title"
        assert final_data["description"] == "Final Desc"
        assert final_data["priority"] == "Alta"
        assert final_data["completed"] is True
    
    def test_delete_removes_completely_from_queries(self, integration_client):
        """
        Cenário: Deletar task e verificar não aparece em nenhuma query
        Esperado: Task não aparece em GET /tasks/ nem GET /tasks/{id}
        """
        # Create 3 tasks
        ids = []
        for i in range(3):
            response = integration_client.post("/tasks/", json={"title": f"Task {i}"})
            ids.append(response.json()["id"])
        
        # Delete middle task
        integration_client.delete(f"/tasks/{ids[1]}")
        
        # Verify not in list
        all_tasks = integration_client.get("/tasks/").json()
        all_ids = [t["id"] for t in all_tasks]
        
        assert ids[1] not in all_ids
        assert ids[0] in all_ids
        assert ids[2] in all_ids
        
        # Verify direct GET returns 404
        assert integration_client.get(f"/tasks/{ids[1]}").status_code == 404
