#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings
from django.template.loader import render_to_string
from django.test import RequestFactory

def test_template_render():
    print("=== Template Render Test ===")
    
    # Get the global hero
    gs = GlobalSettings.get_settings()
    hero = gs.global_hero
    
    if not hero:
        print("❌ No global hero found")
        return
    
    print(f"✅ Hero: {hero.title}")
    print(f"✅ Is Active: {hero.is_active}")
    print(f"✅ Hero Media Count: {hero.hero_media.count()}")
    print(f"✅ Background Type: {hero.background_type}")
    print(f"✅ Background Video: {hero.background_video}")
    
    # Create a mock request
    rf = RequestFactory()
    request = rf.get('/global/?global=1')
    
    # Render the template
    context = {
        'hero': hero,
        'upcoming_events': [],
        'featured_events': [],
        'public_ministries': [],
        'latest_news': [],
        'latest_sermons': [],
        'nearest_church': None,
        'all_events': [],
        'all_ministries': [],
        'recent_testimonies': [],
        'country': None,
        'city': None,
    }
    
    try:
        html = render_to_string('core/home.html', context, request=request)
        
        # Check for carousel elements
        if 'swiper hero-swiper' in html:
            print("✅ Swiper carousel found in HTML")
        else:
            print("❌ Swiper carousel NOT found in HTML")
        
        if 'swiper-slide' in html:
            print("✅ Swiper slides found in HTML")
        else:
            print("❌ Swiper slides NOT found in HTML")
        
        if 'swiper-pagination' in html:
            print("✅ Swiper pagination found in HTML")
        else:
            print("❌ Swiper pagination NOT found in HTML")
        
        # Check for video elements
        if '<video' in html:
            print("✅ Video element found in HTML")
        else:
            print("❌ Video element NOT found in HTML")
        
        # Save the HTML for inspection
        with open('template_test_output.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ HTML saved to template_test_output.html")
        
        # Check the hero media condition
        hero_media_exists = hero.hero_media.exists()
        print(f"✅ Hero media exists: {hero_media_exists}")
        
        if hero_media_exists:
            print("✅ Template should show carousel")
        else:
            print("❌ Template should NOT show carousel")
            
    except Exception as e:
        print(f"❌ Error rendering template: {e}")

if __name__ == "__main__":
    test_template_render() 