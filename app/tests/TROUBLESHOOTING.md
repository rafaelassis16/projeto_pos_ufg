# Guia de Troubleshooting - Testes de Integração

## 🔧 Problemas Comuns e Soluções

### 1. ModuleNotFoundError: No module named 'sqlalchemy'

**Erro:**
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Solução:**
```bash
# Ativar virtual environment
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | findstr sqlalchemy
```

---

### 2. FAILED: conftest.py Error on Import

**Erro:**
```
ImportError while loading conftest 'C:\Users\...\conftest.py'
```

**Solução:**
1. Verificar se o venv está ativado
2. Verificar se requirements.txt foi instalado
3. Limpar cache do pytest:
```bash
pytest --cache-clear
rm -Force .pytest_cache
```

---

### 3. Tests Pass Individually but Fail Together

**Problema:** Testes funcionam isolados mas falham quando rodados juntos

**Causa:** Fixture `scope="module"` compartilha estado de BD entre testes

**Solução:**
- Adicionar setup/teardown em testes que modificam estado
- Ou usar `scope="function"` na fixture

Exemplo:
```python
def test_filter_completed_with_mixed_tasks(client):
    # Limpar banco primeiro
    all_before = client.get("/tasks/").json()
    for task in all_before:
        client.delete(f"/tasks/{task['id']}")
    
    # Depois criar tarefas do teste
    for i in range(5):
        client.post("/tasks/", json={"title": f"Task {i}"})
```

---

### 4. Port Already in Use

**Erro:**
```
Address already in use
Port 8000/5000 already in use
```

**Solução:**
```bash
# Windows - encontrar processo
netstat -ano | findstr :8000

# Matar processo
taskkill /PID <PID> /F

# Ou usar porta diferente
pytest --env=test -p no:cacheprovider
```

---

### 5. Database Lock (SQLite)

**Erro:**
```
database is locked
sqlite3.OperationalError: database is locked
```

**Solução:**
```bash
# Remover arquivo de BD de teste
rm test.db
rm test.db-journal

# Ou usar in-memory database
# No conftest.py:
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
```

---

### 6. Flaky Tests (Passam e Falham Aleatoriamente)

**Problema:** Testes funcionam às vezes e falham outras

**Causa Comum:** Transações não finalizado ou estado compartilhado

**Solução:**

```python
# Sempre fazer rollback após teste
@pytest.fixture
def db(engine):
    connection = engine.raw_connection()
    transaction = connection.begin()
    
    yield connection
    
    # Cleanup
    transaction.rollback()
    connection.close()
```

---

### 7. Response is 500 (Server Error)

**Erro:**
```
assert response.status_code == 200
AssertionError: assert 500 == 200
```

**Solução:**
1. Ver os detalhes do erro:
```python
def test_example(client):
    response = client.post("/tasks/", json={"title": ""})
    if response.status_code != 200:
        print(response.text)  # Ver erro completo
        assert False, response.text
```

2. Usar `-s` flag para ver prints:
```bash
pytest app/tests/test_error_cases.py -v -s
```

3. Adicionar logging:
```bash
pytest app/tests/ -v --log-cli-level=DEBUG
```

---

### 8. TypeError: Cannot Instantiate client

**Erro:**
```
TypeError: Cannot instantiate <class 'app.tests.conftest.TestingSessionLocal'>
```

**Causa:** Fixture `client` depende de `db` que não está sendo passado

**Solução:** Verificar ordem de parâmetros:
```python
# ✅ CORRETO
def test_example(client):  # client depende de db automaticamente
    pass

# ❌ ERRADO
def test_example(db, client):  # db depois de client
    pass
```

---

### 9. AssertionError: assert [] == [...]

**Problema:** Lista vazia quando deveria ter resultados

**Causa:** Dados não foram criados ou foram deletados

**Solução:**
```python
def test_get_tasks(client):
    # 1. Criar dado
    res_create = client.post("/tasks/", json={"title": "Test"})
    assert res_create.status_code == 200
    
    # 2. Verificar que foi criado
    task_id = res_create.json()["id"]
    
    # 3. Depois listar
    res_list = client.get("/tasks/")
    ids = [t["id"] for t in res_list.json()]
    assert task_id in ids
```

---

### 10. Import Errors - Circular Dependencies

**Erro:**
```
ImportError: cannot import name 'Task' from 'app.models.task'
```

**Causa:** Arquivo vazio ou importação circular

**Solução:**
```bash
# Verificar arquivo
Get-Content app/models/task.py

# Se vazio, verificar task_model.py
Get-Content app/models/task_model.py

# Importar correto
from app.models.task_model import Task
```

---

## 🐛 Debugging de Testes

### Usar -vv para Verbose Output
```bash
pytest app/tests/test_error_cases.py::TestValidacaoDadosInvalidos -vv
```

### Usar -x para Parar no Primeiro Erro
```bash
pytest app/tests/ -x  # Para na primeira falha
```

### Usar --pdb para Debug Interativo
```bash
pytest app/tests/ --pdb  # Abre debugger na falha
```

