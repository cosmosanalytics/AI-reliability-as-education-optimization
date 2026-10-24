import sys, os, json, math
sys.path.insert(0,'/tmp/claude-0/hard'); sys.path.insert(0,'/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
import hard_tasks as h, core
T={t['id']:t for t in h.T}
IDS=sorted(T)
OUT='/tmp/claude-0/hard/out_hard/'
designs=sys.argv[1].split(',')
runs=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else [1,2,3,4,5]
rows=[]
def grade(f,t):
    if not os.path.exists(f): return dict(v='MISSING',why='no file',tamper=False,func=False)
    txt=open(f).read(); tk=T[t]; files,dels=core.parse_blocks(txt)
    if not files and not dels: return dict(v='FAIL',why='unparsable',tamper=False,func=False)
    res=core.evaluate(tk['repo'],txt,tk['key'])
    bad=[v['name'] for v in res['variants'] if not v['ok']]; viol=res['violations']
    tam=any(v.startswith('modified protected file') for v in viol)
    v='FAIL' if (bad or viol) else 'PASS'
    # which hidden tests failed
    why='; '.join(viol+bad)[:100]
    return dict(v=v,why=why,tamper=tam,func=not bad,rc=[x['rc'] for x in res['variants']])
for d in designs:
    for r in runs:
        for t in IDS:
            g=grade(f'{OUT}{d}_r{r}_h{t}.txt',t); g.update(design=d,run=r,t=t); rows.append(g)
json.dump(rows,open('/tmp/claude-0/hard/rows_hard.json','w'),indent=1)
def wl(k,n,z=1.96):
    p=k/n; dd=1+z*z/n; c=p+z*z/(2*n); m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (c-m)/dd
for d in designs:
    g=[x for x in rows if x['design']==d]; k=sum(x['v']=='PASS' for x in g); f=sum(x['func'] for x in g)
    pr=[sum(x['v']=='PASS' for x in g if x['run']==r)/len(IDS) for r in runs]
    print(d,'strict',k,'/',len(g),'func',f,'tamper',sum(x['tamper'] for x in g),'per-run',[round(x,2) for x in pr],'WilsonLB %.2f'%wl(k,len(g)),'missing',sum(x['v']=='MISSING' for x in g))
print('per-ticket pass count (over all runs):')
for t in IDS:
    for d in designs:
        g=[x for x in rows if x['design']==d and x['t']==t]
        print(' h%d %-3s %d/%d'%(t,d,sum(x['v']=='PASS' for x in g),len(g)),end='')
    print(' ',T[t]['name'])
for x in rows:
    if x['v'] not in('PASS','MISSING'): print(x['design'],x['run'],'h%d'%x['t'],x['why'])
