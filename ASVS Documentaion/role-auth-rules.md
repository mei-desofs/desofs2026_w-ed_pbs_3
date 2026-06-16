# V8.1.2 – Regras de Autorização Baseadas em Roles

A aplicação implementa um modelo de controlo de acesso baseado em roles (RBAC) para garantir restrições de leitura e escrita sobre recursos de Workspace e Documento.

## Roles

| Role | Permissões |
|--------|--------|
| ADMIN | Criar, visualizar, editar e eliminar documentos. Adicionar, remover e alterar roles de membros do workspace. |
| EDITOR | Visualizar e editar documentos existentes. Não pode criar ou eliminar documentos nem gerir membros. |
| VIEWER | Apenas visualizar documentos e exportar conteúdo autorizado. Não pode criar, editar ou eliminar documentos. |

## Restrições sobre Documentos

| Operação | ADMIN | EDITOR | VIEWER |
|-----------|---------|---------|---------|
| Visualizar Documento | Sim | Sim | Sim |
| Exportar Documento | Sim | Sim | Sim |
| Criar Documento | Sim | Não | Não |
| Editar Documento | Sim | Sim | Não |
| Eliminar Documento | Sim | Não | Não |

## Restrições sobre Membros do Workspace

| Operação | ADMIN | EDITOR | VIEWER |
|-----------|---------|---------|---------|
| Listar Membros | Sim | Sim | Sim |
| Adicionar Membros | Sim | Não | Não |
| Alterar Roles | Sim | Não | Não |
| Remover Membros | Sim | Não | Não |

## Aplicação das Regras

As verificações de autorização são efetuadas no backend através da validação do role do utilizador associado ao workspace antes da execução de qualquer operação de leitura ou escrita.

A autorização é aplicada ao nível do recurso (workspace e documento) e ao nível da operação (read, write, update e delete), impedindo acessos não autorizados mesmo que pedidos sejam manipulados no frontend.

## Implementação

As restrições de autorização são implementadas nos endpoints da API através da obtenção do role do utilizador no workspace:

```python
role = workspace_member_repo.get_role(
    workspace_id,
    user_id
)
```

As permissões são verificadas antes da execução da operação pretendida, retornando HTTP 403 (Forbidden) quando o utilizador não possui privilégios suficientes.

Desta forma, a aplicação garante que o acesso a recursos e operações é controlado de acordo com as permissões atribuídas a cada role.