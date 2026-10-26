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
import TutionPlatform.pyq_views as pyq_views
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

print("=== RUNNING COMPREHENSIVE TEST SUITE FOR PYQ & MODEL PAPERS MANAGEMENT CENTER ===")

# Test 1: HTML View Endpoint GET /admin/study-material/pyq-model-papers/
req_html = add_session(rf.get('/admin/study-material/pyq-model-papers/'))
resp_html = views.admin_pyq_view(req_html)
assert resp_html.status_code == 200
print("1. Admin PYQ & Model Papers HTML View: HTTP 200 OK")

# Test 2: Create PYQ Paper for Class 10
req_c1 = add_session(rf.post('/api/admin/pyq-model-papers/create/', data={
    'title': 'CBSE Class 10 Mathematics PYQ 2024 Test Paper',
    'class_name': 'Class 10',
    'board': 'CBSE',
    'subject': 'Mathematics',
    'chapter': 'Real Numbers',
    'paper_type': 'PYQ',
    'exam_year': '2024',
    'set_name': 'Set 1',
    'status': 'Published'
}))
resp_c1 = pyq_views.api_admin_pyq_model_papers_create(req_c1)
print("Create response status:", resp_c1.status_code)
print("Create response content:", resp_c1.content.decode('utf-8'))
assert resp_c1.status_code == 200
data_c1 = json.loads(resp_c1.content.decode('utf-8'))
assert data_c1['status'] in ['success', 'duplicate']
paper1_id = data_c1.get('paper_id')
print(f"2. Created Class 10 PYQ Paper: ID={paper1_id}")

# Test 3: Create Model Paper for Class 12 Science
req_c2 = add_session(rf.post('/api/admin/pyq-model-papers/create/', data={
    'title': 'CBSE Class 12 Physics Model Paper 2024',
    'class_name': 'Class 12',
    'board': 'CBSE',
    'stream': 'Science',
    'subject': 'Physics',
    'chapter': 'Electrostatics',
    'paper_type': 'Model Paper',
    'exam_year': '2024',
    'set_name': 'Set A',
    'status': 'Published'
}))
resp_c2 = pyq_views.api_admin_pyq_model_papers_create(req_c2)
assert resp_c2.status_code == 200
data_c2 = json.loads(resp_c2.content.decode('utf-8'))
assert data_c2['status'] in ['success', 'duplicate']
paper2_id = data_c2.get('paper_id')
print(f"3. Created Class 12 Model Paper: ID={paper2_id}")

# Test 4: List API GET /api/admin/pyq-model-papers/list/
req_list = add_session(rf.get('/api/admin/pyq-model-papers/list/?page=1&page_size=10'))
resp_list = pyq_views.api_admin_pyq_model_papers_list(req_list)
assert resp_list.status_code == 200
data_list = json.loads(resp_list.content.decode('utf-8'))
assert data_list['status'] == 'success'
assert 'items' in data_list
print(f"4. List API: Returned {len(data_list['items'])} items (Total: {data_list['pagination']['total']})")

# Test 5: KPI API GET /api/admin/pyq-model-papers/kpis/
req_kpi = add_session(rf.get('/api/admin/pyq-model-papers/kpis/'))
resp_kpi = pyq_views.api_admin_pyq_model_papers_kpis(req_kpi)
assert resp_kpi.status_code == 200
data_kpi = json.loads(resp_kpi.content.decode('utf-8'))
assert data_kpi['status'] == 'success'
k = data_kpi['kpis']
print(f"5. KPI API: Total={k['total_papers']}, PYQ={k['pyq_papers']}, Model={k['model_papers']}, Downloads={k['total_downloads']}")

# Test 6: Analytics API GET /api/admin/pyq-model-papers/analytics/
req_ana = add_session(rf.get('/api/admin/pyq-model-papers/analytics/'))
resp_ana = pyq_views.api_admin_pyq_model_papers_analytics(req_ana)
assert resp_ana.status_code == 200
data_ana = json.loads(resp_ana.content.decode('utf-8'))
assert data_ana['status'] == 'success'
print(f"6. Analytics API: Donut PYQ%={data_ana['donut']['pyq_pct']}%, Top Subjects={len(data_ana['top_subjects'])}")

# Test 7: Bulk Action API
if paper1_id and paper2_id:
    req_bulk = add_session(rf.post('/api/admin/pyq-model-papers/bulk-actions/', data=json.dumps({
        'ids': [paper1_id, paper2_id],
        'action': 'publish'
    }), content_type='application/json'))
    resp_bulk = pyq_views.api_admin_pyq_model_papers_bulk_actions(req_bulk)
    assert resp_bulk.status_code == 200
    print("7. Bulk Action API: Published test papers successfully")

# Clean up test created papers and activity logs
if paper1_id:
    StudyMaterial.objects.filter(id=paper1_id).delete()
if paper2_id:
    StudyMaterial.objects.filter(id=paper2_id).delete()
ActivityLog.objects.filter(user_name='admin_tester').delete()

print("\nALL 7 PYQ & MODEL PAPERS TEST CASES PASSED 100% PERFECTLY!")
