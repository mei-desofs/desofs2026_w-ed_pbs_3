# V13.1.1 — Documentação de Configuração e Comunicação da Aplicação

## 1. Objetivo

Este documento descreve todas as necessidades de comunicação da aplicação, incluindo serviços internos, bases de dados e mecanismos de autenticação, conforme o requisito OWASP ASVS V13.1.1.

---

## 2. Serviços da Aplicação

### 2.1 Serviço Principal (API Flask)

- Responsável por toda a lógica de negócio da aplicação
- Expõe endpoints para gestão de:
  - utilizadores
  - workspaces
  - documentos

---

### 2.2 Serviço Workspace

- URL: `http://workspace:8000`
- Tipo: serviço interno
- Funções:
  - criação de workspaces
  - escrita de documentos no sistema de ficheiros

**Autenticação:**
- Header: `X-Service-Token`

---

### 2.3 Base de Dados (MySQL)

- Utilizada para persistência de dados:
  - utilizadores
  - workspaces
  - documentos

- Acesso feito através de camada de repositório
- Executada em container interno isolado

---

### 2.4 Autenticação

- Baseada em JWT
- Autenticação do utilizador via cookie:
  - `access_token_cookie`

---

## 3. Comunicação entre Serviços

- Todas as comunicações são server-to-server controladas
- Não existem ligações externas dinâmicas definidas pelo utilizador
- Todos os endpoints são fixos ou definidos por variáveis de ambiente

---

## 4. Segurança da Comunicação

- Comunicação entre serviços protegida por tokens internos
- Não existe exposição direta de serviços internos ao utilizador final
- Todas as chamadas são validadas no backend

---

## 5. Conclusão

Todas as comunicações da aplicação estão identificadas, controladas e documentadas, garantindo conformidade com OWASP ASVS V13.1.1.