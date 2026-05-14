import uuid
from value_objects import UserName, HashedPassword

class User:
    def __init__(self, user_id: uuid.UUID, user_name: UserName, password: HashedPassword):
        self.id = user_id
        self._user_name = user_name
        self._password = password

    @classmethod
    def create(cls, user_name_str: str, plain_password_str: str):
        user_id = uuid.uuid4()
        user_name = UserName.validate_and_create(user_name_str)
        password = HashedPassword.create_from_plain_text(plain_password_str)
        
        return cls(user_id, user_name, password)

    @property
    def user_name(self) -> str:
        return self._user_name.value

    @property
    def password_hash(self) -> str:
        return self._password.value

    def __repr__(self):
        return f"<User {self.id} | {self.user_name}>"