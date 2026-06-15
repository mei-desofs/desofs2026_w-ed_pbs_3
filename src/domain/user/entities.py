import uuid
from sqlalchemy.orm import reconstructor
from .value_objects import UserName, HashedPassword

class User:
    def __init__(self, user_id: str, user_name: UserName, password: HashedPassword, oauth_provider: str = None, oauth_id: str = None):
        self.id = user_id
        # Atributos que o ORM usa
        self._username = user_name.value
        # Se for OAuth, guardamos None na db, caso contrário o valor do hash
        self._password_hash = password.value if password else None

        # Atributos OAuth 
        self.oauth_provider = oauth_provider
        self.oauth_id = oauth_id

        # Value Objects em memória
        self._username_vo = user_name
        self._password_vo = password

    @classmethod
    def create(cls, username_str: str, plain_password_str: str):
        """Criação para utilizadores tradicionais (com password)"""
        user_id = str(uuid.uuid4())
        username = UserName.validate_and_create(username_str)
        password_hash = HashedPassword.create_from_plain_text(plain_password_str)
        return cls(user_id, username, password_hash)
    
    @classmethod
    def create_oauth(cls, username_str: str, oauth_provider: str, oauth_id: str):
        """Criação segura para utilizadores federados (ASVS 5.0 - Sem password)"""
        user_id = str(uuid.uuid4())
        username = UserName.validate_and_create(username_str)
        
        password_placeholder = HashedPassword("OAUTH_EXTERNAL_ACCOUNT")
        
        user = cls(user_id, username, password_placeholder, oauth_provider, oauth_id)
        
        # Forçar o hash que vai para a db a ser NULL
        user._password_hash = None 
        return user
    
    @reconstructor
    def _reconstruct_from_db(self):
        self._username_vo = UserName(self._username)
        # Se na db estiver NULL (None), usamos com a string sinalizadora para proteger o domínio
        hash_val = self._password_hash if self._password_hash else "OAUTH_EXTERNAL_ACCOUNT"
        self._password_vo = HashedPassword(hash_val)

    @property
    def username(self) -> str:
        return self._username

    @property
    def hash_of_password(self) -> str:
        return self._password_hash  
    
    @property
    def password_vo(self) -> HashedPassword:
        return self._password_vo

    @property
    def username_vo(self) -> UserName:
        return self._username_vo

    def __repr__(self):
        return f"<User {self.id} | {self.username} | OAuth: {self.oauth_provider}>"