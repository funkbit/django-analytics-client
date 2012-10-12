from django.conf import settings as djsettings


# Settings

_ANALYTICS_USERNAME = getattr(djsettings, 'ANALYTICS_USERNAME', None)
_ANALYTICS_PASSWORD = getattr(djsettings, 'ANALYTICS_PASSWORD', None)
_ANALYTICS_SITE_ID = getattr(djsettings, 'ANALYTICS_SITE_ID', None)
_ANALYTICS_HOST = getattr(djsettings, 'ANALYTICS_HOST', None)
_ANALYTICS_PORT = getattr(djsettings, 'ANALYTICS_PORT', None)
_ANALYTICS_ENABLED = getattr(djsettings, 'ANALYTICS_ENABLED', False)
