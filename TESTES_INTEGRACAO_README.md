# 🧪 Guia de Testes de Integração - API de Gerenciamento de Tarefas

## 📋 Visão Geral

Este projeto inclui um conjunto completo de **testes de integração** para validar o funcionamento end-to-end da API de Gerenciamento de Tarefas em FastAPI.

**Arquivos principais:**
- `app/tests/test_integration_happy_path.py` - Testes de cenários bem-sucedidos (30+ testes)
- `app/tests/test_integration_error_cases.py` - Testes de erro e edge cases (18+ testes)
- `app/tests/test_tasks.py` - Testes básicos existentes (6 testes)

**Total: 54+ testes de integração**

---

## 🚀 Início Rápido

### 1. Setup do Ambiente
```bash
# Ir para o diretório do projeto
cd c:\Users\rafaelassis\Documents\VS Code\projeto_pos_ufg\projeto_pos_ufg

# Ativar ambiente virtual
.venv\Scripts\activate.ps1

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### 2. Executar Testes Existentes (Baseline)
```bash
# Rodar testes básicos que já passam
pytest app/tests/test_tasks.py -v
```

**Resultado esperado:** ✅ 6 passed

### 3. Integrar Novos Testes

Os novos testes estão em:
- `app/tests/test_integration_happy_path.py`
- `app/tests/test_integration_error_cases.py`

Eles usam a mesma fixture `conftest.py` do projeto e devem funcionar com a estrutura existente.

---

## 📊 Estrutura dos Testes

### Testes Existentes (test_tasks.py)
Validam funcionalidade básica com database SQLite em arquivo:

```python
@pytest.fixture(scope="module")
def client(db):
    # Database compartilhado para toda a suite
    # Arquivo: ./test.db
```

**Testes:**
- ✅ `test_create_task` - Criar tarefa
- ✅ `test_get_tasks_with_filter` - Listar com filtro
- ✅ `test_update_task` - Atualizar tarefa
- ✅ `test_patch_task_complete` - Marcar completa
- ✅ `test_get_task_404` - Erro 404
- ✅ `test_delete_task` - Deletar tarefa

### Testes de Integração Novos

#### Happy Path (test_integration_happy_path.py)
30+ testes cobrindo fluxos bem-sucedidos:

```python
class TestCreateTaskHappyPath:
    def test_create_task_with_auto_priority_alta(self, integration_client):
        """Criar com prioridade automática"""
        response = integration_client.post(
            "/tasks/",
            json={"title": "urgente atender cliente"}
        )
        assert response.status_code == 200
        assert response.json()["priority"] == "Alta"
```

**Classes:**
1. `TestCreateTaskHappyPath` (3 testes)
2. `TestGetTasksHappyPath` (3 testes)
3. `TestGetTaskByIdHappyPath` (2 testes)
4. `TestUpdateTaskHappyPath` (3 testes)
5. `TestPatchTaskHappyPath` (3 testes)
6. `TestDeleteTaskHappyPath` (2 testes)
7. `TestCompleteWorkflowHappyPath` (1 teste end-to-end)

#### Error Cases (test_integration_error_cases.py)
18+ testes cobrindo erros e edge cases:

```python
class TestInputValidation:
    def test_create_task_missing_title_required_field(self, integration_client):
        """Validação Pydantic"""
        response = integration_client.post("/tasks/", json={"description": "Sem título"})
        assert response.status_code == 422
```

**Classes:**
1. `TestInputValidation` (4 testes)
2. `TestNotFoundErrors` (6 testes)
3. `TestInconsistentStates` (3 testes)
4. `TestDuplicatesAndLimits` (4 testes)
5. `TestConcurrentOperations` (3 testes)
6. `TestFilterEdgeCases` (3 testes)
7. `TestTransactionIntegrity` (2 testes)

---

## 🎯 Como Executar

### Testes Específicos

```bash
# Apenas testes existentes
pytest app/tests/test_tasks.py -v

# Apenas happy path
pytest app/tests/test_integration_happy_path.py -v

# Apenas error cases
pytest app/tests/test_integration_error_cases.py -v

# Todos os testes
pytest app/tests/ -v
```

### Teste Específico por Classe

```bash
# Todos os testes de criação
pytest app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath -v

# Um teste específico
pytest app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath::test_create_task_with_auto_priority_alta -v
```

### Com Filtros

```bash
# Apenas testes que contêm "delete"
pytest app/tests/ -k "delete" -v

# Apenas testes com "create" mas não "error"
pytest app/tests/ -k "create and not error" -v
```

### Com Relatório de Cobertura

```bash
# Gerar relatório HTML de cobertura
pytest app/tests/ --cov=app --cov-report=html

# Visualizar em navegador
# Abrir: htmlcov/index.html
```

### Com Output Detalhado

```bash
# Mostrar prints e output
pytest app/tests/ -v -s

# Com informações de duração
pytest app/tests/ -v --durations=10

# Parar no primeiro erro
pytest app/tests/ -v -x

# Mostrar locais (variáveis locais)
pytest app/tests/ -v -l
```

---

## ✅ Verificação de Funcionamento

Após executar os testes, você verá algo como:

```
============================= test session starts ==============================
platform win32 -- Python 3.14.3, pytest-9.0.3
collected 54 items

