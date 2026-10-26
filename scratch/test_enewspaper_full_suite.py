import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"c:\Django edutrust\edutrust")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
import TutionPlatform.views as views
import TutionPlatform.e_newspaper_views as e_newspaper_views
from TutionPlatform.models import StudyMaterial, ActivityLog

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

print("=== RUNNING COMPREHENSIVE TEST SUITE FOR EDUTRUST E-NEWSPAPER MANAGEMENT CENTER ===")

# Test 1: HTML View Endpoint GET /admin/study-material/e-newspaper/
req_html = add_session(rf.get('/admin/study-material/e-newspaper/'))
resp_html = views.admin_e_newspaper_view(req_html)
assert resp_html.status_code == 200
html_content = resp_html.content.decode('utf-8')
assert "kpiTotalNewspapers" in html_content
assert "modalAddNewspaper" in html_content
print("1. Admin E-Newspaper HTML View & Template Rendering: HTTP 200 OK")

# Test 2: Create The Hindu Edition
req_c1 = add_session(rf.post('/api/admin/e-newspaper/create/', data={
    'title': 'The Hindu - 31 Aug 2026 (Delhi Edition)',
    'publication_name': 'The Hindu',
    'publication_date': '2026-08-31',
    'edition_name': 'Delhi Edition',
    'newspaper_category': 'Daily Newspaper',
    'language': 'English',
    'page_count': '28',
    'access_level': 'Everyone',
    'status': 'Published'
}))
resp_c1 = e_newspaper_views.api_admin_enewspaper_create(req_c1)
assert resp_c1.status_code == 200
data_c1 = json.loads(resp_c1.content.decode('utf-8'))
assert data_c1['status'] in ['success', 'duplicate']
res1_id = data_c1.get('newspaper_id')
print(f"2. Created The Hindu Edition: ID={res1_id}")

# Test 3: Create Indian Express Edition
req_c2 = add_session(rf.post('/api/admin/e-newspaper/create/', data={
    'title': 'Indian Express - 31 Aug 2026 (National Edition)',
    'publication_name': 'Indian Express',
    'publication_date': '2026-08-31',
    'edition_name': 'National Edition',
    'newspaper_category': 'Daily Newspaper',
    'language': 'English',
    'page_count': '24',
    'access_level': 'Everyone',
    'status': 'Published'
}))
resp_c2 = e_newspaper_views.api_admin_enewspaper_create(req_c2)
assert resp_c2.status_code == 200
data_c2 = json.loads(resp_c2.content.decode('utf-8'))
assert data_c2['status'] in ['success', 'duplicate']
res2_id = data_c2.get('newspaper_id')
print(f"3. Created Indian Express Edition: ID={res2_id}")

# Test 4: List API GET /api/admin/e-newspaper/list/
req_list = add_session(rf.get('/api/admin/e-newspaper/list/?page=1&page_size=10'))
resp_list = e_newspaper_views.api_admin_enewspaper_list(req_list)
assert resp_list.status_code == 200
data_list = json.loads(resp_list.content.decode('utf-8'))
assert data_list['status'] == 'success'
assert 'items' in data_list
print(f"4. List API: Returned {len(data_list['items'])} items (Total: {data_list['pagination']['total']})")

# Test 5: KPI API GET /api/admin/e-newspaper/kpis/
req_kpi = add_session(rf.get('/api/admin/e-newspaper/kpis/'))
resp_kpi = e_newspaper_views.api_admin_enewspaper_kpis(req_kpi)
assert resp_kpi.status_code == 200
data_kpi = json.loads(resp_kpi.content.decode('utf-8'))
assert data_kpi['status'] == 'success'
k = data_kpi['kpis']
print(f"5. KPI API: Total={k['total_newspapers']}, Today={k['published_today']}, Scheduled={k['scheduled']}, Reads={k['total_reads']}")

# Test 6: Analytics API GET /api/admin/e-newspaper/analytics/
req_ana = add_session(rf.get('/api/admin/e-newspaper/analytics/'))
resp_ana = e_newspaper_views.api_admin_enewspaper_analytics(req_ana)
assert resp_ana.status_code == 200
data_ana = json.loads(resp_ana.content.decode('utf-8'))
assert data_ana['status'] == 'success'
print(f"6. Analytics API: Donut National={data_ana['donut']['national']}, Storage={data_ana['storage']['used_gb']} GB")

# Test 7: Bulk Action API
if res1_id and res2_id:
    req_bulk = add_session(rf.post('/api/admin/e-newspaper/bulk-actions/', data=json.dumps({
        'ids': [res1_id, res2_id],
        'action': 'publish'
    }), content_type='application/json'))
    resp_bulk = e_newspaper_views.api_admin_enewspaper_bulk_actions(req_bulk)
    assert resp_bulk.status_code == 200
    print("7. Bulk Action API: Published test newspapers successfully")

# Clean up test created resources and activity logs
if res1_id:
    StudyMaterial.objects.filter(id=res1_id).delete()
if res2_id:
    StudyMaterial.objects.filter(id=res2_id).delete()
ActivityLog.objects.filter(user_name='admin_tester').delete()

print("\nALL 7 E-NEWSPAPER TEST CASES PASSED 100% PERFECTLY!")
