#!/usr/bin/env bash
# exit on error
set -o errexit

echo "---------------------------------------------"
echo "--- DEDEKTIF BASLADI: static ICINDE NE VAR? ---"
ls -R static/
echo "---------------------------------------------"

# Normal kurulum devam ediyor
pip install -r requirements.txt
python manage.py collectstatic --no-input --clear --verbosity 2
python manage.py migrate