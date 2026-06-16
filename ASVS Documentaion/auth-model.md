## V8.1.3 — Environmental and Contextual Attributes Used for Authorization

### Observations

No sistema atual, as decisões de autenticação e autorização são baseadas exclusivamente em atributos lógicos do utilizador e do recurso, não sendo utilizados fatores ambientais dinâmicos como localização geográfica, IP, hora do dia ou tipo de dispositivo.

As regras de segurança são aplicadas da seguinte forma:

### 1. Autenticação
- Baseada em JWT (`flask_jwt_extended`)
- O `user_id` é obtido através do token autenticado (`get_jwt_identity()`)

### 2. Autorização
- Baseada em roles atribuídas por workspace:
  - `ADMIN`
  - `EDITOR`
  - `VIEWER`

### 3. Contexto utilizado nas decisões de segurança
As seguintes propriedades são atualmente utilizadas:

- **User identity**
  - `user_id` extraído do JWT

- **Workspace membership**
  - Associação `user_id ↔ workspace_id`

- **Role do utilizador no workspace**
  - Determina permissões:
    - `ADMIN`: criar, editar, eliminar documentos e gerir membros
    - `EDITOR`: editar e visualizar documentos
    - `VIEWER`: apenas leitura

- **Resource attributes**
  - `workspace_id`
  - `document_id`
  - `created_by`
  - estado lógico do recurso (ex: existência no DB)

### 4. Contexto NÃO utilizado
O sistema não utiliza os seguintes atributos ambientais para decisões de segurança:

- IP address do utilizador
- localização geográfica
- hora do dia
- tipo de dispositivo ou user-agent
- fingerprint do dispositivo
- network context (VPN, ASN, etc.)

### 5. Segurança aplicada
- Todas as decisões de autorização são server-side
- Não existe lógica de autorização no frontend
- Todas as rotas protegidas usam `@jwt_required()`
- Roles são validados em cada endpoint crítico

### Conclusão
O sistema implementa um modelo de autorização baseado em RBAC (Role-Based Access Control) dentro do contexto de workspace, sem dependência de atributos ambientais ou contextuais externos.