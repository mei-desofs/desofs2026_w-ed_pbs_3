# V13.1.3 — Estratégia de Gestão de Recursos

## 1. Objetivo

Este documento define a estratégia de gestão de recursos da aplicação, incluindo base de dados, comunicação HTTP e serviços internos, conforme OWASP ASVS V13.1.3.

---

## 2. Comunicação HTTP entre Serviços

A aplicação utiliza a biblioteca `requests` para comunicação entre serviços internos.

### Estratégia definida:

- Chamadas HTTP são síncronas
- Timeout recomendado: 3 a 5 segundos
- Não são utilizados retries automáticos agressivos
- Em caso de falha:
  - a operação é abortada
  - é feito rollback de dados quando necessário
  - o erro é registado em logs

---

## 3. Base de Dados

- Utiliza padrão Repository Pattern
- Gestão de conexão delegada ao driver/ORM
- Não existe gestão manual de conexões
- Operações são curtas e por request

---

## 4. Sistema de Ficheiros

- Escrita de ficheiros realizada através do serviço workspace
- A API principal não acede diretamente ao sistema de ficheiros
- Isto evita bloqueios de I/O no serviço principal

---

## 5. Controlo de Recursos

- Limitação de recursos por utilizador:
  - máximo de workspaces por utilizador
- Rate limiting aplicado a endpoints críticos
- Proteção contra abuso e sobrecarga do sistema

---

## 6. Estratégia de Falhas

- Fail-fast approach aplicado em toda a aplicação
- Não existem loops de retry ilimitados
- Erros são registados e devolvidos de forma controlada
- A aplicação não entra em estados inconsistentes em caso de falha

---

## 7. Conclusão

A aplicação define uma estratégia clara de gestão de recursos, garantindo estabilidade, prevenção de sobrecarga e comportamento previsível em caso de falhas.