from pathlib import Path
root_tp = Path('teacher_photos')
media_tp = Path('media/teacher_photos')
if root_tp.exists():
    for f in root_tp.iterdir():
        mf = media_tp / f.name
        print(f"File {f.name}: in media/teacher_photos? {mf.exists()}")
