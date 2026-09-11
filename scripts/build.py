"""Build a dependency-free static redesign from archived Wilkris content.
Run with Python and beautifulsoup4. Original wording is extracted, not rewritten.
"""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, urlparse, unquote, quote
from html import escape as E
import re, json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist'
ORIGINAL = ROOT / 'source-original'
NAV = [('main.htm','Home'),('product.htm','Products'),('freq.htm','Frequently Asked Questions'),('fluid_filling.htm','Fluid Filling'),('contact.htm','Contact Wilkris')]
PAGES = {}

def norm(t): return re.sub(r'\s+', ' ', t).strip()
def local(url, path):
    u = urlparse(urljoin('http://www.wilkris.com/'+path,url))
    if u.hostname == 'www.wilkris.com': return quote(unquote(u.path),safe='/') + ('#'+u.fragment if u.fragment else '')
    return url

for file in sorted(ORIGINAL.rglob('*.htm')):
    path = file.relative_to(ORIGINAL).as_posix()
    soup = BeautifulSoup(file.read_text(encoding='latin1'), 'html.parser')
    cells = soup.find_all('td',colspan='5')
    cell = max(cells,key=lambda t:len(t.get_text()))
    for table in list(cell.find_all('table')):
        labels = [norm(a.get_text()) for a in table.find_all('a')]
        if 'Home' in labels and 'Frequently Asked Questions' in labels: table.decompose()
    images = [{'src':local(i['src'],path),'width':i.get('width'),'height':i.get('height')} for i in cell.find_all('img') if i.get('src')]
    links = [{'href':local(a['href'],path),'text':norm(a.get_text())} for a in cell.find_all('a') if a.get('href') and norm(a.get_text()) and norm(a.get_text()) not in dict(NAV).values()]
    movies = [local(i['src'],path) for i in cell.find_all('embed') if i.get('src')]
    for t in cell.find_all(['object','script','style']): t.decompose()
    for t in cell.find_all('br'): t.replace_with('\n')
    for t in cell.find_all(['p','div','h1','h2','h3','td','li']):
        t.insert_before('\n'); t.insert_after('\n')
    lines=[norm(x) for x in cell.get_text().split('\n') if norm(x)]
    # Breadcrumbs can share a paragraph with body copy; discard only the breadcrumb line.
    lines=[x for x in lines if not (x.startswith('Home') and '>' in x)]
    modified=[x for x in lines if x.startswith('Page last modified')]
    lines=[x for x in lines if not x.startswith('Page last modified')]
    PAGES[path]={'lines':lines,'images':images,'links':links,'movies':movies,'modified':modified}

(ORIGINAL/'content.json').write_text(json.dumps(PAGES,indent=2,ensure_ascii=False))

def text_html(text, page=None):
    value=E(text)
    if page:
        for link in sorted(page['links'],key=lambda l:len(l['text']),reverse=True):
            label=E(link['text'])
            if label and label in value and '<a ' not in value:
                value=value.replace(label,f'<a href="{E(link["href"])}">{label}</a>',1)
    value=re.sub(r'(?<![\w:])513\.271\.9344', '<a href="tel:+15132719344">513.271.9344</a>',value)
    return value

def nav(active, footer=False):
    return ''.join(f'<a href="/{p}"'+(' aria-current="page"' if p==active else '')+(' class="nav-contact"' if p=='contact.htm' and not footer else '')+f'>{n}</a>' for p,n in NAV)

def shell(title, body, path, section=None):
    active=section or (path if path in dict(NAV) else ('product.htm' if path.startswith('product/') else 'freq.htm' if path.startswith('freq/') else 'fluid_filling.htm' if path.startswith('fluid_filling/') else 'product.htm'))
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} | Wilkris Company</title><meta name="description" content="Wilkris Company, producer of extremely accurate and dependable level sensing and fluid filling technology">
<meta name="theme-color" content="#112a38"><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner"><a class="wordmark" href="/main.htm" aria-label="Wilkris Company home"><img src="/assets/wilkris-logo.png" alt="Wilkris Company"></a><button class="menu-button" aria-expanded="false" aria-controls="primary-nav">Menu <span aria-hidden="true">☰</span></button><nav id="primary-nav" aria-label="Main navigation">{nav(active)}</nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="wrap footer-grid"><div><a class="wordmark" href="/main.htm"><img src="/assets/wilkris-logo.png" alt="Wilkris Company"></a><p>Producers of the Digistick<br>Fluid Leveling Gauge</p></div><nav aria-label="Footer navigation">{nav(active,True)}</nav><div><span class="eyebrow">Contact Information</span><p><a href="tel:+15132719344">513.271.9344</a><br><a href="mailto:info@wilkris.com">info@wilkris.com</a></p><p>P.O. Box 230<br>Terrace Park, OH 45174</p></div></div><div class="wrap footer-bottom"><span>© Wilkris Company, Inc.</span><span>Page last modified September 10, 2026</span><a href="#main">Back to top ↑</a></div></footer></body></html>'''

