import os
import re
from pathlib import Path

BASE_DIR = Path('.')
tpl_pattern = re.compile(r'render\s*\(\s*request\s*,\s*[\'"]([^\'"]+)[\'"]')
tpl_name_pattern = re.compile(r'template_name\s*=\s*[\'"]([^\'"]+)[\'"]')

template_refs = set()

for py_file in BASE_DIR.rglob('*.py'):
    if any(p in str(py_file) for p in ['.git', '__pycache__', 'scratch']):
        continue
    try:
        content = py_file.read_text(encoding='utf-8')
        for match in tpl_pattern.findall(content):
            template_refs.add((match, str(py_file)))
        for match in tpl_name_pattern.findall(content):
            template_refs.add((match, str(py_file)))
    except Exception:
        pass

print(f"Total template references in Python: {len(template_refs)}")
sorted_refs = sorted(template_refs, key=lambda x: x[0])
for tpl, src in sorted_refs:
    exists = (BASE_DIR / 'templates' / tpl).exists()
    status = "OK" if exists else "MISSING"
    print(f"[{status}] {tpl:<45} (referenced in {src})")
