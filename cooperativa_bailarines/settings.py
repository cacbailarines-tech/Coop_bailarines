import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path):
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(',') if item.strip()]


load_env_file(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-bailarines-coop-2026-change-this-in-production')
DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '127.0.0.1,localhost')
railway_public_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
if railway_public_domain and railway_public_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_public_domain)
if '*' not in ALLOWED_HOSTS and DEBUG:
    ALLOWED_HOSTS.append('*')

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
app_base_url = os.getenv('APP_BASE_URL', 'http://127.0.0.1:8000').strip()
if app_base_url.startswith('http://') or app_base_url.startswith('https://'):
    if app_base_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(app_base_url)
if railway_public_domain:
    railway_origin = f'https://{railway_public_domain}'
    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'socios',
    'cuentas',
    'creditos',
    'multas',
    'reportes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cooperativa_bailarines.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'core.context_processors.nav_counts',
        ],
    },
}]

WSGI_APPLICATION = 'cooperativa_bailarines.wsgi.application'

default_db_url = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:root@127.0.0.1:5432/bailarines'
)
external_db_url = os.getenv('EXTERNAL_DATABASE_URL', '').strip()
DATABASES = {
    'default': dj_database_url.parse(default_db_url, conn_max_age=600, ssl_require=False)
}
if external_db_url:
    # Optional second DB connection (e.g. another Railway Postgres service).
    DATABASES['external'] = dj_database_url.parse(external_db_url, conn_max_age=600, ssl_require=False)

DATABASE_ROUTERS = ['core.db_router.DatabaseRouter']

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

APP_BASE_URL = app_base_url
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '').strip()
GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID', '').strip()
GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET', '').strip()
GMAIL_REFRESH_TOKEN = os.getenv('GMAIL_REFRESH_TOKEN', '').strip()
GMAIL_SENDER_EMAIL = os.getenv('GMAIL_SENDER_EMAIL', '').strip()
WEBPUSH_ENABLED = env_bool('WEBPUSH_ENABLED', True)
WEBPUSH_VAPID_PUBLIC_KEY = os.getenv('WEBPUSH_VAPID_PUBLIC_KEY', '').strip()
WEBPUSH_VAPID_PRIVATE_KEY = os.getenv('WEBPUSH_VAPID_PRIVATE_KEY', '').replace('\\n', '\n').strip()
WEBPUSH_VAPID_ADMIN_EMAIL = os.getenv('WEBPUSH_VAPID_ADMIN_EMAIL', EMAIL_HOST_USER or 'no-reply@bailarines.local').strip()
DEFAULT_FROM_EMAIL = os.getenv(
    'DEFAULT_FROM_EMAIL',
    (f'Cooperativa Bailarines <{GMAIL_SENDER_EMAIL}>' if GMAIL_SENDER_EMAIL else '')
    or f'Cooperativa Bailarines <{EMAIL_HOST_USER or "no-reply@bailarines.local"}>'
)
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '20'))

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)

# Logging básico a consola (Railway captura stdout/stderr).
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'INFO').upper(),
    },
    'loggers': {
        # Tracebacks de errores 500.
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', 'INFO').upper(),
            'propagate': False,
        },
    },
}

# JAZZMIN CONFIGURATION
JAZZMIN_SETTINGS = {
    "site_title": "Coop Bailarines Admin",
    "site_header": "Cooperativa Bailarines",
    "site_brand": "Coop. Bailarines",
    "site_logo": "img/logo.png",
    "login_logo": "img/logo.png",
    "site_icon": "img/logo.png",
    "welcome_sign": "Bienvenido al Panel de Administración",
    "copyright": "Cooperativa Bailarines",
    "search_model": ["socios.Socio", "creditos.Credito"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Inicio",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Ver Sitio", "url": "/", "new_window": True},
        {"name": "Respaldar BD", "url": "descargar_respaldo_bd", "permissions": ["auth.add_user"], "icon": "fas fa-database"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "socios.Socio": "fas fa-user-friends",
        "socios.Libreta": "fas fa-book",
        "socios.AporteMensual": "fas fa-piggy-bank",
        "creditos.Credito": "fas fa-hand-holding-usd",
        "creditos.PagoCredito": "fas fa-money-bill-wave",
        "multas.Multa": "fas fa-exclamation-circle",
        "multas.Reunion": "fas fa-calendar-check",
        "cuentas.CuentaBancaria": "fas fa-university",
        "cuentas.Transaccion": "fas fa-exchange-alt",
        "core.PushSubscription": "fas fa-bell",
        "reportes.Reporte": "fas fa-chart-line",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

