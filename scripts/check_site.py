#!/usr/bin/env python3
"""Validate HCL v10 with Python's standard library only.

Checks local links, page structure, visible baselines/bars/gains, CSV/JSON
consistency, and the exact supplied manuscript and figure provenance.
It does not check network availability, real videos, or a live deployment.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Node:
    def __init__(self, tag: str, attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children: list[Node | str] = []
    @property
    def text(self) -> str:
        return ' '.join(''.join(c.text if isinstance(c, Node) else c for c in self.children).split())
    def has(self, name: str) -> bool:
        return name in (self.attrs.get('class') or '').split()
    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node): yield from c.walk()
    def cls(self, name: str) -> 'Node':
        return next(n for n in self.walk() if n.has(name))

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].children.append(n)
        if tag not in VOID: self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID: self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break
    def handle_data(self, value): self.stack[-1].children.append(value)

def dec(value) -> Decimal: return Decimal(str(value))
def num(value, setting): return str(int(value)) if setting == 'minecraft' else f'{dec(value):.2f}'

def main() -> int:
    errors, notes = [], []
    def require(ok, message):
        if not ok: errors.append(message)
    required = ['index.html','.nojekyll','citation.bib','README.md','DEPLOY.zh-CN.md',
                'DESIGN.zh-CN.md','SOURCES.md','LICENSE','static/css/style.css',
                'static/js/config.js','static/js/main.js','static/images/social-card.png',
                'static/images/framework.png','static/images/figure-1-comparison.png','static/images/figure-1-comparison.webp','static/images/figure-1-comparison-1600.webp','static/data/results.json',
                'static/data/results.csv','static/data/figure-provenance.json','static/paper/HCL.pdf']
    for name in required: require((ROOT/name).is_file(), 'Missing file: '+name)
    if not (ROOT/'index.html').is_file():
        print('\n'.join(errors)); return 1
    html = (ROOT/'index.html').read_text(encoding='utf-8')
    site_url = 'https://boringkey.github.io/Harness-Continual-Learning/'
    require(site_url in html, 'Project deployment URL must match the target repository.')
    require('https://boringkey.github.io/HCL/' not in html, 'Stale /HCL/ absolute URL remains.')
    require('https://github.com/boringKey/HCL' not in html, 'Website source points to the old repository.')
    parser = Page(); parser.feed(html)
    nodes = list(parser.root.walk())
    ids = [n.attrs['id'] for n in nodes if n.attrs.get('id')]
    by_id = {n.attrs['id']: n for n in nodes if n.attrs.get('id')}
    counts = Counter(n.tag for n in nodes)
    require(len(set(ids)) == len(ids), 'Duplicate HTML ids.')
    require(counts['video'] == 2, 'Expected exactly two comparison-video slots.')
    require(counts['h1'] == 1 and counts['h2'] == 5, 'Expected one paper title and five content sections.')
    require(not counts['table'] and not counts['details'], 'Full tables / nested expandable sections must not return.')
    order = ['top','demos','overview','method','experiments','citation']
    require(all(x in ids for x in order) and [ids.index(x) for x in order] == sorted(ids.index(x) for x in order), 'Incorrect page order.')
    for key, text in [('demos-title','Continual learning in Minecraft'),
                      ('overview-title','The harness becomes the continual learning state.')]:
        require(key in by_id and by_id[key].text == text, 'Incorrect heading: '+key)
    for cls in ['concept-figure','shared-principle','framework-reading']:
        require(any(n.has(cls) for n in nodes), 'Missing principal content: '+cls)
    require(any(n.has('brand') and n.text == 'Harness Continual Learning' for n in nodes), 'Navbar must use the full project name.')
    require(sum(n.has('paper-figure') for n in nodes) == 2, 'Expected original Figures 1 and 2.')
    require(sum(n.has('result-pictogram') for n in nodes) == 4, 'Expected four experiment icons.')
    require(not any(n.has('state-equation') or n.has('learning-panel') for n in nodes), 'Removed website formula / handmade comparison must not return.')
    # Important claims belong in normal body content, not an old tiny footer.
    for name in ['Task Interface','Experience Memory','Capability Map','Adaptive Router',
                 'Frozen weights do not eliminate forgetting.','Acquire new capabilities.',
                 'Retain earlier ones.','One objective, two learning states.']:
        require(name in parser.root.text, 'Missing explanatory content: '+name)
    for token in ['Figure 1 in the paper', 'Original figure ↗', 'Full experiments', 'HCL in open-world interaction', 'HCL in action','The objective is shared:', 'concept-connections',
                  'model-reference','Retention is an explicit constraint','Full per-task results',
                  'Research project','A frozen model.','An evolving harness.',
                  'fonts.googleapis.com','googletagmanager.com','google-analytics.com']:
        require(token not in html, 'Stale or prohibited page content: '+token)
    for n in nodes:
        if n.tag == 'a':
            href = n.attrs.get('href') or ''
            require(not ('HCL.pdf#' in href), 'Redundant section-level manuscript link remains: '+href)
    require(sum(n.tag == 'a' and 'data-figure' in n.attrs and n.text == 'Enlarge figure' for n in nodes) == 2,
            'Keep both image enlargement controls.')
    assets = []
    for n in nodes:
        for key in ['href','src','poster']:
            if n.attrs.get(key): assets.append(n.attrs[key])
        if n.attrs.get('srcset'):
            assets.extend(x.strip().split()[0] for x in n.attrs['srcset'].split(','))
    for url in assets:
        u = urlsplit(url)
        if u.scheme or u.netloc: continue
        if not u.path:
            require(not u.fragment or unquote(u.fragment) in ids, 'Unknown local anchor: '+url)
            continue
        p = (ROOT/unquote(u.path)).resolve()
        require(not url.startswith('/') and p.is_relative_to(ROOT) and p.is_file(), 'Missing / unsafe asset: '+url)
    meta = {n.attrs.get('name') or n.attrs.get('property'): n.attrs.get('content') for n in nodes if n.tag == 'meta'}
    for name in ['viewport','og:image','citation_title','citation_pdf_url']:
        require(bool(meta.get(name)), 'Missing metadata: '+name)
    require(by_id['bibtex-code'].text == ' '.join((ROOT/'citation.bib').read_text().split()), 'Citation file / HTML mismatch.')
    try:
        data = json.loads((ROOT/'static/data/results.json').read_text())
        results = [n for n in nodes if n.has('selected-result')]
        require([n.attrs['data-setting'] for n in results] == data['display_order'], 'Incorrect result order.')
        for result in results:
            a = result.attrs; key = a['data-setting']; ds = data[key]
            primary = data['starting_point_comparisons'][key]
            secondary = data['selected_comparisons'][key]
            method = a['data-method']; is_mc = key == 'minecraft'
            def value_for(m):
                return ds['completed_tasks'][m] if is_mc else next(r[-2] for r in ds['rows'] if r[0] == m)
            value = value_for(method)
            require(method == primary['method'] == secondary['method'], 'Selected method mismatch: '+key)
            require(dec(a['data-value']) == dec(value), 'Selected value mismatch: '+key)
            require(num(value,key) in result.cls('result-number').text, 'Wrong visible headline number: '+key)
            require(ds['backbone'] in result.cls('result-model').text, 'Wrong or missing backbone: '+key)
            require(method in result.cls('result-profile').text, 'Missing HCL configuration: '+key)
            expected_baseline = 'Static Harness' if is_mc or key == 'alfworld' else 'Zero-shot'
            require(a['data-baseline'] == primary['baseline_method'] == expected_baseline, 'Incorrect primary baseline label: '+key)
            for comp, primary_flag in [(primary,True),(secondary,False)]:
                bm = comp['baseline_method']; baseline = value_for(bm)
                gain = dec(value)-dec(baseline)
                require(dec(comp['selected_value']) == dec(value) and dec(comp['baseline_value']) == dec(baseline), 'Comparison/source mismatch: '+key)
                require(dec(comp['absolute_gain']) == gain, 'Incorrect gain in JSON: '+key)
                expected_unit = 'tasks' if is_mc else ('pts' if key == 'multimodal' else 'pp')
                require(comp['unit'] == expected_unit, 'Incorrect gain unit: '+key)
                gain_text = '+'+num(gain,key)+' '+expected_unit
                if primary_flag:
                    require(dec(a['data-baseline-value']) == dec(baseline) and dec(a['data-gain']) == gain, 'Primary data attributes mismatch: '+key)
                    require(gain_text == result.cls('result-gain').text, 'Primary gain not visibly correct: '+key)
                    require(bm in result.cls('result-baseline').text, 'Primary baseline not visible: '+key)
                elif not is_mc:
                    require(baseline == max(r[-2] for r in ds['rows'] if 'HCL' not in r[0]), 'Secondary baseline is not highest non-HCL table score: '+key)
                    require(gain_text in result.cls('secondary-comparison').text and bm in result.cls('secondary-comparison').text, 'Missing visible secondary comparison: '+key)
            bars = [n for n in result.walk() if n.has('bar-entry')]
            expected_methods = [primary['baseline_method']]+([] if is_mc else [secondary['baseline_method']])+[method]
            require([n.attrs['data-method'] for n in bars] == expected_methods, 'Incorrect bar methods or order: '+key)
            for bar in bars:
                bm = bar.attrs['data-method']; value = value_for(bm)
                suffix = '/50' if is_mc else ('' if key == 'multimodal' else '%')
                label = bar.cls('bar-label').text
                require(bm in label and num(value,key)+suffix in label and dec(bar.attrs['data-value']) == dec(value), 'Bar label/value mismatch: '+key+'/'+bm)
                track = next(n for n in bar.cls('bar-track').walk() if n.tag == 'span')
                width = re.search(r'width:([\d.]+)%',track.attrs.get('style',''))
                want_width = dec(value)*(2 if is_mc else 1)
                require(width is not None and dec(width[1]) == want_width, 'Incorrect bar length: '+key+'/'+bm)
            context = result.cls('result-context').text
            if is_mc:
                for m, v in ds['environment_actions'].items():
                    require(str(v) in context, 'Missing action count: '+m)
                require('Zero-shot' not in result.text, 'Minecraft Static Harness mislabeled as Zero-shot.')
            else:
                row = next(r for r in ds['rows'] if r[0] == method)
                require(f'{row[-1]:.2f}% average forgetting' in context, 'Missing/incorrect forgetting context: '+key)
                if key == 'alfworld': require('Zero-shot' not in result.text, 'ALFWorld Static Harness mislabeled as Zero-shot.')
        expected = []
        for key in data['display_order']:
            ds = data[key]
            if key == 'minecraft':
                for metric in ['completed_tasks','environment_actions']:
                    for method, value in ds[metric].items():
                        expected.append((key,method,metric,str(value),ds['source_label'],str(ds['page'])))
            else:
                for row in ds['rows']:
                    for metric,value in zip(ds['columns'][1:],row[1:]):
                        expected.append((key,row[0],metric,'' if value is None else f'{value:.2f}',ds['source_label'],str(ds['page'])))
        with (ROOT/'static/data/results.csv').open(encoding='utf-8',newline='') as f:
            actual = [tuple(r[k] for k in ['setting','method','metric','value','source','pdf_page']) for r in csv.DictReader(f)]
        require(expected == actual, 'Source CSV / JSON mismatch.')
        sha = hashlib.sha256((ROOT/data['source']['local_pdf']).read_bytes()).hexdigest()
        require(sha == data['source']['sha256'], 'Manuscript hash changed: recheck source values.')
        provenance = json.loads((ROOT/'static/data/figure-provenance.json').read_text())
        require(provenance['sha256'] == sha, 'Figure provenance refers to another manuscript.')
        for info in provenance['figures'].values():
            require((ROOT/info['png']).is_file(), 'Missing original figure: '+info['png'])
    except (OSError,ValueError,KeyError,TypeError,StopIteration) as e:
        errors.append('Data/provenance validation failed: '+str(e))
    config = (ROOT/'static/js/config.js').read_text()
    for kind,path in re.findall(r'^\s*(src|poster|captions):\s*["\']([^"\']*)["\']',config,re.MULTILINE):
        if not path:
            if kind == 'src': notes.append('Comparison video slot intentionally empty.')
            continue
        u = urlsplit(path)
        if not u.scheme and not u.netloc:
            f = (ROOT/unquote(u.path)).resolve()
            require(not path.startswith('/') and f.is_relative_to(ROOT) and f.is_file(), 'Invalid configured '+kind+': '+path)
    for f in ROOT.rglob('*'):
        require(f.suffix.lower() not in {'.ttf','.otf','.woff','.woff2'}, 'Do not distribute font files: '+f.name)
    for note in notes: print('NOTE:',note)
    for error in errors: print('ERROR:',error)
    if errors:
        print(f'FAILED: {len(errors)} problem(s).'); return 1
    print(f'PASS: {len(ids)} unique anchors; 2 video slots; 2 original paper figures; 4 icon-identified result groups; no full tables or expandable layers.')
    print('PASS: visible zero-shot/static and adaptive baselines, bar lengths, absolute gains, selected forgetting/action counts.')
    print('PASS: local assets, source PDF hash, figure provenance, citation, and archived CSV/JSON consistency.')
    print('Not checked: external links, real-recording playback, or live GitHub Pages deployment.')
    return 0

if __name__ == '__main__': sys.exit(main())
