from app.services.priority_advisor import PriorityAdvisor

def test_priority_high():
    assert PriorityAdvisor.advise("Comprar leite urgente") == "Alta"
    assert PriorityAdvisor.advise("Crítico: consertar bug") == "Alta"

def test_priority_medium():
    assert PriorityAdvisor.advise("Tarefa importante") == "Média"
    assert PriorityAdvisor.advise("Resolver em breve") == "Média"

def test_priority_low():
    assert PriorityAdvisor.advise("Lavar louça") == "Baixa"
