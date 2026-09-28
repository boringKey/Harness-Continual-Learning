#!/usr/bin/env python3
"""Optional synthetic interaction tests; run after browser_smoke.py."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os, shutil, sys
R=Path(__file__).resolve().parents[1]
base=Path(sys.argv[1] if len(sys.argv)>1 else R.parent/'HCL-v10-preview.html').read_text()
CHROMIUM=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
if not CHROMIUM: raise SystemExit('Set CHROMIUM_PATH to an installed Chromium/Chrome executable.')
marker='/* Progressive enhancement: all research content remains readable without JavaScript. */'
assert marker in base
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=CHROMIUM,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':390,'height':844})
 mock='''window.HCL_CONFIG.codeUrl="https://example.invalid/research";
window.HCL_CONFIG.videos[0].title="Configured comparison";
window.HCL_CONFIG.videos[0].caption="Configured caption";
window.HCL_CONFIG.videos[0].src="https://example.invalid/test.mp4";
'''
 page.route('https://example.invalid/**',lambda route:route.fulfill(status=404,body='Synthetic media error for UI test'))
 page.set_content(base.replace(marker,mock+marker),wait_until='load')
 assert page.locator('#code-resource>a').get_attribute('href')=='https://example.invalid/research'
 assert page.locator('#comparison-1 .video-title').inner_text()=='Configured comparison'
 assert page.locator('#comparison-1 .video-caption').inner_text()=='Configured caption'
 page.locator('#comparison-1 video').evaluate("x => x.dispatchEvent(new Event('error'))")
 assert page.locator('#comparison-1 .video-placeholder').is_visible()
 assert page.locator('#comparison-1 .placeholder-label').inner_text()=='Video unavailable'
 assert page.locator('#comparison-1 video').is_hidden()
 page.set_content(base.replace(marker,'window.HCL_CONFIG.codeUrl="javascript:alert(1)"; window.HCL_CONFIG.videos[0].src="javascript:alert(1)";\n'+marker),wait_until='load')
 assert page.locator('#code-resource>a').count()==0
 assert page.locator('#comparison-1 video').get_attribute('src') is None
 b.close()
report=json.loads((R/'tests/browser-report.json').read_text())
report['checks']['config_and_media_error']='Editable title/caption and code URL applied. Synthetic unavailable-media event restores the placeholder. This is not real video playback.'
report['checks']['unsafe_url_rejection']='javascript: values rejected for video and research-code URL.'
(R/'tests/browser-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print('PASS: configuration, synthetic media-error fallback, unsafe URL rejection.')
