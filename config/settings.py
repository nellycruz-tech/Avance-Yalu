from django.urls import reverse_lazy
from pathlib import Path
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ['192.168.1.4', '192.168.1.6', 'localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'huey.contrib.djhuey',
    'django_extensions',
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "usuarios",
    "catalogo",
    "ventas",
    "trabajos",
    "comentarios"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'config.urls'

# Funcionamiento con Nginx
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

HUEY = {
    'huey_class': 'huey.SqliteHuey',
    'name': 'my-app',
    'results': True,
    'immediate': False,
}

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'yalu_db'),
        'USER': os.environ.get('DB_USER', 'yalu_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'yalu_pass_2026'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

UNFOLD = {
    "SITE_TITLE": "Yalú Admin",
    "SITE_HEADER": "Librería Bazar Yalú",
    "SITE_SUBHEADER": "Panel de administración",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SITE_SYMBOL": "storefront",
    "COLORS": {
        "primary": {
            "50": "255 247 237",
            "100": "255 237 213",
            "200": "254 215 170",
            "300": "253 186 116",
            "400": "251 146 60",
            "500": "249 115 22",
            "600": "234 88 12",
            "700": "194 65 12",
            "800": "154 52 18",
            "900": "124 45 18",
            "950": "67 20 7",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Catálogo",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Productos",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:catalogo_producto_changelist"),
                    },
                    {
                        "title": "Categorías",
                        "icon": "category",
                        "link": reverse_lazy("admin:catalogo_categoria_changelist"),
                    },
                    {
                        "title": "Marcas",
                        "icon": "sell",
                        "link": reverse_lazy("admin:catalogo_marca_changelist"),
                    },
                ],
            },
            {
                "title": "Ventas",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Pedidos",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:ventas_pedido_changelist"),
                    },
                    {
                        "title": "Pagos",
                        "icon": "payments",
                        "link": reverse_lazy("admin:ventas_pago_changelist"),
                    },
                    {
                        "title": "Comprobantes",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:ventas_comprobante_changelist"),
                    },
                ],
            },
            {
                "title": "Trabajos Manuales",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Proyectos",
                        "icon": "brush",
                        "link": reverse_lazy("admin:trabajos_trabajomanual_changelist"),
                    },
                    {
                        "title": "Fotos",
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:trabajos_trabajomanualfoto_changelist"),
                    },
                ],
            },
            {
                "title": "Usuarios",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Usuarios",
                        "icon": "person",
                        "link": reverse_lazy("admin:usuarios_usuario_changelist"),
                    },
                    {
                        "title": "Roles",
                        "icon": "shield",
                        "link": reverse_lazy("admin:usuarios_rol_changelist"),
                    },
                    {
                        "title": "Direcciones",
                        "icon": "map",
                        "link": reverse_lazy("admin:usuarios_direccion_changelist"),
                    },
                ],
            },
            {
                "title": "Autenticación",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Grupos",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://localhost:5173",
    "http://localhost:5174",
    "https://localhost:5174",
    "http://127.0.0.1:5173",
    "https://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://127.0.0.1:5174",
    "http://192.168.1.4:5173",
    "https://192.168.1.4:5173",
    "http://192.168.1.6:5173",
    "https://192.168.1.6:5173",
]

CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.SessionAuthentication', # Prioridad a sesión
        'core.authentication.FirebaseAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.AllowAny', # Globalmente permitido, restringe por vista
    ],
}

FIREBASE_KEY_PATH = os.environ.get("FIREBASE_KEY_PATH", str(BASE_DIR / 'firebase_credentials.json'))

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase OK")
    except Exception as e:
        print(f"Firebase no disponible: {e}")

HCAPTCHA_SECRET  = os.environ.get("HCAPTCHA_SECRET")
CULQI_SECRET_KEY = os.environ.get("CULQI_SECRET_KEY")   # ← LÍNEA NUEVA

MICROSERVICES_GATEWAY = os.environ.get("MICROSERVICES_GATEWAY", "http://localhost:8080")