import os
import django

# Django ayarlarını yükle
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auraluna_project.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Render ayarlarından bilgileri al, yoksa varsayılanları kullan
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
password = os.environ.get('ADMIN_PASSWORD', 'admin12345') # Güçlü bir şifre belirle

if not User.objects.filter(username=username).exists():
    print(f"--- YONETICI OLUSTURULUYOR: {username} ---")
    User.objects.create_superuser(username, email, password)
    print("--- YONETICI BASARIYLA OLUSTURULDU ---")
else:
    print("--- YONETICI ZATEN MEVCUT, GECILIYOR ---")