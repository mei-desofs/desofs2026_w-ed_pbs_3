from flask import Flask, jsonify, request
import json
from flask_jwt_extended import create_access_token

class AuthenticationError(Exception):
    pass

class UserService:
    def authenticate(self, email_str, password_raw) -> json:
        """
        Valida credencias de login
        ARGS: email_str (str), password_raw(str)
        returns: token caso a validação seja bem sucedida
        """
        if email_str == 'admin' and password_raw == 'password':
            token = create_access_token(identity=email_str)
            return token
        else:
            raise AuthenticationError()