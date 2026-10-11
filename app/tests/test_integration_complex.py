"""
Testes de Integração Complexa - API de Gerenciamento de Tarefas

Cobertura:
- Fluxos CRUD completos
- Operações em lote
- Priority Advisor integration
- Transações e consistência
"""

import pytest


class TestFluxosCRUDCompletos:
    """Testes de fluxo CRUD completo end-to-end"""

    def test_full_crud_workflow(self, client):
        """Fluxo completo: Create → Read → Update → Delete"""
        # CREATE
        res_create = client.post(
            "/tasks/",
            json={"title": "CRUD Test", "description": "Initial"},
        )
        assert res_create.status_code == 200
        task_id = res_create.json()["id"]
        assert res_create.json()["description"] == "Initial"

        # READ individual
        res_read = client.get(f"/tasks/{task_id}")
        assert res_read.status_code == 200
        assert res_read.json()["title"] == "CRUD Test"
        assert res_read.json()["id"] == task_id

        # UPDATE
        res_update = client.put(
            f"/tasks/{task_id}", json={"description": "Updated"}
        )
        assert res_update.status_code == 200
        assert res_update.json()["description"] == "Updated"
        assert res_update.json()["title"] == "CRUD Test"

        # LIST - verificar que está lá
        res_list = client.get("/tasks/")
        assert res_list.status_code == 200
        task_ids = [t["id"] for t in res_list.json()]
        assert task_id in task_ids

        # DELETE
        res_delete = client.delete(f"/tasks/{task_id}")
        assert res_delete.status_code == 200
        assert "deletada" in res_delete.json()["msg"].lower()

        # Verify deleted
        res_verify = client.get(f"/tasks/{task_id}")
        assert res_verify.status_code == 404

    def test_create_read_complete_workflow(self, client):
        """Fluxo: Create → Read → Complete → Read novamente"""
        # CREATE
        res_create = client.post(
            "/tasks/", json={"title": "Complete Workflow", "completed": False}
        )
        assert res_create.status_code == 200
        task = res_create.json()
        task_id = task["id"]
        assert task["completed"] is False

        # READ
        res_read1 = client.get(f"/tasks/{task_id}")
        assert res_read1.json()["completed"] is False

        # COMPLETE
        res_patch = client.patch(
            f"/tasks/{task_id}/complete?completed=true"
        )
        assert res_patch.status_code == 200
        assert res_patch.json()["completed"] is True

        # READ again
        res_read2 = client.get(f"/tasks/{task_id}")
        assert res_read2.json()["completed"] is True

    def test_create_update_multiple_times(self, client):
        """Criar e atualizar tarefa múltiplas vezes"""
        # CREATE
        res_create = client.post("/tasks/", json={"title": "Initial Title"})
        task_id = res_create.json()["id"]

        # UPDATE 1
        res_update1 = client.put(
            f"/tasks/{task_id}", json={"title": "Updated Title 1"}
        )
        assert res_update1.status_code == 200
        assert res_update1.json()["title"] == "Updated Title 1"

        # UPDATE 2
        res_update2 = client.put(
            f"/tasks/{task_id}",
            json={"description": "Added description"},
        )
        assert res_update2.status_code == 200
        assert res_update2.json()["title"] == "Updated Title 1"
        assert res_update2.json()["description"] == "Added description"

        # UPDATE 3
        res_update3 = client.put(
            f"/tasks/{task_id}", json={"priority": "Alta"}
        )
        assert res_update3.status_code == 200
        assert res_update3.json()["priority"] == "Alta"

        # Verificar estado final
        res_final = client.get(f"/tasks/{task_id}")
        final_task = res_final.json()
        assert final_task["title"] == "Updated Title 1"
        assert final_task["description"] == "Added description"
        assert final_task["priority"] == "Alta"


