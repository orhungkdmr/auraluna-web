#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- 1. PAKETLER YUKLENIYOR ---"
pip install -r requirements.txt

echo "--- 2. STATIK DOSYALAR TOPLANIYOR (DETAYLI MOD) ---"
# --clear: Eski dosyaları siler
# --verbosity 2: İşlenen her dosyayı ekrana yazar
python manage.py collectstatic --no-input --clear --verbosity 2

echo "--- 3. VERITABANI GUNCELLEMESI ---"
python manage.py migrate