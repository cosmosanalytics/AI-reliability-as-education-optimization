import sys
sys.path.insert(0, 'C:/Users/richa/ai-engineering/extracted_code/harness')
sys.path.insert(0, 'C:/Users/richa/ai-engineering/extracted_code/benchmarks')
import sep_tasks, core

def pt(files):
    return ''.join('=== FILE: %s ===\n%s\n=== END ===\n' % (p, c.rstrip('\n')) for p, c in files.items())

print('Validating sep_tasks...')
all_ok = True
for t in sep_tasks.T:
    ref = core.evaluate(t['repo'], pt(t['ref']), t['key'])
    emp = core.evaluate(t['repo'], '', t['key'])
    ref_ok = all(v['ok'] for v in ref['variants']) and not ref['violations']
    emp_fail = not emp['variants'][0]['ok']
    print('Task %d: %s | Ref Pass: %s | Unpatched Fails: %s' % (t['id'], t['name'], ref_ok, emp_fail))
    if not ref_ok or not emp_fail:
        all_ok = False
        print('  Ref violations:', ref['violations'])
        print('  Ref variant results:', ref['variants'])
        print('  Emp variant results:', emp['variants'])

print('All validated cleanly:', all_ok)