class TestOperacoesEmLote:
    """Testes de operações em lote"""

    def test_bulk_create_and_filter(self, client):
        """Criar múltiplas tarefas e filtrar"""
        # Criar 10 tarefas variadas
        created_ids = []
        for i in range(10):
            res = client.post(
                "/tasks/",
                json={
                    "title": f"Task {i}",
                    "completed": i % 3 == 0,
                },
            )
            assert res.status_code == 200
            created_ids.append(res.json()["id"])

        # Filtrar completadas
        res_completed = client.get("/tasks/?completed=true")
        completed_tasks = res_completed.json()
        # Tarefas 0, 3, 6, 9 estão completadas
        assert len(completed_tasks) >= 4
        assert all(t["completed"] is True for t in completed_tasks)

        # Filtrar pendentes
        res_pending = client.get("/tasks/?completed=false")
        pending_tasks = res_pending.json()
        # Tarefas 1, 2, 4, 5, 7, 8 estão pendentes
        assert len(pending_tasks) >= 6
        assert all(t["completed"] is False for t in pending_tasks)

    def test_bulk_complete_all_pending(self, client):
        """Completar todas as tarefas pendentes em operações"""
        # Criar tarefas variadas
        for i in range(5):
            client.post(
                "/tasks/",
                json={"title": f"Task {i}", "completed": i % 2 == 0},
            )

        # Listar pendentes
        res_pending = client.get("/tasks/?completed=false")
        pending_tasks = res_pending.json()
        initial_pending_count = len(pending_tasks)

        # Completar todos pendentes
        for task in pending_tasks:
            response = client.patch(
                f"/tasks/{task['id']}/complete?completed=true"
            )
            assert response.status_code == 200
            assert response.json()["completed"] is True

        # Verificar nenhum pendente restante
        res_final = client.get("/tasks/?completed=false")
        final_pending_tasks = res_final.json()
        assert len(final_pending_tasks) == 0

    def test_bulk_delete_and_verify_removal(self, client):
        """Deletar múltiplas tarefas e verificar remoção"""
        # Criar 5 tarefas
        task_ids = []
        for i in range(5):
            res = client.post("/tasks/", json={"title": f"Delete Task {i}"})
            task_ids.append(res.json()["id"])

        # Verificar que estão lá
        res_before = client.get("/tasks/")
        all_ids_before = [t["id"] for t in res_before.json()]
        for task_id in task_ids:
            assert task_id in all_ids_before

        # Deletar todos
        for task_id in task_ids:
            response = client.delete(f"/tasks/{task_id}")
            assert response.status_code == 200

        # Verificar que foram removidos
        res_after = client.get("/tasks/")
        all_ids_after = [t["id"] for t in res_after.json()]
        for task_id in task_ids:
            assert task_id not in all_ids_after

    def test_bulk_update_titles(self, client):
        """Atualizar títulos de múltiplas tarefas"""
        # Criar tarefas
        task_ids = []
        for i in range(3):
            res = client.post("/tasks/", json={"title": f"Original {i}"})
            task_ids.append(res.json()["id"])

        # Atualizar todos os títulos
        for i, task_id in enumerate(task_ids):
            response = client.put(
                f"/tasks/{task_id}", json={"title": f"Updated {i}"}
            )
            assert response.status_code == 200
            assert response.json()["title"] == f"Updated {i}"

        # Verificar alterações
        for i, task_id in enumerate(task_ids):
            res = client.get(f"/tasks/{task_id}")
            assert res.json()["title"] == f"Updated {i}"


