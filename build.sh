#!/usr/bin/env bash
# exit on error
set -o errexit

echo "---------------------------------------------"
echo "--- DEDEKTIF BASLADI: NEREDEYIM? ---"
pwd
echo "---------------------------------------------"

echo "--- BURADA HANGI DOSYALAR VAR? (LISTE) ---"
ls -la
echo "---------------------------------------------"

echo "--- STATIC KLASORU VAR MI? ---"
if [ -d "static" ]; then
  echo "EVET: 'static' klasörü kök dizinde bulundu."
  echo "ICINDE NE VAR?:"
  ls -la static
else
  echo "HAYIR: Kök dizinde 'static' diye bir klasör YOK!"
  echo "Belki harf hatası vardır (Static vs static)?:"
  ls -d *tatic* 2>/dev/null || echo "Benzer isimli klasör de yok."
fi
echo "---------------------------------------------"

# Kurulum Devam Ediyor
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate