# desofs2026_w-ed_pbs_3

## Organização do Repositório

# Estrutura do Projeto

```text
.
├── deliverables/                 # Documentação, diagramas de arquitetura e entregáveis
│
├── docker/                       # Configurações de containerização
│   ├── flask.Dockerfile
│   └── postgres.Dockerfile
│
├── src/
│   ├── api/                      # Camada de Interface (Controllers / HTTP Routes)
│   │   ├── user_routes.py
│   │   ├── workspace_routes.py
│   │   └── document_routes.py
│   │
│   ├── application/              # Camada de Aplicação (Services)
│   │   ├── user_service.py
│   │   ├── workspace_service.py
│   │   └── document_service.py
│   │
│   ├── domain/                   # Camada de Domínio (Core do sistema)
│   │   ├── user/
│   │   │   ├── entities.py       # User (Aggregate Root)
│   │   │   └── value_objects.py  # Username, HashedPass
│   │   │
│   │   ├── workspace/
│   │   │   ├── entities.py       # Workspace (Root), Member (Entity)
│   │   │   └── value_objects.py  # Role, WorkspaceName, FolderPath
│   │   │
│   │   └── document/
│   │       ├── entities.py       # Document (Aggregate Root)
│   │       └── value_objects.py  # DocumentTitle, MarkdownContent, FilePath
│   │
│   ├── infrastructure/           # Detalhes de implementação (Adapters / Persistence)
│   │   ├── persistence/          # Repositórios (SQLAlchemy / PostgreSQL)
│   │   └── filesystem/           # Integração com o sistema de ficheiros Linux
│   │
│   └── shared/                   # Código partilhado (utils, exceções, helpers)
│
├── tests/                        # Testes unitários, integração e E2E
├── app.py                        # Ponto de entrada da aplicação Flask
├── requirements.txt              # Dependências Python
└── .env                          # Variáveis de ambiente
```
