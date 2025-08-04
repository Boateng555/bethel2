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
import re

def test_video_display():
    print("=== Comprehensive Video Display Test ===")
    
    # Get the hero
    gs = GlobalSettings.get_settings()
    hero = gs.global_hero
    
    if not hero:
        print("❌ No global hero set")
        return
    
    print(f"✅ Hero: {hero.title}")
    print(f"✅ Background Type: {hero.background_type}")
    print(f"✅ Background Video: {hero.background_video}")
    print(f"✅ Video URL: {hero.get_background_video_url()}")
    
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
        
        # Check for video element
        video_pattern = r'<video[^>]*id="hero-video"[^>]*>'
        video_match = re.search(video_pattern, html, re.IGNORECASE)
        
        if video_match:
            print("✅ Video element found with correct ID")
            
            # Extract the video element and its attributes
            video_start = video_match.start()
            video_end = html.find('</video>', video_start) + 8
            video_element = html[video_start:video_end]
            
            print("\n=== Video Element Analysis ===")
            print(video_element)
            
            # Check for source element
            source_pattern = r'<source[^>]*src="([^"]*)"[^>]*>'
            source_match = re.search(source_pattern, video_element)
            
            if source_match:
                video_src = source_match.group(1)
                print(f"\n✅ Video source found: {video_src}")
                
                # Check if source matches expected URL
                expected_url = hero.get_background_video_url()
                if video_src == expected_url:
                    print("✅ Video source URL matches expected URL")
                else:
                    print(f"❌ Video source URL mismatch:")
                    print(f"   Expected: {expected_url}")
                    print(f"   Found: {video_src}")
            else:
                print("❌ No source element found in video")
            
            # Check for autoplay attribute
            if 'autoplay' in video_element.lower():
                print("✅ Autoplay attribute found")
            else:
                print("❌ Autoplay attribute missing")
            
            # Check for muted attribute
            if 'muted' in video_element.lower():
                print("✅ Muted attribute found")
            else:
                print("❌ Muted attribute missing")
            
            # Check for CSS classes
            if 'absolute' in video_element:
                print("✅ Absolute positioning found")
            else:
                print("❌ Absolute positioning missing")
            
            if 'object-cover' in video_element:
                print("✅ Object-cover class found")
            else:
                print("❌ Object-cover class missing")
                
        else:
            print("❌ Video element with ID 'hero-video' not found")
            
            # Look for any video element
            any_video_pattern = r'<video[^>]*>'
            any_video_match = re.search(any_video_pattern, html, re.IGNORECASE)
            if any_video_match:
                print("⚠️ Found video element but without correct ID")
            else:
                print("❌ No video element found at all")
        
        # Check for JavaScript
        if 'hero-video' in html:
            print("✅ JavaScript references to hero-video found")
        else:
            print("❌ No JavaScript references to hero-video")
        
        # Save HTML for manual inspection
        with open('video_debug_output.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n✅ Full HTML saved to video_debug_output.html")
        
        # Check for potential CSS issues
        print("\n=== Potential Issues ===")
        
        # Check if video is hidden by CSS
        if 'display: none' in html or 'visibility: hidden' in html:
            print("⚠️ Found CSS that might hide elements")
        
        # Check for z-index issues
        if 'z-index' in html:
            print("⚠️ Z-index found - check for layering issues")
        
        # Check for overflow hidden
        if 'overflow-hidden' in html:
            print("⚠️ Overflow hidden found - might clip video")
            
    except Exception as e:
        print(f"❌ Error rendering template: {e}")

if __name__ == "__main__":
    test_video_display() 