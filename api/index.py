import sys
import os

from werkzeug.middleware.proxy_fix import ProxyFix

# Ajout du dossier parent au PATH pour les imports sous Vercel Serverless
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Configuration ProxyFix pour l'infrastructure Vercel Edge
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
