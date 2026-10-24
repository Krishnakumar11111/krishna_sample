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

req_html = add_session(rf.get('/admin/study-material/e-library/'))
resp_html = views.admin_e_library_view(req_html)
html_content = resp_html.content.decode('utf-8')

print("Template rendered size:", len(html_content))

idx = html_content.find("kpiTotalResources")
print("kpiTotalResources index:", idx)
if idx != -1:
    print("Snippet:", html_content[idx-100:idx+300])
else:
    print("Snippet top 500:", html_content[:500])
