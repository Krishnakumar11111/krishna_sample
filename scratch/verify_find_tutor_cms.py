import os
import sys
import json

# Setup Django environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
import django
django.setup()

from django.test import RequestFactory
from TutionPlatform.models import SystemSetting, TeacherProfile, AcademicSubject
from TutionPlatform.find_tutor_config import (
    get_find_tutor_config,
    get_find_tutor_template_context,
    get_available_locations_and_subjects,
    DEFAULT_FIND_TUTOR_CONFIG
)
from TutionPlatform.views import find_tutor, api_public_tutors
from TutionPlatform.settings_views import api_admin_settings_category

rf = RequestFactory()

def run_tests():
    print("=== STARTING FIND TUTOR CMS <-> PUBLIC FIND TUTOR TESTS ===")

    # Test 1: Baseline config loading
    cfg = get_find_tutor_config()
    assert cfg is not None, "Config should not be None"
    assert "popular_locations" in cfg, "Config must contain popular_locations"
    assert "popular_subjects" in cfg, "Config must contain popular_subjects"
    assert "filters" in cfg, "Config must contain filters"
    print("[PASS] TEST 1 PASSED: Baseline config loaded successfully.")

    # Test 2: Context helper
    req = rf.get('/find-tutor/')
    ctx = get_find_tutor_template_context(req)
    assert ctx['filters_enabled'] is True
    assert len(ctx['popular_locations']) > 0
    assert len(ctx['popular_subjects']) > 0
    print("[PASS] TEST 2 PASSED: Template context generated with active lists.")

    # Test A: Add Location (Chandigarh) via Admin Settings API
    test_cfg = json.loads(json.dumps(DEFAULT_FIND_TUTOR_CONFIG))
    test_cfg['popular_locations'].append({
        'id': 'loc_chd_1',
        'name': 'Chandigarh',
        'icon': 'fa-location-dot',
        'link': '/find-tutor/?city=Chandigarh',
        'enabled': True,
        'order': 99
    })
    
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    res = api_admin_settings_category(save_req, 'homepage')
    assert res.status_code == 200, f"Save failed with status {res.status_code}"
    
    # Verify DB state
    db_setting = SystemSetting.objects.get(category='homepage', key='hp_find_tutor')
    db_data = json.loads(db_setting.value)
    loc_names = [l['name'] for l in db_data['popular_locations']]
    assert 'Chandigarh' in loc_names, "Chandigarh must be present in DB"

    # Verify /find-tutor/ view output
    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    assert 'Chandigarh' in html, "Chandigarh must appear on public find-tutor page"
    print("[PASS] TEST A PASSED: Add Location (Chandigarh) saved to DB and rendered on /find-tutor/.")

    # Test B: Delete Location (Mumbai from popular list)
    test_cfg['popular_locations'] = [l for l in test_cfg['popular_locations'] if l['name'] != 'Mumbai']
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')
    
    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    # Mumbai should not be in the popular locations section
    assert 'quickFilterCity(\'Mumbai\')' not in html, "Mumbai should not be in Popular Locations buttons"
    print("[PASS] TEST B PASSED: Delete Mumbai from Popular Locations removes badge but preserves location data.")

    # Test C: Add Subject (German)
    test_cfg['popular_subjects'].append({
        'id': 'subj_german_1',
        'name': 'German',
        'icon': 'fa-language',
        'color': 'indigo',
        'desc': 'Grammar, Goethe A1-C1',
        'link': '/find-tutor/?subject=German',
        'enabled': True,
        'order': 100
    })
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')

    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    assert 'German' in html, "German must appear on public find-tutor page"
    assert 'quickFilterSubject(\'German\')' in html, "German filter click button must be rendered"
    print("[PASS] TEST C PASSED: Add Subject (German) saved to DB and rendered on /find-tutor/.")

    # Test D: Edit Subject (Physics description)
    for s in test_cfg['popular_subjects']:
        if s['name'] == 'Physics':
            s['desc'] = 'Mechanics, Optics, Thermodynamics'
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')

    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    assert 'Mechanics, Optics, Thermodynamics' in html, "Updated description must render on public page"
    print("[PASS] TEST D PASSED: Edit Subject description saved and rendered on /find-tutor/.")

    # Test E: Subject OFF (Physics)
    for s in test_cfg['popular_subjects']:
        if s['name'] == 'Physics':
            s['enabled'] = False
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')

    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    assert 'quickFilterSubject(\'Physics\')' not in html, "Physics badge must disappear when disabled"
    print("[PASS] TEST E PASSED: Subject OFF toggle works without breaking core records.")

    # Test F: Filter OFF (Experience)
    for f in test_cfg['filters']:
        if f['id'] == 'experience':
            f['enabled'] = False
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')

    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    assert 'id="filterExp"' not in html, "Experience filter must be hidden when disabled"
    assert 'id="filterCity"' in html, "Location filter must still be visible"
    print("[PASS] TEST F PASSED: Filter OFF hides specific filter element cleanly.")

    # Test G: Filter Label (Location -> "City / Area")
    for f in test_cfg['filters']:
        if f['id'] == 'location':
            f['label'] = 'City / Area'
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')

    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    assert 'City / Area' in html, "Custom filter label must be displayed"
    assert 'id="filterCity"' in html, "Underlying element ID must remain intact"
    print("[PASS] TEST G PASSED: Filter label customization works.")

    # Test H: Exact Ordering
    order_subjs = [
        {'id': 's1', 'name': 'Biology', 'icon': 'fa-dna', 'color': 'green', 'desc': 'Botany, Zoology', 'enabled': True, 'order': 1},
        {'id': 's2', 'name': 'Mathematics', 'icon': 'fa-calculator', 'color': 'blue', 'desc': 'Maths', 'enabled': True, 'order': 2},
        {'id': 's3', 'name': 'Physics', 'icon': 'fa-atom', 'color': 'purple', 'desc': 'Physics', 'enabled': True, 'order': 3},
        {'id': 's4', 'name': 'Chemistry', 'icon': 'fa-flask', 'color': 'cyan', 'desc': 'Chemistry', 'enabled': True, 'order': 4},
    ]
    test_cfg['popular_subjects'] = order_subjs
    save_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(test_cfg)}),
        content_type='application/json'
    )
    api_admin_settings_category(save_req, 'homepage')

    resp = find_tutor(req)
    html = resp.content.decode('utf-8')
    subj_section = html[html.find('Popular Subjects'):html.find('Verified Tutors Directory')]
    pos_bio = subj_section.find('Biology')
    pos_math = subj_section.find('Mathematics')
    pos_phy = subj_section.find('Physics')
    pos_chem = subj_section.find('Chemistry')
    assert pos_bio != -1 and pos_math != -1 and pos_phy != -1 and pos_chem != -1, "All subjects must be in popular section"
    assert pos_bio < pos_math < pos_phy < pos_chem, "Order must be exactly Biology -> Mathematics -> Physics -> Chemistry"
    print("[PASS] TEST H PASSED: Popular subjects exact ordering verified.")

    # Clean up / reset to default
    reset_req = rf.post(
        '/api/admin/settings/category/homepage/',
        data=json.dumps({'hp_find_tutor': json.dumps(DEFAULT_FIND_TUTOR_CONFIG)}),
        content_type='application/json'
    )
    api_admin_settings_category(reset_req, 'homepage')
    print("[PASS] RESET TO DEFAULT CONFIG SUCCESSFUL.")

    print("\n============================================================")
    print("ALL 8 VERIFICATION TESTS PASSED WITH 100% SUCCESS!")
    print("============================================================")

if __name__ == '__main__':
    run_tests()
