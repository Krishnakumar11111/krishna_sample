import os
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

print("=" * 60)
print("EDUTRUST PROJECT IN-DEPTH ANALYSIS")
print("=" * 60)

# 1. Root structure
print("\n[1] ROOT DIRECTORY ITEMS:")
for item in sorted(BASE_DIR.iterdir()):
    if item.name.startswith('.'):
        continue
    if item.is_dir():
        file_count = sum(1 for _ in item.rglob('*') if _.is_file())
        print(f"  [DIR]  {item.name:<25} ({file_count} files)")
    else:
        print(f"  [FILE] {item.name:<25} ({item.stat().st_size} bytes)")

# 2. Database verification
print("\n[2] DATABASE ANALYSIS:")
db_path = BASE_DIR / 'db.sqlite3'
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print(f"  SQLite DB exists, size: {db_path.stat().st_size} bytes")
    print(f"  Total tables: {len(tables)}")
    app_tables = [t for t in tables if not t.startswith('django_') and not t.startswith('auth_') and not t.startswith('sqlite_')]
    print(f"  Application tables ({len(app_tables)}):")
    for t in sorted(app_tables):
        cur.execute(f"SELECT count(*) FROM {t};")
        count = cur.fetchone()[0]
        print(f"    - {t:<35} ({count} rows)")
    conn.close()
else:
    print("  db.sqlite3 not found!")

# 3. Media analysis
print("\n[3] MEDIA DIRECTORY ANALYSIS:")
media_dir = BASE_DIR / 'media'
if media_dir.exists():
    for sub in sorted(media_dir.iterdir()):
        if sub.is_dir():
            count = sum(1 for _ in sub.rglob('*') if _.is_file())
            print(f"  media/{sub.name:<25} ({count} files)")
        else:
            print(f"  media/{sub.name} (file)")

# Check root teacher_photos vs media/teacher_photos
root_tp = BASE_DIR / 'teacher_photos'
media_tp = media_dir / 'teacher_photos'
if root_tp.exists():
    print(f"  root teacher_photos: {list(root_tp.iterdir())}")
    print(f"  media/teacher_photos: {list(media_tp.iterdir()) if media_tp.exists() else 'none'}")

# Check root images
root_img = BASE_DIR / 'images'
if root_img.exists():
    print(f"  root images: {list(root_img.iterdir())}")

# 4. Templates analysis
print("\n[4] TEMPLATES DIRECTORY ANALYSIS:")
tpl_dir = BASE_DIR / 'templates'
if tpl_dir.exists():
    subdirs = {}
    root_tpls = []
    for f in sorted(tpl_dir.rglob('*.html')):
        rel = f.relative_to(tpl_dir)
        parts = rel.parts
        if len(parts) == 1:
            root_tpls.append(parts[0])
        else:
            parent_dir = str(rel.parent)
            subdirs.setdefault(parent_dir, []).append(parts[-1])
    print(f"  Root templates ({len(root_tpls)}): {', '.join(root_tpls[:10])}...")
    for sdir, files in sorted(subdirs.items()):
        print(f"  templates/{sdir:<25} ({len(files)} templates)")

# 5. Static directory analysis
print("\n[5] STATIC ASSETS ANALYSIS:")
static_dir = BASE_DIR / 'static'
if static_dir.exists():
    for sub in sorted(static_dir.iterdir()):
        if sub.is_dir():
            count = sum(1 for _ in sub.rglob('*') if _.is_file())
            print(f"  static/{sub.name:<20} ({count} files)")
            for sf in sub.glob('*'):
                if sf.is_file():
                    print(f"    - {sf.name}")
        else:
            print(f"  static/{sub.name} (file)")

# 6. Django apps
print("\n[6] DJANGO APPS ANALYSIS:")
for app_name in ['TutionPlatform', 'bookings', 'edutrust']:
    app_p = BASE_DIR / app_name
    if app_p.exists():
        py_files = [f.name for f in app_p.glob('*.py')]
        mig_dir = app_p / 'migrations'
        mig_files = [f.name for f in mig_dir.glob('*.py') if f.name != '__init__.py'] if mig_dir.exists() else []
        print(f"  App: {app_name}")
        print(f"    Py files: {', '.join(py_files)}")
        print(f"    Migrations ({len(mig_files)}): {', '.join(mig_files)}")

print("\nAnalysis completed.")
