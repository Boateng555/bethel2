#!/bin/bash

echo "🔧 Installing all missing packages for Django project..."

# Install all required packages
echo "📦 Installing Django REST Framework..."
sudo pip3 install djangorestframework

echo "📦 Installing Django CORS Headers..."
sudo pip3 install django-cors-headers

echo "📦 Installing WhiteNoise..."
sudo pip3 install whitenoise

echo "📦 Installing Python Dotenv..."
sudo pip3 install python-dotenv

echo "📦 Installing QR Code..."
sudo pip3 install qrcode

echo "📦 Installing Pillow..."
sudo pip3 install pillow

echo "📦 Installing Requests..."
sudo pip3 install requests

echo "✅ All packages installed!"
echo ""
echo "🚀 Now trying to run the management command..."
python3 manage.py fix_all_images 