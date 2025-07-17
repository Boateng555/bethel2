from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary
import cloudinary.uploader
import tempfile
import os

class Command(BaseCommand):
    help = 'Test Cloudinary upload using Django configuration'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing Cloudinary with Django management command...")
        self.stdout.write("=" * 50)

        # Get credentials from Django settings
        cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        api_key = settings.CLOUDINARY_STORAGE['API_KEY']
        api_secret = settings.CLOUDINARY_STORAGE['API_SECRET']

        self.stdout.write(f"Cloud Name: {cloud_name}")
        self.stdout.write(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
        self.stdout.write(f"API Secret: {api_secret[:8]}...{api_secret[-4:] if len(api_secret) > 12 else '***'}")

        self.stdout.write("\n" + "=" * 50)

        try:
            # Configure Cloudinary
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("This is a test file for Django Cloudinary management command.")
                temp_file_path = f.name
            
            try:
                # Test upload with the temporary file
                result = cloudinary.uploader.upload(
                    temp_file_path,
                    public_id="test_django_mgmt_command",
                    overwrite=True
                )
                
                self.stdout.write(self.style.SUCCESS("✅ Django Cloudinary upload test successful!"))
                self.stdout.write(f"Test file URL: {result.get('secure_url', 'N/A')}")
                
                # Clean up test file from Cloudinary
                cloudinary.uploader.destroy("test_django_mgmt_command")
                self.stdout.write("🧹 Test file cleaned up from Cloudinary")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Django Cloudinary test failed: {e}"))
            self.stdout.write("\nPossible issues:")
            self.stdout.write("1. Invalid API credentials")
            self.stdout.write("2. Network connectivity issues")
            self.stdout.write("3. Cloudinary account restrictions")
            self.stdout.write("4. API key/secret mismatch")

        self.stdout.write("\n" + "=" * 50) 