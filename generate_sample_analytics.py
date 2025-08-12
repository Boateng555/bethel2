#!/usr/bin/env python
"""
Generate sample analytics data for testing the beautiful dashboard
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.analytics_models import VisitorSession, PageView, AnalyticsSettings
from core.models import Church
from django.utils import timezone

def generate_sample_data():
    """Generate realistic sample analytics data"""
    print("🎯 Generating sample analytics data...")
    
    # Get or create analytics settings
    settings, created = AnalyticsSettings.objects.get_or_create()
    print(f"✅ Analytics settings: {'Created' if created else 'Found'}")
    
    # Sample countries and cities
    locations = [
        ('United States', 'New York', '127.0.0.1'),
        ('United States', 'Los Angeles', '127.0.0.2'),
        ('Germany', 'Berlin', '127.0.0.3'),
        ('Germany', 'Hamburg', '127.0.0.4'),
        ('United Kingdom', 'London', '127.0.0.5'),
        ('Canada', 'Toronto', '127.0.0.6'),
        ('Australia', 'Sydney', '127.0.0.7'),
        ('France', 'Paris', '127.0.0.8'),
        ('Netherlands', 'Amsterdam', '127.0.0.9'),
        ('Sweden', 'Stockholm', '127.0.0.10'),
    ]
    
    # Sample pages
    pages = [
        '/',
        '/global/',
        '/about/',
        '/events/',
        '/ministries/',
        '/sermons/',
        '/contact/',
        '/prayer-request/',
        '/donate/',
        '/church/1/',
        '/church/1/about/',
        '/church/1/events/',
    ]
    
    # Sample browsers and devices
    browsers = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Opera']
    devices = ['desktop', 'mobile', 'tablet']
    
    # Generate sessions over the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    session_count = 0
    page_view_count = 0
    
    for i in range(150):  # Generate 150 sessions
        # Random date within last 30 days
        session_date = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Random location
        country, city, ip = random.choice(locations)
        
        # Random device and browser
        device = random.choice(devices)
        browser = random.choice(browsers)
        
        # Create session
        session = VisitorSession.objects.create(
            session_id=f"sample_session_{i}_{random.randint(1000, 9999)}",
            ip_address=ip,
            user_agent=f"Mozilla/5.0 ({device}) {browser}/120.0",
            country=country,
            city=city,
            region="",
            device_type=device,
            browser=browser,
            browser_version="120.0",
            os="Windows 10" if device == 'desktop' else "iOS" if device == 'mobile' else "Android",
            referrer="",
            referrer_domain="",
            church=None,
            page_views_count=random.randint(1, 8),
            duration=random.randint(30, 1800),  # 30 seconds to 30 minutes
            started_at=session_date,
            last_activity=session_date + timedelta(minutes=random.randint(5, 45)),
            ended_at=session_date + timedelta(minutes=random.randint(5, 45))
        )
        session_count += 1
        
        # Generate page views for this session
        num_pages = session.page_views_count
        for j in range(num_pages):
            page_view_date = session_date + timedelta(minutes=random.randint(0, 30))
            
            PageView.objects.create(
                session=session,
                url=f"http://localhost:8000{random.choice(pages)}",
                path=random.choice(pages),
                page_title=f"Sample Page {j+1}",
                view_name="sample_view",
                church=None,
                load_time=random.randint(200, 2000),
                viewed_at=page_view_date
            )
            page_view_count += 1
    
    print(f"✅ Generated {session_count} visitor sessions")
    print(f"✅ Generated {page_view_count} page views")
    print("🎉 Sample analytics data created successfully!")
    print("\n📊 You can now view the beautiful analytics dashboard at:")
    print("   http://127.0.0.1:8000/analytics/")
    print("\n🔍 Features you'll see:")
    print("   🌍 Interactive world map with visitor locations")
    print("   📈 Beautiful gradient charts and graphs")
    print("   📊 Real-time statistics with animations")
    print("   📱 Device and browser breakdowns")
    print("   🌍 Geographic visitor distribution")
    print("   🔥 Most popular pages analysis")

if __name__ == '__main__':
    generate_sample_data()
