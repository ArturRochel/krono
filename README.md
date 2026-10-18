# ⏳ Krono — Organizador Pessoal de Rotina e Compromissos

O **Krono** é uma aplicação Web Full-Stack (Desktop & Mobile PWA) projetada para reduzir a carga cognitiva matinal na organização da rotina. O sistema centraliza compromissos com hora marcada e tarefas (da faculdade, trabalho e vida pessoal) em uma visão diária dividida por blocos de energia (**Manhã**, **Tarde** e **Noite**), com rollover automático de pendências e preparação nativa para inteligência artificial.

---

## ✨ Funcionalidades Principais

- **Visão do Dia por Turnos (`Manhã`, `Tarde`, `Noite`):**
  - **Tarefas** são alocadas diretamente no turno em que você planeja executá-las.
  - **Compromissos** têm seu turno deduzido automaticamente a partir do horário de início (`00h–11h59` Manhã, `12h–17h59` Tarde, `18h–23h59` Noite).
- **Separação entre "Data Planejada" e "Prazo Final":**
  - Planeje _quando_ deseja executar uma tarefa (`scheduled_date`) sem perder de vista o prazo fatal de entrega (`deadline_at`).
- **Rollover Automático de Pendências:**
  - Tarefas não concluídas em dias anteriores permanecem visíveis na lista do dia atual com indicação clara de atraso (ex: _Ontem_, _Segunda_), evitando que caiam no esquecimento.
- **Contexto Rápido por Labels:**
  - Categorização visual com cores e ícones customizáveis para diferenciar contextos (ex: _Faculdade_, _Trabalho_, _Pessoal_).
- **Anexos e Links Estruturados:**
  - Suporte a múltiplos links e referências de arquivos em cada tarefa ou compromisso para acesso imediato ao material de apoio.
- **Hábitos e Tarefas Recorrentes:**
  - Marcação de atividades diárias/recorrentes para fácil acompanhamento de rotina.
- **Gamificação sem Atrito (Streak & Contadores):**
  - Cálculo automático de **dias seguidos de ofensiva (streak)** e **total de atividades concluídas** diretamente a partir do histórico de execução.
- **Multiplataforma (Web Desktop + PWA iOS):**
  - Layout responsivo adaptado para monitores widescreen no navegador e instalável na tela de início do Safari no iPhone via Web App Manifest.

---

## 🛠️ Stack Tecnológica

### Frontend

- **React 18 + TypeScript** (via Vite)
- **Tailwind CSS v4** (Estilização responsiva Mobile-First & Desktop)
- **TanStack Query (React Query)** (Gerenciamento de estado assíncrono, cache e _optimistic updates_)
- **Lucide React** (Biblioteca de ícones)
- **Vite Plugin PWA** (Suporte a instalação standalone no iOS/Desktop)

### Backend

- **Python 3.12 + FastAPI** (API RESTful de alta performance e documentação OpenAPI automática)
- **SQLAlchemy 2.0** (ORM com tipagem moderna via `Mapped` e `mapped_column`)
- **Pydantic v2** (Validação de dados e serialização de schemas)
- **Psycopg 3** (Driver moderno para PostgreSQL)

### Banco de Dados & Infraestrutura

- **PostgreSQL 16 (`pgvector/pgvector:pg16`)** (Banco relacional já preparado com extensão vetorial para futura camada de LLM)
- **Docker & Docker Compose** (Ambiente isolado e reprodutível para desenvolvimento local e deploy em VPS)

---

## 📂 Arquitetura de Pastas

```text
krono/
├── docker-compose.yml          # Orquestração dos containers (db, backend, frontend)
├── .env                        # Variáveis de ambiente
├── README.md                   # Documentação do projeto
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Inicialização do FastAPI e CORS
│       ├── database.py         # Engine e sessão do SQLAlchemy 2.0
│       ├── models.py           # Modelos relacionais (Label, Task, Appointment)
│       ├── schemas.py          # Contratos de entrada/saída (Pydantic)
│       └── routers/            # Endpoints da API (/briefing, /tasks, /appointments, /labels)
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts          # Configuração do Vite, Tailwind e PWA
    └── src/
        ├── components/         # Componentes visuais (Cards, Modais, Sidebar, Header)
        ├── pages/              # Telas da aplicação (Visão do Dia, Planejamento)
        ├── services/           # Cliente HTTP e hooks do TanStack Query
        └── types/              # Interfaces TypeScript espelhadas do Backend
```
