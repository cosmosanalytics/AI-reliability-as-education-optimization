import sys; sys.path.insert(0,'/tmp/claude-0/hard3'); sys.path.insert(0,'/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
import hard3_tasks as h, core
def pt(files): return ''.join('=== FILE: %s ===\n%s\n=== END ===\n'%(p,c.rstrip('\n')) for p,c in files.items())
for t in h.T:
    ref=core.evaluate(t['repo'],pt(t['ref']),t['key']); emp=core.evaluate(t['repo'],'',t['key'])
    ok=all(v['ok'] for v in ref['variants']) and not ref['violations'] and ref['visible_rc']==0
    print(t['id'],t['name'],'REF OK' if ok else 'REF FAIL','| unpatched hidden fails',not emp['variants'][0]['ok'],'| repo lines',sum(c.count('\n') for c in t['repo'].values()))
    if not ok:
        d=core.build_dir(t['repo'],core.parse_blocks(pt(t['ref']))[0],[],overlay=t['key']['variants'][0]['overlay'])
        print(core.run_pytest(d,['tests'])[1][-2000:])
