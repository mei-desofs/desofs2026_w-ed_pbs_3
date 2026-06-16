import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from unittest.mock import MagicMock, patch

from src.API.Application.user_service import UserService, AuthenticationError
from src.domain.user.value_objects import HashedPassword, PasswordError, InvalidUserNameError


BASE = "src.API.Application.user_service"


# Fixtures
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_DECODE_ALGORITHMS"] = ["HS256"]
    app.config["JWT_DECODE_AUDIENCE"] = None
    JWTManager(app)
    return app


@pytest.fixture
def svc():
    return UserService()


def _make_user(user_id="user-uuid-1234", username="testuser"):
    user = MagicMock()
    user.id = user_id
    user._username = username
    user.username = username
    user._password_vo = MagicMock()
    user.password_vo = user._password_vo
    return user


# authenticate() 

class TestAuthenticate:

    def test_raises_when_credentials_missing(self, app, svc):
        """Deve rejeitar quando username ou password estão vazios."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="credenciais"):
                svc.authenticate("", "")

    def test_raises_when_username_not_found(self, app, svc):
        """Deve rejeitar quando o username não existe na BD."""
        with app.app_context():
            with patch(f"{BASE}.get_user_by_username", return_value=None):
                with pytest.raises(AuthenticationError, match="Username inválido"):
                    svc.authenticate("naoexiste", "qualquerpass")

    def test_raises_when_password_wrong(self, app, svc):
        """Deve rejeitar quando a password não corresponde ao hash guardado."""
        user = _make_user()
        user._password_vo.matches.return_value = False

        with app.app_context():
            with patch(f"{BASE}.get_user_by_username", return_value=user), \
                 patch(f"{BASE}.revoke_all_user_tokens"):
                with pytest.raises(AuthenticationError, match="Credenciais inválidas"):
                    svc.authenticate("testuser", "passErrada")

    def test_success_returns_tokens(self, app, svc):
        """Deve retornar access token e refresh token válidos."""
        user = _make_user()
        user._password_vo.matches.return_value = True

        with app.app_context():
            with patch(f"{BASE}.get_user_by_username", return_value=user), \
                 patch(f"{BASE}.revoke_all_user_tokens"), \
                 patch(f"{BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate("testuser", "correctPass1!")

        assert isinstance(a_token, str) and a_token
        assert isinstance(r_token, str) and r_token

    def test_revoke_failure_does_not_abort_login(self, app, svc):
        """Uma falha ao revogar sessões anteriores NÃO deve impedir o login."""
        from src.infrastructure.persistance.access_tokensDB import RefreshTokenPersistenceError

        user = _make_user()
        user._password_vo.matches.return_value = True

        with app.app_context():
            with patch(f"{BASE}.get_user_by_username", return_value=user), \
                 patch(f"{BASE}.revoke_all_user_tokens",
                       side_effect=RefreshTokenPersistenceError("DB down")), \
                 patch(f"{BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate("testuser", "correctPass1!")

        assert a_token and r_token

    def test_raises_when_refresh_token_persistence_fails(self, app, svc):
        """Deve propagar AuthenticationError se save_refresh_token falhar."""
        from src.infrastructure.persistance.access_tokensDB import RefreshTokenPersistenceError

        user = _make_user()
        user._password_vo.matches.return_value = True

        with app.app_context():
            with patch(f"{BASE}.get_user_by_username", return_value=user), \
                 patch(f"{BASE}.revoke_all_user_tokens"), \
                 patch(f"{BASE}.save_refresh_token",
                       side_effect=RefreshTokenPersistenceError("DB down")):
                with pytest.raises(AuthenticationError, match="indisponível"):
                    svc.authenticate("testuser", "correctPass1!")


# authenticate_oauth()

    def test_raises_when_oauth_data_missing(self, app, svc):
        """Deve rejeitar quando oauth_id ou oauth_provider estão vazios."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match="inválidos"):
                svc.authenticate_oauth("", "", "email@exemplo.com")

    def test_registers_new_user_when_not_found(self, app, svc):
        """Deve criar utilizador novo quando não existe conta OAuth correspondente."""
        new_user = _make_user(username="email_exemplo_com")

        with app.app_context():
            with patch(f"{BASE}.get_user_by_oauth", return_value=None), \
                 patch(f"{BASE}.find_by_username", return_value=None), \
                 patch(f"{BASE}.User.create_oauth", return_value=new_user), \
                 patch(f"{BASE}.create_user_oauth"), \
                 patch(f"{BASE}.revoke_all_user_tokens"), \
                 patch(f"{BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate_oauth(
                    "google", "google-sub-999", "email@exemplo.com"
                )

        assert a_token and r_token

    def test_logs_in_existing_oauth_user(self, app, svc):
        """Deve emitir tokens para utilizador OAuth já registado."""
        existing_user = _make_user(username="utilizador_existente")

        with app.app_context():
            with patch(f"{BASE}.get_user_by_oauth", return_value=existing_user), \
                 patch(f"{BASE}.revoke_all_user_tokens"), \
                 patch(f"{BASE}.save_refresh_token"):
                a_token, r_token = svc.authenticate_oauth(
                    "google", "google-sub-111", "existente@exemplo.com"
                )

        assert a_token and r_token

    def test_raises_when_save_refresh_token_fails_on_oauth(self, app, svc):
        """Deve propagar AuthenticationError se save_refresh_token falhar no fluxo OAuth."""
        from src.infrastructure.persistance.access_tokensDB import RefreshTokenPersistenceError

        existing_user = _make_user(username="utilizador_existente")

        with app.app_context():
            with patch(f"{BASE}.get_user_by_oauth", return_value=existing_user), \
                 patch(f"{BASE}.revoke_all_user_tokens"), \
                 patch(f"{BASE}.save_refresh_token",
                       side_effect=RefreshTokenPersistenceError("DB down")):
                with pytest.raises(AuthenticationError, match="indisponível"):
                    svc.authenticate_oauth("google", "google-sub-111", "existente@exemplo.com")