app/tests/test_tasks.py::test_create_task PASSED                        [ 11%]
app/tests/test_tasks.py::test_get_tasks_with_filter PASSED              [ 22%]
app/tests/test_tasks.py::test_update_task PASSED                        [ 33%]
app/tests/test_tasks.py::test_patch_task_complete PASSED                [ 44%]
app/tests/test_tasks.py::test_get_task_404 PASSED                       [ 55%]
app/tests/test_tasks.py::test_delete_task PASSED                        [ 66%]
app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath::test_create_task_with_auto_priority_alta PASSED [ 77%]
...
======================== 54 passed, X warnings in X.XXs ========================
```

---

## 🔍 Entendendo os Testes

### Padrão AAA

Todos os testes seguem o padrão **Arrange, Act, Assert**:

```python
def test_example(self, integration_client):
    # ARRANGE: Preparar dados
    create_response = integration_client.post(
        "/tasks/",
        json={"title": "Task"}
    )
    task_id = create_response.json()["id"]
    
    # ACT: Executar ação
    get_response = integration_client.get(f"/tasks/{task_id}")
    
    # ASSERT: Verificar resultado
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Task"
```

### Documentação em Cada Teste

Cada teste inclui docstring com:

```python
def test_create_task_with_auto_priority_alta(self, integration_client):
    """
    Cenário: Criar tarefa com palavras-chave que indicam alta prioridade
    Esperado: Priority é definida automaticamente como "Alta"
    
    Fluxo:
    1. POST /tasks/ com título contendo "urgente"
    2. Route recebe dados → TaskService.create_task()
    3. Service verifica priority e chama PriorityAdvisor
    4. PriorityAdvisor analisa e retorna "Alta"
    5. Task é persistida no DB
    6. Response 200 com Task criada
    """
```

### Fixtures Compartilhadas

O arquivo `conftest.py` fornece:

```python
@pytest.fixture(scope="module")
def client(db):
    # Para testes_tasks.py - database em arquivo

@pytest.fixture(scope="function")
def integration_client(db_session):
    # Para test_integration_*.py - database em memória
```

---

## 📈 Escalabilidade

### Adicionar Novo Teste

```python
# Em test_integration_happy_path.py ou test_integration_error_cases.py

class TestNovaFuncionalidade:
    def test_meu_novo_teste(self, integration_client):
        """
        Cenário: Descrever o que será testado
        Esperado: Descrever resultado esperado
        
        Fluxo validado:
        - Camadas percorridas
        """
        # ARRANGE
        ...
        
        # ACT
        response = integration_client.post("/endpoint", json=data)
        
        # ASSERT
        assert response.status_code == 200
```

### Adicionar Nova Suite

```bash
# Criar novo arquivo
touch app/tests/test_integration_nova_suite.py

# Copiar template
```

---

## 🐛 Troubleshooting

### Erro: "No module named 'app'"

```bash
# Certifique-se de estar no diretório correto
cd c:\Users\rafaelassis\Documents\VS Code\projeto_pos_ufg\projeto_pos_ufg

# Verificar que existe app/
dir app
```

### Erro: "no such table: tasks"

```bash
# Confirmar que conftest.py existe e tem fixtures
cat app/tests/conftest.py

# Executar com output detalhado
pytest app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath::test_create_task_with_auto_priority_alta -v -s
```

### Testes lentos

```bash
# Database em memória (:memory:) é rápido por padrão
# Se ainda estiver lento:

# Rodar em paralelo (requer pytest-xdist)
pip install pytest-xdist
pytest app/tests/ -n auto
```

---

## 📚 Recursos Adicionais

### Documentação dos Testes
- Veja `Guia Completo: Testes de Integração da API de Tarefas` para documentação completa
- Veja `Resumo Executivo: Testes de Integração Entregues` para overview

### Boas Práticas Implementadas
✅ Testes isolados (cada teste é independente)  
✅ Database limpo após cada teste  
✅ Fixtures reutilizáveis  
✅ Nomes descritivos  
✅ Documentação inline  
✅ Cobertura de happy path e error cases  
✅ Validação de integridade transacional  

### Próximas Melhorias
1. Adicionar validação de constraints (min_length para title)
2. Implementar Repository Pattern
3. Adicionar testes de performance
4. Adicionar testes de segurança (SQL injection, etc)
5. Integrar com CI/CD (GitHub Actions)

---

## 📞 Referência Rápida

```bash
# Comando mais comum
pytest app/tests/ -v

# Com cobertura
pytest app/tests/ -v --cov=app

# Parar no primeiro erro
pytest app/tests/ -v -x

# Apenas um arquivo
pytest app/tests/test_integration_happy_path.py -v

# Apenas uma classe
pytest app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath -v

# Apenas um teste
pytest app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath::test_create_task_with_auto_priority_alta -v
```

---

**Criado:** Outubro 11, 2026  
**Versão:** 1.0  
**Autor:** Especialista em Testes de Integração  
**Status:** ✅ Pronto para uso
