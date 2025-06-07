"""
Django settings for OpenReplay MCP Server
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'openreplay-mcp-server-dev-key')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django_mcp_server',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'openreplay_mcp.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

USE_TZ = True
TIME_ZONE = 'UTC'

# OpenReplay Configuration
OPENREPLAY_CONFIG = {
    'API_URL': os.getenv('OPENREPLAY_API_URL', 'https://api.openreplay.com'),
    'API_KEY': os.getenv('OPENREPLAY_API_KEY', ''),
    'PROJECT_ID': os.getenv('OPENREPLAY_PROJECT_ID', ''),
}