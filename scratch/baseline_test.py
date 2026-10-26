import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
django.setup()

from django.test import Client

client = Client()
routes = [
    '/',
    '/about/',
    '/contact/',
    '/find-tutor/',
    '/login/',
    '/teacher-registration/',
    '/student-registration/',
    '/admin/contact-enquiries/',
    '/admin/demo-bookings/',
    '/admin/teacher-enquiries/',
    '/admin/student-parent-enquiries/',
    '/api/admin/dashboard/stats/',
]

for r in routes:
    resp = client.get(r, follow=True)
    print(f"{r:<35} -> HTTP {resp.status_code}")
