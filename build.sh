#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- 1. PAKETLER YUKLENIYOR ---"
pip install -r requirements.txt

echo "--- 2. MANUEL DOSYA KOPYALAMA BASLADI ---"
# Hedef klasörü oluştur
mkdir -p staticfiles

# 'assets' klasörü var mı kontrol et ve kopyala
if [ -d "assets" ]; then
    echo "Assets klasörü bulundu, kopyalanıyor..."
    cp -r assets/* staticfiles/
    echo "Kopyalama tamamlandı."
    ls -R staticfiles/ | head -n 10 # İlk 10 dosyayı listele (Kanıt)
else
    echo "HATA: 'assets' klasörü bulunamadı!"
    ls -la # Mevcut dizini listele
fi

echo "--- 3. DJANGO COLLECTSTATIC (ADMIN DOSYALARI ICIN) ---"
# Admin panelinin CSS'leri için bu gerekli
python manage.py collectstatic --no-input

echo "--- 4. VERITABANI GUNCELLEMESI ---"
python manage.py migrate