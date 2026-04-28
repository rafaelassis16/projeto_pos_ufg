import pytest

def test_create_task(client):
    response = client.post(
        "/tasks/",
        json={"title": "API Task", "description": "urgente"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Task"
    assert data["priority"] == "Alta" # Advised Alta

def test_get_task_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada"

def test_delete_task_404(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada"

def test_create_task_invalid_payload(client):
    response = client.post(
        "/tasks/",
        json={"wrong_field": "test"} # Missing 'title'
    )
    assert response.status_code == 422 # Unprocessable Entity
