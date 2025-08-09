import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# NGROK va local development uchun
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'django_filters',  # Django Filter for advanced filtering capabilities
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'phonenumber_field',
    
    # Local apps
    'accounts',
    'categories',
    'products',
    'orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Swagger/OpenAPI Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'E-commerce API',
    'DESCRIPTION': 'API documentation for E-commerce platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Internationalization
LANGUAGE_CODE = 'uz-uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS Settings - ngrok uchun ham qo'shish
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend uchun
    "http://127.0.0.1:3000",
    "https://376bf220df09.ngrok-free.app",  # ngrok uchun
]
CORS_ALLOW_ALL_ORIGINS = True  # Development uchun

# Phone number field settings
PHONENUMBER_DEFAULT_REGION = 'UZ'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Vercel deployment settings
if 'VERCEL' in os.environ:
    DEBUG = False
    
    # Allowed hosts
    ALLOWED_HOSTS = [
        '.vercel.app',
        'localhost',
        '127.0.0.1'
    ]
    
    # Database
    if 'DATABASE_URL' in os.environ:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])
    
    # Static files
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # CORS for production
    CORS_ALLOWED_ORIGINS = [
        "https://localhost:3000",
        "https://127.0.0.1:3000",
    ]
    CORS_ALLOW_ALL_ORIGINS = True