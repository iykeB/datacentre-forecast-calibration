"""Ireland: score EirGrid demand forecast editions against outcomes, recalibrate the
Low to High ranges with a split conformal factor, and test it by leaving one edition out.

Inputs: data/eirgrid_gcs/ter_vintages.csv, data/cso/mec02.csv
Output: results/ireland_scoring.json
"""
import csv, json, collections, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
os.makedirs(D('results'), exist_ok=True)

# ---------- outcomes ----------
cso = collections.defaultdict(lambda: collections.defaultdict(float))
for x in csv.DictReader(open(D('data/cso/mec02.csv'), encoding='utf-8-sig')):
    cso[x['Electricity Consumption']][int(x['Quarter'][:4])] += float(x['VALUE']) / 1000
cso_tot, cso_dc = cso['All metered electricity consumption'], cso['Data centres']

ter_rows = list(csv.DictReader(open(D('data/eirgrid_gcs/ter_vintages.csv'))))
# reported outcome = the first (historical) row of each later edition, latest edition wins
reported = {}
for x in ter_rows:
    if x['note'].startswith('first row') and x['scenario'].lower().startswith('med') and x['ter_twh_ireland']:
        reported[int(x['year'])] = float(x['ter_twh_ireland'])
ratio = np.array([reported[y] / cso_tot[y] for y in reported if y in cso_tot])
r_mean, r_sd = ratio.mean(), ratio.std(ddof=1)
outcome = dict(reported)
derived = {}
for y in range(2015, 2026):
    if y not in outcome and y in cso_tot:
        outcome[y] = r_mean * cso_tot[y]; derived[y] = True

# ---------- forecasts ----------
F = collections.defaultdict(dict); base = {}
for x in ter_rows:
    if not x['ter_twh_ireland']: continue
    e, y = x['edition'].split(' (')[0], int(x['year'])
    if x['note'].startswith('first row'):
        base[e] = min(base.get(e, 9999), y)
    elif x['note'] == 'forecast':
        F[(e, y)][x['scenario'].split()[0].lower()] = float(x['ter_twh_ireland'])
pairs = []
for (e, y), d in F.items():
    if y in outcome and {'low', 'median', 'high'} <= set(d) and e in base:
        L, M, H = sorted([d['low'], d['median'], d['high']])[0], d['median'], max(d['low'], d['high'])
        pairs.append(dict(edition=e, year=y, h=y - base[e], L=L, M=M, H=H, A=outcome[y], derived=y in derived))
pairs.sort(key=lambda p: (p['edition'], p['year']))
E_list = sorted({p['edition'] for p in pairs}, key=lambda e: (base[e], e))

# ---------- scores of the published ranges ----------
def tri_crps(L, M, H, a, n=4000):
    if H - L < 1e-9: return abs(M - a)
    u = (np.arange(n) + 0.5) / n; c = (M - L) / (H - L)
    q = np.where(u < c, L + np.sqrt(np.clip(u * (H - L) * (M - L), 0, None)), H - np.sqrt(np.clip((1 - u) * (H - L) * (H - M), 0, None)))
    return float(np.mean(np.abs(q - a)) - 0.5 * np.mean(np.abs(q[:, None] - q[None, ::40])))

def interval_score(lo, hi, a, alpha=0.1):
    return (hi - lo) + 2 / alpha * max(lo - a, 0) + 2 / alpha * max(a - hi, 0)

for p in pairs:
    p['inside'] = bool(p['L'] <= p['A'] <= p['H'])
    p['err_pct'] = 100 * (p['M'] / p['A'] - 1)
    p['crps_rel'] = tri_crps(p['L'], p['M'], p['H'], p['A']) / p['A']
    p['is_rel'] = interval_score(p['L'], p['H'], p['A']) / p['A']
    # nonconformity: log distance from median in units of the edition's own half range on that side
    la, lm = math.log(p['A']), math.log(p['M'])
    p['s'] = (la - lm) / math.sqrt(p['h'])          # signed, horizon scaled log error

def summ(sel):
    return dict(n=len(sel), coverage=float(np.mean([p['inside'] for p in sel])),
                mean_err_pct=float(np.mean([p['err_pct'] for p in sel])),
                mape=float(np.mean([abs(p['err_pct']) for p in sel])),
                share_over=float(np.mean([p['err_pct'] > 0 for p in sel])),
                crps_rel=float(np.mean([p['crps_rel'] for p in sel])),
                is_rel=float(np.mean([p['is_rel'] for p in sel])))
bands = {'1-2': (1, 2), '3-5': (3, 5), '6-10': (6, 10)}
published = {'all': summ(pairs), **{b: summ([p for p in pairs if lo <= p['h'] <= hi]) for b, (lo, hi) in bands.items()}}

# ---------- split conformal recalibration ----------
def kappa(scores, level=0.9):
    # two sided split conformal: finite sample quantiles of signed scores at (1-level)/2 and (1+level)/2
    s = np.sort(scores); n = len(s)
    kl = max(math.floor((n + 1) * (1 - level) / 2), 1); ku = min(math.ceil((n + 1) * (1 + level) / 2), n)
    return (float(s[kl - 1]), float(s[ku - 1]))

def calibrated(p, k):
    r = math.sqrt(p['h'])
    lo, hi = p['M'] * math.exp(k[0] * r), p['M'] * math.exp(k[1] * r)
    return min(lo, p['L']), max(hi, p['H'])       # never narrower than the published range

