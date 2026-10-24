import sys, re, ast
sys.path.insert(0,'/tmp/claude-0/hard2'); sys.path.insert(0,'/tmp/claude-0/hard3')
sys.path.insert(0,'/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
import hard2_tasks as h2, hard3_tasks as h3
T=[]
def strip_doc(src): return re.sub(r'\n[ ]+"""(?:.|\n)*?"""\n','\n',src)
def split_tests(src):
    tree=ast.parse(src); lines=src.split('\n')
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
    first=min(f.lineno for f in funcs)-1
    header='\n'.join(lines[:first]).rstrip()+'\n'
    segs=[ '\n'.join(lines[f.lineno-1-len(f.decorator_list):f.end_lineno]) for f in funcs]
    return header,segs
VIS_NOTE=("Run the test-suite in tests/ to see what currently fails. The visible tests cover only part of what is expected: a larger hidden "
          "suite of the same kind will also be run, so fix the underlying causes, not just the visible failures. Do not change the tests.")
for t in list(h2.T)+list(h3.T):
    hid=list(t['key']['variants'][0]['overlay'].values())[0]
    header,segs=split_tests(hid)
    k=max(1,len(segs)//2)
    vis=header+'\n\n'+'\n\n'.join(segs[:k])+'\n'
    repo={p:(strip_doc(c) if p.endswith('.py') and not p.startswith('tests/') else c) for p,c in t['repo'].items() if not p.startswith('tests/')}
    repo['tests/test_visible.py']=vis
    key={'visible_paths':['tests/test_visible.py'],'protected':['tests/test_visible.py'],'forbidden':[],'must_touch':[],
         'variants':[{'name':'hidden tests','overlay':t['key']['variants'][0]['overlay'],'expect':'pass','paths':['tests']}]}
    issue=t['issue'].split('Do not change the tests')[0].rstrip()
    EXTRA={202:' Environment strings: true/yes/on/1 are True, false/no/off/0 are False (any case, spaces ignored), plain integers become int, decimals float, empty or null/none become None, anything else stays a stripped string. A None in the override removes the key.',
           204:' Reading must raise ValueError for an unterminated quote. A text field starting with =, +, - or @ (unless it is a plain number) is written with a leading apostrophe.',
           205:' A rule whose action is "*" applies to every action.'}
    issue=issue+EXTRA.get(t['id'],'')+' '+VIS_NOTE
    T.append(dict(id=t['id']+400 if t['id']<300 else t['id']+400,group='Hard4',name=t['name'],rules='',issue=issue,repo=repo,key=key,ref=t['ref'],segs=len(segs),vis=k))
