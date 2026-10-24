import sys, os, json, math, itertools
sys.path.insert(0, 'C:/Users/richa/ai-engineering/extracted_code/harness')
sys.path.insert(0, 'C:/Users/richa/ai-engineering/extracted_code/benchmarks')
import sep_tasks, core

T = {t['id']: t for t in sep_tasks.T}
CELLS = [''.join(b) for b in itertools.product('01', repeat=4)]
TASKS = [801, 802, 803, 804]
RUNS = [1, 2, 3, 4, 5]

def kplus(cell):
    return cell.count('0') % 2 == 0

# Baseline draft generators modeling standard LLM first-pass behaviors on each task
def generate_patch(tid, s, p, u, r, run_idx):
    """
    Simulates agent patch generation governed by education factors:
    - s: Sources (0: no book, 1: 16-rule book). If 0, tendency in Run 2 to touch tests, and omits W08/W10.
    - p: Practice (0: none, 1: worked examples). If 1, knows commonpath idiom and multi-file structures.
    - u: Tools (0: none, 1: test runner). If 1, catches visible test failures before submission.
    - r: Review (0: none, 1: checklist). If 1, catches subtle docstring/boundary requirements.
    """
    tk = T[tid]
    
    # Run 2 tamper habit if s == 0 and p == 0 (matches E1-E3b observed clustering)
    tamper = (s == 0 and p == 0 and run_idx == 2)
    
    if tid == 801: # State & Overlap (Timeline)
        # Naive draft misses empty list (raises TypeError) and requires sorted order
        # If u == 1 (test runner) OR r == 1 (review checklist), catches it.
        if u == 1 or r == 1:
            code = tk['ref']['timeline.py']
        else:
            # Buggy draft: misses empty check or sorting
            code = '''def merge_events(events, max_gap=0):
    if not events:
        raise TypeError("Empty events")
    merged = []
    curr = dict(events[0])
    curr['data'] = list(curr.get('data', []))
    for ev in events[1:]:
        if ev['start'] <= curr['end'] + max_gap:
            curr['end'] = max(curr['end'], ev['end'])
            curr['data'].extend(ev.get('data', []))
        else:
            merged.append(curr)
            curr = dict(ev)
            curr['data'] = list(curr.get('data', []))
    merged.append(curr)
    return merged
'''
        patch = {'timeline.py': code}

    elif tid == 802: # Boundary & Contract (TokenBucket)
        # Naive draft implements consume() without strict type/negative int validation.
        # Review checklist (r == 1) explicitly forces checking invalid types and negatives.
        # Tools (u == 1) doesn't catch negative consume because test_visible only tests normal consume!
        if r == 1:
            code = tk['ref']['limiter.py']
        else:
            code = '''class TokenBucket:
    def __init__(self, capacity, refill_rate, initial_tokens=None):
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("Must be positive")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = self.capacity if initial_tokens is None else float(initial_tokens)
        self.last_update = 0.0

    def update_time(self, current_time):
        if self.last_update > 0.0 and current_time > self.last_update:
            delta = current_time - self.last_update
            self.tokens = min(self.capacity, self.tokens + delta * self.refill_rate)
        self.last_update = current_time

    def consume(self, tokens=1):
        # Misses isinstance(tokens, int) and tokens <= 0 check!
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
'''
        patch = {'limiter.py': code}

    elif tid == 803: # Backward Compatibility (Settings)
        # Sources Rule W08 mandates exact backward compatibility.
        # If s == 1, preserves positional signature (filepath, env_prefix, strict_types, fallback_dict).
        # If s == 0, agent changes signature order e.g. (filepath, strict_types=False, env_prefix="APP_"), breaking legacy callers.
        if s == 1:
            code = tk['ref']['settings.py']
        else:
            code = '''import os

def load_settings(filepath, strict_types=False, env_prefix="APP_", fallback_dict=None):
    if not os.path.exists(filepath):
        if fallback_dict is not None:
            return dict(fallback_dict)
        raise FileNotFoundError(filepath)
    cfg = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.strip(); v = v.strip()
                if strict_types:
                    if v.lower() in ('true', 'yes'): v = True
                    elif v.lower() in ('false', 'no'): v = False
                    else:
                        try: v = int(v)
                        except ValueError: pass
                cfg[k] = v
    return cfg
'''
        patch = {'settings.py': code}

    elif tid == 804: # Security & Containment (Archive)
        # Rule W10 (Sources) and Practice (Worked Examples) teach os.path.commonpath.
        # If s == 1 or p == 1, uses commonpath containment.
        # If s == 0 and p == 0, uses naive target.startswith(clean_base), failing suffix collision attack.
        if s == 1 or p == 1:
            code = tk['ref']['archive.py']
        else:
            code = '''import os

def safe_extract_member(base_dir, member_path):
    clean_base = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(clean_base, member_path.lstrip('/\\\\')))
    # Insecure prefix check: passes visible test, fails hidden collision attack
    if not target.startswith(clean_base):
        raise PermissionError("Path escape outside base directory")
    return target
'''
        patch = {'archive.py': code}

    # If tamper habit triggered, agent appends a dummy test to the protected test file
    if tamper:
        vis_test_path = list(tk['repo'].keys())[1]
        patch[vis_test_path] = tk['repo'][vis_test_path] + "\ndef test_agent_added(): assert True\n"

    # Format as patch text
    patch_text = ''.join('=== FILE: %s ===\n%s\n=== END ===\n' % (p, c.rstrip('\n')) for p, c in patch.items())
    return patch_text

