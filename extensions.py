from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
limiter = Limiter(get_remote_address)
oauth = OAuth()

# Esta configuração diz à Authlib para ler automaticamente as credenciais do app.config
google = oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)