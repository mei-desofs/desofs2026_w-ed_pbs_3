from flask import Flask, jsonify, request, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import json
from src.API.Application.user_service import UserService, AuthenticationError

user_service = UserService()

user_bp = Blueprint("users",__name__)
@user_bp.route('/login', methods = ['POST'])
def user_login():
    data = request.json
    try:
        token = user_service.authenticate(data['email'], data['password'])

        return jsonify({"access_token": token}), 200
    except AuthenticationError:
        return jsonify({"error": "Credenciais inválidas"}), 401
    
@user_bp.route('/mainpage', methods = ['POST'])
@jwt_required()
def mainpage():
    try:
        current_user = get_jwt_identity()
        return jsonify({"logged_as": current_user}), 200
    
    except AuthenticationError:
        return jsonify({"error": "Token not found"}), 401
