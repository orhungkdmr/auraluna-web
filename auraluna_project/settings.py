from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını yükle (Varsa)
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==================================================
# === ORTAM KONTROLÜ (RENDER MI LOCAL MI?) ===
# ==================================================
# Render otomatik olarak 'RENDER' değişkenini set eder.
IN_RENDER = os.environ.get('RENDER')

if IN_RENDER:
    # Canlı Sunucu (Render)
    DEBUG = False
    print("--- DURUM: CANLI SUNUCUDAYIZ (RENDER) ---")
else:
    # Yerel Bilgisayar
    DEBUG = True
    print("--- DURUM: YEREL BILGISAYARDAYIZ (LOCAL) ---")

# ==================================================
# === GÜVENLİK AYARLARI ===
# ==================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-varsayilan-anahtar-degistir')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# ==================================================
# === UYGULAMALAR (APPS) ===
# ==================================================
INSTALLED_APPS = [
    'cloudinary_storage', # En üstte olmalı
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Whitenoise
    'cloudinary', # Cloudinary

    # Kendi Uygulamalarımız
    'products',
    'pages',
    'cart',
    'orders',
    'accounts',
    
    # 3. Parti
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'anymail', 
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

ROOT_URLCONF = 'auraluna_project.urls'

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
                'cart.context_processors.cart',
                'cart.context_processors.main_categories',
                'pages.context_processors.site_settings', 
                'cart.context_processors.structured_nav_categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'auraluna_project.wsgi.application'


# ==================================================
# === VERİTABANI AYARI ===
# ==================================================
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}


# ==================================================
# === ŞİFRE VE DİL AYARLARI ===
# ==================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True


# ==================================================
# === STATİK VE MEDYA AYARLARI (KESİN ÇÖZÜM) ===
# ==================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Dosyalar 'assets' klasöründe
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]

# --- RENDER (CANLI) AYARLARI ---
if IN_RENDER:
    # Statik Dosyalar (CSS/JS) -> Whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    
    # Medya Dosyaları (Resimler) -> Cloudinary
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Cloudinary'ye statik dosyaları karıştırma diyoruz
    CLOUDINARY_STORAGE_MANAGE_STATICFILES = False
    
    # DİKKAT: Canlıda MEDIA_URL tanımlamıyoruz, Cloudinary URL'i kendi verir.

# --- LOCAL (BILGISAYAR) AYARLARI ---
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==================================================
# === DİĞER AYARLAR ===
# ==================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CART_SESSION_ID = 'cart'
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"
LOGIN_URL = "login"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# E-posta
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Stripe
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_API_VERSION = '2024-06-20'