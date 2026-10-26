import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

folders_to_clean = [
    'templates',
    'static',
    'images',
    'teacher_photos',
    'edutrust',
    'TutionPlatform',
    'bookings',
    'media',
    'exports',
]

print("Cleaning up old root directories (already verified inside frontend/ and backend/)...")
for folder in folders_to_clean:
    p = ROOT / folder
    if p.exists() and p.is_dir():
        shutil.rmtree(p)
        print(f"  Removed old root folder: {folder}")

print("Clean-up finished!")
