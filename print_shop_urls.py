#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Church

for church in Church.objects.all():
    print(f"{church.name}: {church.shop_url}") 