#!/usr/bin/env bash
# Script de build para Render / Vercel
echo "Instalando dependencias de Frontend..."
pip install -r requirements.txt

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Aplicando migraciones..."
python manage.py migrate --noinput
