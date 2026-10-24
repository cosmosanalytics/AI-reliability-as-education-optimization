import json, sys
import core, tasks
def patch_text(files):
    return ''.join('=== FILE: %s ===\n%s\n=== END ===\n' % (p, c.rstrip('\n')) for p, c in files.items())
bad = 0
for t in tasks.T:
    key = t['key']
    empty = core.evaluate(t['repo'], '', key)
    ref = core.evaluate(t['repo'], patch_text(t['ref']), key)
    ok_ref = all(v['ok'] for v in ref['variants']) and not ref['violations']
    empty_hidden_fail = not empty['variants'][0]['ok']
    print(t['id'], t['name'][:36].ljust(36), 'ref ok' if ok_ref else 'REF FAILS %s %s' % ([ (v['name'], v['rc']) for v in ref['variants'] if not v['ok']], ref['violations']), '| unpatched hidden fails:' , empty_hidden_fail, '| visible unpatched rc', empty['visible_rc'], 'ref diff', ref['diff_lines'])
    if not ok_ref: bad += 1
print('bad', bad)
