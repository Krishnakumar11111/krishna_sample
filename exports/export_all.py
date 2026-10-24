"""
EduTrust Data Export Script — CSV + JSON (Read-Only, No Changes)
Exports all admin panel tables to exports/csv/ and exports/json/
"""
import os, sys, json, csv, django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutrust.settings')
django.setup()

from TutionPlatform.models import (
    TeacherProfile, StudentProfile, ContactEnquiry,
    TuitionRequirement, StudyMaterial,
    ActivityLog, VisitorTracker, AdminNotification
)

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE, 'csv')
JSON_DIR = os.path.join(BASE, 'json')

EXPORTS = {
    'teachers': {
        'model': TeacherProfile,
        'fields': ['teacher_id','full_name','mobile','email','gender','qualification',
                   'experience','teaching_mode','subjects','class_range',
                   'city','locality','verification_status','approved',
                   'account_status','created_at']
    },
    'students': {
        'model': StudentProfile,
        'fields': ['student_id','full_name','mobile','email','gender','class_name',
                   'school_name','parent_name','parent_mobile','city','locality',
                   'subjects_needed','account_status','created_at']
    },
    'enquiries': {
        'model': ContactEnquiry,
        'fields': ['id','name','email','phone','subject','message','status','created_at']
    },
    'tuition_requirements': {
        'model': TuitionRequirement,
        'fields': ['id','requirement_id','student_name','mobile','class_name',
                   'subjects','tuition_type','locality','city','budget',
                   'status','created_at']
    },
    'study_materials': {
        'model': StudyMaterial,
        'fields': ['id','material_id','title','class_name','subject','chapter',
                   'unit','keywords','pdf_file','file_size','visibility',
                   'download_permission','status','featured','download_count',
                   'view_count','uploaded_by','created_at']
    },
    'activity_logs': {
        'model': ActivityLog,
        'fields': ['id','activity_type','user_name','user_role','description',
                   'page_url','ip_address','browser','device_type','created_at']
    },
    'visitor_tracker': {
        'model': VisitorTracker,
        'fields': ['id','ip_address','page_visited','browser','device_type',
                   'referrer','visit_count','first_visit','last_visit']
    },
}

total_records = 0

for name, config in EXPORTS.items():
    Model = config['model']
    fields = config['fields']
    
    # Get available fields (skip missing ones gracefully)
    available_fields = []
    for f in fields:
        try:
            Model._meta.get_field(f)
            available_fields.append(f)
        except Exception:
            pass
    
    qs = Model.objects.all()
    count = qs.count()
    total_records += count
    
    # --- CSV Export ---
    csv_path = os.path.join(CSV_DIR, f'{name}.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(available_fields)
        for obj in qs:
            row = []
            for field in available_fields:
                val = getattr(obj, field, '')
                row.append(str(val) if val is not None else '')
            writer.writerow(row)
    
    # --- JSON Export ---
    json_path = os.path.join(JSON_DIR, f'{name}.json')
    records = []
    for obj in qs:
        record = {}
        for field in available_fields:
            val = getattr(obj, field, '')
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            elif hasattr(val, 'name'):
                val = str(val)
            record[field] = str(val) if val is not None else ''
        records.append(record)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'table': name, 'count': count, 'records': records}, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {name}: {count} records -> CSV + JSON exported")

print(f"")
print(f"Total: {total_records} records exported across {len(EXPORTS)} tables")
print(f"CSV Files: exports/csv/")
print(f"JSON Files: exports/json/")
