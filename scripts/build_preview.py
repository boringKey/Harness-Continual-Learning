#!/usr/bin/env python3
"""Build a portable HTML preview, using only the Python standard library.
Usage: python3 scripts/build_preview.py /path/to/HCL-v10-preview.html
The normal GitHub Pages site must use index.html and its relative assets instead.
"""
from pathlib import Path
from urllib.parse import urlsplit
import base64
import json
import mimetypes
import re
import sys

ROOT=Path(__file__).resolve().parents[1]

def data_url(relative):
    p=(ROOT/relative).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file():
        raise ValueError('Missing or unsafe preview asset: '+relative)
    mime=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode('ascii')

def build(output):
    text=(ROOT/'index.html').read_text(encoding='utf-8')
    # External CSS/JS are embedded; JS is placed after markup to preserve load order.
    text=re.sub(r'<link\b[^>]*href="static/css/style.css"[^>]*>',
                lambda m:'<style>\n'+(ROOT/'static/css/style.css').read_text()+'\n</style>',text)
    text=re.sub(r'<script\b[^>]*src="static/js/(?:config|main).js"[^>]*></script>','',text)
    # Use the full PNG in the portable preview. The deployed site keeps responsive WebP.
    text=re.sub(r'<source\b[^>]*>','',text)
    assets=set(re.findall(r'(?:href|src)="(static/images/[^"#]+)"',text))
    for asset in assets:
        text=text.replace('="'+asset+'"','="'+data_url(asset)+'"')
    text=text.replace('href="citation.bib"','href="'+data_url('citation.bib')+'"')
    text=re.sub(r'href="static/paper/HCL.pdf(?:#page=(\d+))?"',
                lambda m:'href="#" data-inline-paper-page="'+(m.group(1) or '')+'"',text)
    encoded=base64.b64encode((ROOT/'static/paper/HCL.pdf').read_bytes()).decode('ascii')
    pdf_js='''(() => {
 const raw=atob(PDF_BASE64), bytes=new Uint8Array(raw.length);
 for(let i=0;i<raw.length;i++) bytes[i]=raw.charCodeAt(i);
 const url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));
 document.querySelectorAll('[data-inline-paper-page]').forEach(a=>{
   const p=a.dataset.inlinePaperPage; a.href=url+(p?'#page='+p:'');
 });
})();'''.replace('PDF_BASE64',json.dumps(encoded))
    scripts='\n'.join('<script>\n'+content.replace('</script','<\\/script')+'\n</script>' for content in [pdf_js,(ROOT/'static/js/config.js').read_text(),(ROOT/'static/js/main.js').read_text()])
    text=text.replace('</body>',scripts+'\n</body>')
    output=Path(output).resolve()
    if output==ROOT/'index.html': raise ValueError('Do not overwrite deployment index.html.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(text,encoding='utf-8')
    print(str(output),output.stat().st_size,'bytes')

if __name__=='__main__':
    build(sys.argv[1] if len(sys.argv)>1 else ROOT.parent/'HCL-v10-preview.html')
