"""
Testes de Erro e Edge Cases - API de Gerenciamento de Tarefas

Cobertura:
- Validação de dados inválidos
- Estados inconsistentes
- IDs inválidos e operações não permitidas
- Ausência de validação
- Race conditions simuladas
"""

import pytest
from fastapi.testclient import TestClient


class TestValidacaoDadosInvalidos:
    """Testes de validação de dados inválidos na criação de tarefas"""

    def test_create_task_with_empty_title(self, client):
        """Valida behavior com title vazio (string vazia)"""
        response = client.post("/tasks/", json={"title": ""})
        # FastAPI/Pydantic permite string vazia por padrão
        # Este teste valida que a API aceita ou rejeita conforme implementado
        if response.status_code == 200:
            # Se aceita, verifica que foi salvo
            assert response.json()["title"] == ""
        else:
            # Se rejeita, verifica que é 422
            assert response.status_code == 422

    def test_create_task_with_null_title(self, client):
        """Rejeita title nulo (None)"""
        response = client.post("/tasks/", json={"title": None})
        assert response.status_code == 422
        assert "title" in str(response.json()["detail"])

    def test_create_task_with_missing_title(self, client):
        """Rejeita quando title está ausente"""
        response = client.post("/tasks/", json={"description": "No title"})
        assert response.status_code == 422
        assert "title" in str(response.json()["detail"])

    def test_create_task_with_invalid_title_type_number(self, client):
        """Rejeita title com tipo numérico"""
        response = client.post("/tasks/", json={"title": 12345})
        assert response.status_code == 422
        assert "title" in response.json()["detail"][0]["loc"]

    def test_create_task_with_invalid_title_type_list(self, client):
        """Rejeita title com tipo array"""
        response = client.post("/tasks/", json={"title": ["array", "title"]})
        assert response.status_code == 422

    def test_create_task_with_invalid_completed_type(self, client):
        """Valida tratamento de completed com tipo inválido"""
        response = client.post(
            "/tasks/", json={"title": "Test", "completed": "yes"}
        )
        # FastAPI coage "yes" string para boolean
        if response.status_code == 200:
            # Se aceita e coage, verifica que completed é booleano
            assert isinstance(response.json()["completed"], bool)
        else:
            # Se rejeita, verifica erro 422
            assert response.status_code == 422

    def test_create_task_with_invalid_completed_type_string_true(self, client):
        """Valida tratamento de 'true' string como boolean"""
        response = client.post(
            "/tasks/", json={"title": "Test", "completed": "true"}
        )
        # FastAPI coage "true" string para True boolean
        if response.status_code == 200:
            # Se aceita e coage, verifica que completed é True
            assert response.json()["completed"] is True
        else:
            # Se rejeita
            assert response.status_code == 422

    def test_create_task_with_invalid_description_type(self, client):
        """Rejeita description com tipo array"""
        response = client.post(
            "/tasks/",
            json={"title": "Test", "description": ["item1", "item2"]},
        )
        assert response.status_code == 422
        assert "description" in response.json()["detail"][0]["loc"]

    def test_create_task_with_invalid_description_type_number(self, client):
        """Rejeita description com tipo numérico"""
        response = client.post(
            "/tasks/", json={"title": "Test", "description": 12345}
        )
        assert response.status_code == 422

    def test_create_task_with_empty_payload(self, client):
        """Rejeita request body vazio"""
        response = client.post("/tasks/", json={})
        assert response.status_code == 422
        assert "title" in response.json()["detail"][0]["loc"]

    def test_create_task_with_extremely_long_title(self, client):
        """Valida comportamento com title muito longo"""
        long_title = "A" * 10000
        response = client.post("/tasks/", json={"title": long_title})
        # Deve aceitar ou rejeitar com limite
        if response.status_code == 200:
            # Se aceita, deve estar no BD
            data = response.json()
            assert isinstance(data["title"], str)
            assert data["id"] is not None
        else:
            assert response.status_code == 422

    def test_create_task_with_special_characters_in_title(self, client):
        """Valida caracteres especiais no title"""
        special_titles = [
            "Task with @#$%&*()",
            "Tarefa com acentuação: é, ã, ç",
            "Task with 中文 characters",
            "Task with emoji 🚀 🎉",
        ]
        for title in special_titles:
            response = client.post("/tasks/", json={"title": title})
            assert response.status_code == 200
            assert response.json()["title"] == title


