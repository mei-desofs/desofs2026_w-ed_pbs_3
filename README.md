# desofs2026_w-ed_pbs_3

## Organização do Repositório

/
├── deliverables/           # Entregáveis
├── docker/                 # Configurações de containerização (Dockerfile, docker-compose)
│   ├── flask.Dockerfile
│   └── postgres.Dockerfile
├── src/
│   ├── api/                # Camada de Interface (Controllers / HTTP Routes)
│   │   ├── user_routes.py
│   │   ├── workspace_routes.py
│   │   └── document_routes.py
│   │
│   ├── application/        # Camada de Aplicação (Services)
│   │   ├── user_service.py
│   │   ├── workspace_service.py
│   │   └── document_service.py
│   │
│   ├── domain/             # Camada de Domínio (O coração do software)
│   │   ├── user/
│   │   │   ├── entities.py       # User (Aggregate Root)
│   │   │   └── value_objects.py  # Email, HashedPass
│   │   │
│   │   ├── workspace/
│   │   │   ├── entities.py       # Workspace (Root), Member (Entity)
│   │   │   └── value_objects.py  # Role, WorkspaceName, FolderPath
│   │   │
│   │   └── document/
│   │       ├── entities.py       # Document (Aggregate Root)
│   │       └── value_objects.py  # DocumentTitle, MarkdownContent, FilePath
│   │
│   ├── infrastructure/     
│   │   ├── persistence/    # Repositórios (SQLAlchemy)
│   │   └── filesystem/     # Integração com o Sistema de Ficheiros Linux
│   │
│   └── shared/             # Código partilhado (Utils, exceções base, etc.)
│
├── tests/                  
├── app.py                  # Ponto de entrada da aplicação Flask
├── requirements.txt        # Dependências do Python
└── .env                    # Variáveis de ambiente