class TestPriorityAdvisorIntegration:
    """Testes de integração com o Priority Advisor"""

    def test_priority_detection_high_keywords(self, client):
        """Priority automática para keywords de alta prioridade"""
        keywords_alta = ["urgente", "crítico", "imediato"]

        for keyword in keywords_alta:
            response = client.post(
                "/tasks/", json={"title": f"Task {keyword}"}
            )
            assert response.status_code == 200
            assert response.json()["priority"] == "Alta"

    def test_priority_detection_medium_keywords(self, client):
        """Priority automática para keywords de média prioridade"""
        keywords_media = ["importante", "breve"]

        for keyword in keywords_media:
            response = client.post(
                "/tasks/", json={"title": f"Task {keyword}"}
            )
            assert response.status_code == 200
            assert response.json()["priority"] == "Média"

    def test_priority_detection_default_low(self, client):
        """Priority padrão é Baixa para keywords neutras"""
        response = client.post(
            "/tasks/", json={"title": "Regular task"}
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "Baixa"

    def test_priority_detection_in_description(self, client):
        """Priority detectada também pela description"""
        response = client.post(
            "/tasks/",
            json={"title": "Task", "description": "Conteúdo urgente"},
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "Alta"

    def test_explicit_priority_overrides_detection(self, client):
        """Priority explícita é sobrescrita pelo PriorityAdvisor se == 'Baixa'"""
        response = client.post(
            "/tasks/",
            json={
                "title": "Urgente task",
                "priority": "Baixa",
            },
        )
        assert response.status_code == 200
        # Comportamento atual: priority "Baixa" dispara advisor
        # O advisor detecta "urgente" no title e retorna "Alta"
        assert response.json()["priority"] == "Alta"

    def test_explicit_medium_priority(self, client):
        """Priority explícita Média"""
        response = client.post(
            "/tasks/",
            json={
                "title": "Regular task",
                "priority": "Média",
            },
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "Média"

    def test_null_priority_triggers_detection(self, client):
        """Priority None dispara detecção automática"""
        response = client.post(
            "/tasks/",
            json={
                "title": "Urgente task",
                "priority": None,
            },
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "Alta"

    def test_priority_update_preserves_automatic_if_not_changed(self, client):
        """Update sem alterar priority a mantém"""
        res_create = client.post(
            "/tasks/",
            json={"title": "Urgente task"},
        )
        original_priority = res_create.json()["priority"]

        res_update = client.put(
            f"/tasks/{res_create.json()['id']}", json={"description": "New desc"}
        )
        assert res_update.json()["priority"] == original_priority

    def test_priority_update_with_new_value(self, client):
        """Update pode alterar priority"""
        res_create = client.post(
            "/tasks/",
            json={"title": "Urgente task"},
        )
        task_id = res_create.json()["id"]

        res_update = client.put(
            f"/tasks/{task_id}", json={"priority": "Baixa"}
        )
        assert res_update.json()["priority"] == "Baixa"


class TestConsistenciaTransacional:
    """Testes de consistência transacional"""

    def test_sequential_operations_maintain_consistency(self, client):
        """Operações sequenciais mantêm consistência"""
        # CREATE
        res_create = client.post(
            "/tasks/",
            json={"title": "Consistency Test", "completed": False},
        )
        task_id = res_create.json()["id"]

        # UPDATE
        client.put(f"/tasks/{task_id}", json={"description": "Updated"})

        # COMPLETE
        client.patch(f"/tasks/{task_id}/complete?completed=true")

        # Verificar estado final
        res_final = client.get(f"/tasks/{task_id}")
        final_task = res_final.json()
        assert final_task["title"] == "Consistency Test"
        assert final_task["description"] == "Updated"
        assert final_task["completed"] is True

    def test_list_reflects_all_operations(self, client):
        """Lista reflete todas as operações"""
        # Criar tarefas
        res1 = client.post("/tasks/", json={"title": "Task 1"})
        res2 = client.post("/tasks/", json={"title": "Task 2"})
        task1_id = res1.json()["id"]
        task2_id = res2.json()["id"]

        # Atualizar uma
        client.put(f"/tasks/{task1_id}", json={"title": "Updated Task 1"})

        # Completar outra
        client.patch(f"/tasks/{task2_id}/complete?completed=true")

        # Verificar lista
        res_list = client.get("/tasks/")
        all_tasks = {t["id"]: t for t in res_list.json()}

        assert all_tasks[task1_id]["title"] == "Updated Task 1"
        assert all_tasks[task2_id]["completed"] is True


class TestOperacoesComMultiplosEstados:
    """Testes com múltiplos estados simultâneos"""

    def test_mixed_completed_and_pending_operations(self, client):
        """Operações mistas em tarefas completadas e pendentes"""
        # Criar 4 tarefas: 2 completadas, 2 pendentes
        res_c1 = client.post(
            "/tasks/",
            json={"title": "Completed 1", "completed": True},
        )
        res_c2 = client.post(
            "/tasks/",
            json={"title": "Completed 2", "completed": True},
        )
        res_p1 = client.post(
            "/tasks/",
            json={"title": "Pending 1", "completed": False},
        )
        res_p2 = client.post(
            "/tasks/",
            json={"title": "Pending 2", "completed": False},
        )

        # IDs
        c1_id = res_c1.json()["id"]
        c2_id = res_c2.json()["id"]
        p1_id = res_p1.json()["id"]
        p2_id = res_p2.json()["id"]

        # Atualizar completadas
        client.put(f"/tasks/{c1_id}", json={"description": "Updated completed 1"})
        client.put(f"/tasks/{c2_id}", json={"description": "Updated completed 2"})

        # Completar pendentes
        client.patch(f"/tasks/{p1_id}/complete?completed=true")
        # Deixar p2 pendente mas atualizar

        client.put(f"/tasks/{p2_id}", json={"description": "Updated pending"})

        # Verificar filtros
        res_completed = client.get("/tasks/?completed=true")
        completed = [t["id"] for t in res_completed.json()]
        assert c1_id in completed
        assert c2_id in completed
        assert p1_id in completed  # Agora está completa
        assert p2_id not in completed

        res_pending = client.get("/tasks/?completed=false")
        pending = [t["id"] for t in res_pending.json()]
        assert p2_id in pending
        assert c1_id not in pending

    def test_mixed_priority_levels_operations(self, client):
        """Operações com múltiplos níveis de prioridade"""
        # Criar tarefas com diferentes prioridades
        res_high = client.post(
            "/tasks/", json={"title": "Urgente task", "priority": "Alta"}
        )
        res_med = client.post(
            "/tasks/", json={"title": "Important task", "priority": "Média"}
        )
        res_low = client.post(
            "/tasks/", json={"title": "Regular task", "priority": "Baixa"}
        )

        high_id = res_high.json()["id"]
        med_id = res_med.json()["id"]
        low_id = res_low.json()["id"]

        # Atualizar prioridades
        client.put(f"/tasks/{high_id}", json={"priority": "Baixa"})
        client.put(f"/tasks/{low_id}", json={"priority": "Alta"})

        # Verificar
        res_final = client.get("/tasks/")
        tasks = {t["id"]: t for t in res_final.json()}

        assert tasks[high_id]["priority"] == "Baixa"
        assert tasks[med_id]["priority"] == "Média"
        assert tasks[low_id]["priority"] == "Alta"


class TestLimitesDeRecurso:
    """Testes de limites e performance"""

    def test_create_many_tasks(self, client):
        """Criar grande número de tarefas"""
        count = 100
        for i in range(count):
            response = client.post(
                "/tasks/", json={"title": f"Task {i}"}
            )
            assert response.status_code == 200

        # Verificar contagem na lista
        res_list = client.get("/tasks/")
        assert len(res_list.json()) >= count

    def test_filter_with_many_results(self, client):
        """Filtrar com muitos resultados"""
        # Criar muitas tarefas
        for i in range(50):
            client.post(
                "/tasks/",
                json={"title": f"Task {i}", "completed": False},
            )

        # Filtrar pendentes
        res = client.get("/tasks/?completed=false")
        assert res.status_code == 200
        results = res.json()
        assert len(results) >= 50
        assert all(t["completed"] is False for t in results)

    def test_list_performance_with_many_tasks(self, client):
        """Performance de listagem com muitas tarefas"""
        # Criar tarefas
        for i in range(100):
            client.post("/tasks/", json={"title": f"Task {i}"})

        # Listar várias vezes
        for _ in range(5):
            res = client.get("/tasks/")
            assert res.status_code == 200
            assert len(res.json()) >= 100
