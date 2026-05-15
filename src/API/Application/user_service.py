from flask import Flask, jsonify, request
import json
from flask_jwt_extended import create_access_token, create_refresh_token
from src.domain.user.entities import User
from src.domain.user.value_objects import InvalidUserNameError, PasswordError
from src.infrastructure.persistance.userDB import find_by_username, create_user, UserPersistanceError
class AuthenticationError(Exception):
    pass

class UserService:
    def authenticate(self, email_str, password_raw) -> tuple[str, str]:
        """
        Valida credencias de login
        ARGS: email_str (str), password_raw(str)
        returns: token de acesso e refresh token caso a validação seja bem sucedida
        """
        #TODO Fazer Alteração quando lógica de BD for implementada
        #TODO inseir tempo de duração de token

        #!! Verificação manual a ser alterada
        if email_str == 'admin' and password_raw == 'password':
            a_token = create_access_token(identity=email_str)
            r_token = create_refresh_token(identity=email_str)
            return a_token, r_token
        else:
            raise AuthenticationError()
        
    def refreshtoken(self, email_str) -> str:
        """
        Atualiza o token a JWT
        ARGS: email_str(str)
        returns: token
        """

        new_token = create_access_token(identity=email_str)
        return new_token
    
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

            # TODO: Implementar registo de tokens
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
        # Relança os erros de domínio para que o Controller decida o status HTTP
            raise e
        
        except Exception as e:
            # Log centralizado do erro real para auditoria interna (Prevenção de fuga de informação)
            print(f"[CRITICAL ERROR] Falha inesperada no registo: {e}")
            raise Exception("Ocorreu um erro interno no sistema.")