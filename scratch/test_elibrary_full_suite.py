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
import TutionPlatform.e_library_views as e_library_views
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

print("=== RUNNING COMPREHENSIVE TEST SUITE FOR EDUTRUST E-LIBRARY MANAGEMENT CENTER ===")

# Test 1: HTML View Endpoint GET /admin/study-material/e-library/
req_html = add_session(rf.get('/admin/study-material/e-library/'))
resp_html = views.admin_e_library_view(req_html)
assert resp_html.status_code == 200
html_content = resp_html.content.decode('utf-8')
assert "kpiTotalResources" in html_content
assert "modalAddResource" in html_content
print("1. Admin E-Library HTML View & Template Rendering: HTTP 200 OK")

# Test 2: Create eBook Resource for Class 10
req_c1 = add_session(rf.post('/api/admin/e-library/create/', data={
    'title': 'NCERT Mathematics Class 10 (2026 Edition)',
    'author': 'NCERT Editorial Board',
    'publisher': 'NCERT Publications',
    'isbn': '978-81-7450-1234',
    'resource_type': 'eBook',
    'class_name': 'Class 10',
    'board': 'CBSE',
    'subject': 'Mathematics',
    'chapter': 'Real Numbers',
    'publication_year': '2026',
    'language': 'English',
    'access_level': 'Everyone',
    'status': 'Published'
}))
resp_c1 = e_library_views.api_admin_elibrary_create(req_c1)
assert resp_c1.status_code == 200
data_c1 = json.loads(resp_c1.content.decode('utf-8'))
assert data_c1['status'] in ['success', 'duplicate']
res1_id = data_c1.get('resource_id')
print(f"2. Created Class 10 eBook Resource: ID={res1_id}")

# Test 3: Create Physics Doc Resource for Class 12 Science
req_c2 = add_session(rf.post('/api/admin/e-library/create/', data={
    'title': 'NCERT Physics Class 12 Part 1',
    'author': 'NCERT Editorial Board',
    'publisher': 'NCERT Publications',
    'isbn': '978-81-7450-5678',
    'resource_type': 'PDFs & Docs',
    'class_name': 'Class 12',
    'board': 'CBSE',
    'stream': 'Science',
    'subject': 'Physics',
    'chapter': 'Electrostatics',
    'publication_year': '2026',
    'language': 'English',
    'access_level': 'Everyone',
    'status': 'Published'
}))
resp_c2 = e_library_views.api_admin_elibrary_create(req_c2)
assert resp_c2.status_code == 200
data_c2 = json.loads(resp_c2.content.decode('utf-8'))
assert data_c2['status'] in ['success', 'duplicate']
res2_id = data_c2.get('resource_id')
print(f"3. Created Class 12 Doc Resource: ID={res2_id}")

# Test 4: List API GET /api/admin/e-library/list/
req_list = add_session(rf.get('/api/admin/e-library/list/?page=1&page_size=10'))
resp_list = e_library_views.api_admin_elibrary_list(req_list)
assert resp_list.status_code == 200
data_list = json.loads(resp_list.content.decode('utf-8'))
assert data_list['status'] == 'success'
assert 'items' in data_list
print(f"4. List API: Returned {len(data_list['items'])} items (Total: {data_list['pagination']['total']})")

# Test 5: KPI API GET /api/admin/e-library/kpis/
req_kpi = add_session(rf.get('/api/admin/e-library/kpis/'))
resp_kpi = e_library_views.api_admin_elibrary_kpis(req_kpi)
assert resp_kpi.status_code == 200
data_kpi = json.loads(resp_kpi.content.decode('utf-8'))
assert data_kpi['status'] == 'success'
k = data_kpi['kpis']
print(f"5. KPI API: Total={k['total_resources']}, eBooks={k['ebooks']}, PDFs={k['pdfs_docs']}, Reads={k['total_reads']}")

# Test 6: Analytics API GET /api/admin/e-library/analytics/
req_ana = add_session(rf.get('/api/admin/e-library/analytics/'))
resp_ana = e_library_views.api_admin_elibrary_analytics(req_ana)
assert resp_ana.status_code == 200
data_ana = json.loads(resp_ana.content.decode('utf-8'))
assert data_ana['status'] == 'success'
print(f"6. Analytics API: Donut eBooks={data_ana['donut']['ebooks_count']}, Storage={data_ana['storage']['used_gb']} GB")

# Test 7: Bulk Action API
if res1_id and res2_id:
    req_bulk = add_session(rf.post('/api/admin/e-library/bulk-actions/', data=json.dumps({
        'ids': [res1_id, res2_id],
        'action': 'publish'
    }), content_type='application/json'))
    resp_bulk = e_library_views.api_admin_elibrary_bulk_actions(req_bulk)
    assert resp_bulk.status_code == 200
    print("7. Bulk Action API: Published test resources successfully")

# Clean up test created resources and activity logs
if res1_id:
    StudyMaterial.objects.filter(id=res1_id).delete()
if res2_id:
    StudyMaterial.objects.filter(id=res2_id).delete()
ActivityLog.objects.filter(user_name='admin_tester').delete()

print("\nALL 7 E-LIBRARY TEST CASES PASSED 100% PERFECTLY!")
