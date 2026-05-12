from flask import Flask, jsonify, request, Blueprint, render_template, redirect, url_for
from flask_jwt_extended import unset_access_cookies, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies
from src.API.Application.user_service import UserService, AuthenticationError

user_service = UserService()

user_bp = Blueprint("users",__name__, template_folder='./user_templates')
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
@user_bp.route('/refresh', methods=['POST', 'GET'])
@jwt_required(refresh=True)
def refresh():

    identity = get_jwt_identity()

    new_token = user_service.refreshtoken(identity)

    resp = jsonify({"msg": "token refreshed"})
    set_access_cookies(resp, new_token)

    return resp
    
@user_bp.route('/mainpage', methods = ['GET'])
@jwt_required()
def mainpage():
    if request.method == 'GET':
        return render_template('/mainpage.html')

#Talvez venha a remover, serve apenas para testar a mainpage
@user_bp.route('/get_current_user')
@jwt_required()
def get_current_user():
    return jsonify({"logged_as": get_jwt_identity()}), 200

@user_bp.route('/logout',methods = ['POST'])
@jwt_required()
def logout():
    resp = jsonify({"msg": "Logout Successful"})
    unset_access_cookies
    return resp, 200


@user_bp.route('/profile', methods=['POST'])
@jwt_required()
def profile():

    current_user = get_jwt_identity()

    return jsonify({
        "logged_as": current_user
    }), 200