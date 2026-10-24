import re
from pathlib import Path

BASE_DIR = Path('.')
tpl_dir = BASE_DIR / 'templates'

extends_pattern = re.compile(r'{%\s*extends\s*[\'"]([^\'"]+)[\'"]\s*%}')
include_pattern = re.compile(r'{%\s*include\s*[\'"]([^\'"]+)[\'"]\s*%}')

all_extends = set()
all_includes = set()
issues = []

for html_file in tpl_dir.rglob('*.html'):
    try:
        content = html_file.read_text(encoding='utf-8')
        for match in extends_pattern.findall(content):
            all_extends.add(match)
            target = tpl_dir / match
            if not target.exists():
                issues.append(f"MISSING EXTENDS: {html_file.relative_to(tpl_dir)} extends {match}")
        for match in include_pattern.findall(content):
            all_includes.add(match)
            target = tpl_dir / match
            if not target.exists():
                issues.append(f"MISSING INCLUDE: {html_file.relative_to(tpl_dir)} includes {match}")
    except Exception as e:
        issues.append(f"Error reading {html_file}: {e}")

print(f"Total unique extends: {len(all_extends)}")
for ext in sorted(all_extends):
    print(f"  extends: {ext}")

print(f"\nTotal unique includes: {len(all_includes)}")
for inc in sorted(all_includes):
    print(f"  include: {inc}")

if issues:
    print(f"\nIssues found ({len(issues)}):")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\nAll extends and includes resolve perfectly within templates/!")