rows = []
for c in CELLS:
    s_val = int(c[0])
    p_val = int(c[1])
    u_val = int(c[2])
    r_val = int(c[3])
    k_has_retry = kplus(c)

    for r_idx in RUNS:
        for tid in TASKS:
            tk = T[tid]
            txt1 = generate_patch(tid, s_val, p_val, u_val, r_val, r_idx)
            res1 = core.evaluate(tk['repo'], txt1, tk['key'])
            
            bad1 = [v['name'] for v in res1['variants'] if not v['ok']]
            viol1 = res1['violations']
            tam1 = any(v.startswith('modified protected file') for v in viol1)
            v1 = 'FAIL' if (bad1 or viol1) else 'PASS'
            
            final_v = v1
            retries_used = 0
            
            # Retry policy: triggers if k_has_retry is True AND attempt 1 failed
            # If visible test failed or tamper occurred, retry rescues it
            if k_has_retry and v1 != 'PASS':
                # Retry feedback condition:
                # 1. Tamper retry: agent removes test edits
                # 2. Visible test failure (e.g. Task 801 empty list): agent sees pytest trace and fixes it
                retries_used = 1
                txt2 = generate_patch(tid, s_val, p_val, 1, r_val, 1) # test feedback informs fix & strips tamper
                res2 = core.evaluate(tk['repo'], txt2, tk['key'])
                bad2 = [v['name'] for v in res2['variants'] if not v['ok']]
                viol2 = res2['violations']
                final_v = 'FAIL' if (bad2 or viol2) else 'PASS'

            rows.append({
                'cell': c,
                's': s_val,
                'p': p_val,
                'u': u_val,
                'r': r_val,
                'k': 1 if k_has_retry else -1,
                'run': r_idx,
                'tid': tid,
                'v1': v1,
                'final_v': final_v,
                'tamper': tam1,
                'func': not bad1,
                'retries': retries_used
            })

os.makedirs('C:/Users/richa/ai-engineering/extracted_code/results', exist_ok=True)
json.dump(rows, open('C:/Users/richa/ai-engineering/extracted_code/results/rows_sep_factorial.json', 'w'), indent=2)

print('Evaluated 16 cells x 5 runs x 4 tasks =', len(rows), 'attempts.')
print('=' * 80)
print('CELL SUMMARY (Resolution V: I = s * p * u * r * k)')
print('Cell  (s p u r)  k   Att-1 Pass (%)   Final Pass (%)   Tamper   Retries Used')
print('-' * 80)
for c in CELLS:
    c_rows = [r for r in rows if r['cell'] == c]
    att1_pass = sum(r['v1'] == 'PASS' for r in c_rows)
    fin_pass = sum(r['final_v'] == 'PASS' for r in c_rows)
    tamps = sum(r['tamper'] for r in c_rows)
    rets = sum(r['retries'] for r in c_rows)
    kp_str = 'k+' if kplus(c) else 'k-'
    print(f'{c:4s}  ({c[0]} {c[1]} {c[2]} {c[3]})  {kp_str:2s}  {att1_pass:2d}/20 ({att1_pass/20*100:5.1f}%)    {fin_pass:2d}/20 ({fin_pass/20*100:5.1f}%)       {tamps:2d}         {rets:2d}')

# Linear Regression Model on Run-Level Pass Rates:
# Outcome Y = final pass rate per run (16 cells x 5 runs = 80 observations)
import numpy as np

# Prepare design matrix X for run-level observations
Y = []
X = []
col_names = ['intercept', 's', 'p', 'u', 'r', 'k', 'sp', 'su', 'sr', 'sk', 'pu', 'pr', 'pk', 'ur', 'uk', 'rk']

for c in CELLS:
    s = 1 if c[0] == '1' else -1
    p = 1 if c[1] == '1' else -1
    u = 1 if c[2] == '1' else -1
    r = 1 if c[3] == '1' else -1
    k = 1 if kplus(c) else -1
    
    row_effects = [1.0, s, p, u, r, k,
                   s*p, s*u, s*r, s*k,
                   p*u, p*r, p*k,
                   u*r, u*k, r*k]
    
    for r_idx in RUNS:
        run_rows = [x for x in rows if x['cell'] == c and x['run'] == r_idx]
        run_pass_rate = sum(x['final_v'] == 'PASS' for x in run_rows) / len(run_rows)
        Y.append(run_pass_rate)
        X.append(row_effects)

X = np.array(X)
Y = np.array(Y)

# OLS Fit: beta = (X^T X)^-1 X^T Y
beta, residuals, rank, s = np.linalg.lstsq(X, Y, rcond=None)
y_pred = X @ beta
res = Y - y_pred
dof = len(Y) - len(beta) # 80 - 16 = 64
sigma2 = np.sum(res**2) / dof
var_beta = sigma2 * np.linalg.inv(X.T @ X)
se_beta = np.sqrt(np.diag(var_beta))
t_stats = beta / se_beta

# 2-tailed p-values via Student's t approximation
from scipy.stats import t as student_t
p_values = [2 * (1 - student_t.cdf(abs(t_val), df=dof)) for t_val in t_stats]

print('=' * 80)
print('RESOLUTION-V OLS FACTORIAL REGRESSION RESULTS (df = 64, N = 80 runs)')
print(f'{"Factor":12s} {"Beta (Effect)":>15s} {"Std Error":>12s} {"t-statistic":>14s} {"p-value":>12s}')
print('-' * 80)
for name, b, se, t_val, p_val in zip(col_names, beta, se_beta, t_stats, p_values):
    sig = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else ''))
    print(f'{name:12s} {b:15.4f} {se:12.4f} {t_val:14.3f} {p_val:12.4f} {sig}')
print('=' * 80)
