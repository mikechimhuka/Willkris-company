"""Prepare the validated static website for a GitHub Pages project URL."""
from pathlib import Path
import re
import shutil
import sys

root = Path(__file__).resolve().parent.parent
base = '/' + sys.argv[1].strip('/') if len(sys.argv) > 1 and sys.argv[1].strip('/') else ''
out = root / '_site'
if out.exists():
    shutil.rmtree(out)
shutil.copytree(root / 'dist', out, ignore=shutil.ignore_patterns('.DS_Store'))
for file in out.rglob('*'):
    if file.suffix.lower() in {'.html', '.htm'}:
        text = file.read_text()
        text = re.sub(r'((?:href|src|data-movie)=["\'])/(?!/)', lambda m: m[1] + base + '/', text)
        file.write_text(text)
    elif file.name == 'site.css':
        text = re.sub(r'(url\(["\']?)/(?!/)', lambda m: m[1] + base + '/', file.read_text())
        file.write_text(text)
    elif file.name == 'site.js':
        file.write_text(file.read_text().replace("'/assets/ruffle/ruffle.js'", repr(base + '/assets/ruffle/ruffle.js')))
(out / '.nojekyll').touch()
print(f'Prepared {out} for {base or "/"}')
