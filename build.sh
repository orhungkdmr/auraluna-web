#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Paketleri Kur
pip install -r requirements.txt

# 2. Statik Dosyaları Topla (Debug parametrelerini kaldırdık)
python manage.py collectstatic --no-input

# 3. Veritabanını Güncelle
python manage.py migrate