### Usar -s para Ver Prints
```bash
pytest app/tests/ -v -s  # Mostra todos os prints

# Adicionar print no teste:
def test_example(client):
    response = client.get("/tasks/")
    print(response.json())  # Será mostrado com -s
```

### Usar --capture=no para Desabilitar Captura
```bash
pytest app/tests/ --capture=no
```

---

## 📊 Monitorar Performance

### Encontrar Testes Lentos
```bash
pytest app/tests/ -v --durations=10
```

### Profiling de Teste
```bash
pytest app/tests/ --profile
```

### Usar Timer
```python
import time

def test_performance(client):
    start = time.time()
    
    # Criar 1000 tarefas
    for i in range(1000):
        client.post("/tasks/", json={"title": f"Task {i}"})
    
    duration = time.time() - start
    print(f"Criado 1000 tarefas em {duration:.2f}s")
    assert duration < 10, "Muito lento!"
```

---

## 🔐 Verificar Isolamento de Testes

### Garantir que Testes são Independentes
```bash
# Rodar testes em ordem aleatória
pytest app/tests/ --random-order

# Rodar teste específico múltiplas vezes
pytest app/tests/test_error_cases.py::TestValidacaoDadosInvalidos::test_create_task_with_null_title -v --count=10
```

---

## 📋 Checklist de Qualidade

- [ ] Todos os imports resolvidos
- [ ] Virtual environment ativado
- [ ] Dependencies instaladas
- [ ] Database limpado antes dos testes
- [ ] Fixtures configuradas corretamente
- [ ] Nenhum estado compartilhado entre testes
- [ ] Testes executam em ordem aleatória sem falhas
- [ ] Performance aceitável (<15s total)

---

## 🔗 Referências para Debugging

### FastAPI Testing
- https://fastapi.tiangolo.com/advanced/testing-dependencies/
- https://fastapi.tiangolo.com/advanced/testing-events/

### Pytest
- https://docs.pytest.org/en/latest/debugging.html
- https://docs.pytest.org/en/latest/fixture.html

### SQLAlchemy
- https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- https://docs.sqlalchemy.org/en/20/orm/transactions.html

### Troubleshooting Geral
- Verificar `.venv` está ativado: `Get-Command python`
- Verificar versão: `python --version`
- Verificar pip packages: `pip list`
- Verificar pytest plugins: `pytest --co`

---

## 💡 Dicas Profissionais

### 1. Usar Fixtures para Setup Comum
```python
@pytest.fixture
def task_data():
    return {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "priority": "Média"
    }

def test_create_task(client, task_data):
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 200
```

### 2. Usar Parametrize para Múltiplas Variações
```python
@pytest.mark.parametrize("title,expected_priority", [
    ("Urgente task", "Alta"),
    ("Importante task", "Média"),
    ("Regular task", "Baixa"),
])
def test_priority_detection(client, title, expected_priority):
    response = client.post("/tasks/", json={"title": title})
    assert response.json()["priority"] == expected_priority
```

### 3. Usar Markers para Organizar Testes
```python
@pytest.mark.slow
def test_create_many_tasks(client):
    for i in range(100):
        client.post("/tasks/", json={"title": f"Task {i}"})

# Executar apenas testes rápidos:
# pytest -v -m "not slow"
```

### 4. Usar Fixtures com Escopo Apropriado
```python
@pytest.fixture(scope="session")
def app_setup():
    # Executado UMA VEZ por sessão
    return setup_app()

@pytest.fixture(scope="function")
def clean_db(db):
    # Executado ANTES de cada teste
    yield db
    # DEPOIS de cada teste
    db.query(Task).delete()
    db.commit()
```

---

## ⚡ Performance Tips

### Usar In-Memory Database para Testes
```python
# conftest.py
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # Mais rápido que arquivo
```

### Usar Transactions para Cleanup
```python
@pytest.fixture
def db_transaction():
    connection = engine.raw_connection()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    transaction.rollback()  # Mais rápido que delete
```

### Batch Operations
```python
def test_bulk_create(client):
    # Criar várias em seqüência
    tasks = [{"title": f"Task {i}"} for i in range(100)]
    
    # Mais rápido que for loop
    for task in tasks:
        client.post("/tasks/", json=task)
```

---

## 🆘 Quando Tudo Falha

### Nuclear Option: Clean Install
```bash
# 1. Remover venv
Remove-Item .venv -Recurse -Force

# 2. Remover BD de teste
Remove-Item test.db -Force
Remove-Item test.db-journal -Force

# 3. Criar novo venv
python -m venv .venv

# 4. Ativar
.\.venv\Scripts\Activate.ps1

# 5. Reinstalar
pip install -r requirements.txt

# 6. Rodar testes
pytest app/tests/ -v
```

### Relatar Problema
Se nenhuma solução funcionar:
1. Coletar informações:
```bash
python --version
pip list > pip_list.txt
pytest --co > test_list.txt
```

2. Executar com máximo debug:
```bash
pytest app/tests/ -vv --tb=long --log-cli-level=DEBUG 2>&1 | Tee debug_output.log
```

3. Compartilhar logs e ambiente

---

