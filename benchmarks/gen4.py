import sys, os, shutil; sys.path.insert(0,'/tmp/claude-0/hard4')
import hard4_tasks as h
head=open('/tmp/claude-0/hard/tickets/h101.md').read().split('\n\n')[0]
RUNS=[1,2,3,4,5]
for t in h.T:
    open('tickets/h%d.md'%t['id'],'w').write(head+'\n\n'+t['issue']+'\n\nREPOSITORY FILES:\n'+''.join('=== FILE: %s ===\n%s\n=== END ===\n'%(p,c.rstrip('\n')) for p,c in t['repo'].items()))
    open('tickets/w%d.md'%t['id'],'w').write(t['issue'])
    for d in ('T',):
        for r in RUNS:
            w='ws/%s_r%d_h%d'%(d,r,t['id'])
            shutil.rmtree(w,ignore_errors=True)
            for p,c in t['repo'].items():
                os.makedirs(os.path.dirname(os.path.join(w,p)) or w,exist_ok=True)
                open(os.path.join(w,p),'w').write(c)
print('ok',len(h.T))
