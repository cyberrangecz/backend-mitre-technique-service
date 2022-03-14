"""
Django settings for mitre_visualizer project.

Generated by 'django-admin startproject' using Django 2.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from kypo.mitre_common_lib.kypo_service_config import KypoServiceConfig

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

KYPO_MITRE_TECHNIQUE_SERVICE_CONFIG_PATH = os.path.join(BASE_DIR, 'tests/config.yml')
KYPO_SERVICE_CONFIG = KypoServiceConfig.from_file(KYPO_MITRE_TECHNIQUE_SERVICE_CONFIG_PATH)
KYPO_CONFIG = KYPO_SERVICE_CONFIG.app_config
os.environ['REQUESTS_CA_BUNDLE'] = KYPO_CONFIG.ssl_ca_certificate_verify

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&#syipmic=iv3t)gx!a@0vjmx2lx(8l_(1(q#f*o_z%zdl69xv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = KYPO_SERVICE_CONFIG.debug

ALLOWED_HOSTS = tuple(KYPO_SERVICE_CONFIG.allowed_hosts)


# Application definition

CORS_ORIGIN_ALLOW_ALL = KYPO_SERVICE_CONFIG.cors_origin_allow_all
CORS_ORIGIN_WHITELIST = tuple(KYPO_SERVICE_CONFIG.cors_origin_whitelist)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg2',
    'rest_framework',

    'kypo.mitre_matrix_visualizer_app.apps.MitreMatrixVisualizerAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kypo.mitre_technique_project.urls'

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

WSGI_APPLICATION = 'kypo.mitre_technique_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = f'/{KYPO_SERVICE_CONFIG.microservice_name}/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSIONS_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
}
