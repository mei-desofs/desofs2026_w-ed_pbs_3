import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from src.API.Application.user_service import UserService, AuthenticationError 


# Fixture: Configura uma app Flask mínima para o JWT funcionar nos testes
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    JWTManager(app)
    return app

# Fixture: Cria uma instância do serviço para cada teste
@pytest.fixture
def user_service():
    return UserService()

# --- TESTES UNITÁRIOS ---

def test_authenticate_success(app, user_service):
    """Testa se o login com credenciais corretas retorna os tokens"""
    with app.app_context():
        access_token, refresh_token = user_service.authenticate('admin', 'password')
        
        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)

def test_authenticate_invalid_credentials(app, user_service):
    """Testa se o login falha com credenciais erradas"""
    with app.app_context():
        # Verifica se a exceção correta é lançada
        with pytest.raises(AuthenticationError):
            user_service.authenticate('user_errado', 'pass_errada')

def test_refresh_token_success(app, user_service):
    """Testa se a geração de um novo access token funciona"""
    with app.app_context():
        email = "test@example.com"
        new_token = user_service.refreshtoken(email)
        
        assert new_token is not None
        assert isinstance(new_token, str)