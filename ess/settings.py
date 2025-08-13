import os
from pathlib import Path
import cloudinary
import cloudinary.uploader
import cloudinary.api
# from decouple import config

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'django-insecure-(7y7#dcke$n(vm08zlz2@7y@uzz4sw)bh)irmws$(^rmzj46vp'
DEBUG = True
# SECURE_SSL_REDIRECT = True

# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

ALLOWED_HOSTS = [
    "ess-backend-fg6m.onrender.com",
    "localhost",
    "127.0.0.1"
]

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'csp',#Content Security Policy (CSP) make sure install pip install django-csp
    'authentication',
    'attendance',
    'leaves',
    'chat',
    'payroll',
    'documents',
    'projectmanagement',
    'kpi',
    'Pincode',
    'Create_New_Item',
    'Quotation_Estimate',
    'Sales_Invoice',
    'Payment_In',
    'helpdesk',
    'Proforma_Invoice',
    'Delivery_Challan',
    'Credit_Note',
    'Sales_Person',
    'armanagement',
    'ClientPurchaseOrder',
    'Sales_Order',
    'purchase_order',
    'cloudinary',
    'cloudinary_storage',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS Middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL and WSGI application
ROOT_URLCONF = 'ess.urls'
WSGI_APPLICATION = 'ess.wsgi.application'
# ASGI_APPLICATION = 'ess.asgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Database configuration
DATABASES = {

    'default': {
         'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',
        'USER': 'avnadmin',
        'PASSWORD':'AVNS_LuWXHmgGfdMCnLFl530',
        'HOST': 'mysql-3af8b8a0-ess-be14-7c79.j.aivencloud.com',
        'PORT': '19368',

    }
    
    
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'defaultdb',
    #     'USER': 'avnadmin',
    #     'PASSWORD':'AVNS_asRAKO4vm9Wp0wloPL6',
    #     'HOST': 'mysql-405f950-sudhakar-eeaa.l.aivencloud.com',
    #     'PORT': '27448',
    # }

    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'defaultdb',
    #     'USER': 'avnadmin',
    #     'PASSWORD':'AVNS_gJqH5H3-pMbO0vWcv8U',
    #     'HOST': 'mysql-3a19ca01-ssudhakarg0-93bc.d.aivencloud.com',
    #     'PORT': '12680',
    # }
}


# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sudhakar.ibacustech@gmail.com'
EMAIL_HOST_PASSWORD = 'cvke ezid zfvf nzgh'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



# CORS settings
CORS_ALLOW_CREDENTIALS = True

# If using Django 4.0 or higher, use CORS_ORIGIN_ALLOW_ALL for more control:
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://ess-frontent.vercel.app",
    "https://ess-backend-fg6m.onrender.com"
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://ess-backend-fg6m.onrender.com",
  "https://ess-frontent.vercel.app"
]

# Optional: Allow specific headers and methods
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
    'x-requested-with',
    'accept',
    'origin',
    'content-encoding',
    "accept-encoding", 
    "dnt",
    "user-agent",
   
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "http://localhost:5173","https://ess-frontent.vercel.app/")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'authentication.validators.CustomPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        '_main_': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Default, using database-backed sessions
SESSION_COOKIE_NAME = 'sessionid'  # Default cookie name
SESSION_COOKIE_AGE = 1209600  # Default: 2 weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keeps session until expiry time
SESSION_COOKIE_HTTPONLY = True  # Make the session cookie accessible only by the server
SESSION_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS in production
SESSION_COOKIE_SAMESITE = 'None'  # Allows cross-site cookie transmission (for CORS issues)


# CSRF_COOKIE_SECURE = True  # Disable for testing (useful for development)
# CSRF_COOKIE_HTTPONLY = True

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.TokenAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ),
    
# }

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
}


GEMINI_API_KEY = "AIzaSyC01qmdHp_Yf0pqntVf2pFb9qfzNoFgcys"





# Static and media files
# STATIC_URL = '/static/'
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# MEDIA_URL = '/media/'
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'des18xto4',
    'API_KEY': '261227867793152',
    'API_SECRET': 'ifFBr7V4lULLlp3RrQ4ZZOaxTMU'
}


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# CLOUDINARY_URL=cloudinary://261227867793152:ifFBr7V4lULLlp3RrQ4ZZOaxTMU@des18xto4
