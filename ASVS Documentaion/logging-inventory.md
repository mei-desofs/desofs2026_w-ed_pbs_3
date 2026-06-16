# ASVS V16 — Logging Inventory & Security Logging Specification

## 1. Objetivo

Este documento define o inventário completo de logging da aplicação, incluindo eventos registados, formato, armazenamento, retenção e controlos de segurança, em conformidade com OWASP ASVS V16.

---

## 2. Inventário de Logging (V16.1.1)

A aplicação implementa logging estruturado nas seguintes camadas:

---

### 2.1 API Layer (Flask Controllers)

Responsável por registar eventos de autenticação, ações de utilizadores e operações HTTP.

**Eventos registados:**
- Criação de workspace
- Listagem de workspaces
- Eliminação de workspace
- Adição de membros
- Criação de documentos
- Leitura de documentos
- Atualização de documentos
- Eliminação de documentos
- Tentativas de acesso não autorizado
- Erros de validação e autenticação
- Falhas em serviços externos

---

### 2.2 Service Layer (Comunicação entre serviços)

Regista interações entre microserviços internos.

**Eventos registados:**
- Falhas em chamadas HTTP entre serviços
- Erros de comunicação com workspace-service
- Falhas em escrita/leitura distribuída
- Erros de integração com serviços externos
- Timeouts e erros de rede

---

### 2.3 Data Access Layer (Repositories)

Regista operações de persistência na base de dados.

**Eventos registados:**
- CREATE, READ, UPDATE, DELETE de entidades
- Falhas de acesso a dados
- Operações negadas por permissões
- Inconsistências de dados

---

## 3. Formato dos logs (V16.2.4)

Todos os logs seguem formato estruturado e consistente:

# ASVS V16 — Logging Inventory & Security Logging Specification

## 1. Objetivo

Este documento define o inventário completo de logging da aplicação, incluindo eventos registados, formato, armazenamento, retenção e controlos de segurança, em conformidade com OWASP ASVS V16.

---

## 2. Inventário de Logging (V16.1.1)

A aplicação implementa logging estruturado nas seguintes camadas:

---

### 2.1 API Layer (Flask Controllers)

Responsável por registar eventos de autenticação, ações de utilizadores e operações HTTP.

**Eventos registados:**
- Criação de workspace
- Listagem de workspaces
- Eliminação de workspace
- Adição de membros
- Criação de documentos
- Leitura de documentos
- Atualização de documentos
- Eliminação de documentos
- Tentativas de acesso não autorizado
- Erros de validação e autenticação
- Falhas em serviços externos

---

### 2.2 Service Layer (Comunicação entre serviços)

Regista interações entre microserviços internos.

**Eventos registados:**
- Falhas em chamadas HTTP entre serviços
- Erros de comunicação com workspace-service
- Falhas em escrita/leitura distribuída
- Erros de integração com serviços externos
- Timeouts e erros de rede

---

### 2.3 Data Access Layer (Repositories)

Regista operações de persistência na base de dados.

**Eventos registados:**
- CREATE, READ, UPDATE, DELETE de entidades
- Falhas de acesso a dados
- Operações negadas por permissões
- Inconsistências de dados

---

## 3. Formato dos logs (V16.2.4)

Todos os logs seguem formato estruturado e consistente:

### Exemplo:

2026-06-15T12:00:00Z | INFO | event=workspace_created | who=user123 | workspace_id=abc | ip=127.0.0.1


**Campos obrigatórios em cada log:**
- timestamp (UTC)
- level (INFO, WARNING, ERROR)
- event (ação executada)
- who (identificador do utilizador)
- resource identifiers (workspace_id, doc_id)
- contexto adicional quando necessário

---

## 4. Armazenamento de logs (V16.2.3)

Os logs são armazenados localmente:

logs/app.log


Implementação:
- RotatingFileHandler
- Máximo 10MB por ficheiro
- 5 backups automáticos
- StreamHandler para output em consola (debug)

---

## 5. Retenção de logs

- Retenção baseada em rotação automática
- Substituição de logs antigos
- Sem retenção permanente indefinida
- Gestão automática por tamanho de ficheiro

---

## 6. Proteção de logs (V16.4)

- Sanitização de inputs para evitar log injection
- Remoção de caracteres perigosos (\n, \r, |)
- Não são registados dados sensíveis (tokens, passwords, cookies)
- Apenas identificadores técnicos são registados (IDs)
- Logs não são editáveis pelo utilizador

---

## 7. Sincronização temporal (V16.2.2)

- Todos os timestamps são gerados em UTC
- Formato ISO 8601 consistente
- Garantia de consistência entre serviços distribuídos

---

## 8. Controlo de acesso aos logs (V16.2.3)

- Logs armazenados localmente no servidor
- Sem exposição via API
- Acesso restrito a administradores do sistema
- Sem envio para serviços externos de logging

---

## 9. Integridade dos logs

- Logs não podem ser modificados externamente
- RotatingFileHandler garante consistência e rotação
- StreamHandler apenas para debugging local

---

## 10. Eventos de segurança registados (V16.3)

- Autenticação (sucesso e falha)
- Autorização negada
- Acessos inválidos a recursos
- Falhas em integração entre serviços
- Erros inesperados da aplicação

---

## 11. Utilização dos logs

Os logs são utilizados para:

- Auditoria de segurança
- Investigação de incidentes
- Debug da aplicação
- Monitorização de sistema
- Rastreabilidade de ações de utilizadores

---

## 12. Conclusão

A implementação de logging cumpre os requisitos do OWASP ASVS V16, garantindo:

- Inventário completo de eventos  
- Formato estruturado e consistente  
- Uso de UTC  
- Proteção contra log injection  
- Armazenamento controlado  
- Controlo de acesso aos logs  
- Suporte a auditoria e investigação de segurança  