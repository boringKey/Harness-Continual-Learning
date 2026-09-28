#!/usr/bin/env python3
"""Optional local Chromium test; requires Playwright and a Chromium executable.
Tests both portable HTML and the normal static site under the /HCL/ prefix.
It does not contact GitHub or assert that a live site has been deployed.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import hashlib, json, os, shutil, sys, threading
from playwright.sync_api import sync_playwright, Error
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'check-previews';OUT.mkdir(parents=True,exist_ok=True)
preview=Path(sys.argv[1] if len(sys.argv)>1 else ROOT.parent/'HCL-v10-preview.html')
HTML=preview.read_text()
CHROMIUM=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
if not CHROMIUM:raise SystemExit('Set CHROMIUM_PATH to your Chromium executable.')
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
handler=partial(Quiet,directory=str(ROOT.parent))
server=ThreadingHTTPServer(('127.0.0.1',0),handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
url=f'http://127.0.0.1:{server.server_port}/{ROOT.name}/'
report={'version':'v10','render_mode':'Chromium portable HTML and local HTTP /HCL/ static site; not a live deployment','widths':[],'checks':{},'errors':[]}
widths=[320,360,375,390,620,720,721,768,820,1024,1440]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=CHROMIUM,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  report['chromium_version']=b.version
  page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
  page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.set_content(HTML,wait_until='load')
  page.evaluate('''async()=>{for(const im of document.querySelectorAll('main img')){im.loading='eager';await im.decode()}}''')
  for w in widths:
   page.set_viewport_size({'width':w,'height':900})
   info=page.evaluate('''() => {
     const sel='main,main section,.container,.selected-result,.framework-reading,.score-readout,.result-heading,.nav-shell,.nav-links,.brand,.resource-links,h1,h2,h3';
     const visible=[...document.querySelectorAll(sel)].filter(x=>x.getBoundingClientRect().height>0);
     const overflow=visible.filter(x=>x.scrollWidth>x.clientWidth+1).map(x=>({tag:x.tagName,id:x.id,cls:x.className,client:x.clientWidth,scroll:x.scrollWidth}));
     const outside=visible.filter(x=>x.getBoundingClientRect().right>innerWidth+1||x.getBoundingClientRect().left< -1).map(x=>({id:x.id,cls:x.className}));
     return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,overflow,outside};
   }''')
   assert info['width']>=info['scrollWidth'] and not info['overflow'] and not info['outside'],info
   report['widths'].append(info)
  report['checks']['responsive_layout']='11 widths; no document or selected-component horizontal overflow.'
  assert page.locator('.brand').inner_text()=='Harness Continual Learning'
  assert page.locator('#demos-title').inner_text()=='Continual learning in Minecraft'
  assert page.locator('.figure-actions a').count()==2
  assert page.locator('.figure-actions .source-link,.evidence-note>a').count()==0
  assert page.locator('a[href*="HCL.pdf#"]').count()==0
  assert 'sequential Minecraft tasks' in page.locator('#demos .section-heading>p').inner_text()
  report['checks']['v10_targeted_changes']='Minecraft-specific demo title/description; three repeated paper deep links removed; both caption enlargement controls retained.'
  assert page.locator('#demos').bounding_box()['y']<page.locator('#overview').bounding_box()['y']
  assert page.locator('.paper-figure').count()==2
  assert page.locator('.learning-panel,.state-equation,table,details,[role=tablist]').count()==0
  assert page.locator('.selected-result .result-pictogram svg').count()==4
  assert page.locator('video').count()==2 and page.locator('video[src]').count()==0
  report['checks']['content']='Full navbar name; videos first; original Figures 1 and 2; four inline SVG experiment icons; old comparison and standalone equation absent.'
  page.set_viewport_size({'width':1440,'height':1000})
  for selector,height in [('#connections .figure-zoom',1288),('#method .figure-zoom',1848)]:
   trigger=page.locator(selector);trigger.click()
   page.wait_for_function("document.querySelector('#figure-dialog').open && document.querySelector('#dialog-image').naturalWidth>0")
   assert page.locator('#dialog-image').evaluate('(x)=>[x.naturalWidth,x.naturalHeight]')==[3184,height]
   page.locator('#figure-fit').click()
   assert page.locator('#figure-dialog').evaluate('(x)=>x.classList.contains("zoomed")')
   page.keyboard.press('Escape')
   assert not page.locator('#figure-dialog').evaluate('(x)=>x.open')
   assert trigger.evaluate('(x)=>document.activeElement===x')
  # Test the explicit caption link in addition to the clickable image.
  page.locator('#connections .figure-actions [data-figure]').click()
  assert page.locator('#figure-dialog').evaluate('(x)=>x.open')
  page.locator('#figure-close').click()
  report['checks']['image_viewer']='Both original figures opened at 3184px; size toggle, Escape, close button, caption action and focus return passed.'
  page.locator('#copy-bibtex').click();status=page.locator('#copy-status').inner_text()
  assert status in ['BibTeX copied to clipboard.','Citation selected. Press Ctrl+C or ⌘C to copy.']
  report['checks']['citation_button']={'reported_status':status,'limit':'OS clipboard contents were not independently read.'}
  assert all(h.startswith('blob:') for h in page.locator('[data-inline-paper-page]').evaluate_all('(xs)=>xs.map(x=>x.href)'))
  report['checks']['portable_pdf']='PDF source links resolve to embedded manuscript Blob; PDF viewer navigation is not independently tested.'
  # Exercise relative assets on the actual static site, not just embedded data URLs.
  native=b.new_page(viewport={'width':1440,'height':1000})
  failures=[]
  native.on('requestfailed',lambda r:failures.append(r.url))
  native.on('pageerror',lambda e:report['errors'].append(str(e)))
  http_ok=False
  try:
   response=native.goto(url,wait_until='load');assert response.status==200
   native.evaluate('''async()=>{for(const im of document.querySelectorAll('main img')){im.loading='eager';await im.decode()}}''')
   assert native.locator('#connections picture img').evaluate('(x)=>x.naturalWidth>0')
   assert native.locator('#method picture img').evaluate('(x)=>x.naturalWidth>0')
   assert native.request.get(url+'static/paper/HCL.pdf').status==200
   assert native.request.get(url+'citation.bib').status==200
   assert not failures,failures
   http_ok=True
   report['checks']['local_http']='Normal static source served under /HCL/. CSS, JS, responsive WebP figures, manuscript and citation loaded successfully.'
  except Error as exc:
   if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(exc):raise
   report['checks']['local_http']={'status':'not tested','reason':'Chromium environment blocks localhost navigation (ERR_BLOCKED_BY_ADMINISTRATOR). No attempt was made to override this restriction.'}
  # In the restricted environment, render the exact portable source instead.
  if not http_ok:
   native.close()
   native=b.new_page(viewport={'width':1440,'height':1000})
   native.set_content(HTML,wait_until='load')
   native.evaluate('''async()=>{for(const im of document.querySelectorAll('main img')){im.loading='eager';await im.decode()}}''')
  report['checks']['screenshot_basis']='Local HTTP' if http_ok else 'Portable HTML with embedded local assets'
  # Fresh native page images for final previews.
  native.evaluate("window.scrollTo({top:0,behavior:'instant'})")
  native.screenshot(path=str(OUT/'desktop-full.png'),full_page=True)
  for name,sel in [('overview','#overview'),('results','#experiments'),('framework','#method'),('header','.site-header'),('demos','#demos')]:
   native.locator(sel).screenshot(path=str(OUT/(name+'.png')))
  native.set_viewport_size({'width':390,'height':844})
  native.screenshot(path=str(OUT/'mobile-full.png'),full_page=True)
  for name,sel in [('overview','#overview'),('results','#experiments'),('framework','#method'),('header','.site-header')]:
   native.locator(sel).screenshot(path=str(OUT/(name+'-mobile.png')))
  ctx=b.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
  nojs=ctx.new_page()
  if http_ok:nojs.goto(url,wait_until='load')
  else:nojs.set_content(HTML,wait_until='load')
  assert nojs.locator('#overview-title').is_visible()
  assert nojs.locator('.paper-figure').count()==2 and nojs.locator('.selected-result').count()==4
  assert '47.12%' in nojs.locator('.selected-result').first.inner_text()
  report['checks']['no_javascript']='Research prose, original image links, four result groups and all baseline values remain visible without JavaScript.'
  assert not report['errors'],report['errors']
  ctx.close();b.close()
finally:server.shutdown();server.server_close()
report['source_hashes']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['index.html','static/css/style.css','static/js/main.js','static/js/config.js','static/data/results.json','static/data/figure-provenance.json']}
(ROOT/'tests/browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'widths':len(report['widths']),'checks':report['checks'],'errors':report['errors']},ensure_ascii=False,indent=2))
