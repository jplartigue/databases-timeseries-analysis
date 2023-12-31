"""
Django settings for application_benchmark project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$pot#6r#_qc=@@^0$eu=n_@x5ez)7#y!5s&31#lr6lk45)!xy!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djongo',
    'django_extensions',
    'application_benchmark',
    'benchmark_app_for_databases',
    'psqlextra',
    'timescale',
    "django.contrib.postgres",
    "postgres_benchmark",
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

ROOT_URLCONF = 'application_benchmark.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'application_benchmark.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    "postgres": {
        "NAME": "postgres",
        # "ENGINE": "django.db.backends.postgresql",
        "ENGINE": 'psqlextra.backend',
        "USER": "test",
        "PASSWORD": "password",
        "HOST": "postgres",
        'PORT': '5432',
    },
    'timescale': {
        'ENGINE': 'timescale.db.backends.postgresql',
        # "ENGINE": "django.db.backends.postgresql",
        'NAME': 'postgres',
        'USER': 'test',
        'PASSWORD': 'password',
        'HOST': 'timescale',
        'PORT': '5432',
    },
    'mongo': {
        'ENGINE': 'djongo',
        'NAME': 'mongo',
        'ENFORCE_SCHEMA': False,
        'HOST': 'mongo',
        'PORT': 27017,
        'USERNAME': 'test',
        'PASSWORD': 'password',
        'AUTH_SOURCE': 'mongo',
        'CLIENT': {
            # 'host': 'mongodb+srv://<test>:<password>@<atlas cluster>/<myFirstDatabase>?retryWrites=true&w=majority'
            'host': 'mongo',
            'port': 27017,
            'username': 'test',
            'password': 'password',
            'authSource': 'admin',
            'authMechanism': 'SCRAM-SHA-1'
        }
    },
    "questdb": {
        "NAME": "qdb",
        # "ENGINE": "django.db.backends.postgresql",
        "ENGINE": 'psqlextra.backend',
        "USER": "admin",
        "PASSWORD": "quest",
        # "HOST": "questdb",
        'PORT': '8812',
    },
}

DATABASE_ROUTERS = ["benchmark_app_for_databases.routeur.BenchmarkRouter"]
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


PSQLEXTRA_PARTITIONING_MANAGER = 'postgres_benchmark.partitioning.manager'

POSTGRES_EXTRA_DB_BACKEND_BASE = 'django.db.backends.postgresql'