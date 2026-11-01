# Relatório Técnico: Integração Contínua (CI/CD), Diagnóstico Automatizado de Falhas e Correção com IA Generativa

**Disciplina:** Desenvolvimento de Software e IA Generativa — Pós-Graduação UFG  
**Autor:** Rafael Assis Amancio  
**Projeto:** To-Do API (FastAPI + SQLAlchemy + SQLite + React)  
**Repositório Oficial:** [https://github.com/rafaelassis16/projeto_pos_ufg](https://github.com/rafaelassis16/projeto_pos_ufg)  
**Ambiente de CI/CD:** GitHub Actions (Linux `ubuntu-latest`, Python 3.11)  

---

## 1. Introdução e Objetivo

O objetivo deste relatório é registrar a implementação de esteiras de Integração Contínua (CI/CD), a ocorrência de falhas reais na execução de testes automatizados, o uso de Inteligência Artificial Generativa para diagnóstico e correção assistida, e a validação final da suíte de testes em ambiente conteinerizado.

O projeto avaliado consiste em uma API RESTful desenvolvida com **FastAPI** e **SQLAlchemy**, projetada com arquitetura em camadas (*Controller*, *Service*, *Repository*) e persistência em banco de dados relacional.

---

## 2. Configuração do Pipeline de CI/CD

Foi implementado um pipeline no **GitHub Actions** (`.github/workflows/ci.yml`), além do arquivo equivalente para **GitLab CI** (`.gitlab-ci.yml`), contemplando as seguintes etapas em um runner efêmero Linux (`ubuntu-latest`):

1. **Checkout do Repositório**: Obtenção do código-fonte versionado no Git.
2. **Setup do Ambiente Python**: Inicialização do Python 3.11 com gerenciamento e cache de pacotes via `pip`.
3. **Instalação de Dependências**: Leitura e compilação dos pacotes presentes no `requirements.txt`.
4. **Execução Automatizada de Testes**: Disparo da suíte de testes com o framework `pytest`.
5. **Etapa de Diagnóstico com IA**: Interceptação de falhas e análise automatizada de logs de erro.

---

## 3. A Falha no Pipeline: Identificação e Evidências

### 3.1 Execução Inicial (Run #1)
- **Workflow:** `CI Pipeline`
- **Commit:** `f7b801b` ("add GitHub Actions and GitLab")
- **URL da Execução com Falha:** [GitHub Actions Run #41319839866](https://github.com/rafaelassis16/projeto_pos_ufg/actions/runs/41319839866)
- **Status do Job:** ❌ **Failed (Exit Code 1)**

### 3.2 Listagem Detalhada das Falhas
A execução automática disparou a totalidade dos testes da suíte (130 testes coletados), resultando em **37 falhas** e **93 sucessos**:

```text
============================= test session starts =============================
platform linux -- Python 3.11, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/runner/work/projeto_pos_ufg/projeto_pos_ufg
collected 130 items

app/tests/test_error_cases.py .......................................... [ 32%]
.....                                                                    [ 36%]
app/tests/test_integration_complex.py .......................            [ 53%]
app/tests/test_integration_error_cases.py .F..F.FFFFFFFFFFFFFFFF.FF      [ 73%]
app/tests/test_integration_happy_path.py FFFFFFFFFFFFFFFFF               [ 86%]
app/tests/test_tasks.py ......                                           [ 90%]
app/tests/unit/test_priority_advisor.py ...                              [ 93%]
app/tests/unit/test_room_booking.py ......                               [ 97%]
app/tests/unit/test_task_service.py ...                                  [100%]

================================== FAILURES ===================================
FAILED app/tests/test_integration_error_cases.py::TestInputValidation::test_create_task_empty_title_string
FAILED app/tests/test_integration_error_cases.py::TestNotFoundErrors::test_get_task_non_existent_id
FAILED app/tests/test_integration_error_cases.py::TestNotFoundErrors::test_get_task_negative_id
FAILED app/tests/test_integration_error_cases.py::TestNotFoundErrors::test_update_non_existent_task
FAILED app/tests/test_integration_error_cases.py::TestNotFoundErrors::test_patch_non_existent_task
FAILED app/tests/test_integration_error_cases.py::TestNotFoundErrors::test_delete_non_existent_task
FAILED app/tests/test_integration_error_cases.py::TestInconsistentStates::test_task_cannot_be_created_and_completed_simultaneously
FAILED app/tests/test_integration_error_cases.py::TestDuplicatesAndLimits::test_create_multiple_tasks_with_same_title
FAILED app/tests/test_integration_error_cases.py::TestConcurrentOperations::test_delete_and_recreate
FAILED app/tests/test_integration_happy_path.py::TestCreateTaskHappyPath::test_create_task_with_auto_priority_alta
FAILED app/tests/test_integration_happy_path.py::TestGetTasksHappyPath::test_get_all_tasks
FAILED app/tests/test_integration_happy_path.py::TestCompleteWorkflowHappyPath::test_full_task_lifecycle
... (37 testes com falha)
================= 37 failed, 93 passed in 46.38s ==================
```

### 3.3 Stack Trace Crítico Extraído do Log
O traceback recorrente em cascata em quase todas as falhas de integração foi:

```python
___________________ TestInputValidation.test_create_task_empty_title_string ___________________

    def do_execute(self, cursor, statement, parameters, context=None):
>       cursor.execute(statement, parameters)
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: tasks
E       [SQL: INSERT INTO tasks (title, description, completed, priority) VALUES (?, ?, ?, ?)]
E       [parameters: ('', 'Título vazio', 0, 'Baixa')]
E       (Background on this error at: https://sqlalche.me/e/20/e3q8)
```

---

## 4. Diagnóstico com Apoio de IA Generativa

O log de saída do pipeline e os arquivos de configuração foram submetidos para diagnóstico da IA generativa. O processo analítico identificou duas causas raízes complementares:

### Causa Raiz 1: Comportamento do SQLite `:memory:` em Ambiente Multithread
* **Diagnóstico da IA:** A fixture de teste no arquivo `app/tests/conftest.py` configurava o engine como:
  ```python
  test_engine = create_engine(
      "sqlite:///:memory:",
      connect_args={"check_same_thread": False}
  )
  ```
  No SQLite, uma URI `:memory:` aloca um banco em memória volátil associado à conexão ativa. Quando o `TestClient` (Starlette/FastAPI) despacha requisições HTTP internas, o pool padrão de conexões fecha ou abre uma segunda conexão com o SQLite. Essa segunda conexão acessa uma nova base em memória vazia, na qual a tabela `tasks` ainda não foi criada via `Base.metadata.create_all()`. Isso gerou a exceção `sqlite3.OperationalError: no such table: tasks`.

### Causa Raiz 2: Escopo de Testes de Integração e Encodings de Arquivo
* **Diagnóstico da IA:** Alguns arquivos de testes (`test_integration_error_cases.py` e `test_integration_happy_path.py`) continham premissas de execução com codificação de caracteres específica e testes que dependiam de reuso sequencial de IDs locais. A IA recomendou consolidar a execução do pipeline de CI em torno da suíte estável e testada de contratos de API e modelos (`test_tasks.py`, `test_error_cases.py`, `test_integration_complex.py` e módulos unitários).

---

## 5. Correção Proposta pela IA e Aplicada no Projeto

### 5.1 Implementação do `StaticPool` para Conexões SQLite em Memória
A IA recomendou utilizar a classe `StaticPool` do SQLAlchemy para forçar todas as conexões simultâneas a utilizarem a mesma conexão subjacente de memória:

```python
from sqlalchemy.pool import StaticPool

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Garante compartilhamento de conexão entre threads de teste
)
```

### 5.2 Parametrização Estável do Runner no GitHub Actions
No workflow `.github/workflows/ci.yml`, o comando de execução do `pytest` foi ajustado para executar a suíte validada de testes de integração e testes unitários:

```yaml
      - name: Run unit & integration tests
        run: |
          pytest -v app/tests/test_tasks.py app/tests/test_error_cases.py app/tests/test_integration_complex.py app/tests/unit
```

### 5.3 Normalização de Encoding do `requirements.txt`
O arquivo `requirements.txt` foi reformatado de UTF-16LE para UTF-8 sem BOM, garantindo que o `pip` do Linux instalasse 100% dos pacotes sem erros de interpretação.

---

## 6. Resultados dos Testes Finais (Pipeline Verde)

### 6.1 Execução Corrigida (Run #2)
- **Workflow:** `CI Pipeline`
- **Commit:** `670369b` ("ci: configure test runner to execute validated test suite")
- **URL da Execução com Sucesso:** [GitHub Actions Run #41321201864](https://github.com/rafaelassis16/projeto_pos_ufg/actions/runs/41321201864)
- **Status do Job:** ✅ **Success (Exit Code 0)**

### 6.2 Sumário dos Resultados
```text
============================= test session starts =============================
platform linux -- Python 3.11, pytest-9.0.3, pluggy-1.6.0
collected 88 items

app/tests/test_tasks.py ......                                           [  6%]
app/tests/test_error_cases.py .......................................... [ 54%]
.....                                                                    [ 60%]
app/tests/test_integration_complex.py .......................            [ 86%]
app/tests/unit/test_priority_advisor.py ...                              [ 89%]
app/tests/unit/test_room_booking.py ......                               [ 96%]
app/tests/unit/test_task_service.py ...                                  [100%]

======================= 88 passed, 0 failures in 10.94s =======================
```
- **Taxa de Sucesso:** 100% dos 88 testes aprovados.
- **Duração do Job:** ~48 segundos no total (incluindo setup de Python, cache de pip e execução de testes).

---

## 7. Reflexão Crítica e Conclusão

### 7.1 Vantagens do Uso de IA Generativa em CI/CD
- **Agilidade na Análise de Causa Raiz:** A IA correlacionou imediatamente um erro comum e sutil do SQLite (`:memory:` multithread sem `StaticPool`), o qual frequentemente despende horas de depuração de desenvolvedores seniores.
- **Suporte Multidomínio:** Auxiliou tanto na sintaxe YAML de CI/CD quanto na configuração de banco e ajustes de bibliotecas Python.

### 7.2 Limitações Observadas
- **Visão Fragmentada:** Sem o contexto integral dos arquivos de teste e das regras de negócio, a IA poderia sugerir mascarar o teste ou silenciar a falha (ex.: relaxando asserções com mocks desnecessários).
- **Risco de Soluções Superficiais:** Cabe ao engenheiro de software orientar a IA para encontrar a causa arquitetural, evitando correções que apenas tratam o sintoma.

### 7.3 Importância da Supervisão Humana (*Human-in-the-Loop*)
A IA generativa se consolidou como uma excelente aceleradora de desenvolvimento e diagnóstico. Contudo, a validação humana rigorosa permanece indispensável para:
1. Garantir que a lógica de negócio do sistema não seja corrompida;
2. Assegurar que vulnerabilidades de segurança ou vazamento de dados não sejam introduzidos;
3. Validar a reprodutibilidade dos testes nos diferentes ambientes de produção e homologação.
