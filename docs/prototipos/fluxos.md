# Fluxos de navegação e protótipos lógicos

Complementam os wireframes HTML e rastreiam os casos de uso UC-01 a UC-05.

---

## 1. Fluxo principal do usuário (happy path)

```mermaid
flowchart TD
    A[Acessa aplicação] --> B[UC-02 Lista carregada]
    B --> C{Ação do usuário}
    C -->|Nova Tarefa| D[Abre formulário]
    D --> E[Preenche título e opcionais]
    E --> F{Título válido?}
    F -->|Não| G[Exibe erro de validação]
    G --> E
    F -->|Sim| H[POST /tasks]
    H --> I[UC-06 Prioridade se aplicável]
    I --> J[Atualiza lista + toast sucesso]
    J --> B
    C -->|Editar| K[Abre formulário preenchido]
    K --> L[PUT /tasks/id]
    L --> J
    C -->|Excluir| M[DELETE /tasks/id]
    M --> J
    C -->|Alternar status| N[PATCH complete]
    N --> B
```

---

## 2. Fluxo de criação com regra de prioridade

```mermaid
sequenceDiagram
    actor U as Usuário
    participant FE as Frontend
    participant API as FastAPI
    participant S as TaskService
    participant PA as PriorityAdvisor
    participant DB as SQLite

    U->>FE: Nova Tarefa + Salvar
    FE->>FE: Validação Zod (título)
    FE->>API: POST /tasks {title, description, priority?}
    API->>S: create_task
    S->>PA: advise(title, description)
    PA-->>S: Alta | Média | Baixa
    S->>DB: INSERT task
    DB-->>S: task com id
    S-->>API: Task
    API-->>FE: 200 + JSON
    FE-->>U: Toast sucesso + lista atualizada
```

---

## 3. Mapa de telas (protótipo de navegação)

```mermaid
flowchart LR
    subgraph Telas
        L[Lista / DataTable]
        M[Modal Formulário]
    end
    L -->|Nova Tarefa| M
    L -->|Editar| M
    M -->|Salvar OK| L
    M -->|Cancelar| L
    L -->|Status / Excluir| L
```

> O MVP usa **duas “telas” lógicas** (lista + modal), o que é suficiente para um CRUD de escopo controlado e evita navegação multi-página desnecessária.

---

## 4. Como visualizar os protótipos HTML

1. Abra no navegador (duplo clique ou “Open with Live Server”):
   - `docs/prototipos/wireframe-lista.html`
   - `docs/prototipos/wireframe-formulario.html`
2. Compare com o protótipo vivo:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Evidência em vídeo: `Videos/Teste frontend.mp4`
