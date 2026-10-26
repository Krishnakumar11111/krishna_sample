import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
import django
django.setup()

from django.conf import settings
from django.test import Client
from django.template.loader import get_template
from TutionPlatform.models import TeacherProfile, StudentProfile, ContactEnquiry

print("=" * 60)
print("RUNNING EDUTRUST BACKEND VERIFICATION SUITE")
print("=" * 60)

# 1. Paths verification
print("\n[CHECK 1] Path configurations:")
print(f"  BASE_DIR:         {settings.BASE_DIR}")
print(f"  FRONTEND_DIR:     {settings.FRONTEND_DIR}")
print(f"  TEMPLATES DIRS:   {settings.TEMPLATES[0]['DIRS']}")
print(f"  STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
print(f"  STATIC_ROOT:      {settings.STATIC_ROOT}")
print(f"  MEDIA_ROOT:       {settings.MEDIA_ROOT}")
print(f"  DB NAME:          {settings.DATABASES['default']['NAME']}")

assert settings.FRONTEND_DIR.exists(), "FRONTEND_DIR does not exist!"
assert (settings.FRONTEND_DIR / "templates").exists(), "frontend/templates does not exist!"
assert (settings.FRONTEND_DIR / "static").exists(), "frontend/static does not exist!"
assert Path(settings.DATABASES['default']['NAME']).exists(), "db.sqlite3 does not exist!"
print("  [OK] All configured paths exist and are valid!")

# 2. Template discovery
print("\n[CHECK 2] Template discovery:")
test_templates = [
    'about.html',
    'contact.html',
    'findtutor.html',
    'edutrust_tuition_platform.html',
    'admin.html',
    'admin/contact_enquiries.html',
    'admin/settings.html',
    'components/public_header.html',
    'teacher_modules/dashboard.html',
]
for tpl_name in test_templates:
    tpl = get_template(tpl_name)
    print(f"  [OK] Loaded template: {tpl_name:<35} ({tpl.origin.name})")

# 3. Database records
print("\n[CHECK 3] Database models & records count:")
teacher_count = TeacherProfile.objects.count()
student_count = StudentProfile.objects.count()
enquiry_count = ContactEnquiry.objects.count()
print(f"  TeacherProfile: {teacher_count} records")
print(f"  StudentProfile: {student_count} records")
print(f"  ContactEnquiry: {enquiry_count} records")
assert teacher_count > 0, "TeacherProfile should have records!"
print("  [OK] Database data intact and accessible!")

# 4. HTTP Route rendering
print("\n[CHECK 4] HTTP route rendering:")
client = Client()
routes_to_test = [
    ('/', 200),
    ('/about/', 200),
    ('/contact/', 200),
    ('/find-tutor/', 200),
    ('/login/', 200),
    ('/teacher-registration/', 200),
    ('/student-registration/', 200),
    ('/admin/contact-enquiries/', 200),
    ('/admin/demo-bookings/', 200),
    ('/admin/teacher-enquiries/', 200),
    ('/admin/student-parent-enquiries/', 200),
    ('/api/admin/dashboard/stats/', 401),
]

all_passed = True
for url, expected_status in routes_to_test:
    response = client.get(url, follow=True)
    if response.status_code == expected_status:
        print(f"  [OK] {url:<35} -> HTTP {response.status_code}")
    else:
        print(f"  [FAIL] {url:<35} -> HTTP {response.status_code} (Expected {expected_status})")
        all_passed = False

assert all_passed, "Some HTTP routes failed!"

# 5. Media preservation check
print("\n[CHECK 5] Uploaded media check:")
media_root = Path(settings.MEDIA_ROOT)
media_files = list(media_root.rglob('*.*'))
print(f"  Total media files in backend/media: {len(media_files)}")
assert len(media_files) > 100, "Media files should be preserved!"
print("  [OK] Uploaded media successfully preserved!")

print("\n" + "=" * 60)
print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
print("=" * 60)
