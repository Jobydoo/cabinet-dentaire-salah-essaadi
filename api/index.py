import sys
import os

# Ajout du dossier parent au PATH pour les imports sous Vercel Serverless
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel WSGI entrypoint
# app est l'instance WSGI Flask
