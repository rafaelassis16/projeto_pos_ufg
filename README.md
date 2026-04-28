# 📝 To-Do API (Micro-API de Gerenciamento de Tarefas)

## 📌 Descrição

A **To-Do API** é uma micro-API RESTful desenvolvida com foco em demonstrar conceitos de arquitetura mínima, boas práticas de desenvolvimento e uso de Inteligência Artificial no ciclo de vida do software.

A aplicação permite o gerenciamento de tarefas (To-Do List), incluindo criação, listagem, atualização, exclusão e marcação de status (concluída ou pendente).

Este projeto foi desenvolvido como um **Produto Mínimo Viável (MVP)**, com escopo controlado e foco em aprendizado prático.

---

## 🎯 Objetivos do Projeto

* Aplicar conceitos de arquitetura em camadas (Controller, Service, Repository)
* Utilizar IA generativa no desenvolvimento de software
* Implementar uma API RESTful simples e funcional
* Praticar versionamento com Git e GitHub
* Criar documentação técnica clara e objetiva

---

## 🛠️ Tecnologias Utilizadas

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

### Banco de Dados

* SQLite (ambiente local)

### Testes

* Pytest

### Ferramentas de Apoio

* VS Code
* Git / GitHub
* IA Generativa (ChatGPT / Copilot)

---

## 🏗️ Arquitetura do Projeto

A aplicação segue uma arquitetura em camadas:

* **Routes (Controller):** Recebe as requisições HTTP
* **Services:** Contém as regras de negócio e o **PriorityAdvisor**
* **Repository:** Responsável pela persistência de dados (através do SQLAlchemy)
* **Models:** Representação das entidades no banco
* **Schemas:** Validação e serialização de dados (Pydantic)

---

## 📁 Estrutura de Pastas

```
projeto_pos_ufg/
│
├── app/
│   ├── __init__.py
│   ├── database/
│   ├── models/
│   ├── repository/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── tests/
│       ├── results/         # Relatórios de testes e cobertura
│       └── unit/            # Testes unitários
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Como Executar o Projeto

### 1. Clonar o repositório

```
git clone https://github.com/rafaelassis16/projeto_pos_ufg.git
cd projeto_pos_ufg
```

### 2. Criar ambiente virtual

```
python -m venv .venv
```

### 3. Ativar o ambiente virtual

**Windows:**

```
.venv\Scripts\activate
```

**Linux/Mac:**

```
source .venv/bin/activate
```

### 4. Instalar dependências

```
pip install -r requirements.txt
```

### 5. Executar a aplicação

```
uvicorn app.main:app --reload
```

---

## 🌐 Acessar a API

Documentação interativa (Swagger):

👉 http://127.0.0.1:8000/docs

---

## 📡 Endpoints Principais

### Criar tarefa

```
POST /tasks
```

### Listar tarefas (com filtro opcional)

```
GET /tasks
GET /tasks?completed=true
```

### Buscar tarefa por ID

```
GET /tasks/{id}
```

### Atualizar tarefa (Completo)

```
PUT /tasks/{id}
```

### Marcar como concluída (Parcial)

```
PATCH /tasks/{id}/complete?completed=true
```

### Deletar tarefa

```
DELETE /tasks/{id}
```

---

## 🧪 Testes

Para executar os testes e gerar relatório de cobertura:

```
pytest --cov=app --cov-report=term-missing
```

Os resultados detalhados são salvos em `app/tests/results/`.
**Cobertura atual: 95%**

---

## 🤖 Uso de Inteligência Artificial

A IA generativa foi utilizada seguindo estas diretrizes:

- **Contexto:** API REST com FastAPI, SQLAlchemy e SQLite.
- **Objetivo:** Geração de endpoints CRUD completos.
- **Requisitos:**
    - `POST /tasks`
    - `GET /tasks` (filtro opcional)
    - `PUT /tasks/{id}`
    - `DELETE /tasks/{id}`
    - `PATCH /tasks/{id}/complete`
- **Regras:** Uso de `SessionLocal`, `Depends(get_db)`, tratamento de erros 404 e código modular.

---

## 🎨 Frontend (Futuro)

Para a implementação do frontend, deve-se utilizar obrigatoriamente a skill **design-system** baseada no **WEG Design System (@weg-react-ui)**, garantindo:
- Componentes React consistentes.
- Layouts com Grid de 12 colunas.
- Formulários com React Hook Form + Zod.
- Uso de `DataTable` para listagens.

---

## ⚠️ Limitações

* Não possui autenticação de usuários
* Banco de dados local (SQLite)
* Cobertura de testes ainda básica
* Não implementa paginação

---

## 🚀 Próximos Passos

* Implementar autenticação com JWT
* Migrar banco para PostgreSQL
* Adicionar paginação e filtros avançados
* Melhorar cobertura de testes
* Criar frontend em React
* Deploy em ambiente cloud

---

## 🏷️ Versionamento

Versão atual:

```
v1.0.0
```

## 🛠️ Ferramentas Utilizadas

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Testes:** Pytest, Pytest-cov
- **IA:** Antigravity (Google DeepMind)
- **IDEs:** Cursor / VS Code

---


## 👨‍💻 Autor

Projeto desenvolvido por **Rafael Amancio**.

---

## 📄 Licença

Este projeto é apenas para fins acadêmicos e de aprendizado.
