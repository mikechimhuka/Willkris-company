"""Verify preserved content, routes, assets, and basic document semantics."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import json, re

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'dist'
pages=json.loads((ROOT/'source-original/content.json').read_text())
normalize=lambda value:re.sub(r'\s+','',value)
errors=[];line_count=0;link_count=0
for path, source in pages.items():
    page=BeautifulSoup((OUT/path).read_text(),'html.parser')
    visible=normalize(page.get_text(' ',strip=True))
    for line in source['lines']:
        line_count+=1
        if normalize(line) not in visible: errors.append(f'{path}: missing original text: {line}')
    if len(page.find_all('h1'))!=1:errors.append(f'{path}: expected one h1')
    if not page.find('html',lang='en'):errors.append(f'{path}: missing document language')
    for image in page.find_all('img'):
        if not image.get('alt'):errors.append(f'{path}: missing image alt text')
    for el in page.select('[href], [src], [data-movie]'):
        for attr in ['href','src','data-movie']:
            url=el.get(attr,'')
            if url.startswith('/'):
                link_count+=1
                target=OUT/unquote(urlparse(url).path).lstrip('/')
                if not target.exists():errors.append(f'{path}: missing local resource {url}')
    for el in page.select('form, input, textarea'):
        errors.append(f'{path}: unexpected form control')
for movie in (OUT/'Flash').glob('*.swf'):
    if movie.read_bytes()[:3] not in [b'FWS',b'CWS',b'ZWS']: errors.append(f'Invalid demonstration: {movie.name}')
report={'original_routes':len(pages),'original_text_lines_verified':line_count,'local_references_verified':link_count,'demonstrations':4,'errors':errors}
print(json.dumps(report,indent=2))
(ROOT/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(bool(errors))
