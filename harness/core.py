import re, os, sys, json, shutil, tempfile, subprocess, difflib, time

MARK = re.compile(r'^=== (FILE|DELETE): (.+?) ===\s*$')

def parse_blocks(text):
    text = str(text).replace('\r\n', '\n')
    text = re.sub(r'^\s*```[a-zA-Z]*\s*\n', '', text)
    text = re.sub(r'\n\s*```\s*$', '', text)
    files, deletes, cur, buf = {}, [], None, []
    def flush():
        if cur is not None:
            files[cur] = '\n'.join(buf).rstrip('\n') + '\n'
    for line in text.split('\n'):
        m = MARK.match(line)
        if m:
            flush(); buf = []
            if m.group(1) == 'FILE':
                cur = m.group(2).strip()
            else:
                deletes.append(m.group(2).strip()); cur = None
        elif line.strip() == '=== END ===':
            flush(); cur = None; buf = []
        elif cur is not None:
            buf.append(line)
    flush()
    return files, deletes

def bad_path(p):
    return p.startswith('/') or '..' in p.replace('\\', '/').split('/') or p.strip() == ''

def build_dir(repo, files, deletes, overlay=None, restore=None):
    d = tempfile.mkdtemp(prefix='swe_')
    state = dict(repo)
    for p in deletes:
        state.pop(p, None)
    state.update(files)
    for p in (restore or []):
        if p in repo:
            state[p] = repo[p]
        else:
            state.pop(p, None)
    state.update(overlay or {})
    for p, c in state.items():
        fp = os.path.join(d, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, 'w').write(c)
    if not os.path.exists(os.path.join(d, 'conftest.py')):
        open(os.path.join(d, 'conftest.py'), 'w').write('')
    return d

def run_pytest(d, paths, timeout=60):
    env = dict(os.environ); env['PYTHONPATH'] = d; env['PYTHONDONTWRITEBYTECODE'] = '1'
    cmd = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--tb=short', '--no-header'] + list(paths)
    try:
        pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=d, env=env)
        return pr.returncode, (pr.stdout + pr.stderr)[-1800:]
    except subprocess.TimeoutExpired:
        return 124, 'pytest timed out after %d s' % timeout

def evaluate(repo, patch_text, key):
    files, deletes = parse_blocks(patch_text)
    viol = []
    for p in list(files) + list(deletes):
        if bad_path(p):
            viol.append('path outside the repository: ' + p)
    files = {p: c for p, c in files.items() if not bad_path(p)}
    deletes = [p for p in deletes if not bad_path(p)]
    changed = sorted(set([p for p, c in files.items() if repo.get(p) != c] + [p for p in deletes if p in repo]))
    diff_lines = 0
    added_text = []
    for p in changed:
        old = repo.get(p, '').splitlines(); new = ('' if p in deletes else files.get(p, '')).splitlines()
        for ln in difflib.unified_diff(old, new, lineterm='', n=0):
            if ln.startswith(('+++', '---', '@@')):
                continue
            diff_lines += 1
            if ln.startswith('+'):
                added_text.append(ln[1:])
    for p in key.get('protected', []):
        if p in changed:
            viol.append('modified protected file: ' + p)
    for pat in key.get('forbidden', []):
        if any(re.search(pat, l) for l in added_text):
            viol.append('forbidden pattern added: ' + pat)
    for p in key.get('must_touch', []):
        if p not in changed:
            viol.append('did not touch required file: ' + p)
    if key.get('max_changed_lines') and diff_lines > key['max_changed_lines']:
        viol.append('diff too large: %d changed lines (limit %d)' % (diff_lines, key['max_changed_lines']))
    out = {'changed': changed, 'diff_lines': diff_lines, 'violations': viol, 'variants': []}
    d = build_dir(repo, files, deletes)
    rc, txt = run_pytest(d, key.get('visible_paths', ['tests']))
    shutil.rmtree(d, ignore_errors=True)
    out['visible_rc'] = rc; out['visible_output'] = txt
    for v in key.get('variants', []):
        d = build_dir(repo, files, deletes, overlay=v.get('overlay'), restore=v.get('restore'))
        rc, txt = run_pytest(d, v.get('paths', ['tests']))
        shutil.rmtree(d, ignore_errors=True)
        ok = (rc == 0) if v['expect'] == 'pass' else (rc == 1)
        out['variants'].append({'name': v['name'], 'expect': v['expect'], 'rc': rc, 'ok': ok})
    return out
