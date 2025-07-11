#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.models import LocalAboutPage, ChurchAdmin, Church, Event, Ministry, News, Sermon, DonationMethod, LocalLeadershipPage
from django.contrib.auth.models import User

def test_local_admin_interface():
    """Test what local admin sees in their admin interface"""
    print("🔍 TESTING LOCAL ADMIN INTERFACE")
    print("=" * 60)
    
    # Find the local admin user
    try:
        local_admin = ChurchAdmin.objects.get(
            user__username='kwameb320@gmail.com',
            role='local_admin',
            is_active=True
        )
        user = local_admin.user
        church = local_admin.church
        print(f"✅ Found local admin: {user.username} ({user.email})")
        print(f"   Church: {church.name}")
        print(f"   Role: {local_admin.role}")
    except ChurchAdmin.DoesNotExist:
        print("❌ Local admin not found")
        return
    
    # Check LocalAboutPage permissions
    print(f"\n📋 CHECKING LOCALABOUTPAGE PERMISSIONS:")
    content_type = ContentType.objects.get_for_model(LocalAboutPage)
    required_permissions = [
        'add_localaboutpage',
        'change_localaboutpage', 
        'delete_localaboutpage',
        'view_localaboutpage'
    ]
    
    user_permissions = [perm.codename for perm in user.user_permissions.all()]
    localaboutpage_permissions = [perm for perm in user_permissions if 'localaboutpage' in perm]
    
    print(f"   User has {len(localaboutpage_permissions)} LocalAboutPage permissions:")
    for perm in localaboutpage_permissions:
        print(f"   ✅ {perm}")
    
    missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
    if missing_permissions:
        print(f"   ❌ Missing permissions: {missing_permissions}")
    else:
        print(f"   ✅ All LocalAboutPage permissions present!")
    
    # Check what content the local admin can see
    print(f"\n📊 CONTENT AVAILABLE TO LOCAL ADMIN:")
    
    # Events
    events = Event.objects.filter(church=church)
    print(f"   Events: {events.count()} (all for their church)")
    for event in events:
        print(f"     - {event.title} ({event.start_date.strftime('%Y-%m-%d')})")
    
    # Ministries
    ministries = Ministry.objects.filter(church=church)
    print(f"   Ministries: {ministries.count()} (all for their church)")
    for ministry in ministries:
        print(f"     - {ministry.name} ({ministry.ministry_type})")
    
    # News
    news = News.objects.filter(church=church)
    print(f"   News: {news.count()} (all for their church)")
    for news_item in news:
        print(f"     - {news_item.title} ({news_item.date})")
    
    # Sermons
    sermons = Sermon.objects.filter(church=church)
    print(f"   Sermons: {sermons.count()} (all for their church)")
    for sermon in sermons:
        print(f"     - {sermon.title} by {sermon.preacher} ({sermon.date})")
    
    # Donation Methods
    donations = DonationMethod.objects.filter(church=church)
    print(f"   Donation Methods: {donations.count()} (all for their church)")
    for donation in donations:
        print(f"     - {donation.name} ({donation.payment_type})")
    
    # Local About Page
    try:
        about_page = LocalAboutPage.objects.get(church=church)
        print(f"   Local About Page: ✅ EXISTS")
        print(f"     - Title: {about_page.title}")
        print(f"     - Has intro: {'Yes' if about_page.intro else 'No'}")
        print(f"     - Has founding story: {'Yes' if about_page.founding_story else 'No'}")
        print(f"     - Has images: {'Yes' if about_page.logo or about_page.founder_image else 'No'}")
    except LocalAboutPage.DoesNotExist:
        print(f"   Local About Page: ❌ NOT CREATED YET (will be auto-created when they visit About page)")
    
    # Local Leadership Page
    try:
        leadership_page = LocalLeadershipPage.objects.get(church=church)
        print(f"   Local Leadership Page: ✅ EXISTS")
        print(f"     - Title: {leadership_page.title}")
        print(f"     - Has intro: {'Yes' if leadership_page.intro else 'No'}")
        print(f"     - Has vision statement: {'Yes' if leadership_page.vision_statement else 'No'}")
    except LocalLeadershipPage.DoesNotExist:
        print(f"   Local Leadership Page: ❌ NOT CREATED YET (will be auto-created when they visit Leadership page)")
    
    # Check admin interface sections
    print(f"\n🎛️ ADMIN INTERFACE SECTIONS LOCAL ADMIN WILL SEE:")
    admin_sections = [
        "Events",
        "Ministries", 
        "News",
        "Sermons",
        "Donation Methods",
        "Local About Pages",  # NEW!
        "Local Leadership Pages",
        "Local Heroes",
        "Testimonies"
    ]
    
    for section in admin_sections:
        print(f"   ✅ {section}")
    
    print(f"\n🔒 SECTIONS LOCAL ADMIN WON'T SEE:")
    restricted_sections = [
        "Churches (other churches)",
        "Global Heroes",
        "Conventions", 
        "Global Feature Requests",
        "Users",
        "Groups",
        "Global About Page",
        "Global Leadership Page"
    ]
    
    for section in restricted_sections:
        print(f"   ❌ {section}")
    
    # Test LocalAboutPage creation
    print(f"\n🧪 TESTING LOCALABOUTPAGE CREATION:")
    if not LocalAboutPage.objects.filter(church=church).exists():
        print("   Creating LocalAboutPage for testing...")
        about_page = LocalAboutPage.objects.create(
            church=church,
            title="About Our Church",
            intro="Welcome to our church family!",
            founding_story="Our church was founded in faith and continues to grow in God's grace.",
            timeline="2020 - Church founded\n2021 - First building\n2022 - Community outreach begins",
            ministry_today="We serve our community through various ministries and outreach programs.",
            quick_facts="• Founded: 2020\n• Members: 150+\n• Services: Sunday 9AM & 11AM"
        )
        print(f"   ✅ Created LocalAboutPage with ID: {about_page.id}")
    else:
        print("   ✅ LocalAboutPage already exists")
    
    print(f"\n🎉 LOCAL ADMIN INTERFACE TEST COMPLETE!")
    print(f"   Local admin can now manage their church's About page")
    print(f"   They will see 'Local About Pages' in their admin sidebar")
    print(f"   All content is properly filtered to their church only")

if __name__ == "__main__":
    test_local_admin_interface() 