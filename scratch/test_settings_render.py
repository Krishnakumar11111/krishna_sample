import os, sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
import django
django.setup()
from django.test import RequestFactory
from django.contrib.auth.models import User
from TutionPlatform.settings_views import admin_settings_view
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

rf = RequestFactory()
req = rf.get('/admin/settings/')
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
req.user = admin_user
SessionMiddleware(lambda r: None).process_request(req)
req.session.save()
MessageMiddleware(lambda r: None).process_request(req)

resp = admin_settings_view(req)
print('Settings view status:', resp.status_code)
content = resp.content.decode('utf-8')
print('Has settingsContainer:', 'settingsContainer' in content)
print('Has settingsFormContainer:', 'settingsFormContainer' in content)
print('Has catFieldsArea:', 'catFieldsArea' in content)
print('Has catNavList:', 'catNavList' in content)
print('Has initSettingsModule:', 'initSettingsModule' in content)
print('data-active-module="settings":', 'data-active-module="settings"' in content)
print('data-server-rendered="true":', 'data-server-rendered="true"' in content)
