#!/usr/bin/env bash
# build.sh

set -o errexit

# 1. Kütüphaneleri kur
pip install -r requirements.txt

# 2. Statik dosyaları topla (Whitenoise için)
python manage.py collectstatic --no-input

# 3. Veritabanı migrasyonlarını uygula
python manage.py migrate

# 4. YENİ: Temel verileri (Kategoriler, Renkler vb.) yükle
python manage.py loaddata initial_data.json