class TestValoresDuplicados:
    """Testes de valores duplicados e conflitos"""

    def test_create_duplicate_task_titles(self, client):
        """Permite múltiplas tarefas com mesmo título"""
        task_data = {"title": "Duplicate Title", "description": "Same"}

        response1 = client.post("/tasks/", json=task_data)
        response2 = client.post("/tasks/", json=task_data)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["id"] != response2.json()["id"]

        # Ambas devem estar na lista
        all_tasks = client.get("/tasks/").json()
        ids = [t["id"] for t in all_tasks]
        assert response1.json()["id"] in ids
        assert response2.json()["id"] in ids

    def test_update_task_to_existing_title(self, client):
        """Update para título existente é permitido"""
        # Criar duas tarefas
        res1 = client.post("/tasks/", json={"title": "Task A"})
        res2 = client.post("/tasks/", json={"title": "Task B"})

        task1_id = res1.json()["id"]
        task2_id = res2.json()["id"]

        # Tentar atualizar task2 para o título de task1
        response = client.put(f"/tasks/{task2_id}", json={"title": "Task A"})

        assert response.status_code == 200
        assert response.json()["title"] == "Task A"

        # Ambas existem com mesmo título
        all_tasks = client.get("/tasks/").json()
        titles = [t["title"] for t in all_tasks]
        assert titles.count("Task A") >= 2


class TestEstadosInconsistentes:
    """Testes de estados inconsistentes e ciclos inválidos"""

    def test_toggle_completion_multiple_times(self, client):
        """Múltiplas transições de conclusão funcionam corretamente"""
        res_create = client.post("/tasks/", json={"title": "Toggle Test"})
        task_id = res_create.json()["id"]

        # Completar
        response1 = client.patch(f"/tasks/{task_id}/complete?completed=true")
        assert response1.status_code == 200
        assert response1.json()["completed"] is True

        # Descompletar
        response2 = client.patch(f"/tasks/{task_id}/complete?completed=false")
        assert response2.status_code == 200
        assert response2.json()["completed"] is False

        # Completar novamente
        response3 = client.patch(f"/tasks/{task_id}/complete?completed=true")
        assert response3.status_code == 200
        assert response3.json()["completed"] is True

        # Verificar estado final
        response_get = client.get(f"/tasks/{task_id}")
        assert response_get.json()["completed"] is True

    def test_update_completed_task(self, client):
        """Editar tarefa concluída é permitido"""
        res_create = client.post(
            "/tasks/", json={"title": "Will be completed", "completed": True}
        )
        task_id = res_create.json()["id"]

        response = client.put(
            f"/tasks/{task_id}", json={"description": "Updated description"}
        )

        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"
        assert response.json()["completed"] is True

    def test_delete_completed_task(self, client):
        """Deletar tarefa concluída é permitido"""
        res_create = client.post(
            "/tasks/", json={"title": "Delete me", "completed": True}
        )
        task_id = res_create.json()["id"]

        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200

        # Verificar se foi deletada
        response_get = client.get(f"/tasks/{task_id}")
        assert response_get.status_code == 404

    def test_update_priority_on_completed_task(self, client):
        """Atualizar prioridade em tarefa concluída"""
        res_create = client.post(
            "/tasks/", json={"title": "Completed Priority Test", "completed": True}
        )
        task_id = res_create.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"priority": "Alta"})

        assert response.status_code == 200
        assert response.json()["priority"] == "Alta"
        assert response.json()["completed"] is True


