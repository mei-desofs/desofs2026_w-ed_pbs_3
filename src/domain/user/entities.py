import uuid
from .value_objects import UserName, HashedPassword

class User:
    def __init__(self, user_id: uuid.UUID, user_name: UserName, password: HashedPassword):
        self.id = user_id
        self._username = user_name
        self._password_hash = password

    @classmethod
    def create(cls, username_str: str, plain_password_str: str):
        user_id = str(uuid.uuid4())
        username = UserName.validate_and_create(username_str)
        password_hash = HashedPassword.create_from_plain_text(plain_password_str)
        
        return cls(user_id, username.value, password_hash.value)

    @property
    def username(self) -> str:
        return self._username.value

    @property
    def hash_of_password(self) -> str:
        return self._password_hash.value

    def __repr__(self):
        return f"<User {self.id} | {self.username}>"