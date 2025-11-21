# ... (Dosyanın en tepesindeki importların olduğu yere şunu ekle/kontrol et)
import os
import sys # Bunu ekle

# ... (BASE_DIR tanımının hemen altına şu print komutunu ekle)
# Bu komut Render loglarında klasörün nerede olduğunu bize söyleyecek
print(f" --- DEBUG: BASE_DIR is: {BASE_DIR} ---")

# ... (Aşağı in ve STATİK AYARLARI kısmını tamamen bununla değiştir)

# ==================================================
# === STATİK VE MEDYA AYARLARI (DEBUG SÜRÜMÜ) ===
# ==================================================
STATIC_URL = '/static/'

# Render'ın dosyaları toplayacağı yer (collectstatic buraya atar)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Senin oluşturduğun dosyaların bulunduğu yer
# os.path.join kullanarak işletim sistemi farkını ortadan kaldırıyoruz
static_dir = os.path.join(BASE_DIR, 'static')

# Loglara klasörün var olup olmadığını yazdıralım
if os.path.exists(static_dir):
    print(f" --- DEBUG: 'static' klasörü bulundu: {static_dir} ---")
else:
    print(f" --- DEBUG: DİKKAT! 'static' klasörü BULUNAMADI: {static_dir} ---")
    # Alternatif isimleri kontrol et (Büyük/Küçük harf hatası için)
    for item in os.listdir(BASE_DIR):
        if item.lower() == 'static':
            print(f" --- DEBUG: Ama '{item}' adında bir klasör var. Harf hatası olabilir! ---")

STATICFILES_DIRS = [
    static_dir,
]

# Whitenoise Ayarları
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    
    # Medya (Resimler)
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE_MANAGE_STATICFILES = False
    MEDIA_URL = '/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')