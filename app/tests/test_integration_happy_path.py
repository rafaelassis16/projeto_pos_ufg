"""
Testes de Integração - Happy Path
API de Gerenciamento de Tarefas em FastAPI

Cobre fluxos bem-sucedidos entre todas as camadas (Routes → Service → Repository → Database).
Usa fixtures do conftest.py

Arquivo: app/tests/test_integration_happy_path.py
"""

import pytest


# ============================================================================
# TESTE 1: Criação de Tarefa com Prioridade Automática (Happy Path)
# ============================================================================

class TestCreateTaskHappyPath:
    """Fluxo completo: Route → Service → PriorityAdvisor → Repository → DB"""
    
    def test_create_task_with_auto_priority_alta(self, integration_client):
        """
        Cenário: Criar tarefa com palavras-chave que indicam alta prioridade
        Esperado: Priority é definida automaticamente como "Alta"
        
        Fluxo:
        1. POST /tasks/ com {"title": "urgente atender", "description": "bug crítico"}
        2. Route recebe dados e chama TaskService.create_task()
        3. Service verifica priority == None, chama PriorityAdvisor.advise()
        4. PriorityAdvisor analisa title/description, retorna "Alta"
        5. Service cria Task no banco via ORM
        6. DB insere e retorna ID
        7. Route retorna 200 com Task criada
        """
        response = integration_client.post(
            "/tasks/",
            json={
                "title": "urgente atender cliente",
                "description": "bug crítico no sistema"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validações do fluxo completo
        assert data["id"] is not None  # ID gerado no DB
        assert data["title"] == "urgente atender cliente"
        assert data["description"] == "bug crítico no sistema"
        assert data["priority"] == "Alta"  # Priority automática
        assert data["completed"] is False  # Default
    
    def test_create_task_with_explicit_priority(self, integration_client):
        """
        Cenário: Criar tarefa com prioridade explícita (não será sobrescrita)
        Esperado: Prioridade fornecida é respeitada
        
        Fluxo validado:
        - Route recebe prioridade explícita
        - Service NÃO sobrescreve (prioridade já está definida)
        - Task é criada com prioridade fornecida
        """
        response = integration_client.post(
            "/tasks/",
            json={
                "title": "Tarefa média",
                "description": "Prioridade explícita",
                "priority": "Média"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "Média"
        assert data["title"] == "Tarefa média"
    
    def test_create_multiple_tasks_incremental_ids(self, integration_client):
        """
        Cenário: Criar múltiplas tarefas sequencialmente
        Esperado: IDs incrementam corretamente, todas são persistidas
        
        Fluxo validado:
        - Cada POST cria nova Task no DB
        - Cada Task recebe ID único sequencial
        """
        tasks_data = [
            {"title": "Tarefa 1", "description": "Primeira"},
            {"title": "Tarefa 2", "description": "Segunda"},
            {"title": "Tarefa 3", "description": "Terceira"}
        ]
        
        created_ids = []
        for task_data in tasks_data:
            response = integration_client.post("/tasks/", json=task_data)
            assert response.status_code == 200
            created_ids.append(response.json()["id"])
        
        # Validar IDs incrementam
        assert created_ids == sorted(created_ids)
        assert len(set(created_ids)) == 3  # Todos únicos


# ============================================================================
# TESTE 2: Leitura de Tarefas com Filtro (Happy Path)
# ============================================================================

class TestGetTasksHappyPath:
    """Fluxo: GET /tasks → Service.get_tasks() → ORM query → DB select"""
    
    def test_get_all_tasks(self, integration_client):
        """
        Cenário: Recuperar todas as tarefas sem filtro
        Esperado: Lista contém todas as tarefas criadas
        
        Fluxo:
        1. Criar 3 tarefas com estados diferentes
        2. GET /tasks/ sem query params
        3. Service consulta todas as tasks
        4. ORM executa SELECT * FROM tasks
        5. Retorna lista com 3 tarefas
        """
        # Setup: criar tarefas
        integration_client.post("/tasks/", json={"title": "Task 1", "completed": True})
        integration_client.post("/tasks/", json={"title": "Task 2", "completed": False})
        integration_client.post("/tasks/", json={"title": "Task 3", "completed": False})
        
        # Teste
        response = integration_client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 3
        assert all(isinstance(task, dict) for task in data)
        assert all("id" in task and "title" in task for task in data)
    
    def test_get_tasks_filter_completed_true(self, integration_client):
        """
        Cenário: Filtrar apenas tarefas completadas
        Esperado: Retorna apenas tarefas com completed=True
        
        Fluxo validado:
        - Route recebe query param ?completed=true
        - Service filtra: WHERE completed = true
        - ORM executa query filtrada
        """
        # Setup
        integration_client.post("/tasks/", json={"title": "Done 1", "completed": True})
        integration_client.post("/tasks/", json={"title": "Done 2", "completed": True})
        integration_client.post("/tasks/", json={"title": "Pending", "completed": False})
        
        # Teste
        response = integration_client.get("/tasks/?completed=true")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        assert all(task["completed"] is True for task in data)
        assert {task["title"] for task in data} == {"Done 1", "Done 2"}
    
    def test_get_tasks_filter_completed_false(self, integration_client):
        """
        Cenário: Filtrar apenas tarefas pendentes
        Esperado: Retorna apenas tarefas com completed=False
        """
        # Setup
        integration_client.post("/tasks/", json={"title": "Done", "completed": True})
        integration_client.post("/tasks/", json={"title": "Pending 1", "completed": False})
        integration_client.post("/tasks/", json={"title": "Pending 2", "completed": False})
        
        # Teste
        response = integration_client.get("/tasks/?completed=false")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 2
        assert all(task["completed"] is False for task in data)


# ============================================================================
# TESTE 3: Leitura de Tarefa Individual (Happy Path)
# ============================================================================

class TestGetTaskByIdHappyPath:
    """Fluxo: GET /tasks/{id} → Service.get_task() → ORM query → DB"""
    
    def test_get_task_by_id_success(self, integration_client):
        """
        Cenário: Recuperar tarefa específica por ID
        Esperado: Retorna Task correta com todos os campos
        
        Fluxo:
        1. Criar Task com dados específicos
        2. GET /tasks/{id}
        3. Service busca por ID
        4. ORM executa SELECT * FROM tasks WHERE id = ?
        5. Retorna Task completa
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={
                "title": "Specific Task",
                "description": "Detalhes da tarefa",
                "priority": "Alta"
            }
        )
        task_id = create_response.json()["id"]
        
        # Teste
        response = integration_client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert data["title"] == "Specific Task"
        assert data["description"] == "Detalhes da tarefa"
        assert data["priority"] == "Alta"
        assert data["completed"] is False
    
    def test_get_task_preserves_all_fields(self, integration_client):
        """
        Cenário: Verificar que leitura preserva todos os campos
        Esperado: Nenhum campo é perdido no fluxo Route→Service→DB→Route
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={
                "title": "Complete Task",
                "description": "Full description",
                "priority": "Média",
                "completed": True
            }
        )
        task_id = create_response.json()["id"]
        
        # Teste
        response = integration_client.get(f"/tasks/{task_id}")
        data = response.json()
        
        # Verificar todos os campos
        required_fields = {"id", "title", "description", "priority", "completed"}
        assert required_fields.issubset(set(data.keys()))
        assert data["completed"] is True


# ============================================================================
# TESTE 4: Atualização Completa (PUT) - Happy Path
# ============================================================================

class TestUpdateTaskHappyPath:
    """Fluxo: PUT /tasks/{id} → Service.update_task() → ORM update → DB"""
    
    def test_update_task_all_fields(self, integration_client):
        """
        Cenário: Atualizar todos os campos de uma tarefa
        Esperado: Todos os campos são atualizados no DB
        
        Fluxo:
        1. Criar Task original
        2. PUT /tasks/{id} com novos dados
        3. Service busca Task existente
        4. Service atualiza campos via setattr()
        5. ORM executa UPDATE no DB
        6. Retorna Task atualizada
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "Original", "description": "Old"}
        )
        task_id = create_response.json()["id"]
        
        # Teste: Update
        update_response = integration_client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Updated Title",
                "description": "Updated Description",
                "priority": "Alta",
                "completed": True
            }
        )
        
        assert update_response.status_code == 200
        updated_data = update_response.json()
        
        assert updated_data["id"] == task_id
        assert updated_data["title"] == "Updated Title"
        assert updated_data["description"] == "Updated Description"
        assert updated_data["priority"] == "Alta"
        assert updated_data["completed"] is True
    
    def test_update_task_partial_fields(self, integration_client):
        """
        Cenário: Atualizar apenas alguns campos (PUT com exclude_unset=True)
        Esperado: Campos não fornecidos mantêm valores anteriores
        
        Fluxo validado:
        - TaskUpdate permite None para campos opcionales
        - Service usa exclude_unset=True para atualizar só o fornecido
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={
                "title": "Original",
                "description": "Original Description",
                "priority": "Baixa",
                "completed": False
            }
        )
        task_id = create_response.json()["id"]
        
        # Teste: Atualizar apenas title
        response = integration_client.put(
            f"/tasks/{task_id}",
            json={"title": "New Title"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "New Title"
        # Campos não atualizados mantêm valores originais
        assert data["description"] == "Original Description"
        assert data["priority"] == "Baixa"
        assert data["completed"] is False
    
    def test_update_task_idempotent(self, integration_client):
        """
        Cenário: Atualizar tarefa duas vezes com mesmos dados
        Esperado: Resultado final é idêntico
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "Task"}
        )
        task_id = create_response.json()["id"]
        
        update_data = {"title": "Updated", "priority": "Alta"}
        
        # Primeira atualização
        response1 = integration_client.put(f"/tasks/{task_id}", json=update_data)
        data1 = response1.json()
        
        # Segunda atualização com mesmos dados
        response2 = integration_client.put(f"/tasks/{task_id}", json=update_data)
        data2 = response2.json()
        
        # Resultado é idêntico
        assert data1["title"] == data2["title"] == "Updated"
        assert data1["priority"] == data2["priority"] == "Alta"


# ============================================================================
# TESTE 5: Atualização Parcial (PATCH) - Happy Path
# ============================================================================

class TestPatchTaskHappyPath:
    """Fluxo: PATCH /tasks/{id}/complete → Service.patch_task_completion() → DB"""
    
    def test_patch_task_mark_complete(self, integration_client):
        """
        Cenário: Marcar tarefa como completada via PATCH
        Esperado: Campo completed muda para True
        
        Fluxo:
        1. Criar Task com completed=False
        2. PATCH /tasks/{id}/complete?completed=true
        3. Service busca Task
        4. Service atualiza apenas campo 'completed'
        5. ORM executa UPDATE completado=true
        6. Retorna Task atualizada
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "Task to Complete", "completed": False}
        )
        task_id = create_response.json()["id"]
        
        # Teste: Mark complete
        response = integration_client.patch(f"/tasks/{task_id}/complete?completed=true")
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == task_id
        assert data["completed"] is True
        assert data["title"] == "Task to Complete"  # Outros campos não mudam
    
    def test_patch_task_mark_incomplete(self, integration_client):
        """
        Cenário: Marcar tarefa como não completada
        Esperado: Campo completed muda para False
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "Task", "completed": True}
        )
        task_id = create_response.json()["id"]
        
        # Teste
        response = integration_client.patch(f"/tasks/{task_id}/complete?completed=false")
        assert response.status_code == 200
        assert response.json()["completed"] is False
    
    def test_patch_preserves_other_fields(self, integration_client):
        """
        Cenário: PATCH não altera outros campos da tarefa
        Esperado: Apenas 'completed' é alterado
        """
        # Setup com múltiplos campos
        create_response = integration_client.post(
            "/tasks/",
            json={
                "title": "Complex Task",
                "description": "With description",
                "priority": "Alta",
                "completed": False
            }
        )
        task_id = create_response.json()["id"]
        
        # Teste: Patch apenas completion
        response = integration_client.patch(f"/tasks/{task_id}/complete?completed=true")
        data = response.json()
        
        # Verificar que outros campos mantêm valores
        assert data["title"] == "Complex Task"
        assert data["description"] == "With description"
        assert data["priority"] == "Alta"
        assert data["completed"] is True


# ============================================================================
# TESTE 6: Exclusão de Tarefa (Happy Path)
# ============================================================================

class TestDeleteTaskHappyPath:
    """Fluxo: DELETE /tasks/{id} → Service.delete_task() → ORM delete → DB"""
    
    def test_delete_task_success(self, integration_client):
        """
        Cenário: Deletar tarefa existente
        Esperado: Tarefa é removida do DB, resposta 200
        
        Fluxo:
        1. Criar Task
        2. DELETE /tasks/{id}
        3. Service busca Task por ID
        4. Service chama db.delete()
        5. ORM executa DELETE no DB
        6. Retorna sucesso
        """
        # Setup
        create_response = integration_client.post(
            "/tasks/",
            json={"title": "To Delete"}
        )
        task_id = create_response.json()["id"]
        
        # Verify Task exists
        get_response = integration_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        
        # Teste: Delete
        delete_response = integration_client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["msg"] == "Tarefa deletada"
        
        # Verify Task foi removida do DB
        get_after_response = integration_client.get(f"/tasks/{task_id}")
        assert get_after_response.status_code == 404
    
    def test_delete_task_removes_from_list(self, integration_client):
        """
        Cenário: Tarefa deletada não aparece na lista
        Esperado: GET /tasks/ não retorna task deletada
        """
        # Setup
        response1 = integration_client.post("/tasks/", json={"title": "Task 1"})
        response2 = integration_client.post("/tasks/", json={"title": "Task 2"})
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        
        # Get all - 2 tarefas
        list_before = integration_client.get("/tasks/").json()
        assert len(list_before) == 2
        
        # Delete Task 1
        integration_client.delete(f"/tasks/{id1}")
        
        # Get all - 1 tarefa
        list_after = integration_client.get("/tasks/").json()
        assert len(list_after) == 1
        assert list_after[0]["id"] == id2


# ============================================================================
# TESTE 7: Fluxo Completo End-to-End (Happy Path)
# ============================================================================

class TestCompleteWorkflowHappyPath:
    """Testa sequência realista de operações"""
    
    def test_full_task_lifecycle(self, integration_client):
        """
        Cenário: Ciclo de vida completo de uma tarefa
        Tarefa: Planejamento de projeto
        
        Fluxo:
        1. Criar tarefa (criação com prioridade automática)
        2. Ler tarefa (verificar dados)
        3. Atualizar descrição (PUT parcial)
        4. Marcar como completa (PATCH)
        5. Deletar (DELETE)
        6. Verificar que foi removida (404 ao tentar ler)
        """
        
        # Step 1: Create
        create_response = integration_client.post(
            "/tasks/",
            json={
                "title": "Planejar projeto novo",
                "description": "Inicial"
            }
        )
        assert create_response.status_code == 200
        task_id = create_response.json()["id"]
        created_task = create_response.json()
        
        assert created_task["priority"] == "Alta"  # Auto-prioridade (palavras-chave)
        assert created_task["completed"] is False
        
        # Step 2: Read
        get_response = integration_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        read_task = get_response.json()
        assert read_task["id"] == task_id
        assert read_task["title"] == "Planejar projeto novo"
        
        # Step 3: Update
        update_response = integration_client.put(
            f"/tasks/{task_id}",
            json={"description": "Descrição completa do projeto"}
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["description"] == "Descrição completa do projeto"
        
        # Step 4: Complete (PATCH)
        complete_response = integration_client.patch(f"/tasks/{task_id}/complete?completed=true")
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["completed"] is True
        
        # Step 5: Delete
        delete_response = integration_client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 200
        
        # Step 6: Verify deletion
        final_get = integration_client.get(f"/tasks/{task_id}")
        assert final_get.status_code == 404
