import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from src.API.Application.user_service import UserService, AuthenticationError 
from src.domain.user.value_objects import HashedPassword, PasswordError, HashedPassword, InvalidUserNameError
from unittest.mock import MagicMock, patch


# Fixtures, sumulações para teste
@pytest.fixture
def app():
    """App Flask mínima para que o contexto JWT funcione."""
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    app.config["JWT_ALGORITHM"] = "HS256"
    JWTManager(app)
    return app


@pytest.fixture
def svc():
    """Instância limpa do serviço para cada teste."""
    return UserService()


def _make_user(user_id="user-uuid-1234", username="testuser"):
    """fbrica de utilizadores mock reutilizável."""
    user = MagicMock()
    user.id = user_id
    user._username = username
    user.username = username
    user._password_vo = MagicMock()
    user.password_vo = user._password_vo          # alias usado em set_passw_to0s()
    return user



# authenticate()


class TestAuthenticate:

    BASE = "src.API.Application.user_service"

    def test_raises_when_credentials_missing(self, app, svc):
        """Deve rejeitar quando username ou password estão vazios."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="credenciais"):
                svc.authenticate("", "")

    def test_raises_when_username_not_found(self, app, svc):
        """Deve rejeitar quando o username não existe na BD."""
        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_username", return_value=None):
                with pytest.raises(AuthenticationError, match="Username inválido"):
                    svc.authenticate("naoexiste", "qualquerpass")

    def test_raises_when_password_wrong(self, app, svc):
        """Deve rejeitar quando a password não corresponde ao hash guardado."""
        user = _make_user()
        user._password_vo.matches.return_value = False

        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_username", return_value=user), \
                 patch(f"{self.BASE}.revoke_all_user_tokens"):
                with pytest.raises(AuthenticationError, match="Credenciais inválidas"):
                    svc.authenticate("testuser", "passErrada")

    def test_success_returns_tokens(self, app, svc):
        """Deve retornar access token e refresh token válidos com credenciais corretas."""
        user = _make_user()
        user._password_vo.matches.return_value = True

        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_username", return_value=user), \
                 patch(f"{self.BASE}.revoke_all_user_tokens"), \
                 patch(f"{self.BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate("testuser", "correctPass1!")

        assert isinstance(a_token, str) and a_token
        assert isinstance(r_token, str) and r_token

    def test_revoke_failure_does_not_abort_login(self, app, svc):
        """Uma falha ao revogar sessões anteriores NÃO deve impedir o login (warn apenas)."""
        from src.infrastructure.persistance.access_tokensDB import RefreshTokenPersistenceError

        user = _make_user()
        user._password_vo.matches.return_value = True

        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_username", return_value=user), \
                 patch(f"{self.BASE}.revoke_all_user_tokens",
                       side_effect=RefreshTokenPersistenceError("DB down")), \
                 patch(f"{self.BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate("testuser", "correctPass1!")

        assert a_token and r_token  # login concluído na mesma

    def test_raises_when_refresh_token_persistence_fails(self, app, svc):
        """Deve propagar AuthenticationError se save_refresh_token falhar."""
        from src.infrastructure.persistance.access_tokensDB import RefreshTokenPersistenceError

        user = _make_user()
        user._password_vo.matches.return_value = True

        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_username", return_value=user), \
                 patch(f"{self.BASE}.revoke_all_user_tokens"), \
                 patch(f"{self.BASE}.save_refresh_token",
                       side_effect=RefreshTokenPersistenceError("DB down")):
                with pytest.raises(AuthenticationError, match="indisponível"):
                    svc.authenticate("testuser", "correctPass1!")


# authenticate_oauth()
class TestAuthenticateOAuth:

    BASE = "src.API.Application.user_service"
 
    def test_raises_when_oauth_data_missing(self, app, svc):
        """Deve rejeitar quando oauth_id ou oauth_provider estão vazios."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="inválidos"):
                svc.authenticate_oauth("", "", "email@exemplo.com")
 
    def test_registers_new_user_when_not_found(self, app, svc):
        """Deve criar utilizador novo quando não existe conta OAuth correspondente."""
        new_user = _make_user(username="email_exemplo_com")
 
        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_oauth", return_value=None), \
                 patch(f"{self.BASE}.find_by_username", return_value=None), \
                 patch(f"{self.BASE}.User.create_oauth", return_value=new_user), \
                 patch(f"{self.BASE}.create_user_oauth"), \
                 patch(f"{self.BASE}.revoke_all_user_tokens"), \
                 patch(f"{self.BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate_oauth(
                    "google", "google-sub-999", "email@exemplo.com"
                )
 
        assert a_token and r_token
 
    def test_logs_in_existing_oauth_user(self, app, svc):
        """Deve emitir tokens para utilizador OAuth já registado."""
        existing_user = _make_user(username="utilizador_existente")
 
        with app.app_context():
            with patch(f"{self.BASE}.get_user_by_oauth", return_value=existing_user), \
                 patch(f"{self.BASE}.revoke_all_user_tokens"), \
                 patch(f"{self.BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate_oauth(
                    "google", "google-sub-111", "existente@exemplo.com"
                )
 
        assert a_token and r_token


# refresh_atoken()

class TestRefreshAtoken:

    BASE = "src.API.Application.user_service"

    def test_raises_when_token_invalid_or_revoked(self, app, svc):
        """Deve rejeitar refresh token inválido ou já revogado."""
        with app.app_context():
            with patch(f"{self.BASE}.find_valid_token", return_value=None):
                with pytest.raises(AuthenticationError, match="inválido ou revogado"):
                    svc.refresh_atoken("user-uuid-1234", "token-invalido")

    def test_success_returns_new_access_token(self, app, svc):
        """Deve retornar um novo access token quando o refresh token é válido."""
        with app.app_context():
            with patch(f"{self.BASE}.find_valid_token", return_value=MagicMock()):
                new_token = svc.refresh_atoken("user-uuid-1234", "token-valido")

        assert isinstance(new_token, str) and new_token



# register_user()
class TestRegisterUser:

    BASE = "src.API.Application.user_service"
 
    def test_raises_when_username_already_taken(self, app, svc):
        """Deve rejeitar registo se o username já estiver em uso."""
        mock_user = _make_user()
 
        with app.app_context():
            with patch(f"{self.BASE}.User.create", return_value=mock_user), \
                 patch(f"{self.BASE}.find_by_username", return_value=MagicMock()):
                with pytest.raises(InvalidUserNameError):
                    svc.register_user("testuser", "ValidPass1!")
 
    def test_raises_domain_error_on_invalid_username(self, app, svc):
        """Deve propagar InvalidUserNameError lançada pelo agregado de domínio."""
        with app.app_context():
            with patch(f"{self.BASE}.User.create",
                       side_effect=InvalidUserNameError("Username inválido")):
                with pytest.raises(InvalidUserNameError):
                    svc.register_user("u", "ValidPass1!")
 
    def test_raises_domain_error_on_weak_password(self, app, svc):
        """Deve propagar PasswordError lançada pelo agregado de domínio."""
        with app.app_context():
            with patch(f"{self.BASE}.User.create",
                       side_effect=PasswordError("Password fraca")):
                with pytest.raises(PasswordError):
                    svc.register_user("testuser", "fraca")

 
    def test_success_returns_user_with_zeroed_password(self, app, svc):
        """Registo bem-sucedido deve retornar utilizador com hash zerado em memória."""
        mock_user = _make_user()
 
        with app.app_context():
            with patch(f"{self.BASE}.User.create", return_value=mock_user), \
                 patch(f"{self.BASE}.find_by_username", return_value=None), \
                 patch(f"{self.BASE}.create_user"):
                result = svc.register_user("testuser", "ValidPass1!")
 
        assert result is mock_user
        mock_user.password_vo.set_passw_to0s.assert_called_once()


# HashedPassword — testes de Value Object

class TestHashedPassword:

    def test_password_min_length_accepted(self):
        """Password no limite mínimo deve ser aceite sem exceção."""
        vo = HashedPassword.create_from_plain_text("ValidPass1!")
        assert vo.value is not None
 
    def test_password_64_chars_accepted(self):
        """Password com 64 caracteres deve ser aceite (limite recomendado ASVS)."""
        long_pass = "A" * 60 + "1!aB"  # 64 chars com complexidade
        vo = HashedPassword.create_from_plain_text(long_pass)
        assert vo.matches(long_pass) is True
 
    def test_password_at_least_64_characters_permitted(self):
        """Passwords com mais de 64 caracteres devem ser aceites (ASVS 5.0 §2.1.2)."""
        long_password = "a" * 70
        vo = HashedPassword.create_from_plain_text(long_password)
        assert vo.value is not None
        assert vo.matches(long_password) is True
 
    def test_hash_is_not_plaintext(self):
        """O valor guardado nunca deve ser igual ao texto simples."""
        plain = "SecretPass99!"
        vo = HashedPassword.create_from_plain_text(plain)
        assert vo.value != plain
 
    def test_wrong_password_does_not_verify(self):
        """Uma password diferente não deve verificar contra o hash guardado."""
        vo = HashedPassword.create_from_plain_text("CorrectHorse1!")
        assert vo.matches("WrongHorse1!") is False
 
    def test_set_passw_to0s_clears_value(self):
        """set_passw_to0s() deve zerar o valor em memória."""
        vo = HashedPassword.create_from_plain_text("SecretPass99!")
        vo.set_passw_to0s()
        # Após zerar, o valor deve ser None, vazio, ou composto apenas de '0'
        zeroed = vo.value if hasattr(vo, "value") else vo._value
        assert not zeroed or set(str(zeroed)) == {"0"}
 