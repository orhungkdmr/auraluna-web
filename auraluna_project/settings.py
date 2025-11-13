from pathlib import Path
import os
# YENİ: .env dosyasını okumak için importlar
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# YENİ: .env dosyasını yükle
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==================================================
# === GÜVENLİK AYARLARI GÜNCELLENDİ ===
# ==================================================

# ESKİ (SİLİN): SECRET_KEY = 'django-insecure-kp5!!&ztm%ah(oma3!dp1irv^j#0@zl-zmbc)ounb+#9t=q#!@'
# YENİ:
SECRET_KEY = os.environ.get('SECRET_KEY')

# ESKİ (SİLİN): DEBUG = True
# YENİ: .env'den al (True/False)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ESKİ (SİLİN): ALLOWED_HOSTS = []
# YENİ: .env'den al (virgülle ayrılmış listeyi oku)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
# ==================================================


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # === GÜNCELLEME BURADA ===
    # 1. Cloudinary Storage (staticfiles'dan önce)
    'cloudinary_storage', 
    
    # 2. Staticfiles (SADECE BİR KEZ BURADA)
    'django.contrib.staticfiles', 
    
    # 3. Cloudinary
    'cloudinary', 
    # === GÜNCELLEME SONU ===

    # Kendi Uygulamalarımız
    'products',
    'pages',
    'cart',
    'orders',
    'accounts',
    
    # 3. Parti Uygulamalar
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
  
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
# === VERİTABANI AYARI GÜNCELLENDİ ===
# ==================================================

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}
# ==================================================


AUTH_PASSWORD_VALIDATORS = [
    # ... (Aynı kalır) ...
]

LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# YENİ: collectstatic komutunun dosyaları toplayacağı yer
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# YENİ: Whitenoise'un dosyaları sunmasını sağlayan ayar
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# YENİ: Cloudinary ayarları
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL') # .env'den okur
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/' # Cloudinary bu URL'i otomatik olarak yönlendirir

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CART_SESSION_ID = 'cart'
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==================================================
# === E-POSTA VE STRIPE AYARLARI GÜNCELLENDİ ===
# ==================================================
# ==================================================
# === E-POSTA AYARLARI (.env'den okuma) ===
# ==================================================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND') # .env'den 'django.core.mail.backends.smtp.EmailBackend' okur
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') # .env'den 'orhungokdemir@gmail.com' okur

# YENİ: SMTP ayarlarını .env'den okuma
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS') == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')


# ==================================================

STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_API_VERSION = '2024-06-20'
# ==================================================