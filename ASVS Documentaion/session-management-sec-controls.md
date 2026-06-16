# Session Management & Security Controls (V8.3.3)

## Overview

A aplicação utiliza autenticação baseada em JSON Web Tokens (JWT), sem utilização de sessões server-side tradicionais.

Os tokens JWT são emitidos após autenticação bem-sucedida e utilizados para validar o acesso a todos os endpoints protegidos.

---

## Session Handling Mechanism

- A autenticação é realizada via JWT (`Flask-JWT-Extended`)
- O token é armazenado no cliente e enviado em cada request através do header `Authorization`

---

## Token Expiration & Validity

- Os tokens possuem tempo de expiração configurado (TTL)
- Após expiração, o utilizador deve autenticar novamente
- Tokens expirados são automaticamente rejeitados pelo middleware JWT

---

## Logout & Session Invalidation

- O logout remove o token do lado do cliente
- Não existe blacklist de tokens (modelo stateless)
- A invalidação ocorre naturalmente após expiração do JWT

---

## Security Controls

- Tokens são assinados digitalmente e validados no backend
- O acesso a recursos protegidos requer JWT válido
- Cada request valida identidade via `get_jwt_identity()`

---

## Risk Considerations

- Não existe reutilização de sessão server-side
- Não existe sessão persistente entre dispositivos
- Não são utilizados refresh tokens nem step-up authentication

---

## Summary

A aplicação implementa um modelo de sessão stateless baseado em JWT, garantindo autenticação segura com expiração de token e validação por request.