# refresh_atoken() 
class TestRefreshAtoken:

    def test_raises_when_token_invalid_or_revoked(self, app, svc):
        """Deve rejeitar refresh token inválido ou já revogado."""
        with app.app_context():
            with patch(f"{BASE}.find_valid_token", return_value=None):
                with pytest.raises(AuthenticationError, match="inválido ou revogado"):
                    svc.refresh_atoken("user-uuid-1234", "token-invalido")

    def test_success_returns_new_access_token(self, app, svc):
        """Deve retornar um novo access token quando o refresh token é válido."""
        with app.app_context():
            with patch(f"{BASE}.find_valid_token", return_value=MagicMock()):
                new_token = svc.refresh_atoken("user-uuid-1234", "token-valido")

        assert isinstance(new_token, str) and new_token


#  register_user() 

class TestRegisterUser:

    def test_raises_when_username_already_taken(self, app, svc):
        """Deve rejeitar registo se o username já estiver em uso."""
        mock_user = _make_user()

        with app.app_context():
            with patch(f"{BASE}.User.create", return_value=mock_user), \
                 patch(f"{BASE}.find_by_username", return_value=True):
                with pytest.raises(InvalidUserNameError):
                    svc.register_user("testuser", "ValidPass1!")

    def test_raises_domain_error_on_invalid_username(self, app, svc):
        """Deve propagar InvalidUserNameError lançada pelo agregado de domínio."""
        with app.app_context():
            with patch(f"{BASE}.User.create",
                       side_effect=InvalidUserNameError("Username inválido")):
                with pytest.raises(InvalidUserNameError):
                    svc.register_user("u", "ValidPass1!")

    def test_raises_domain_error_on_weak_password(self, app, svc):
        """Deve propagar PasswordError lançada pelo agregado de domínio."""
        with app.app_context():
            with patch(f"{BASE}.User.create",
                       side_effect=PasswordError("Password fraca")):
                with pytest.raises(PasswordError):
                    svc.register_user("testuser", "fraca")

    def test_success_returns_user_with_zeroed_password(self, app, svc):
        """Registo bem-sucedido deve retornar utilizador com hash zerado em memória."""
        mock_user = _make_user()

        with app.app_context():
            with patch(f"{BASE}.User.create", return_value=mock_user), \
                 patch(f"{BASE}.find_by_username", return_value=False), \
                 patch(f"{BASE}.create_user"):
                result = svc.register_user("testuser", "ValidPass1!")

        assert result is mock_user
        mock_user.password_vo.set_passw_to0s.assert_called_once()