def evaluate(k_of, sel):
    out = []
    for p in sel:
        lo, hi = calibrated(p, k_of(p))
        out.append(dict(inside=lo <= p['A'] <= hi, is_rel=interval_score(lo, hi, p['A']) / p['A'], width_rel=(hi - lo) / p['A']))
    return dict(n=len(out), coverage=float(np.mean([o['inside'] for o in out])),
                is_rel=float(np.mean([o['is_rel'] for o in out])), width_rel=float(np.mean([o['width_rel'] for o in out])))

k_all = kappa([p['s'] for p in pairs])
# leave one edition out (honest held out test)
loeo = []
for e in E_list:
    cal = [p['s'] for p in pairs if p['edition'] != e]
    k = kappa(cal); test = [p for p in pairs if p['edition'] == e]
    loeo.append(dict(edition=e, kappa=k, **evaluate(lambda p, k=k: k, test)))
held = [dict(p, k=next(l['kappa'] for l in loeo if l['edition'] == p['edition'])) for p in pairs]
loeo_pooled = evaluate(lambda p: p['k'], held)
# real time: calibrate only on edition years observed before the edition was published
rt = []
for p in pairs:
    pub = base[p['edition']] + 1
    cal = [q['s'] for q in pairs if q['year'] < pub]
    if len(cal) >= 8:
        rt.append(dict(p, k=kappa(cal)))
realtime = evaluate(lambda p: p['k'], rt) if rt else None
# horizon specific factors
k_band = {b: kappa([p['s'] for p in pairs if lo <= p['h'] <= hi]) for b, (lo, hi) in bands.items()}

res = dict(
    outcome=dict(reported=reported, derived={y: outcome[y] for y in derived}, ter_cso_ratio_mean=r_mean, ter_cso_ratio_sd=r_sd),
    editions=E_list, n_pairs=len(pairs), published_ranges=published,
    kappa_all=k_all, kappa_by_horizon=k_band,
    recalibrated_in_sample=evaluate(lambda p: k_all, pairs),
    leave_one_edition_out=dict(pooled=loeo_pooled, by_edition=loeo),
    real_time=realtime, n_real_time=len(rt),
    pairs=pairs)
json.dump(res, open(D('results/ireland_scoring.json'), 'w'), indent=1)

print(f"TER/CSO ratio {r_mean:.3f} sd {r_sd:.3f}; derived outcome years {sorted(derived)}")
print(f"{len(pairs)} edition-year pairs from {len(E_list)} editions")
for k, v in published.items(): print('published', k, {a: round(b, 3) for a, b in v.items()})
print('quantiles all', k_all, 'by horizon', k_band)
print('recalibrated in sample', res['recalibrated_in_sample'])
print('leave one edition out', loeo_pooled)
print('real time', len(rt), realtime)
for l in loeo: print('  ', l['edition'], [round(v,4) for v in l['kappa']], l['n'], round(l['coverage'], 2))

# ---------- edition block bootstrap (pairs from one edition, and years, are dependent) ----------
B = 2000; rngb = np.random.default_rng(7); boot = collections.defaultdict(list)
for _ in range(B):
    eds = rngb.choice(E_list, len(E_list), replace=True)
    sel = [p for e in eds for p in pairs if p['edition'] == e]
    boot['published_cov'].append(np.mean([p['inside'] for p in sel]))
    boot['published_is'].append(np.mean([p['is_rel'] for p in sel]))
    hsel = [p for e in eds for p in held if p['edition'] == e]
    ev = evaluate(lambda p: p['k'], hsel)
    boot['loeo_cov'].append(ev['coverage']); boot['loeo_is'].append(ev['is_rel'])
    boot['is_gain'].append(boot['published_is'][-1] - ev['is_rel'])
ci = {k: [float(np.quantile(v, 0.05)), float(np.quantile(v, 0.95))] for k, v in boot.items()}
ci['p_is_gain_le_0'] = float(np.mean(np.array(boot['is_gain']) <= 0))
res['bootstrap_90ci'] = ci
json.dump(res, open(D('results/ireland_scoring.json'), 'w'), indent=1)
print('bootstrap 90% CI', ci)

# ---------- naive benchmark: log drift on outcomes known at each edition's base year ----------
ys = sorted(outcome); bench = []
for p in pairs:
    b = base[p['edition']]; hist = [outcome[y] for y in ys if y <= b]
    if len(hist) < 2: continue
    g = (math.log(hist[-1]) - math.log(hist[0])) / (len(hist) - 1)
    f = hist[-1] * math.exp(g * (p['year'] - b))
    bench.append(dict(edition=p['edition'], year=p['year'], h=p['h'], eirgrid_ape=abs(p['err_pct']), drift_ape=abs(100 * (f / p['A'] - 1))))
res['benchmark_drift'] = dict(n=len(bench), mape_eirgrid=float(np.mean([b['eirgrid_ape'] for b in bench])),
                              mape_drift=float(np.mean([b['drift_ape'] for b in bench])),
                              share_eirgrid_better=float(np.mean([b['eirgrid_ape'] < b['drift_ape'] for b in bench])),
                              by_band={k: dict(n=len(s), eirgrid=float(np.mean([b['eirgrid_ape'] for b in s])), drift=float(np.mean([b['drift_ape'] for b in s])))
                                       for k, (lo, hi) in bands.items() for s in [[b for b in bench if lo <= b['h'] <= hi]] if s})
json.dump(res, open(D('results/ireland_scoring.json'), 'w'), indent=1)
print('benchmark', res['benchmark_drift'])