def page_head(title, kicker, intro='', parent=None):
    crumb='<a href="/main.htm">Home</a>'+(f'<span>/</span><a href="/{parent[0]}">{E(parent[1])}</a>' if parent else '')
    return f'<section class="page-head"><div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb">{crumb}</nav><span class="eyebrow">{E(kicker)}</span><h1>{E(title)}</h1>{f"<p class=lead>{intro}</p>" if intro else ""}</div></section>'

def contact_block():
    return '''<div class="contact-grid"><section><h3>Telephone</h3><a class="contact-value" href="tel:+15132719344">513.271.9344</a><h3>Fax</h3><p>513.271.5995</p></section><section><h3>Postal Address</h3><p>P.O. Box 230<br>Terrace Park, OH 45174</p></section><section><h3>Electronic Mail</h3><dl><dt>General Information:</dt><dd><a href="mailto:info@wilkris.com">info@wilkris.com</a></dd><dt>Sales:</dt><dd><a href="mailto:sales@wilkris.com">sales@wilkris.com</a></dd><dt>Customer Support:</dt><dd><a href="mailto:support@wilkris.com">support@wilkris.com</a></dd></dl></section></div>'''

def demos(include_digistick=True):
    items=[('product/digistick_flash_demo.htm','Digistick Flash Demonstration'),('transmission_demo.htm','Transmission Demonstration'),('engine_demo.htm','Engine Demonstration'),('fueltank_demo.htm','Fuel Tank Demonstration')]
    if not include_digistick: items=items[1:]
    return '<div class="demo-links">'+''.join(f'<a href="/{p}"><span class="play-icon" aria-hidden="true">▷</span><span>{name}</span><span aria-hidden="true">↗</span></a>' for p,name in items)+'</div>'

home=PAGES['main.htm']['lines']
home_body=f'''<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><p class="eyebrow">{E(home[0])}</p><h1>Digistick, the standard in digital fluid level measurement.</h1><p class="hero-sub">{E(home[1])}</p><p class="hero-description">{E(home[3])}</p><div class="actions"><a class="button" href="/product.htm">View Products <span aria-hidden="true">↗</span></a><a class="text-link" href="/contact.htm">Contact Wilkris <span aria-hidden="true">→</span></a></div></div><figure class="hero-product"><div class="figure-top"><span>DIGISTICK</span><span>01 / FLUID LEVEL</span></div><div class="product-photo"><img src="/images/Products/digistick/digistick_small.jpg" width="342" height="223" alt="Original Wilkris Digistick portable gauge in its black carrying case" fetchpriority="high"></div><figcaption><div><span class="eyebrow">{E(home[1])}</span><a href="/product/digistick.htm">Digistick <span aria-hidden="true">↗</span></a></div><strong>±1<span>mm</span></strong></figcaption></figure></div><div class="wrap hero-rule"><span>WILKRIS COMPANY, INC.</span><span>PRECISION FLUID LEVEL MEASUREMENT</span></div></section>
<section class="section"><div class="wrap editorial"><div><span class="eyebrow">Digistick</span><h2>We are the standard in precision fluid level measurement.</h2></div><div class="body-copy"><p>{E(home[4])}</p><a class="text-link dark-link" href="/product/digistick.htm">View Digistick <span aria-hidden="true">→</span></a></div></div></section>
<section class="section company-section"><div class="wrap company-grid"><div><span class="eyebrow">Wilkris Company</span><h2>{E(home[5])}</h2><p>{E(home[6])}</p></div><aside class="mission"><span class="section-number" aria-hidden="true">W /</span><h2>Mission Statement</h2><p>{E(home[8])}</p></aside></div></section>
<section class="section"><div class="wrap"><div class="section-heading"><span class="eyebrow">Digistick</span><h2>Demonstrations</h2></div>{demos(False)}</div></section>
<section class="section contact-section"><div class="wrap"><div class="editorial contact-intro"><h2>Contact Information</h2><p>{text_html(home[10],PAGES['main.htm'])}</p></div>{contact_block()}</div></section>'''

