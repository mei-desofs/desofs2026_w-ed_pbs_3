from flask import Flask, jsonify, request
import json
from flask_jwt_extended import create_access_token, create_refresh_token
from src.domain.user.value_objects import InvalidUserNameError, PasswordError
from src.domain.user.entities import User

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
            #Criação e validação no Aggregate Root
            new_user = User.create(username_raw, password_raw)


            #TODO Implementar restante lógica de validação como verificação de password com a repetição e verficações de BD
            # 2. Verificação de unicidade (Lógica de Negócio de nível de Serviço)
            #Vericiar se o username já existe na BD
            # if self.user_repository.find_by_username(new_user.user_name):
            #     raise InvalidUserNameError("Este nome de utilizador já está ocupado.")

            # 3. Persistência (Simulada por agora)
            # self.user_repository.save(new_user)
            
            print(f"[LOG] Utilizador {new_user.user_name} registado com sucesso.")
            return new_user

        except (InvalidUserNameError, PasswordError) as e:
            # RELANÇAR as exceções de domínio para serem capturadas pelo Controller
            raise e
        except Exception as e:
            # Log de erros inesperados
            print(f"[CRITICAL ERROR] Falha inesperada no registo: {e}")
            raise Exception("Ocorreu um erro interno no sistema.")