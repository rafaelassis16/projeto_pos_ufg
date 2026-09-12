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

## 🏗️ Arquitetura do Sistema

```mermaid
graph TD
    User([Usuário/Frontend]) -- HTTP/JSON --> API[FastAPI App]
    
    subgraph Backend [Backend API]
        API --> Routes[Routes / Controller]
        Routes --> Service[TaskService]
        Service --> Advisor[PriorityAdvisor]
        Service --> Repo[Repository / SQLAlchemy]
    end
    
    subgraph Persistence [Persistência]
        Repo --> DB[(SQLite Database)]
    end

    style User fill:#f9f,stroke:#333,stroke-width:2px
    style DB fill:#00d2ff,stroke:#333,stroke-width:2px
    style Backend fill:#f5f5f5,stroke:#999,stroke-dasharray: 5 5
```

> Uma modelagem mais aprofundada da arquitetura (visão de containers inspirada no C4 e jornada crítica em diagrama de sequência) está documentada na seção **[Discovery de Documentação — Diagrams as Code](#-discovery-de-documentação--diagrams-as-code)**.

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

* VS Code / Cursor
* Git / GitHub
* IA Generativa (Antigravity - Google DeepMind)

---

## 🏗️ Arquitetura do Projeto

A aplicação segue uma arquitetura em camadas para garantir separação de responsabilidades e facilidade de manutenção:

* **Routes (Controller):** Gerencia as rotas e validações de entrada via FastAPI.
* **Services:** Implementa a lógica de negócio, incluindo o **PriorityAdvisor** para sugestão automática de prioridade.
* **Repository:** Encapsula o acesso a dados usando SQLAlchemy.
* **Models:** Define a estrutura das tabelas no SQLite.
* **Schemas:** Define os contratos de dados (DTOs) usando Pydantic.

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

## 🎨 Executar Frontend (React)

O frontend foi desenvolvido utilizando o **WEG Design System**.

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Rodar em modo de desenvolvimento

```bash
npm run dev
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
### Níveis de Teste Aplicados

1.  **Testes Unitários:** Validam a lógica de negócio no `TaskService` e `PriorityAdvisor` de forma isolada.
2.  **Testes de Integração (API):** Validam os endpoints utilizando `TestClient`, garantindo que rotas, filtros e códigos de status (200, 404, 422) funcionam como esperado.
3.  **Isolamento de Dados:** Utilização de um banco de dados SQLite exclusivo para testes (`test.db`), garantindo a integridade do banco de desenvolvimento.

**Cobertura atual: 95%**

---

## 📹 Vídeos de Demonstração

Para visualizar o funcionamento da aplicação na prática, consulte os vídeos na pasta `/Videos`:

*   **[Teste backend.mp4](./Videos/Teste%20backend.mp4):** Demonstração da execução dos testes automatizados e funcionamento dos endpoints via Swagger.
*   **[Teste frontend.mp4](./Videos/Teste%20frontend.mp4):** Demonstração da interface do usuário, criação, edição e exclusão de tarefas em tempo real.

---

## 🧭 Discovery de Documentação — Diagrams as Code

> Esta seção atende à atividade prática da **Unidade III**: conduzir uma pequena fase de *discovery* de documentação sobre um sistema real, descrevendo-o em linguagem natural e gerando diagramas em **Mermaid** com apoio de GenAI (abordagem *diagrams as code*), documentando as decisões e ajustes feitos sobre o que o modelo gerou.
>
> **Repositório público:** https://github.com/rafaelassis16/projeto_pos_ufg

### 1) Descrição do sistema em linguagem natural

**Sistema escolhido:** a própria **To-Do API** deste repositório — uma aplicação real de gerenciamento de tarefas, usada como sistema do meu contexto de estudo/trabalho.

- **Escopo.** Gerenciamento do ciclo de vida de tarefas (criar, listar, buscar, atualizar, marcar como concluída e excluir), com uma regra de negócio auxiliar que **sugere automaticamente a prioridade** da tarefa a partir de palavras-chave no título/descrição (`PriorityAdvisor`). É um MVP de escopo controlado, sem multiusuário.
- **Nível da visão.** A documentação abaixo trabalha em **dois níveis**: uma **visão estrutural de containers** (inspirada no nível 2 do C4 — quais peças executáveis existem e como conversam) e uma **visão comportamental** (nível de runtime, mostrando a troca de mensagens de uma jornada específica). Não descemos ao nível de componentes internos de classe por classe, mantendo o foco em *discovery*.
- **Limites e responsabilidades.**
  - *Frontend (React SPA)*: interface do usuário, validação de formulário (React Hook Form + Zod), feedback visual (toasts). Não contém regra de negócio.
  - *Routes / Controller (FastAPI)*: expõe os endpoints REST, valida payloads via Pydantic e traduz erros em códigos HTTP (404/422).
  - *TaskService*: concentra a lógica de negócio e orquestra persistência e sugestão de prioridade.
  - *PriorityAdvisor*: heurística de classificação de prioridade por palavras-chave.
  - *Camada de dados (SQLAlchemy + SQLite)*: persistência das tarefas.
- **Integrações.** Frontend ↔ Backend via **HTTP/JSON** (cliente `axios`, CORS liberado no backend). Persistência local via **SQLAlchemy** sobre **SQLite**. Documentação interativa exposta via **Swagger/OpenAPI** (`/docs`). Não há integrações externas de terceiros (sem gateways de pagamento, filas ou serviços em nuvem).
- **Restrições.** Sem autenticação/autorização (não há login/JWT); banco local SQLite (arquivo único, `check_same_thread=False`); paginação feita no frontend, não no servidor; regra de prioridade é uma heurística simples de texto, não um modelo de ML.
- **Lacunas conhecidas.** Ausência de multiusuário e controle de acesso; ausência de camada de repositório real (o arquivo `repository/` existe mas está vazio — hoje o acesso a dados vive dentro do `TaskService`); falta de observabilidade/logs estruturados; ausência de deploy e de banco de produção.

### 2) Diagrama estrutural — Visão de Containers (inspirada no C4)

Mostra os *containers* executáveis do sistema e como se comunicam. Foi usada a sintaxe nativa `C4Container` do Mermaid.

```mermaid
C4Container
    title Visão de Containers - To-Do API (inspirada no C4)

    Person(user, "Usuário", "Gerencia suas tarefas pelo navegador")

    System_Boundary(todo, "To-Do API") {
        Container(spa, "Frontend SPA", "React + TypeScript, WEG Design System", "Interface do usuário: formulários, tabela de tarefas e feedback visual")
        Container(api, "Backend API", "Python, FastAPI", "Expõe endpoints REST /tasks e valida os dados de entrada (Pydantic)")
        Container(service, "Regra de Negócio", "TaskService + PriorityAdvisor", "Orquestra o CRUD e sugere a prioridade por palavras-chave")
        ContainerDb(db, "Banco de Dados", "SQLite via SQLAlchemy", "Persiste as tarefas (id, título, descrição, status, prioridade)")
    }

    System_Ext(swagger, "Swagger / OpenAPI", "Documentação interativa em /docs")

    Rel(user, spa, "Usa", "HTTPS")
    Rel(spa, api, "Chama endpoints REST", "HTTP/JSON (axios)")
    Rel(api, service, "Invoca a lógica de negócio", "chamada interna")
    Rel(service, db, "Lê e escreve tarefas", "SQLAlchemy ORM")
    Rel(api, swagger, "Publica o contrato", "OpenAPI")
```

### 3) Diagrama comportamental — Jornada crítica "Criar tarefa com sugestão de prioridade"

Sequência de mensagens da jornada mais crítica do sistema: o usuário cria uma tarefa e o `PriorityAdvisor` decide a prioridade automaticamente quando ela não é informada (ou vem como "Baixa").

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Frontend (React)
    participant API as FastAPI Routes
    participant SVC as TaskService
    participant ADV as PriorityAdvisor
    participant DB as SQLite (SQLAlchemy)

    U->>FE: Preenche formulário e clica em "Salvar"
    FE->>FE: Valida campos (Zod)
    FE->>API: POST /tasks/ {title, description, priority}
    API->>API: Valida payload (Pydantic)
    API->>SVC: create_task(db, task_data)

    alt Prioridade ausente ou "Baixa"
        SVC->>ADV: advise(title, description)
        ADV-->>SVC: "Alta" | "Média" | "Baixa"
        SVC->>SVC: Ajusta task_data.priority
    else Prioridade informada explicitamente
        SVC->>SVC: Mantém prioridade do usuário
    end

    SVC->>DB: add + commit + refresh
    DB-->>SVC: Task persistida (com id)
    SVC-->>API: Task
    API-->>FE: 200 OK + JSON da tarefa
    FE->>U: Toast "Tarefa criada" e atualiza a lista
```

### 4) Decisões e ajustes sobre o que o modelo gerou

Durante o *discovery*, a GenAI foi usada para rascunhar os dois diagramas. As saídas iniciais não entraram "cruas" — abaixo estão os principais ajustes e por quê:

- **Troca do diagrama estrutural genérico por `C4Container`.** O modelo inicialmente propôs um `graph TD` simples (o que já existia no topo do README). Para atender ao pedido de uma *visão de containers inspirada no C4*, migrei para a sintaxe `C4Container` do Mermaid, que expressa explicitamente pessoas, containers, tecnologia e relações — mais fiel ao propósito da atividade.
- **Correção de fidelidade à arquitetura real.** O rascunho mostrava uma camada *Repository* separada. Ao revisar o código, constatei que a pasta `repository/` está **vazia** e que o acesso a dados vive no `TaskService`. Ajustei os diagramas para refletir o estado atual e registrei isso como **lacuna** na descrição, evitando documentar uma arquitetura idealizada em vez da real.
- **Refinamento da jornada crítica.** A primeira versão do diagrama de sequência tratava a criação da tarefa como um fluxo linear. Adicionei o bloco `alt/else` para representar a decisão real do `TaskService`: só chamar o `PriorityAdvisor` quando a prioridade está ausente ou é "Baixa" (comportamento presente em `task_service.py`). Isso tornou o diagrama uma documentação executável da regra de negócio, não só do "caminho feliz".
- **Ajuste de integrações.** Incluí explicitamente o **Swagger/OpenAPI** e o cliente **axios/HTTP-JSON** como integrações, pontos que o rascunho omitia, para deixar os limites do sistema mais claros.
- **Validação de renderização.** Os blocos foram escritos como *diagrams as code* (versionáveis e revisáveis via Git) e conferidos para renderizar no GitHub, que suporta Mermaid nativamente no Markdown.

---

## �🤖 Uso de Inteligência Artificial

A IA Generativa (**Antigravity**) foi utilizada como um "Pair Programmer" em todo o ciclo de vida do MVP:

1.  **Ideação e Arquitetura:** Sugestão da estrutura de pastas e divisão em camadas (Service, Repository, Controller) para garantir escalabilidade.
2.  **Geração de Código (CRUD):** Implementação dos modelos SQLAlchemy, schemas Pydantic e lógica de negócio no `TaskService`.
3.  **Lógica Assistida:** Criação do componente `PriorityAdvisor`, que utiliza processamento de texto simples para sugerir prioridades.
4.  **Testes Automatizados:** Escrita completa da suíte de testes (unitários e integração) e configuração de relatórios de cobertura.
5.  **Resolução de Problemas:** Identificação de erros de migração (colunas faltantes) e correção de encoding em logs do Windows.
6.  **Documentação:** Auxílio na criação do diagrama Mermaid e na estruturação profissional deste README.

Este projeto demonstra como a IA pode acelerar o desenvolvimento mantendo a qualidade técnica e seguindo boas práticas de engenharia de software.

---

## 🎨 Frontend (Implementado)

O frontend foi desenvolvido utilizando React com TypeScript e o **WEG Design System (@weg-react-ui)**, seguindo os padrões:
- **Componentes Consistentes:** Uso de `DataTable`, `Dialog`, `Button`, etc.
- **Layout Responsivo:** Grid de 12 colunas para formulários.
- **Formulários:** Integração com `React Hook Form` + `Zod` para validação robusta.
- **Feedback Visual:** Toasts para ações de CRUD.

---

## 📋 Artefatos de Especificação de Requisitos

Documentação da atividade prática de elicitação e especificação (histórias de usuário, casos de uso, critérios de aceitação e protótipos):

| Documento | Conteúdo |
|-----------|----------|
| [docs/Artefatos_Especificacao.md](./docs/Artefatos_Especificacao.md) | HU, UC, CA, RN/RNF, lacunas e rastreabilidade |
| [docs/prototipos/](./docs/prototipos/) | Wireframes HTML e fluxos Mermaid |

---

## ⚠️ Limitações

* Não possui autenticação de usuários (Login/JWT)
* Banco de dados local (SQLite)
* Não implementa paginação no backend (feita no frontend pelo DataTable)

---

## 🚀 Próximos Passos

* Implementar autenticação com JWT
* Migrar banco para PostgreSQL (Produção)
* Adicionar paginação e filtros avançados no servidor
* Deploy em ambiente cloud (Docker/Vercel)

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