def write(path,title,body,section=None):
    dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(shell(title,body,path,section))

write('main.htm','Home',home_body)
(OUT/'index.html').write_text(shell('Home',home_body,'main.htm'))

# Catalog cards retain the original product descriptions and link destinations.
catalog=PAGES['product.htm']; lines=catalog['lines']
products=[]
for l in catalog['links']:
    if l['href'].startswith('/product/') and 'demo' not in l['href']:
        idx=lines.index(l['text']); products.append((l['href'],l['text'],lines[idx+1]))
cards=[]
for i,(href,title,desc) in enumerate(products):
    detail=PAGES[href.lstrip('/')];src=detail['images'][0]['src']
    cards.append(f'<article class="product-card"><a href="{href}" class="card-image" aria-label="View {E(title)}"><span class="card-number">0{i+1}</span><img src="{src}" alt="{E(title)}" loading="lazy"></a><div class="card-copy"><h2><a href="{href}">{E(title)} <span aria-hidden="true">↗</span></a></h2><p>{E(desc)}</p></div></article>')
write('product.htm','Products',page_head(lines[0],'Wilkris Company',E(lines[1]))+'<section class="section"><div class="wrap product-grid">'+''.join(cards)+'</div></section><section class="section soft-section"><div class="wrap"><h2>Demonstrations</h2><p>'+E(lines[2])+'</p>'+demos()+'</div></section>')

for path,title,kicker in [('freq.htm','Frequently Asked Questions','Questions & answers'),('fluid_filling.htm','Fluid Filling Best Practices','Fluid Filling')]:
    p=PAGES[path];intro=[x for x in p['lines'] if x not in [a['text'] for a in p['links']] and x!=title]
    lead=' '.join(E(x) for x in intro)
    links=''.join(f'<a class="resource-link" href="{l["href"]}"><span class="resource-number">0{i+1}</span><h2>{E(l["text"])}</h2><span class="resource-arrow" aria-hidden="true">↗</span></a>' for i,l in enumerate(p['links']))
    write(path,title,page_head(title,kicker,lead)+'<section class="section"><div class="wrap resource-list">'+links+'</div></section>')

contact=PAGES['contact.htm'];ct=next(x for x in contact['lines'] if x.startswith('Please take'))
write('contact.htm','Contact Wilkris',page_head('Contact Information','Contact Wilkris',text_html(ct,contact))+'<section class="section"><div class="wrap">'+contact_block()+'</div></section>')

HEADINGS=set(['Key Benefits','Key Benefits:','Specifications','Temperature Fixture Specifications','Level Fixture Specifications','Items Included With Gauge','Items Included with Gauge','Options','Applications','Please Note','Capabilities:','What is the Digistick®?','Creating Custom Fluid Level Expansion Curves',"Digistick's® Uses",'Custom Probe Design','Screen Shots From the Digistick®','State of the Art Features :','Outline','I. Common Fluid Filling Methods','II. The Wilkris Method','III. Summary','1. The Vacuum Straw/Stand Pipe method','2. The Weight Method','3. The Volumetric Method','4. The Wire Tie Method','4. The Dipstick Method','Products','Services'])

def article_lines(lines,page):
    out=[];spec=False;table=False
    for line in lines:
        if line in HEADINGS:
            if table:out.append('</tbody></table></div>');table=False
            spec='Specifications' in line
            ident='section-'+str(len(out))
            out.append(f'<h2 id="{ident}">{E(line)}</h2>')
        elif spec and ':' in line and len(line.split(':',1)[0])<55:
            if not table:out.append('<div class="spec-table"><table><caption class="sr-only">Product specifications</caption><tbody>');table=True
            k,v=line.split(':',1);out.append(f'<tr><th scope="row">{E(k)}:</th><td>{E(v.strip())}</td></tr>')
        else:
            if table and spec:
                # A wrapped value belongs to the preceding specification row.
                out[-1]=out[-1].replace('</td></tr>',f'<br>{E(line)}</td></tr>')
                continue
            if table:out.append('</tbody></table></div>');table=False
            cls=' class="numbered-line"' if re.match(r'^(\d+\.?|[A-E]\.)\s',line) else ''
            out.append(f'<p{cls}>{text_html(line,page)}</p>')
    if table:out.append('</tbody></table></div>')
    return ''.join(out)

