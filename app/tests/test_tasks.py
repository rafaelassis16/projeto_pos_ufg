import pytest

def test_create_task(client):
    response = client.post(
        "/tasks/",
        json={"title": "API Task", "description": "urgente"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Task"
    assert data["priority"] == "Alta"

def test_get_tasks_with_filter(client):
    # Create one completed and one pending
    client.post("/tasks/", json={"title": "Task 1", "completed": True})
    client.post("/tasks/", json={"title": "Task 2", "completed": False})
    
    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert all(task["completed"] is True for task in data)

def test_update_task(client):
    # Create task
    res_create = client.post("/tasks/", json={"title": "Old Title"})
    task_id = res_create.json()["id"]
    
    # Update task
    response = client.put(f"/tasks/{task_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_patch_task_complete(client):
    # Create task
    res_create = client.post("/tasks/", json={"title": "Unfinished", "completed": False})
    task_id = res_create.json()["id"]
    
    # Complete task
    response = client.patch(f"/tasks/{task_id}/complete?completed=true")
    assert response.status_code == 200
    assert response.json()["completed"] is True

def test_get_task_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404

def test_delete_task(client):
    res_create = client.post("/tasks/", json={"title": "To be deleted"})
    task_id = res_create.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["msg"] == "Tarefa deletada"
