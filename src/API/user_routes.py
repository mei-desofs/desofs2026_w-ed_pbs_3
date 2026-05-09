from flask import Flask, jsonify, request, Blueprint
from flask_jwt_extended import unset_access_cookies, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies
from src.API.Application.user_service import UserService, AuthenticationError

user_service = UserService()

user_bp = Blueprint("users",__name__)
@user_bp.route('/login', methods = ['POST'])
def user_login():
    data = request.json
    try:
        resp = jsonify({"msg": "Login Successful"})
        a_token, r_token = user_service.authenticate(data['email'], data['password'])
        set_access_cookies (resp, a_token)
        set_refresh_cookies (resp, r_token)

        return resp, 200
    except AuthenticationError:
        return jsonify({"error": "Credenciais inválidas"}), 401


#É necessário criar função JS que chame este endpoint para atualizar o token
@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():

    identity = get_jwt_identity()

    new_token = user_service.refreshtoken(identity)

    resp = jsonify({"msg": "token refreshed"})

    set_access_cookies(resp, new_token)

    return resp
    
@user_bp.route('/mainpage', methods = ['POST'])
@jwt_required()
def mainpage():
    try:
        current_user = get_jwt_identity()
        return jsonify({"logged_as": current_user}), 200
    
    except AuthenticationError:
        return jsonify({"error": "Token not found"}), 401
    
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