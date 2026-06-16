from flask import Flask, request, jsonify, blueprints
from flask_jwt_extended import JWTManager
from flask import redirect, url_for
from werkzeug.exceptions import HTTPException
from src.API.user_routes import user_bp
from datetime import timedelta
from dotenv import load_dotenv
from connection import engine
from connection import engine,SessionLocal
import os
from src.API.workspace_routes import workspace_bp
from src.API.doc_routes import doc_bp
import ssl
import traceback
import logging
from extensions import limiter, oauth
from src.infrastructure.persistance.userDB import (start_mappers,mapper_registry)
from flask_cors import CORS

app = Flask(__name__)

CORS(app, supports_credentials=True, origins=[
    "https://localhost:5003",
    "http://localhost:5003"
])

limiter.init_app(app)
oauth.init_app(app)
# Inicializar ORM
start_mappers()
# Criar tabelas
mapper_registry.metadata.create_all(engine)

# config authlib google 
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "uma-chave-qualquer-estrita")

# inicialização JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
#Allowlist the algoritmos
app.config["JWT_DECODE_ALGORITHMS"] = ["HS256"]  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
# verificação de nbf
app.config["JWT_DECODE_LEEWAY"] = 0
# config de aud
app.config["JWT_ENCODE_AUDIENCE"] = os.getenv("JWT_AUD_KEY")      
app.config["JWT_DECODE_AUDIENCE"] = os.getenv("JWT_AUD_KEY")    
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_REFRESH_COOKIE_PATH"] = "/refresh"
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SECURE"] = True

jwt = JWTManager(app)
# quando tenta acessar recurso protegido sem token, redireciona para login
@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return redirect(url_for("users.user_login"))


def create_ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # TLS 1.2 como mínimo, 1.3 como preferido
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    ctx.set_ciphers(
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-CHACHA20-POLY1305"
    )

    # Força a ordem de preferência do servidor (suite mais forte primeiro)
    ctx.options |= ssl.OP_CIPHER_SERVER_PREFERENCE

    # Desativa compressão TLS
    ctx.options |= ssl.OP_NO_COMPRESSION
    
    ctx.load_cert_chain(
        certfile="certs/cert.pem",
        keyfile="certs/key.pem"
    )
    return ctx

#Handler global e log

# Configura logging para ficheiro
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/error.log"),
        logging.StreamHandler() 
    ]
)
logger = logging.getLogger(__name__)

# Handler de ultimo recurso 
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    logger.error(f"Exceção não tratada: {traceback.format_exc()}")
    
    # Resposta genérica para o cliente
    return jsonify({
        "error": "Ocorreu um erro inesperado. Por favor tente mais tarde."
    }), 500
"""
# Handler para erros HTTP 
"""
@app.errorhandler(HTTPException)
def handle_http_error(e):
    logger.warning(f"Erro HTTP {e.code}: {e.description} — {request.path}")
    return jsonify({"error": e.description}), e.code

# definição de blueprints
app.register_blueprint(user_bp)
app.register_blueprint(workspace_bp)
app.register_blueprint(doc_bp)

'''
#Header de content type
@app.after_request
def set_content_type(response):
    if response.content_type.startswith("application/json"):
        response.content_type = "application/json; charset=utf-8"
    elif response.content_type.startswith("text/html"):
        response.content_type = "text/html; charset=utf-8"
    return response
'''

@app.after_request
def set_security_headers(response):

    # Content-Type normalization
    if response.content_type.startswith("application/json"):
        response.content_type = "application/json; charset=utf-8"
    elif response.content_type.startswith("text/html"):
        response.content_type = "text/html; charset=utf-8"

    # ASVS V14 caching protection
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"


    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "base-uri 'none'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "img-src 'self' data:; "
        "style-src 'self' https://cdn.jsdelivr.net; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self' https://cdn.jsdelivr.net https://accounts.google.com https://*.google.com; "
        "font-src 'self' https://cdn.jsdelivr.net; "
    )

    return response


if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = "5003", ssl_context=create_ssl_context())
