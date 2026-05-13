from flask import Flask, jsonify, request
import json
from flask_jwt_extended import create_access_token, create_refresh_token

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