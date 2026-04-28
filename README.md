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
* **Services:** Contém as regras de negócio
* **Repository:** Responsável pela persistência de dados
* **Models:** Representação das entidades no banco
* **Schemas:** Validação e serialização de dados

---

## 📁 Estrutura de Pastas

```
projeto_pos_ufg/
│
├── app/
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── repository/
│   └── database/
│
├── tests/
├── requirements.txt
├── .gitignore
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

### Listar tarefas

```
GET /tasks
```

### Atualizar tarefa

```
PUT /tasks/{id}
```

### Deletar tarefa

```
DELETE /tasks/{id}
```

### Marcar como concluída

```
PATCH /tasks/{id}/complete
```

---

## 🧪 Testes

Para executar os testes:

```
pytest
```

---

## 🤖 Uso de Inteligência Artificial

A IA generativa foi utilizada em diversas etapas do projeto:

* Geração de código base (CRUD)
* Sugestão de arquitetura
* Criação de testes automatizados
* Geração de documentação (README)
* Refatoração e melhoria de código

Ferramentas utilizadas:

* ChatGPT
* GitHub Copilot

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

---

## 👨‍💻 Autor

Projeto desenvolvido por **Rafael Amancio**.

---

## 📄 Licença

Este projeto é apenas para fins acadêmicos e de aprendizado.
