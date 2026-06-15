# ASVS File Handling Policy — V5.1.1

## 1. Objetivo

Este documento define as regras de processamento, armazenamento e segurança de ficheiros na aplicação, em conformidade com o requisito OWASP ASVS V5.1.1.

---

## 2. Tipos de ficheiros permitidos

A aplicação apenas permite ficheiros nos seguintes formatos:

- Markdown (`.md`)

Não são permitidos outros tipos de ficheiros, incluindo ficheiros executáveis ou binários.

---

## 3. Tamanho máximo de ficheiros

- Tamanho máximo permitido por ficheiro: **100 KB**
- O tamanho é validado antes da persistência do conteúdo

---

## 4. Origem dos ficheiros

- Os ficheiros são gerados internamente pela aplicação
- Não existe funcionalidade de upload de ficheiros por utilizadores externos

---

## 5. Armazenamento

Os ficheiros são armazenados em diretórios isolados por utilizador e workspace:

/workspaces/{user_id}/{workspace_id}/documents/


---

## 6. Segurança e execução

- Os ficheiros não são executados pelo servidor
- Não existe processamento server-side de código dentro dos ficheiros
- O acesso aos ficheiros é controlado pela aplicação

---

## 7. Tratamento de ficheiros inválidos

- Ficheiros acima do limite de tamanho são rejeitados
- Conteúdo inválido não é persistido
- Eventos de erro são registados em logs de segurança

---

## 8. Conclusão

A aplicação garante controlo sobre tipos de ficheiros, tamanho e armazenamento, prevenindo execução de ficheiros maliciosos e reduzindo riscos de segurança associados ao processamento de ficheiros.