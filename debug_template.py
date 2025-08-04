#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import GlobalSettings, Hero
from django.template.loader import render_to_string
from django.test import RequestFactory

def debug_template():
    print("=== Template Debug ===")
    
    # Get the hero
    gs = GlobalSettings.get_settings()
    hero = gs.global_hero
    
    if not hero:
        print("❌ No global hero set")
        return
    
    print(f"✅ Hero: {hero.title}")
    print(f"✅ Background Type: {hero.background_type}")
    print(f"✅ Background Video: {hero.background_video}")
    print(f"✅ Hero Media Count: {hero.hero_media.count()}")
    
    # Create a mock request
    rf = RequestFactory()
    request = rf.get('/global/')
    
    # Prepare context
    context = {
        'hero': hero,
        'upcoming_events': [],
        'ministries': [],
        'sermons': [],
        'news': [],
        'all_events': [],
        'all_ministries': [],
        'user_country': None,
        'user_city': None,
        'nearest_church': None,
        'is_global_site': True,
        'recent_testimonies': [],
    }
    
    # Render the template
    try:
        html = render_to_string('core/home.html', context, request=request)
        
        # Check if video element is in the HTML
        if 'hero-video' in html:
            print("✅ Video element found in HTML")
        else:
            print("❌ Video element NOT found in HTML")
        
        # Check if background video condition is met
        if hero.background_type == 'video' and hero.background_video:
            print("✅ Background video condition is met")
        else:
            print("❌ Background video condition NOT met")
        
        # Check if hero media exists
        if hero.hero_media.all():
            print("🔴 Hero media exists - this will override background video")
        else:
            print("✅ No hero media - background video should be used")
        
        # Look for specific template sections
        if 'background_type == \'video\'' in html:
            print("✅ Video condition found in template")
        else:
            print("❌ Video condition NOT found in template")
            
        if 'get_background_video_url' in html:
            print("✅ Video URL method found in template")
        else:
            print("❌ Video URL method NOT found in template")
        
        # Save HTML to file for inspection
        with open('debug_template_output.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ HTML saved to debug_template_output.html")
        
    except Exception as e:
        print(f"❌ Error rendering template: {e}")

if __name__ == "__main__":
    debug_template() 