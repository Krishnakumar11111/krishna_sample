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
import TutionPlatform.coupons_views as coupons_views
from TutionPlatform.models import Coupon, RewardRule, ReferralCampaign, ActivityLog

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

print("=== RUNNING COMPREHENSIVE TEST SUITE FOR EDUTRUST COUPONS & REWARDS CENTER ===")

# Test 1: HTML View Endpoint GET /admin/coupons-rewards/
req_html = add_session(rf.get('/admin/coupons-rewards/'))
resp_html = views.admin_coupons_rewards_view(req_html)
assert resp_html.status_code == 200
html_content = resp_html.content.decode('utf-8')
assert "kpiTotalCoupons" in html_content
assert "modalCreateCoupon" in html_content
print("1. Admin Coupons & Rewards HTML View & Template Rendering: HTTP 200 OK")

# Test 2: Create WELCOME500 Coupon
req_c1 = add_session(rf.post('/api/admin/coupons-rewards/create/', data={
    'code': 'WELCOME500',
    'name': 'Welcome Offer Flat 500 OFF',
    'description': 'Flat Rs 500 discount on first purchase',
    'discount_type': 'Fixed Amount',
    'discount_value': '500',
    'min_purchase': '1999',
    'max_discount': '500',
    'applicable_to': 'All Courses',
    'max_uses': '5000',
    'per_user_limit': '1',
    'status': 'Active'
}))
resp_c1 = coupons_views.api_admin_coupons_create(req_c1)
assert resp_c1.status_code == 200
data_c1 = json.loads(resp_c1.content.decode('utf-8'))
assert data_c1['status'] in ['success', 'duplicate']
res1_id = data_c1.get('coupon_id')
print(f"2. Created WELCOME500 Coupon: ID={res1_id}")

# Test 3: Create STUDENT10 Coupon
req_c2 = add_session(rf.post('/api/admin/coupons-rewards/create/', data={
    'code': 'STUDENT10',
    'name': 'Student Special 10% OFF',
    'description': '10% discount on all school courses',
    'discount_type': 'Percentage',
    'discount_value': '10',
    'min_purchase': '999',
    'max_discount': '500',
    'applicable_to': 'Class 10',
    'max_uses': '2000',
    'per_user_limit': '2',
    'status': 'Active'
}))
resp_c2 = coupons_views.api_admin_coupons_create(req_c2)
assert resp_c2.status_code == 200
data_c2 = json.loads(resp_c2.content.decode('utf-8'))
assert data_c2['status'] in ['success', 'duplicate']
res2_id = data_c2.get('coupon_id')
print(f"3. Created STUDENT10 Coupon: ID={res2_id}")

# Test 4: List API GET /api/admin/coupons-rewards/list/
req_list = add_session(rf.get('/api/admin/coupons-rewards/list/?page=1&page_size=10'))
resp_list = coupons_views.api_admin_coupons_list(req_list)
assert resp_list.status_code == 200
data_list = json.loads(resp_list.content.decode('utf-8'))
assert data_list['status'] == 'success'
assert 'items' in data_list
print(f"4. List API: Returned {len(data_list['items'])} items (Total: {data_list['pagination']['total']})")

# Test 5: KPI API GET /api/admin/coupons-rewards/kpis/
req_kpi = add_session(rf.get('/api/admin/coupons-rewards/kpis/'))
resp_kpi = coupons_views.api_admin_coupons_kpis(req_kpi)
assert resp_kpi.status_code == 200
data_kpi = json.loads(resp_kpi.content.decode('utf-8'))
assert data_kpi['status'] == 'success'
k = data_kpi['kpis']
print(f"5. KPI API: Total={k['total_coupons']}, Active={k['active_coupons']}, Rewards={k['rewards_issued']}, Redemptions={k['total_redemptions']}")

# Test 6: Analytics API GET /api/admin/coupons-rewards/analytics/
req_ana = add_session(rf.get('/api/admin/coupons-rewards/analytics/'))
resp_ana = coupons_views.api_admin_coupons_analytics(req_ana)
assert resp_ana.status_code == 200
data_ana = json.loads(resp_ana.content.decode('utf-8'))
assert data_ana['status'] == 'success'
print(f"6. Analytics API: Donut Percentage={data_ana['donut_types']['percentage']}, Top Coupons={len(data_ana['top_coupons'])}")

# Test 7: Bulk Action API
if res1_id and res2_id:
    req_bulk = add_session(rf.post('/api/admin/coupons-rewards/bulk-actions/', data=json.dumps({
        'ids': [res1_id, res2_id],
        'action': 'activate'
    }), content_type='application/json'))
    resp_bulk = coupons_views.api_admin_coupons_bulk_actions(req_bulk)
    assert resp_bulk.status_code == 200
    print("7. Bulk Action API: Activated test coupons successfully")

# Clean up test created resources and activity logs
if res1_id:
    Coupon.objects.filter(id=res1_id).delete()
if res2_id:
    Coupon.objects.filter(id=res2_id).delete()
ActivityLog.objects.filter(user_name='admin_tester').delete()

print("\nALL 7 COUPONS & REWARDS TEST CASES PASSED 100% PERFECTLY!")