for path,p in PAGES.items():
    if path in dict(NAV):continue
    lines=p['lines'].copy(); title=lines.pop(0)
    if p['movies']:
        movie=p['movies'][0]
        # Keep legacy Flash instructions as clearly identified original notes.
        notes=''.join(f'<p>{E(x)}</p>' for x in lines)
        body=page_head(title,'Demonstrations',parent=('product.htm','Products'))+f'''<section class="section"><div class="wrap demo-layout"><div class="demo-player" data-movie="{movie}" aria-label="{E(title)}"><button class="button play-demo">Play demonstration <span aria-hidden="true">▷</span></button><p class="player-status" role="status">Select Play to load the original demonstration.</p></div><div class="demo-caption"><a href="{movie}" download>Download original demonstration (.swf)</a><a href="/product.htm">All products →</a></div>{f'<details class="legacy-note"><summary>Original playback instructions</summary>{notes}</details>' if notes else ''}</div></section>'''
        write(path,title,body,'product.htm');continue
    if path.startswith('freq/'):
        prefix=[];groups=[];current=None
        for line in lines:
            if line.endswith('?'):
                if current:groups.append(current)
                current=[line,[]]
            elif current:current[1].append(line)
            else:prefix.append(line)
        if current:groups.append(current)
        content=article_lines(prefix,p)+''.join(f'<details class="faq-item" open><summary>{E(q)}</summary><div class="answer">{article_lines(a,p)}</div></details>' for q,a in groups)
        body=page_head(title,'Frequently Asked Questions',parent=('freq.htm','Frequently Asked Questions'))+f'<section class="section"><div class="wrap reading-layout"><aside class="side-nav"><span class="eyebrow">Categories</span>'+''.join(f'<a href="{l["href"]}"'+(' aria-current="page"' if l['href']=='/'+path else '')+f'>{E(l["text"])}</a>' for l in PAGES['freq.htm']['links'])+f'</aside><article class="article">{content}</article></div></section>'
        write(path,title,body);continue
    gallery=''
    if p['images']:
        figures=[]
        for i,img in enumerate(p['images']):
            src=img['src'];alts={'MainScreen':'Digistick main view','recordlist':'Digistick record list','Models':'Digistick models view','TempTable':'Digistick custom set point entry'}
            alt=next((v for k,v in alts.items() if k in src),title + (' — product detail '+str(i+1) if i else ''))
            full=src.replace('_small.gif','.bmp') if any(k in src for k in alts) else src
            figures.append(f'<figure><a href="{full}" aria-label="Enlarge {E(alt)}"><img src="{src}" loading="lazy" alt="{E(alt)}"></a></figure>')
        gallery='<aside class="product-gallery"><span class="eyebrow">Wilkris Company</span>'+''.join(figures)+'</aside>'
    content=article_lines(lines,p)
    parent=('product.htm','Products') if path.startswith('product/') else ('fluid_filling.htm','Fluid Filling')
    kicker=parent[1]
    if path.startswith('fluid_filling/'):
        links=''.join(f'<a href="{l["href"]}"'+(' aria-current="page"' if l['href']=='/'+path else '')+f'>{E(l["text"])}</a>' for l in PAGES['fluid_filling.htm']['links'])
        gallery=f'<aside class="side-nav"><span class="eyebrow">Fluid Filling</span>{links}</aside>'
    original_note='<span>Page last modified September 10, 2026</span>'
    body=page_head(title,kicker,parent=parent)+f'<section class="section"><div class="wrap reading-layout">{gallery}<article class="article">{content}<div class="original-date"><span>Original content</span>{original_note}</div></article></div></section>'
    write(path,title,body)

# Preserve convenient routes from the earlier design as static aliases.
for alias,source in {'products':'product.htm','frequently-asked-questions':'freq.htm','fluid-filling':'fluid_filling.htm','contact':'contact.htm'}.items():
    (OUT/alias).mkdir(exist_ok=True);(OUT/alias/'index.html').write_text((OUT/source).read_text())
write('404.html','Page not found',page_head('Page not found','Wilkris Company')+'<section class="section"><div class="wrap"><p>This page could not be found.</p><a class="button" href="/main.htm">Return home</a></div></section>')
print(f'Built {len(PAGES)} original routes, homepage, aliases, and 404 page.')
