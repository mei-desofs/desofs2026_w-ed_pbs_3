from werkzeug.security import generate_password_hash, check_password_hash
import re
class PasswordError(Exception): pass
class LengthError(PasswordError): pass
class RockError(PasswordError): pass
class InvalidUserNameError(Exception):pass

class UserName:
    def __init__(self, user_name:str):
        self.user_name = user_name

    @classmethod
    def validate_and_create(cls, user_name: str):
        username = user_name.strip()

        if len(username) < 6 or len(username) > 50:
            raise InvalidUserNameError ("User name inválido, deve ser entre 6 e 50 characteres ")
        if not re.match(r"^\w+$", username):
            raise InvalidUserNameError("Username deve conter apenas letras, números e underscores.")
        
        return cls(username)

    @property
    def value(self):
        return self.value


class HashedPassword:
    COMMON_PASSWORDS = set()
    try:
        with open('rockyou.txt') as f:
            COMMON_PASSWORDS = {line.strip() for line in f}
    except FileNotFoundError:
        print("Aviso: Lista de passwords comuns não encontrada.")

    def __init__(self, hashed_value: str):
        self._value = hashed_value

    @classmethod
    def create_from_plain_text(cls, plain_text: str):
        #Verifica Lenght
        if len(plain_text) < 8:
            raise LengthError("Password muito curta!")
        #Verifica pass comum
        if plain_text in cls.COMMON_PASSWORDS:
            raise RockError("Password demasiado comum.")
        
        #Cria hash com salt 
        hashed_val = generate_password_hash(plain_text, method='scrypt')
        return cls(hashed_val)
            
    @staticmethod
    def verify(hashed_value: str, plain_text: str) -> bool:
        """Função que recebe hash e a senha em plain text
        e compara para aferirir a senha correta
        ARGS: hashed_vale(str), plain_text(str)
        returns: True se correto"""
        return check_password_hash(hashed_value, plain_text)

    @property
    def value(self):
        return self._value

