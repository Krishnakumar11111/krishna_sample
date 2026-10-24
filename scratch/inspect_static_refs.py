import re
from pathlib import Path

BASE_DIR = Path('.')
tpl_dir = BASE_DIR / 'templates'
static_dir = BASE_DIR / 'static'

static_tag_pattern = re.compile(r'{%\s*static\s*[\'"]([^\'"]+)[\'"]\s*%}')

static_refs = set()
missing_refs = []

for html_file in tpl_dir.rglob('*.html'):
    try:
        content = html_file.read_text(encoding='utf-8')
        for match in static_tag_pattern.findall(content):
            static_refs.add((match, str(html_file.relative_to(tpl_dir))))
    except Exception:
        pass

print(f"Total static references in templates: {len(static_refs)}")
unique_paths = sorted(set(r[0] for r in static_refs))
for p in unique_paths:
    exists = (static_dir / p).exists()
    status = "EXISTS" if exists else "NOT FOUND"
    print(f"[{status}] {p}")
