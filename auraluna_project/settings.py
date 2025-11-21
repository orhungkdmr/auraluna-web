from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
import sys
import cloudinary
import cloudinary.uploader
import cloudinary.api

BASE_DIR = Path(__file__).resolve().parent.parent
print(f" --- DEBUG: BASE_DIR is: {BASE_DIR} ---")

load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-varsayilan-anahtar-degistir')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# --- DEBUG AYARI ---
# Render'da otomatik False olur, lokalde True
IN_RENDER = 'RENDER' in os.environ
if IN_RENDER:
    DEBUG = False
    print("--- ORTAM: RENDER (CANLI) ---")
else:
    DEBUG = True
    print("--- ORTAM: LOCAL (BILGISAYAR) ---")

INSTALLED_APPS = [
    'cloudinary_storage',          # 1. SIRA (Çok Önemli)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',                  # 2. SIRA (Mutlaka burada)
    'products',
    'pages',
    'cart',
    'orders',
    'accounts',
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

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

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
# === STATİK DOSYALAR (CSS, JS) ===
# ==================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets')]

if IN_RENDER:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ==================================================
# === MEDYA VE CLOUDINARY (ZORUNLU AKTİF) ===
# ==================================================
# Burası HİÇBİR ŞARTA BAĞLI DEĞİL. Her zaman çalışacak.

# 1. Cloudinary Bilgileri
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dkqwfaufv',
    'API_KEY': '934879957763873',
    'API_SECRET': 'ULTnxyuXxs_EJYOUlVX2--vsf_E' # <--- BURAYI DOLDUR
}

# --- DJANGO 5 İÇİN DEPOLAMA AYARLARI (İSİM HATASI DÜZELTİLDİ) ---
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        # YAZIM HATASI DÜZELTİLDİ: WhiteNoiseStorage yerine doğru sınıf adı:
        "BACKEND": "whitenoise.storage.WhiteNoiseStaticFilesStorage", 
        # NOT: Eğer CompressedStaticFilesStorage hala hata verirse, aşağıdaki basit olanı kullan:
        # "BACKEND": "whitenoise.storage.WhiteNoiseStaticFilesStorage",
    },
}

# 3. Cloudinary Kütüphanesini Manuel Başlatma
import cloudinary
cloudinary.config(
    cloud_name = CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key = CLOUDINARY_STORAGE['API_KEY'],
    api_secret = CLOUDINARY_STORAGE['API_SECRET'],
    secure = True
)

print("--- MOD: DJANGO 5 STORAGES AYARLARI AKTİF (CLOUDINARY) ---")

# ==================================================
# === STATİK BULUCULAR (WHITENOISE/CLOUDINARY FIX) ===
# ==================================================
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # Diğer Finder'lar (örn. Compressors) buraya eklenebilir
]

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