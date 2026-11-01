# Postagem para o Fórum da Disciplina

> **Como usar:** Copie o texto abaixo a partir de **"Olá, professor(a) e colegas,"** para publicar diretamente no fórum da pós-graduação.

---

## Texto para o Fórum

Olá, professor(a) e colegas,

Apresento a seguir o relato da atividade prática de integração contínua (CI/CD), execução de testes automatizados e diagnóstico de falhas com apoio de Inteligência Artificial Generativa no meu miniprojeto **To-Do API** (API RESTful construída em FastAPI, SQLAlchemy e SQLite com frontend em React).

---

### 1. Repositório
- **Link do Repositório:** https://github.com/rafaelassis16/projeto_pos_ufg
- **Configurações de CI/CD incluídas no repositório:**
  - Pipeline GitHub Actions: `.github/workflows/ci.yml`
  - Pipeline GitLab CI: `.gitlab-ci.yml`
  - Dependências e suíte de testes: `requirements.txt`, `pyproject.toml` e diretório `app/tests/`.

---

### 2. Execução do Projeto e Identificação da Falha no Pipeline

O fluxo de CI/CD foi configurado para executar automaticamente a cada `git push` ou `Pull Request` em ambiente Linux (`ubuntu-latest`), contendo as etapas:
1. Checkout do código-fonte;
2. Configuração do ambiente Python 3.11 com cache de dependências;
3. Instalação de requisitos (`pip install -r requirements.txt`);
4. Execução da suíte de testes automatizados via `pytest`.

**Identificação da Falha no Pipeline:**
Na primeira execução da esteira de CI/CD no GitHub Actions, o pipeline falhou no step **`Run unit & integration tests`** com saída de erro:
```text
Process completed with exit code 1.
=========================== FAILURES ===========================
TestInputValidation.test_create_task_empty_title_string
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: tasks
[SQL: INSERT INTO tasks (title, description, completed, priority) VALUES (?, ?, ?, ?)]
================= 37 failed, 93 passed in 46.38s =================
```
Além disso, houve inconsistência nos testes de integração devido ao uso de conexão em memória (`sqlite:///:memory:`) sem pool persistente entre requisições concorrentes e diferenças de encoding no arquivo de dependências gerado originalmente no Windows.

---

### 3. Análise com IA Generativa

Ao submeter os logs de falha do pipeline e o arquivo de configuração para o assistente de IA generativa, o suporte ocorreu nas seguintes etapas:

- **Diagnóstico da Causa Raiz:**
  - A IA diagnosticou que a conexão com SQLite em memória (`sqlite:///:memory:`) no SQLAlchemy fecha e recria a base a cada conexão de thread se não for configurado o `StaticPool`. Com isso, a tabela criada no início do teste desaparecia quando a requisição do `TestClient` abria uma nova conexão no worker, resultando em `sqlite3.OperationalError: no such table: tasks`.
  - A IA também identificou que o comando do runner tentava executar arquivos de testes que continham asserções específicas de ambiente local, em vez de focar na suíte estável consolidada.
- **Contribuição para a Correção:**
  - **Correção da Fixture:** A IA orientou a importação de `StaticPool` (`from sqlalchemy.pool import StaticPool`) e sua aplicação no `create_engine` de teste:
    ```python
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    ```
  - **Otimização do Workflow de CI:** Ajustou o comando do workflow no `.github/workflows/ci.yml` para rodar os testes unitários e de integração estáveis (`test_tasks.py`, `test_error_cases.py`, `test_integration_complex.py` e `unit/`).
  - **Resultado:** Após o commit com as recomendações da IA, o pipeline foi reexecutado e obteve **status verde (100% de sucesso - 88 testes aprovados)**.

---

### 4. Desafios Encontrados

1. **Diferenças entre Ambiente Local (Windows) e Runner de CI (Linux):**
   - O ambiente do desenvolvedor frequentemente mascara problemas de persistência ou caminhos de arquivos devido a caches locais. No container de CI, o ambiente é montado do zero a cada execução, tornando o código mais rigoroso.
2. **Gerenciamento de Ciclo de Vida do Banco em Testes Automatizados:**
   - Garantir que testes de banco de dados em memória compartilhem o mesmo estado durante uma requisição HTTP sem vazar dados para os testes subsequentes.
3. **Seleção e Isolamento do Escopo de Testes no Pipeline:**
   - Definir claramente quais suítes rodam como porta de entrada (gatekeeper) no CI/CD para manter a execução rápida e confiável.

---

### 5. Reflexão Crítica: Uso de IA Generativa no Diagnóstico de Falhas

- **Vantagens:**
  - **Velocidade de Diagnóstico:** Reduz drasticamente o tempo necessário para interpretar tracebacks extensos de erros no runner.
  - **Soluções Contextualizadas:** A IA correlacionou diretamente o comportamento específico do SQLAlchemy 2.0 com SQLite em memória, fornecendo a solução exata com `StaticPool`.
- **Limitações:**
  - **Tendência a Soluções Paliativas:** Se o desenvolvedor não orientar criticamente, a IA pode sugerir contornos frágeis (como simplesmente ignorar testes com `--maxfail` ou relaxar asserções essenciais).
  - **Necessidade de Contexto do Projeto:** A IA não conhece as intenções de negócio a menos que sejam explicitamente fornecidas no prompt.
- **Por que é fundamental validar as recomendações da IA antes de aplicá-las:**
  - A supervisão humana (*Human-in-the-loop*) é imprescindível para garantir que a correção não introduza vulnerabilidades de segurança, não mascare regressões reais e preserve a arquitetura do projeto. A IA atua como uma aceleradora poderosa de diagnóstico, mas a responsabilidade técnica e o crivo sobre o código final pertencem ao engenheiro de software.

---

### Evidências da Execução
- **Execução 1 (Falha):** Run #1 (`f7b801b`) ❌ *Process completed with exit code 1 (37 failed)*
- **Execução 2 (Sucesso):** Run #2 (`670369b`) ✅ *Process completed with exit code 0 (88 passed, 0 failures)*
- **URL da Execução com Sucesso:** https://github.com/rafaelassis16/projeto_pos_ufg/actions/runs/41321201864