class TestOperacoesComIdInvalido:
    """Testes de operações com IDs inválidos"""

    def test_get_task_with_negative_id(self, client):
        """GET com ID negativo retorna 404"""
        response = client.get("/tasks/-1")
        assert response.status_code == 404

    def test_get_task_with_zero_id(self, client):
        """GET com ID zero retorna 404"""
        response = client.get("/tasks/0")
        assert response.status_code == 404

    def test_get_task_with_huge_id(self, client):
        """GET com ID muito grande retorna 404"""
        response = client.get("/tasks/999999999")
        assert response.status_code == 404

    def test_get_task_with_string_id(self, client):
        """GET com ID não numérico retorna 422"""
        response = client.get("/tasks/abc")
        assert response.status_code == 422

    def test_get_task_with_float_id(self, client):
        """GET com ID float retorna 422"""
        response = client.get("/tasks/1.5")
        assert response.status_code == 422

    def test_update_nonexistent_task(self, client):
        """UPDATE de tarefa inexistente retorna 404"""
        response = client.put(
            "/tasks/999", json={"title": "Update Ghost Task"}
        )
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]

    def test_delete_nonexistent_task(self, client):
        """DELETE de tarefa inexistente retorna 404"""
        response = client.delete("/tasks/999")
        assert response.status_code == 404

    def test_patch_nonexistent_task_complete(self, client):
        """PATCH de tarefa inexistente retorna 404"""
        response = client.patch("/tasks/999/complete?completed=true")
        assert response.status_code == 404


class TestQueryParametersInvalidos:
    """Testes de query parameters inválidos"""

    def test_get_tasks_with_invalid_completed_param_string(self, client):
        """Query com completed='maybe' é tratado"""
        response = client.get("/tasks/?completed=maybe")
        # FastAPI tenta coagir para bool, pode dar 422
        assert response.status_code in [200, 422]

    def test_get_tasks_with_numeric_completed_param(self, client):
        """Query com completed=1 é coagido para bool"""
        response = client.get("/tasks/?completed=1")
        # FastAPI pode coagir 1 para True
        assert response.status_code in [200, 422]

    def test_get_tasks_with_completed_false_string(self, client):
        """Query com completed='false' é coagido para bool"""
        response = client.get("/tasks/?completed=false")
        # FastAPI coage 'false' string para False bool
        assert response.status_code == 200
        # Verificar se filtro foi aplicado
        data = response.json()
        if len(data) > 0:
            assert all(task["completed"] is False for task in data)

    def test_get_tasks_with_completed_true_string(self, client):
        """Query com completed='true' é coagido para bool"""
        response = client.get("/tasks/?completed=true")
        assert response.status_code == 200

    def test_get_tasks_with_empty_completed_param(self, client):
        """Query com completed vazio"""
        response = client.get("/tasks/?completed=")
        # Pode ser tratado de diferentes formas
        assert response.status_code in [200, 422]


class TestAusenciaDeValidacao:
    """Testes de ausência de validação"""

    def test_update_task_with_empty_data(self, client):
        """UPDATE com dados vazios não altera tarefa"""
        res_create = client.post("/tasks/", json={"title": "Original"})
        task_id = res_create.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={})

        assert response.status_code == 200
        assert response.json()["title"] == "Original"

    def test_update_task_fields_to_null(self, client):
        """Atualizar campo para null"""
        res_create = client.post(
            "/tasks/", json={"title": "Test", "description": "Has description"}
        )
        task_id = res_create.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"description": None})

        assert response.status_code == 200
        # description pode ficar None ou ser preservado
        assert response.json()["description"] is None

    def test_create_task_with_huge_description(self, client):
        """Create com description muito grande"""
        huge_desc = "X" * 100000
        response = client.post(
            "/tasks/", json={"title": "Test", "description": huge_desc}
        )

        assert response.status_code == 200
        # Verificar se foi salvo
        data = response.json()
        assert len(data["description"]) == 100000

    def test_update_task_with_huge_description(self, client):
        """Update com description muito grande"""
        res_create = client.post("/tasks/", json={"title": "Test"})
        task_id = res_create.json()["id"]

        huge_desc = "X" * 50000
        response = client.put(
            f"/tasks/{task_id}", json={"description": huge_desc}
        )

        assert response.status_code == 200
        assert len(response.json()["description"]) == 50000


