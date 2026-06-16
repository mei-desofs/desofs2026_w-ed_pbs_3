from flask import Flask, jsonify, request, Blueprint, render_template, redirect, url_for
from flask_jwt_extended import unset_access_cookies, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_refresh_cookies
from src.API.Application.user_service import UserService, AuthenticationError
from src.domain.user.value_objects import InvalidUserNameError, LengthError, RockError, PasswordError
from src.infrastructure.persistance.userDB import get_user_by_id
from src.infrastructure.logging.logger_config import (
    logger,
    sanitize_log
)
import traceback
from extensions import limiter, oauth
from authlib.integrations.flask_client import OAuth

user_service = UserService()

user_bp = Blueprint("users",__name__, template_folder='./user_templates', static_folder='./user_templates')
@user_bp.route('/', methods = ['POST', 'GET'])
@limiter.limit("5 per 15 minutes")
def user_login():
    if request.method == 'GET':
        return render_template('/login.html')
    
    #auth
    data = request.get_json()
    try:
        resp = jsonify({"redirect": url_for("users.mainpage")})
        a_token, r_token = user_service.authenticate(data['email'], data['password'])
        set_access_cookies (resp, a_token)
        set_refresh_cookies (resp, r_token)

        logger.info(
            f"event=login_success | username={sanitize_log(data['email'])}"
        )
    
        return resp
    except AuthenticationError:
        logger.warning(
            f"event=login_failure | username={sanitize_log(data['email'])}"
        )
        return jsonify({"error": "Credenciais inválidas"}), 401

#Rota que o utilizador usa para login google
@user_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('users.google_callback', _external=True)
    #Authlib gera e valida internamente o param anti-CSRF 
    return oauth.google.authorize_redirect(redirect_uri)

@user_bp.route('/login/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            return jsonify({"error": "Não foi possível obter dados do Google."}), 400

        google_id = user_info.get('sub') # ID Imutável (ASVS Requirement)
        email = user_info.get('email')   # username inicial do sistema

        #utenticar ou criar o utilizador via OAuth
        a_token, r_token = user_service.authenticate_oauth(oauth_provider='google', oauth_id=google_id,  email_str=email)

        logger.info(
            f"event=oauth_login_success | provider=google | email={sanitize_log(email)}"
        )
        resp = redirect(url_for("users.mainpage"))
        set_access_cookies(resp, a_token)
        set_refresh_cookies(resp, r_token)
        
        return resp

    except AuthenticationError as e:
        logger.warning(
            "event=oauth_login_failed | provider=google"
        )
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        logger.error(
            f"event=oauth_login_error | error={sanitize_log(str(e))}"
        )
        return jsonify({"error": "Falha na autenticação externa."}), 500

@user_bp.route('/regist', methods=['POST', 'GET'])
def regist():
    if request.method == 'GET':
        return render_template('/regist.html')
    
    # Validação de JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "O corpo da requisição deve ser um JSON válido."}), 400

    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Os campos 'username' e 'password' são obrigatórios."}), 400
    
    try:
       #registo
        new_user = user_service.register_user(username, password)
        resp = jsonify({"redirect": url_for("users.user_login")})
        return resp, 201

    except InvalidUserNameError as e:
        # 409 Conflict é o status para duplicação de usernames
        return jsonify({"error": str(e)}), 409

    except PasswordError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Ocorreu um erro interno no servidor. Por favor, tente mais tarde."}), 500


@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    identity = get_jwt_identity()
    raw_refresh_token = request.cookies.get("refresh_token_cookie")

    new_atoken = user_service.refresh_atoken(identity, raw_refresh_token)

    resp = jsonify({"msg": "token refreshed"})
    set_access_cookies(resp, new_atoken, max_age=900)

    logger.info(
        f"event=token_refreshed | user={sanitize_log(identity)}"
    )

    return resp
    
@user_bp.route('/mainpage', methods = ['GET'])
@jwt_required()
def mainpage():
    if request.method == 'GET':
        return render_template('/mainpage.html')

@user_bp.route('/get_current_user', methods=['GET'])
@jwt_required(optional=True)
def get_current_user():
    """
    Obtém informação do utilizador autenticado.

    Returns:
        Username do utilizador autenticado.
    """

    user_id = get_jwt_identity()

    user = get_user_by_id(user_id)

    if user is None:
        return jsonify({
            "error": "Utilizador não encontrado"
        }), 404

    return jsonify({
        "logged_as": user._username
    }), 200

@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Termina a sessão do utilizador autenticado.
    """

    resp = jsonify({
        "redirect": url_for("users.user_login")
    })

    unset_access_cookies(resp)
    unset_refresh_cookies(resp)

    logger.info(
        f"event=logout | user={sanitize_log(get_jwt_identity())}"
    )

    return resp, 200

@user_bp.route('/change_password', methods=['GET','POST'])
@jwt_required()
def change_password():
    """
    Altera a password do utilizador autenticado.
    """

    if request.method == 'GET':
        return render_template('/alterPassw.html')
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "O corpo da requisição deve ser um JSON válido."}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        return jsonify({"error": "Todos os campos são obrigatórios."}), 400
    
    user_id = get_jwt_identity()

    if new_password != confirm_password:
        return jsonify({"error": "As novas passwords não coincidem."}), 400
    
    try:
        user_service.change_password(user_id, current_password, new_password)
        
        return jsonify({"redirect": url_for("users.user_login")}), 200

    except (AuthenticationError, PasswordError) as e:
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        # Log de segurança para erros inesperados do sistema (ex: quebra de ligação à BD)
        print(f"[CRITICAL] Erro inesperado na rota: {e}")
        return jsonify({"error": "Ocorreu um erro interno no sistema."}), 500
