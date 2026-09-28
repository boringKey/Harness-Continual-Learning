#!/usr/bin/env python3
"""Publish this complete site to boringKey/Harness-Continual-Learning.

Requires Python >=3.9 and the GitHub CLI (gh), logged in as the repository owner.
Uses GitHub's Git-data API for atomic, non-force publication, then configures
Pages for main / (root). Never modifies the personal-homepage repository.
No token is requested, printed, embedded, or saved by this script.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'boringKey/Harness-Continual-Learning'
BRANCH = 'main'
SITE = 'https://boringkey.github.io/Harness-Continual-Learning/'
SETTINGS = f'https://github.com/{REPO}/settings/pages'
ACTIONS = f'https://github.com/{REPO}/actions'
EXCLUDED_PARTS = {'.git', '__pycache__', '.DS_Store'}


class PublishError(RuntimeError):
    pass


def run(args: list[str], *, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, input=stdin, text=True, encoding='utf-8',
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)


def api(endpoint: str, method: str = 'GET', payload: dict | None = None,
        allow_404: bool = False):
    command = ['gh', 'api', '--hostname', 'github.com', '--method', method,
               '-H', 'Accept: application/vnd.github+json', endpoint]
    if payload is not None:
        command += ['--input', '-']
    result = run(command, stdin=json.dumps(payload) if payload is not None else None)
    if result.returncode:
        if allow_404 and 'HTTP 404' in result.stderr:
            return None
        raise PublishError(f'GitHub API {method} {endpoint} failed:\n'
                           f'{result.stderr.strip()}\n'
                           'No credentials should be pasted into a chat. Check gh auth status locally.')
    return json.loads(result.stdout) if result.stdout.strip() else None


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def collect_files() -> dict[str, bytes]:
    result = {}
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if any(p in EXCLUDED_PARTS for p in relative.parts):
            continue
        if path.is_symlink():
            raise PublishError(f'Symlink not permitted in this publishing package: {relative}')
        if not path.is_file() or path.suffix in {'.pyc', '.zip'}:
            continue
        if path.stat().st_size > 100 * 1024 * 1024:
            raise PublishError(f'{relative} exceeds the regular GitHub file limit. '
                               'Use external media hosting and set its URL in config.js.')
        result[relative.as_posix()] = path.read_bytes()
    if 'index.html' not in result or '.nojekyll' not in result:
        raise PublishError('Run this script from the full package containing index.html and .nojekyll.')
    return result


def verify_live(expected: dict[str, bytes]) -> bool:
    # Only request public project files. Never send credentials to the website.
    critical = ['index.html', 'static/css/style.css', 'static/js/main.js',
                'static/images/figure-1-comparison-1600.webp', 'static/images/framework-1600.webp']
    for name in critical:
        url = SITE + ('' if name == 'index.html' else name) + f'?verify={time.time_ns()}'
        request = urllib.request.Request(url, headers={'User-Agent': 'HCL-Pages-Verification/1.0',
                                                      'Cache-Control': 'no-cache'})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status != 200 or not response.geturl().startswith(SITE):
                    return False
                actual = response.read()
            if hashlib.sha256(actual).digest() != hashlib.sha256(expected[name]).digest():
                return False
        except (urllib.error.URLError, TimeoutError, OSError):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yes', action='store_true', help='Confirm the displayed publication plan.')
    parser.add_argument('--wait', type=int, default=600, help='Seconds to wait for live verification (default 600).')
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        raise PublishError('Python 3.9 or newer is required.')
    if not shutil.which('gh'):
        raise PublishError('GitHub CLI (gh) is not installed. Install it from https://cli.github.com/ '
                           'or use the browser upload instructions in DEPLOY.zh-CN.md.')
    auth = run(['gh', 'auth', 'status', '--hostname', 'github.com'])
    if auth.returncode:
        raise PublishError('First run: gh auth login --hostname github.com --web\n'
                           'Log in as boringKey, then rerun this script.')
    check = subprocess.run([sys.executable, str(ROOT/'scripts/check_site.py')], cwd=ROOT)
    if check.returncode:
        raise PublishError('Static checks failed. Nothing has been uploaded.')
    user = api('user')
    if user['login'].lower() != 'boringkey':
        raise PublishError(f"Active account is {user['login']}, not boringKey. "
                           'Switch the GitHub CLI account before publishing.')
    repo = api(f'repos/{REPO}')
    if repo['full_name'].lower() != REPO.lower() or repo.get('private') or repo.get('archived'):
        raise PublishError('Unexpected repository state. No changes made.')
    perms = repo.get('permissions', {})
    if not perms.get('push') or not (perms.get('admin') or perms.get('maintain')):
        raise PublishError('Repository push and Pages-management permissions are required.')
    current_pages = api(f'repos/{REPO}/pages', allow_404=True)
    if current_pages and (current_pages.get('cname') or
                          current_pages.get('build_type', 'legacy') != 'legacy' or
                          current_pages.get('source') != {'branch': BRANCH, 'path': '/'}):
        raise PublishError('An existing custom domain or different publishing source was found. '
                           f'To avoid changing an existing deployment, review {SETTINGS} first. '
                           'This script only configures main / (root), without a custom domain.')
    head = api(f'repos/{REPO}/git/ref/heads/{BRANCH}')['object']['sha']
    commit = api(f'repos/{REPO}/git/commits/{head}')
    tree = api(f'repos/{REPO}/git/trees/{commit["tree"]["sha"]}?recursive=1')
    if tree.get('truncated'):
        raise PublishError('Remote tree listing was truncated; stopping rather than guessing.')
    remote = {entry['path']: entry for entry in tree['tree']}
    local = collect_files()
    preserved = []
    # Preserve previously configured videos and their assets on repeat runs.
    for name in list(local):
        if name in remote and (name == 'static/js/config.js' or
                               (name.startswith('static/videos/') and name != 'static/videos/README.md')):
            if git_blob_sha(local[name]) != remote[name]['sha']:
                preserved.append(name)
            del local[name]
    changed = {name: data for name, data in local.items()
               if name not in remote or remote[name]['sha'] != git_blob_sha(data)}
    print(f'\nRepository: {REPO}\nBranch: {BRANCH}\nWebsite: {SITE}')
    print(f'Create/update {len(changed)} files. Remote-only files will NOT be deleted.')
    for name in changed:
        print(f'  {"UPDATE" if name in remote else "ADD   "} {name}')
    for name in preserved:
        print(f'  KEEP existing {name}')
    print('Personal homepage boringKey/boringKey.github.io will NOT be accessed or changed.')
    print('Pages will use main / (root); all website assets will be public.')
    if not args.yes and input('Type PUBLISH to continue: ').strip() != 'PUBLISH':
        print('Cancelled. Nothing uploaded.'); return 1
    published_sha = head
    if changed:
        elements = []
        for i, (name, data) in enumerate(changed.items(), 1):
            blob = api(f'repos/{REPO}/git/blobs', 'POST',
                       {'content': base64.b64encode(data).decode('ascii'), 'encoding': 'base64'})
            if blob['sha'] != git_blob_sha(data):
                raise PublishError(f'Git blob checksum mismatch: {name}. Branch has not been changed.')
            elements.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
            print(f'Uploaded {i}/{len(changed)}: {name}')
        new_tree = api(f'repos/{REPO}/git/trees', 'POST',
                       {'base_tree': commit['tree']['sha'], 'tree': elements})
        new_commit = api(f'repos/{REPO}/git/commits', 'POST',
                         {'message': 'Publish HCL project website with correct Pages paths',
                          'tree': new_tree['sha'], 'parents': [head]})
        latest = api(f'repos/{REPO}/git/ref/heads/{BRANCH}')['object']['sha']
        if latest != head:
            raise PublishError('The remote branch changed during upload. No force push was used. '
                               'Rerun to merge the latest remote state safely.')
        api(f'repos/{REPO}/git/refs/heads/{BRANCH}', 'PATCH',
            {'sha': new_commit['sha'], 'force': False})
        published_sha = new_commit['sha']
        print('Website commit:', published_sha)
    else:
        print('Website files are already current.')
    # Re-read before creating Pages in case it was enabled while files uploaded.
    pages = api(f'repos/{REPO}/pages', allow_404=True)
    if pages is None:
        try:
            api(f'repos/{REPO}/pages', 'POST',
                {'build_type': 'legacy', 'source': {'branch': BRANCH, 'path': '/'}})
        except PublishError as exc:
            raise PublishError('Website files are uploaded, but Pages could not be enabled.\n'
                               f'Open {SETTINGS} and select Deploy from a branch / main / (root).\n{exc}')
    elif (pages.get('cname') or pages.get('build_type', 'legacy') != 'legacy' or
          pages.get('source') != {'branch': BRANCH, 'path': '/'}):
        raise PublishError('Pages settings changed during upload. Review them manually; no settings overwritten.')
    try:
        api(f'repos/{REPO}/pages/builds', 'POST')
    except PublishError:
        print('An explicit build request was not accepted. Checking the automatic deployment instead.')
    if not repo.get('homepage') or repo['homepage'] == SITE:
        try:
            api(f'repos/{REPO}', 'PATCH', {'homepage': SITE})
        except PublishError:
            print('Could not set the repository About link; this does not prevent Pages publication.')
    print('Waiting for the exact homepage, stylesheet, script, and two figures to be served...')
    deadline = time.monotonic() + max(0, args.wait)
    while time.monotonic() < deadline:
        if verify_live(local):
            print(f'\nVERIFIED: HTTP 200 and matching content for the project and key assets.\n{SITE}')
            return 0
        print('Deployment/CDN propagation still pending. See', ACTIONS)
        time.sleep(15)
    print('\nFiles uploaded and Pages configured, but the live website is not yet verified.')
    print(f'Check {ACTIONS}\nand {SETTINGS}\nTarget: {SITE}')
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (PublishError, subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        print(f'\nSTOPPED: {exc}', file=sys.stderr)
        sys.exit(1)
