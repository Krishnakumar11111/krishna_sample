import os, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"c:\Django edutrust\edutrust")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
import TutionPlatform.views as views

rf = RequestFactory()
admin_user, _ = User.objects.get_or_create(username='admin_tester', defaults={'is_staff': True, 'is_superuser': True})

def add_session(req):
    req.user = admin_user
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(req)
    req.session['user_role'] = 'admin'
    req.session['user_name'] = 'admin_tester'
    req.session.save()
    return req

req1 = add_session(rf.get('/admin/study-material/e-library/'))
resp1 = views.admin_e_library_view(req1)
print("GET /admin/study-material/e-library/: status=", resp1.status_code)

req2 = add_session(rf.get('/admin/e-library/'))
resp2 = views.admin_e_library_view(req2)
print("GET /admin/e-library/: status=", resp2.status_code)
