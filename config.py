"""Configure for CSRF and SQLite."""
import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
WTF_CSRF_ENABLED = True

# Generate a secret key
SECRET_KEY = secrets.token_urlsafe()
