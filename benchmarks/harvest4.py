import sys, os; sys.path.insert(0,'/tmp/claude-0/hard4')
import hard4_tasks as h
d=sys.argv[1]; used=0; tot=0
for t in h.T:
    for r in range(1,6):
        w='/tmp/claude-0/hard4/ws/%s_r%d_h%d'%(d,r,t['id'])
        if not os.path.isdir(w): continue
        out=''; 
        for root,dirs,files in os.walk(w):
            dirs[:]=[x for x in dirs if x not in('__pycache__','.pytest_cache')]
            for f in files:
                if f.endswith('.pyc'): continue
                p=os.path.relpath(os.path.join(root,f),w); c=open(os.path.join(root,f)).read()
                if t['repo'].get(p)!=c: out+='=== FILE: %s ===\n%s\n=== END ===\n'%(p,c.rstrip('\n'))
        for p in t['repo']:
            if not os.path.exists(os.path.join(w,p)): out+='=== DELETE: %s ===\n'%p
        open('/tmp/claude-0/hard4/out_hard4/%s_r%d_h%d.txt'%(d,r,t['id']),'w').write(out)
        tot+=1; used+=os.path.isdir(w+'/.pytest_cache')
print('workspaces',tot,'ran pytest',used)