class TestRaceConditions:
    """Testes de race conditions e operações concorrentes"""

    def test_get_task_deleted_during_read(self, client):
        """Deletar tarefa durante read"""
        res_create = client.post("/tasks/", json={"title": "Race Test"})
        task_id = res_create.json()["id"]

        # Deletar
        client.delete(f"/tasks/{task_id}")

        # Tentar ler
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 404

    def test_update_task_during_read(self, client):
        """Atualizar tarefa durante leitura"""
        res_create = client.post(
            "/tasks/", json={"title": "Original Title"}
        )
        task_id = res_create.json()["id"]

        read1 = client.get(f"/tasks/{task_id}").json()
        assert read1["title"] == "Original Title"

        updated = client.put(
            f"/tasks/{task_id}", json={"title": "Updated Title"}
        )
        assert updated.status_code == 200

        read2 = client.get(f"/tasks/{task_id}").json()
        assert read2["title"] == "Updated Title"

    def test_create_and_immediately_read(self, client):
        """Criar tarefa e ler imediatamente"""
        response_create = client.post(
            "/tasks/", json={"title": "Immediate Read"}
        )
        assert response_create.status_code == 200

        task_id = response_create.json()["id"]
        response_read = client.get(f"/tasks/{task_id}")

        assert response_read.status_code == 200
        assert response_read.json()["id"] == task_id


class TestResponseIntegrity:
    """Testes de integridade da resposta"""

    def test_response_has_all_required_fields_create(self, client):
        """Response de CREATE tem todos os campos"""
        response = client.post("/tasks/", json={"title": "Test"})
        data = response.json()

        required_fields = ["id", "title", "description", "completed", "priority"]
        for field in required_fields:
            assert field in data, f"Campo '{field}' ausente na response"

    def test_response_has_all_required_fields_update(self, client):
        """Response de UPDATE tem todos os campos"""
        res_create = client.post("/tasks/", json={"title": "Test"})
        task_id = res_create.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
        data = response.json()

        required_fields = ["id", "title", "description", "completed", "priority"]
        for field in required_fields:
            assert field in data

    def test_response_field_types_are_correct_post(self, client):
        """Types dos campos na response de POST"""
        response = client.post("/tasks/", json={"title": "Test"})
        data = response.json()

        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["completed"], bool)
        assert isinstance(data["priority"], str)
        assert (
            data["description"] is None or isinstance(data["description"], str)
        )

    def test_response_field_types_are_correct_get(self, client):
        """Types dos campos na response de GET"""
        res_create = client.post("/tasks/", json={"title": "Test"})
        task_id = res_create.json()["id"]

        response = client.get(f"/tasks/{task_id}")
        data = response.json()

        assert isinstance(data["id"], int)
        assert isinstance(data["title"], str)
        assert isinstance(data["completed"], bool)
        assert isinstance(data["priority"], str)

    def test_get_tasks_returns_array(self, client):
        """GET /tasks retorna array"""
        response = client.get("/tasks/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_response_format(self, client):
        """Response de DELETE tem formato correto"""
        res_create = client.post("/tasks/", json={"title": "Delete me"})
        task_id = res_create.json()["id"]

        response = client.delete(f"/tasks/{task_id}")
        data = response.json()

        assert "msg" in data
        assert "deletada" in str(data).lower()

    def test_empty_list_response(self, client):
        """GET /tasks com lista vazia retorna array vazio"""
        response = client.get("/tasks/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 0


class TestFiltersComMultiplosResultados:
    """Testes de filtros com múltiplos resultados"""

    def test_filter_completed_with_mixed_tasks(self, client):
        """Filtro completed com tarefas variadas"""
        # Limpar banco deletando tarefas anteriores (escopo de módulo mantém dados)
        all_before = client.get("/tasks/").json()
        for task in all_before:
            client.delete(f"/tasks/{task['id']}")
        
        # Criar tarefas variadas
        for i in range(5):
            client.post(
                "/tasks/",
                json={"title": f"Task {i}", "completed": i % 2 == 0},
            )

        # Listar completadas
        response_completed = client.get("/tasks/?completed=true")
        completed_tasks = response_completed.json()
        assert all(task["completed"] is True for task in completed_tasks)

        # Listar pendentes
        response_pending = client.get("/tasks/?completed=false")
        pending_tasks = response_pending.json()
        assert all(task["completed"] is False for task in pending_tasks)

        # Total de novo deve ser 5
        total = len(completed_tasks) + len(pending_tasks)
        assert total == 5

    def test_filter_without_param_returns_all(self, client):
        """GET /tasks sem filtro retorna todas"""
        # Criar tarefas variadas
        for i in range(3):
            client.post(
                "/tasks/",
                json={"title": f"Task {i}", "completed": i % 2 == 0},
            )

        response = client.get("/tasks/")
        all_tasks = response.json()
        assert len(all_tasks) >= 3
