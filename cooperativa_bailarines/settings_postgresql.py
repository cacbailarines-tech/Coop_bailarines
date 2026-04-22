# ============================================================
# Configuración para PostgreSQL
# Para usar: python manage.py runserver --settings=cooperativa_bailarines.settings_postgresql
# ============================================================
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bailarines',       # nombre de la base de datos
        'USER': 'postgres',          # usuario PostgreSQL
        'PASSWORD': 'tu_contraseña', # cambiar por tu contraseña
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
