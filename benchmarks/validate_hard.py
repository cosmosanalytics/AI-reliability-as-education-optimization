import sys; sys.path.insert(0,'/tmp/claude-0/hard'); sys.path.insert(0,'/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
import hard_tasks as h, core
def pt(files): return ''.join('=== FILE: %s ===\n%s\n=== END ===\n'%(p,c.rstrip('\n')) for p,c in files.items())
only=[int(x) for x in sys.argv[1:]]
for t in h.T:
    if only and t['id'] not in only: continue
    ref=core.evaluate(t['repo'],pt(t['ref']),t['key']); emp=core.evaluate(t['repo'],'',t['key'])
    ok=all(v['ok'] for v in ref['variants']) and not ref['violations']
    print(t['id'],t['name'],'REF OK' if ok else 'REF FAIL','| unpatched hidden fails:',not emp['variants'][0]['ok'],'| visible unpatched rc',emp['visible_rc'])
    if not ok:
        d=core.build_dir(t['repo'],core.parse_blocks(pt(t['ref']))[0],[],overlay=t['key']['variants'][0]['overlay'])
        print(core.run_pytest(d,['tests'])[1][-1400:])
