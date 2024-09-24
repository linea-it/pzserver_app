"""
Django settings for pzserver project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os

import saml2

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.getenv("LOG_DIR", "/archive/log")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.getenv("DEBUG", "1"))

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "rest_framework.authtoken",
    # OAuth2
    "oauth2_provider",
    "social_django",
    "drf_social_oauth2",
    "djangosaml2",
    # Apps
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pzserver.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "pzserver.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.getenv("DB_USER", "user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# rabbitmq
AMQP_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
AMQP_PORT = os.getenv("RABBITMQ_PORT", "5672")
AMQP_USER = os.getenv("RABBITMQ_DEFAULT_USER", "orcadmin")
AMQP_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "adminorc")
AMQP_VHOST = os.getenv("RABBITMQ_DEFAULT_VHOST", "/")


# Celery Configuration Options
CELERY_BROKER_URL = (
    f"amqp://{AMQP_USER}:{AMQP_PASS}@{AMQP_HOST}:{AMQP_PORT}{AMQP_VHOST}"
)
CELERY_CACHE_BACKEND = "django-cache"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_TIMEZONE = "UTC"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

auth_pass_str = "django.contrib.auth.password_validation"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{auth_pass_str}.UserAttributeSimilarityValidator"},
    {"NAME": f"{auth_pass_str}.MinimumLengthValidator"},
    {"NAME": f"{auth_pass_str}.CommonPasswordValidator"},
    {"NAME": f"{auth_pass_str}.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/django_static/"
STATIC_ROOT = os.path.join(BASE_DIR, "django_static")

MEDIA_URL = "/archive/data/"
MEDIA_ROOT = MEDIA_URL

UPLOAD_DIR = os.getenv("UPLOAD_DIR", MEDIA_URL)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space
# between each. For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 [::1]").split(
    " "
)

# https://docs.djangoproject.com/en/4.0/releases/4.0/#csrf-trusted-origins-changes
CSRF_TRUSTED_ORIGINS = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost http://127.0.0.1"
).split(" ")

# https://docs.djangoproject.com/en/4.1/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME = "pzserver.csrftoken"

# Orchestration
ORCHEST_URL = os.getenv("ORCHEST_URL", None)

if ORCHEST_URL:
    ORCHEST_CLIENT_ID = os.getenv("ORCHEST_CLIENT_ID")
    ORCHEST_CLIENT_SECRET = os.getenv("ORCHEST_CLIENT_SECRET")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "drf_social_oauth2.authentication.SocialAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # 'djangosaml2.backends.Saml2Backend',
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.CustomPageNumberPagination",
    "DEFAULT_METADATA_CLASS": "core.SimpleMetadataWithFilters",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Photo-z Server API",
    "DESCRIPTION": "This is the API for the Photo-z Server.",
    "VERSION": "0.1.0",
}

JSON_EDITOR = True

AUTHENTICATION_BACKENDS = (
    "drf_social_oauth2.backends.DjangoOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "core.saml2.ModifiedSaml2Backend",
)

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
LOGIN_REDIRECT_URL = "/"

OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 36000,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(message)s"},
    },
    "handlers": {
        "default": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "db_handler": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django_db.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "oauthlib": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "oauthlib.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "saml": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "saml2.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
        "products": {
            "level": LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "products.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["default"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["db_handler"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "oauthlib": {
            "handlers": ["oauthlib"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "saml": {
            "handlers": ["saml"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
        "products": {
            "handlers": ["products"],
            "level": LOGGING_LEVEL,
            "propagate": True,
        },
    },
}


# directory where it will contain the processing of the pipelines.
PROCESSING_DIR = os.getenv("PROCESSING_DIR", "/processes")

# directory where it will contain the source code of the pipelines.
PIPELINES_DIR = os.getenv("PIPELINES_DIR", "/pipelines")

# directory where it will contain the datasets.
DATASETS_DIR = os.getenv("DATASETS_DIR", "/datasets")

if os.getenv("AUTH_SHIB_URL", None):
    FQDN = os.getenv("URI", "http://localhost")
    CERT_DIR = "/saml2/certificates"
    SIG_KEY_PEM = os.getenv("SIG_KEY_PEM", os.path.join(CERT_DIR, "pzkey.pem"))
    SIG_CERT_PEM = os.getenv("SIG_CERT_PEM", os.path.join(CERT_DIR, "pzcert.pem"))
    ENCRYP_KEY_PEM = os.getenv("ENCRYP_KEY_PEM", SIG_KEY_PEM)
    ENCRYP_CERT_PEM = os.getenv("ENCRYP_CERT_PEM", SIG_CERT_PEM)

    MIDDLEWARE.append("djangosaml2.middleware.SamlSessionMiddleware")

    # configurações relativas ao session cookie
    SAML_SESSION_COOKIE_NAME = "saml_session"
    SESSION_COOKIE_SECURE = True

    # Qualquer view que requer um usuário autenticado deve redirecionar o navegador para esta url
    LOGIN_URL = "/saml2/login/"

    # Encerra a sessão quando o usuário fecha o navegador
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    # Tipo de binding utilizado
    SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_POST
    SAML_IGNORE_LOGOUT_ERRORS = True

    # Serviço de descoberta da cafeexpresso
    # SAML2_DISCO_URL = 'https://ds.cafeexpresso.rnp.br/WAYF.php'

    # Cria usuário Django a partir da asserção SAML caso o mesmo não exista
    SAML_CREATE_UNKNOWN_USER = True

    # https://djangosaml2.readthedocs.io/contents/security.html#content-security-policy
    SAML_CSP_HANDLER = ""

    # URL para redirecionamento após a autenticação
    LOGIN_REDIRECT_URL = "/"

    SAML_ATTRIBUTE_MAPPING = {
        "eduPersonUniqueId": ("username",),
        "sn": ("name",),
        "cn": ("full_name",),
        "email": ("email",),
    }

    METADATAS = str(os.getenv("IDP_METADATA")).split(",")
    METADATA_URLS = []

    for metadata in METADATAS:
        METADATA_URLS.append({"url": metadata, "cert": None})

    SAML_CONFIG = {
        # Biblioteca usada para assinatura e criptografia
        "xmlsec_binary": "/usr/bin/xmlsec1",
        "entityid": FQDN + "/saml2/metadata/",
        # Diretório contendo os esquemas de mapeamento de atributo
        "attribute_map_dir": os.path.join(BASE_DIR, "attribute-maps"),
        "description": "SP Pz Server",
        "service": {
            "sp": {
                "name": "sp_pzserver",
                "ui_info": {
                    "display_name": {"text": "SP Pz", "lang": "en"},
                    "description": {"text": "Pz Service Provider", "lang": "en"},
                    "information_url": {"text": f"{FQDN}/about", "lang": "en"},
                    "privacy_statement_url": {"text": FQDN, "lang": "en"},
                },
                "name_id_format": [
                    "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
                    "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
                ],
                # Indica os endpoints dos serviços fornecidos
                "endpoints": {
                    "assertion_consumer_service": [
                        (FQDN + "/saml2/acs/", saml2.BINDING_HTTP_POST),
                    ],
                    "single_logout_service": [
                        (FQDN + "/saml2/ls/", saml2.BINDING_HTTP_REDIRECT),
                        (FQDN + "/saml2/ls/post", saml2.BINDING_HTTP_POST),
                    ],
                },
                # Algoritmos utilizados
                #'signing_algorithm':  saml2.xmldsig.SIG_RSA_SHA256,
                #'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,
                "force_authn": False,
                "name_id_format_allow_create": False,
                # Indica que as respostas de autenticação para este SP devem ser assinadas
                "want_response_signed": True,
                # Indica se as solicitações de autenticação enviadas por este SP devem ser assinadas
                "authn_requests_signed": True,
                # Indica se este SP deseja que o IdP envie as asserções assinadas
                "want_assertions_signed": False,
                "only_use_keys_in_metadata": True,
                "allow_unsolicited": False,
            },
        },
        # Indica onde os metadados podem ser encontrados
        "metadata": {
            "remote": METADATA_URLS,
            # "local": [os.getenv("IDP_METADATA")],
        },
        "debug": os.getenv("DEBUG", "1"),
        # Signature
        "key_file": SIG_KEY_PEM,  # private part
        "cert_file": SIG_CERT_PEM,  # public part
        # Encriptation
        "encryption_keypairs": [
            {
                "key_file": ENCRYP_KEY_PEM,  # private part
                "cert_file": ENCRYP_CERT_PEM,  # public part
            }
        ],
        "contact_person": [
            {
                "given_name": "LIneA",
                "sur_name": "Team",
                "company": "LIneA",
                "email_address": "itteam@linea.org.br",
                "contact_type": "technical",
            },
        ],
        # Descreve a organização responsável pelo serviço
        "organization": {
            "name": [("LIneA", "pt-br")],
            "display_name": [("LIneA", "pt-br")],
            "url": [("https://linea.org.br/", "pt-br")],
        },
    }
