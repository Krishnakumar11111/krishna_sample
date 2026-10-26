import os
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_DIR = ROOT_DIR / "backend"

print("=" * 60)
print("STARTING EDUTRUST REORGANIZATION")
print(f"Root:     {ROOT_DIR}")
print(f"Frontend: {FRONTEND_DIR}")
print(f"Backend:  {BACKEND_DIR}")
print("=" * 60)

# Create frontend and backend directories
FRONTEND_DIR.mkdir(exist_ok=True)
BACKEND_DIR.mkdir(exist_ok=True)

# 1. SETUP FRONTEND
print("\n[STEP 1] Setting up frontend/ ...")

# 1a. Templates -> frontend/templates
src_templates = ROOT_DIR / "templates"
dst_templates = FRONTEND_DIR / "templates"
if src_templates.exists():
    if dst_templates.exists():
        shutil.rmtree(dst_templates)
    shutil.copytree(src_templates, dst_templates)
    print(f"  [OK] Copied templates/ -> frontend/templates/ ({len(list(dst_templates.rglob('*.html')))} HTML files)")

# 1b. Static -> frontend/static
src_static = ROOT_DIR / "static"
dst_static = FRONTEND_DIR / "static"
if src_static.exists():
    if dst_static.exists():
        shutil.rmtree(dst_static)
    shutil.copytree(src_static, dst_static)
    print(f"  [OK] Copied static/ -> frontend/static/ ({len(list(dst_static.rglob('*')))} files)")

# Ensure standard static subfolders exist
for folder in ["css", "js", "images", "fonts", "vendor"]:
    (dst_static / folder).mkdir(exist_ok=True)

# Copy root images/student.png to frontend/static/images/
root_student_img = ROOT_DIR / "images" / "student.png"
if root_student_img.exists():
    shutil.copy2(root_student_img, dst_static / "images" / "student.png")
    print("  [OK] Copied root images/student.png -> frontend/static/images/student.png")

# 2. SETUP BACKEND
print("\n[STEP 2] Setting up backend/ ...")

# 2a. Django Project package: edutrust -> backend/edutrust
src_edutrust = ROOT_DIR / "edutrust"
dst_edutrust = BACKEND_DIR / "edutrust"
if src_edutrust.exists():
    if dst_edutrust.exists():
        shutil.rmtree(dst_edutrust)
    shutil.copytree(src_edutrust, dst_edutrust)
    print("  [OK] Copied edutrust/ -> backend/edutrust/")

# 2b. Django App: TutionPlatform -> backend/TutionPlatform
src_tution = ROOT_DIR / "TutionPlatform"
dst_tution = BACKEND_DIR / "TutionPlatform"
if src_tution.exists():
    if dst_tution.exists():
        shutil.rmtree(dst_tution)
    shutil.copytree(src_tution, dst_tution)
    print("  [OK] Copied TutionPlatform/ -> backend/TutionPlatform/")

# 2c. Django App: bookings -> backend/bookings
src_bookings = ROOT_DIR / "bookings"
dst_bookings = BACKEND_DIR / "bookings"
if src_bookings.exists():
    if dst_bookings.exists():
        shutil.rmtree(dst_bookings)
    shutil.copytree(src_bookings, dst_bookings)
    print("  [OK] Copied bookings/ -> backend/bookings/")

# 2d. Media directory: media -> backend/media
src_media = ROOT_DIR / "media"
dst_media = BACKEND_DIR / "media"
if src_media.exists():
    if dst_media.exists():
        shutil.rmtree(dst_media)
    shutil.copytree(src_media, dst_media)
    print(f"  [OK] Copied media/ -> backend/media/ ({len(list(dst_media.rglob('*')))} files)")

# Merge root teacher_photos into backend/media/teacher_photos
root_tp = ROOT_DIR / "teacher_photos"
dst_media_tp = dst_media / "teacher_photos"
dst_media_tp.mkdir(parents=True, exist_ok=True)
if root_tp.exists():
    merged_count = 0
    for f in root_tp.iterdir():
        if f.is_file():
            target_f = dst_media_tp / f.name
            if not target_f.exists():
                shutil.copy2(f, target_f)
                merged_count += 1
    print(f"  [OK] Merged root teacher_photos -> backend/media/teacher_photos/ ({merged_count} new files)")

# 2e. Exports directory: exports -> backend/exports
src_exports = ROOT_DIR / "exports"
dst_exports = BACKEND_DIR / "exports"
if src_exports.exists():
    if dst_exports.exists():
        shutil.rmtree(dst_exports)
    shutil.copytree(src_exports, dst_exports)
    print("  [OK] Copied exports/ -> backend/exports/")

# 2f. Database: db.sqlite3 -> backend/db.sqlite3
src_db = ROOT_DIR / "db.sqlite3"
dst_db = BACKEND_DIR / "db.sqlite3"
if src_db.exists():
    shutil.copy2(src_db, dst_db)
    print(f"  [OK] Copied db.sqlite3 -> backend/db.sqlite3 ({dst_db.stat().st_size} bytes)")

# 2g. Database backup folder: backend/database/
dst_database_dir = BACKEND_DIR / "database"
dst_database_dir.mkdir(exist_ok=True)
backup_file = ROOT_DIR / "db.sqlite3.backup"
if backup_file.exists():
    shutil.copy2(backup_file, dst_database_dir / "db.sqlite3.backup")
    print("  [OK] Saved backup -> backend/database/db.sqlite3.backup")

# 2h. manage.py -> backend/manage.py
src_manage = ROOT_DIR / "manage.py"
dst_manage = BACKEND_DIR / "manage.py"
if src_manage.exists():
    shutil.copy2(src_manage, dst_manage)
    print("  [OK] Copied manage.py -> backend/manage.py")

# 2i. Staticfiles directory placeholder: backend/staticfiles/
(BACKEND_DIR / "staticfiles").mkdir(exist_ok=True)
print("  [OK] Created backend/staticfiles/")

print("\nReorganization copy phase completed successfully!")
