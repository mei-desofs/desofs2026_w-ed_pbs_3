from flask import Flask, jsonify, request, Blueprint, render_template, redirect, url_for
from flask_jwt_extended import unset_access_cookies, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies
from src.API.Application.user_service import UserService, AuthenticationError
from src.domain.user.value_objects import InvalidUserNameError, LengthError, RockError
user_service = UserService()

user_bp = Blueprint("users",__name__, template_folder='./user_templates', static_folder='./user_templates')
@user_bp.route('/', methods = ['POST', 'GET'])
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
    
        return resp
    except AuthenticationError:
        return jsonify({"error": "Credenciais inválidas"}), 401


#É necessário criar função JS que chame este endpoint para atualizar o token
@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    identity = get_jwt_identity()

    new_token = user_service.refreshtoken(identity)

    resp = jsonify({"msg": "token refreshed"})
    set_access_cookies(resp, new_token, max_age=900)

    return resp
    
@user_bp.route('/mainpage', methods = ['GET'])
def mainpage():
    if request.method == 'GET':
        return render_template('/mainpage.html')

#Talvez venha a remover, serve apenas para testar a mainpage
@user_bp.route('/get_current_user')
@jwt_required(optional=True)
def get_current_user():
    return jsonify({"logged_as": get_jwt_identity()}), 200

@user_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('/register.html')

    data = request.get_json()
    
    try:
        # O serviço vai chamar o User.create(), que chama o UserName.validate()
        user_service.register_user(data['username'], data['password'])
        return jsonify({"msg": "Utilizador criado com sucesso!"}), 201

    except (InvalidUserNameError, LengthError, RockError) as e:
        # Captura de Errors específicos do Value Object
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # Um "catch-all" para erros inesperados (ex: BD em baixo)
        # Aqui enviamos 500 porque o erro é do nosso lado
        return jsonify({"error": "Erro interno no servidor"}), 500

#TODO Rever logout
@user_bp.route('/logout',methods = ['POST'])
@jwt_required()
def logout():
    resp = jsonify({"msg": "Logout Successful"})
    unset_access_cookies
    return resp, 200
