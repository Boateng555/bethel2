from .models import GlobalSettings

def global_settings(request):
    """Add global settings to all template contexts"""
    try:
        settings = GlobalSettings.get_settings()
        return {
            'global_settings': settings
        }
    except Exception:
        # If there's any error, return empty settings
        return {
            'global_settings': None
        } 