from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
import sys

# 1. ÖNCE BASE_DIR TANIMLANMALI
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SONRA DEBUG PRINT YAPILABİLİR
# Bu satır Render loglarında klasör yolunu görmemizi sağlar (Hata ayıklama için)
print(f" --- DEBUG: BASE_DIR is: {BASE_DIR} ---")

# 3. .ENV YÜKLEME
# .env dosyasını yükle
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==================================================
# === GÜVENLİK AYARLARI ===
# ==================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-varsayilan-anahtar-degistir')

# DEBUG ayarı: .env dosyasında 'True' yazıyorsa True, yoksa False kabul eder.
# Render'da Environment Variables kısmına DEBUG = False eklediğimiz için canlıda False olur.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# ==================================================
# === UYGULAMALAR (APPS) ===
# ==================================================
INSTALLED_APPS = [
    # 3. Parti - Cloudinary
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Whitenoise (staticfiles'dan önce olmasa da olur ama burada durması standarttır)
    'django.contrib.staticfiles',
    
    'cloudinary', # Cloudinary ana uygulaması

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
    'anymail', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Whitenoise BURADA OLMALI
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
                # Proje özel processörler
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
# === VERİTABANI AYARI (HİBRİT) ===
# ==================================================
# Eğer .env dosyasında DATABASE_URL varsa onu kullanır (Render PostgreSQL)
# Yoksa otomatik olarak yerel db.sqlite3 dosyasına düşer.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}


# ==================================================
# === ŞİFRE DOĞRULAMA ===
# ==================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==================================================
# === ULUSLARARASILAŞTIRMA ===
# ==================================================
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True


# ==================================================
# === STATİK VE MEDYA AYARLARI (RENDER UYUMLU & DEBUG) ===
# ==================================================
STATIC_URL = '/static/'

# collectstatic komutunun dosyaları toplayacağı yer (Render burayı kullanır)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Senin oluşturduğun statik dosyaların yeri
# os.path.join kullanarak işletim sistemi farkını ortadan kaldırıyoruz
static_dir = os.path.join(BASE_DIR, 'static')

# Loglara klasörün var olup olmadığını yazdıralım (Hata ayıklama için)
if os.path.exists(static_dir):
    print(f" --- DEBUG: 'static' klasörü bulundu: {static_dir} ---")
else:
    print(f" --- DEBUG: DİKKAT! 'static' klasörü BULUNAMADI: {static_dir} ---")
    # Alternatif isimleri kontrol et (Büyük/Küçük harf hatası için)
    try:
        for item in os.listdir(BASE_DIR):
            if item.lower() == 'static':
                print(f" --- DEBUG: Ama '{item}' adında bir klasör var. Harf hatası olabilir! ---")
    except:
        pass

STATICFILES_DIRS = [
    static_dir,
]

# --- CANLI SUNUCU AYARLARI (DEBUG=False ise) ---
if not DEBUG:
    # Statik dosyalar için Whitenoise (Sıkıştırma ve Caching)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    
    # Medya (Resimler) için Cloudinary
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL') 
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Cloudinary statik dosyaları yönetmesin, onu Whitenoise yapıyor
    CLOUDINARY_STORAGE_MANAGE_STATICFILES = False 
    
    MEDIA_URL = '/media/' 

# --- YEREL GELİŞTİRME AYARLARI (DEBUG=True ise) ---
else:
    # Bilgisayarında resimleri klasöre kaydet
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
    # Yerelde standart Django statik sunucusu kullanılır


# ==================================================
# === DİĞER AYARLAR ===
# ==================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CART_SESSION_ID = 'cart'

# Login/Logout yönlendirmeleri
LOGIN_REDIRECT_URL = "pages:home"
LOGOUT_REDIRECT_URL = "pages:home"
LOGIN_URL = "login"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# E-posta Ayarları (SMTP)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Stripe Ödeme Ayarları
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_API_VERSION = '2024-06-20'