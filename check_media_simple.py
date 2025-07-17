import os
import requests
from django.conf import settings
from core.models import Church, Hero, HeroMedia

def check_environment():
    print("Checking Environment Configuration")
    print("=" * 50)
    
    # Check DEBUG setting
    debug = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
    print(f"DEBUG: {debug}")
    
    # Check Cloudinary credentials
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    print(f"CLOUDINARY_CLOUD_NAME: {'Set' if cloud_name else 'Not set'}")
    print(f"CLOUDINARY_API_KEY: {'Set' if api_key else 'Not set'}")
    print(f"CLOUDINARY_API_SECRET: {'Set' if api_secret else 'Not set'}")
    
    # Check storage backend
    if debug:
        print("Using local storage (DEBUG=True)")
    elif all([cloud_name, api_key, api_secret]):
        print("Using Cloudinary storage")
    else:
        print("Using local storage (Cloudinary not configured)")
    
    print()

def check_media_files():
    print("Checking Media Files")
    print("=" * 50)
    
    # Check churches with media
    churches = Church.objects.all()
    print(f"Total churches: {churches.count()}")
    
    for church in churches:
        print(f"\nChurch: {church.name}")
        print(f"   ID: {church.id}")
        print(f"   Logo: {'Yes' if church.logo else 'No'}")
        if church.logo:
            print(f"   Logo URL: {church.logo.url}")
        
        # Check hero media
        heroes = Hero.objects.filter(church=church, is_active=True)
        print(f"   Active heroes: {heroes.count()}")
        
        for hero in heroes:
            print(f"     Hero: {hero.title}")
            hero_media = HeroMedia.objects.filter(hero=hero)
            print(f"       Media files: {hero_media.count()}")
            for media in hero_media:
                print(f"         - {media.media_type}: {media.media_file.url}")
    
    print()

def test_image_urls():
    print("Testing Image URLs")
    print("=" * 50)
    
    # Test a few image URLs
    churches = Church.objects.filter(logo__isnull=False)[:3]
    
    for church in churches:
        if church.logo:
            print(f"\nTesting logo for {church.name}:")
            print(f"  URL: {church.logo.url}")
            
            # Try to fetch the image
            try:
                response = requests.head(church.logo.url, timeout=5)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  Image accessible")
                else:
                    print(f"  Image not accessible")
            except Exception as e:
                print(f"  Error: {e}")
    
    print()

def check_hero_media():
    print("Checking Hero Media")
    print("=" * 50)
    
    # Check global heroes
    global_heroes = Hero.objects.filter(church__isnull=True, is_active=True)
    print(f"Global heroes: {global_heroes.count()}")
    
    for hero in global_heroes:
        print(f"\nGlobal Hero: {hero.title}")
        hero_media = HeroMedia.objects.filter(hero=hero)
        print(f"  Media files: {hero_media.count()}")
        for media in hero_media:
            print(f"    - {media.media_type}: {media.media_file.url}")
            try:
                response = requests.head(media.media_file.url, timeout=5)
                print(f"      Status: {response.status_code}")
            except Exception as e:
                print(f"      Error: {e}")
    
    print()

if __name__ == "__main__":
    check_environment()
    check_media_files()
    test_image_urls()
    check_hero_media() 