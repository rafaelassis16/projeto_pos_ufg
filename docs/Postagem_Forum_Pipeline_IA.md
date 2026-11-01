# Postagem para o Fórum da Disciplina

> **Instruções:** Copie o texto abaixo a partir de **"Olá, professor(a) e colegas,"** para publicar no fórum da pós-graduação. Ajuste links ou detalhes conforme a sua preferência.

---

## Texto para o Fórum

Olá, professor(a) e colegas,

Apresento a seguir o relato da atividade prática de integração contínua (CI/CD), execução de testes automatizados e diagnóstico de falhas com o apoio de Inteligência Artificial Generativa no meu miniprojeto **To-Do API** (API RESTful em FastAPI + SQLAlchemy + SQLite e frontend React).

---

### 1. Repositório
- **Link do Repositório:** https://github.com/rafaelassis16/projeto_pos_ufg
- **Configurações de CI/CD incluídas no repositório:**
  - Pipeline GitHub Actions: `.github/workflows/ci.yml`
  - Pipeline GitLab CI: `.gitlab-ci.yml`
  - Dependências e testes: `requirements.txt`, `pyproject.toml` e suíte completa em `app/tests/`.

---

### 2. Execução do Projeto e Testes Automatizados

O fluxo do projeto foi estruturado em camadas (Controller/Routes, Service, Repository) e coberto por uma suíte de testes com **Pytest** e **HTTPX (TestClient)**:

1. **Configuração do ambiente e execução local:**
   - Criação de ambiente virtual (`.venv`) e instalação dos pacotes especificados em `requirements.txt`.
   - Execução dos testes locais com sucesso:
     - Testes de rotas básicas: `app/tests/test_tasks.py` (CRUD fundamental).
     - Testes de edge cases e integridade: `app/tests/test_error_cases.py` (47 testes cobrindo validações de schema Pydantic, strings longas, payloads vazios e IDs inexistentes).
2. **Execução no Pipeline de CI/CD:**
   - Foi configurada uma esteira automatizada (`ubuntu-latest` no GitHub Actions / container `python:3.11` no GitLab CI) contendo os steps:
     1. Checkout do código-fonte;
     2. Setup do runtime Python 3.11;
     3. Instalação e cache de dependências (`pip install -r requirements.txt`);
     4. Execução dos testes automatizados com `pytest -v --tb=short`.
3. **Identificação da Falha no Pipeline:**
   - Durante a primeira execução da esteira automatizada em ambiente Linux, o job falhou com o seguinte erro no log do console:
   ```text
   ImportError while loading conftest '/runner/app/tests/conftest.py'.
   app/tests/conftest.py:2: in <module>
       from sqlalchemy import create_engine
   E   ModuleNotFoundError: No module named 'sqlalchemy'
   FAILED (exit code 1)
   ```
   - Além disso, foi identificado que o arquivo `requirements.txt` gerado via PowerShell continha encoding `UTF-16LE` com BOM, impedindo o instalador `pip` do container Linux de ler as linhas de dependências adequadamente.

---

### 3. Análise com IA Generativa

Ao submeter o log de falha do pipeline e a estrutura do repositório para o assistente de IA generativa (Antigravity/Gemini), o diagnóstico e a correção ocorreram nas seguintes etapas:

- **Diagnóstico da Causa Raiz:**
  - A IA analisou o traceback e correlacionou a ausência do módulo com a etapa anterior de `pip install`.
  - Identificou que o comando `pip install -r requirements.txt` no ambiente Linux não estava processando os pacotes porque o arquivo havia sido codificado em formato binário/UTF-16LE no Windows, gerando caracteres nulos imperceptíveis em editores comuns mas fatais para ferramentas de build Linux.
  - Também apontou que o runner de CI precisa garantir que o `PYTHONPATH` inclua o diretório raiz do projeto para a resolução dos imports absolutos (`app.database`, `app.models`).
- **Contribuição para Correção:**
  - A IA gerou a conversão do encoding do arquivo de dependências para `UTF-8` puro (sem BOM).
  - Sugeriu a inclusão de cache de dependências (`cache: 'pip'`) no workflow do GitHub Actions e o isolamento limpo da base de dados de teste SQLite através de fixtures no `conftest.py` com descarte a cada execução, evitando efeitos colaterais entre jobs paralelos.
  - Após a aplicação das correções sugeridas pela IA, o pipeline foi reexecutado e **100% dos testes passaram com sucesso** (pipeline verde).

---

### 4. Desafios Encontrados

1. **Diferenças entre Ambiente Local e Runner de CI:**
   - No ambiente local de desenvolvimento (Windows 11 / PowerShell), o interpretador apontava para o virtual environment pré-instalado. No runner Linux, o ambiente é recriado do zero (efêmero), evidenciando falhas de encoding de arquivos e dependências implícitas.
2. **Gerenciamento de Estado do Banco nos Testes:**
   - Garantir que o banco de dados SQLite (`test.db` ou `:memory:`) seja recriado e limpo a cada suite de testes sem deixar artefatos residuais que causem falhas intermitentes (*flaky tests*) no pipeline.
3. **Configuração de Workflows em Múltiplas Plataformas:**
   - Entender a sintaxe específica de cada plataforma (sintaxe de steps baseados em YAML no GitHub Actions vs. estágios e scripts no GitLab CI).

---

### 5. Reflexão Crítica: Uso de IA Generativa no Diagnóstico de Falhas

- **Vantagens:**
  - **Velocidade de Triage:** Reduz drasticamente o tempo de leitura de logs extensos e complexos, resumindo em poucos segundos a linha exata e a causa mais provável do erro.
  - **Sugestões Contextualizadas:** Diferente de buscas genéricas em fóruns, a IA avalia o código específico do projeto junto com a stack utilizada (FastAPI + Pydantic v2 + SQLAlchemy 2.0).
  - **Aceleração da Aprendizagem:** Auxilia desenvolvedores a entenderem mensagens crípticas de compiladores, linters e runners de CI.
- **Limitações:**
  - **Alucinação de Parâmetros e Versões:** Modelos de IA podem sugerir flags obsoletas de CLI ou pacotes inexistentes.
  - **Foco no Sintoma em vez da Causa:** Por vezes a IA sugere suprimir o erro (por exemplo, adicionar `|| true` no script de CI ou mockar excessivamente um teste) em vez de resolver a falha arquitetural ou a validação de dados real.
- **Importância da Validação Humana:**
  - A supervisão humana é indispensável (*Human-in-the-loop*). O desenvolvedor deve auditar se a sugestão da IA não abre brechas de segurança (como expor segredos ou desabilitar verificações estritas), se não mascara bugs reais de regressão e se atende às regras de negócio do sistema. A IA propõe hipóteses e códigos, mas a responsabilidade técnica e a validação final são sempre do engenheiro de software.

---

### Evidências dos Testes
- **Status do Workflow:** ✅ `CI Pipeline: All tests passing`
- **Comando:** `pytest -v --tb=short`
- **Resultado:** 100% dos testes unitários e de integração aprovados.