# change_password() 

class TestChangePassword:

    def test_raises_when_user_not_found(self, app, svc):
        """Deve rejeitar se o utilizador não existir na BD."""
        with app.app_context():
            with patch(f"{BASE}.get_user_by_id", return_value=None):
                with pytest.raises(AuthenticationError, match="não encontrado"):
                    svc.change_password("user-uuid-1234", "oldpass", "NewPass1!")

    def test_raises_when_current_password_wrong(self, app, svc):
        """Deve rejeitar se a password atual estiver incorrecta."""
        user = _make_user()
        user._password_vo.matches.return_value = False

        with app.app_context():
            with patch(f"{BASE}.get_user_by_id", return_value=user):
                with pytest.raises(AuthenticationError, match="incorreta"):
                    svc.change_password("user-uuid-1234", "wrongpass", "NewPass1!")

    def test_raises_when_new_password_is_weak(self, app, svc):
        """Deve propagar PasswordError se a nova password for fraca."""
        user = _make_user()
        user._password_vo.matches.return_value = True
        user._password_vo.set_password.side_effect = PasswordError("fraca")

        with app.app_context():
            with patch(f"{BASE}.get_user_by_id", return_value=user):
                with pytest.raises(PasswordError):
                    svc.change_password("user-uuid-1234", "correctpass", "fraca")

    def test_success_changes_password(self, app, svc):
        """Alteração bem-sucedida deve chamar update_password e revogar tokens."""
        user = _make_user()
        user._password_vo.matches.return_value = True
        user._password_vo.set_password.return_value = None
        user._password_hash = "novo-hash"

        with app.app_context():
            with patch(f"{BASE}.get_user_by_id", return_value=user), \
                 patch(f"{BASE}.update_password") as mock_update, \
                 patch(f"{BASE}.revoke_all_user_tokens") as mock_revoke:
                svc.change_password("user-uuid-1234", "correctpass", "NewPass1!")

        mock_update.assert_called_once_with(user)
        mock_revoke.assert_called_once_with("user-uuid-1234")


#  HashedPassword (Value Object)
class TestHashedPassword:

    def test_password_min_length_accepted(self):
        """Password no limite mínimo deve ser aceite."""
        vo = HashedPassword.create_from_plain_text("ValidPass1!")
        assert vo.value is not None

    def test_password_64_chars_accepted(self):
        """Password com 64 caracteres deve ser aceite."""
        long_pass = "A" * 60 + "1!aB"
        vo = HashedPassword.create_from_plain_text(long_pass)
        assert vo.matches(long_pass) is True

    def test_password_over_64_characters_permitted(self):
        """Passwords com mais de 64 caracteres devem ser aceites (ASVS 5.0 §2.1.2)."""
        long_password = "aA1!" * 20  # 80 chars com complexidade
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
        zeroed = vo.value
        assert not zeroed or set(str(zeroed)) == {"0"}

    def test_short_password_raises(self):
        """Password abaixo do mínimo deve levantar LengthError."""
        from src.domain.user.value_objects import LengthError
        with pytest.raises(LengthError):
            HashedPassword.create_from_plain_text("curta")