from flask import Flask, jsonify, request
import json
from flask_jwt_extended import create_access_token, create_refresh_token
from src.domain.user.entities import User
from src.domain.user.value_objects import InvalidUserNameError, PasswordError
from src.infrastructure.persistance.userDB import find_by_username, create_user, get_user_by_username, UserPersistanceError
from src.infrastructure.persistance.access_tokensDB import save_refresh_token,revoke_token,find_valid_token, RefreshTokenPersistenceError
from datetime import datetime, timedelta, timezone
from src.domain.user.value_objects import HashedPassword
import traceback

class AuthenticationError(Exception):
    pass

class UserService:
    def authenticate(self, username_str, password_raw) -> tuple[str, str]:
        """
        Valida credencias de login
        ARGS: username_str (str), password_raw(str)
        returns: token de acesso e refresh token caso a validação seja bem sucedida
        """

        if not username_str or not password_raw:
            raise AuthenticationError("Não foram recebidas credenciais")

        user = get_user_by_username(username_str)
        if user is None:
            raise AuthenticationError("Username inválido")

        if not user._HashedPassword.matches(user._password_hash, password_raw):
            raise AuthenticationError("Credenciais inválidas")

        a_token = create_access_token(identity=username_str)
        r_token = create_refresh_token(identity=username_str)

        # Limpa o hash da senha e a senha em plain text para segurança
        user._password_hash.set_passw_to0s()  
        password_raw = "0"*len(password_raw)  
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(days=30) 
            save_refresh_token(
                user_id=str(user.id),
                raw_token=r_token,
                expires_at=expires_at,
            )
        except RefreshTokenPersistenceError as e:
            print(f"[ERROR] Falha ao persistir refresh token para {username_str}: {e}")
            raise Exception("Erro interno ao completar o login.")

        return a_token, r_token
        
    def refresh_atoken(self, username_str:str, raw_refresh_token:str) -> str:
        """
        Atualiza o access token a JWT
        ARGS: username_str(str), raw_refresh_token(str)
        returns: token
        """
        token_data = find_valid_token(raw_refresh_token)
        if not token_data:
            raise AuthenticationError("Refresh token inválido ou revogado.")
        new_atoken = create_access_token(identity=username_str)
        return new_atoken
    
    def register_user(self, username_raw: str, password_raw: str):
        """
        Cria Utilizador a partir de informação raw
        ARGS = username_raw(str), password_raw(str)
        returns: new_user ou outputs de excessões
        """
        try:
            # Criação e validação no Aggregate Root
            new_user = User.create(username_raw, password_raw)

            # Usar propriedade pública se existir, caso contrário mantém o atributo
            username_val = getattr(new_user, 'username', new_user._username)

            # Verificação de duplicidade de username
            if find_by_username(username_val):
                raise InvalidUserNameError("Este nome de utilizador já está ocupado.")
            
            # Persistência
            try:
                create_user(new_user)
            except UserPersistanceError as e:
                print(f"[ERROR] Falha na base de dados ao registar {username_val}: {e}")
                raise Exception("Não foi possível persistir os dados do utilizador de momento.")
            
            print(f"[LOG] Utilizador {username_val} registado com sucesso.")

            return new_user

        except (InvalidUserNameError, PasswordError) as e:
        # Relança os erros de domínio para que o Controller
            raise e
        
        except Exception as e:
            # Log centralizado do erro real para auditoria interna (Prevenção de fuga de informação)
            print(f"[CRITICAL ERROR] Falha inesperada no registo: {e}")
            print(traceback.format_exc())

            raise Exception("Ocorreu um erro interno no sistema.")
