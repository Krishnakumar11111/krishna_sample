import os, sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
import django
django.setup()
from django.test import RequestFactory
from django.contrib.auth.models import User
from TutionPlatform.settings_views import api_admin_settings_list
import json

rf = RequestFactory()
req = rf.get('/api/admin/settings/list/')
admin_user = User.objects.filter(is_superuser=True).first()
req.user = admin_user
resp = api_admin_settings_list(req)
data = json.loads(resp.content)
for cat, items in data.get('settings', {}).items():
    for k, v in items.items():
        val = v.get('value')
        if v.get('type') == 'boolean':
            print(f'[{cat}] {k}: val={repr(val)} type={type(val).__name__}')
