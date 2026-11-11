"""Calibrated outlook for Ireland from the latest EirGrid edition (AIRAA 2026-2035), the data
centre component, and a national energy and exergy analysis of the data centre sector with
propagated uncertainty (demand and thermodynamic parameters).

Inputs: results/ireland_scoring.json, data/eirgrid_gcs/ter_vintages.csv, data/cso/mec02.csv
Output: results/ireland_outlook_exergy.json

Parameter sources (verified, see papers/thermo_inputs/ and the manuscript):
  PUE 2025: uniform 1.18 (Ireland, EC COM(2026) 500, Fig. 2) to 1.36 (EU average 2024, same report)
  PUE decline: uniform 0 to 0.01 per year (LBNL 2024: US 1.4 in 2023 to 1.15-1.35 by 2028), floor 1.10
               (Masanet et al. 2020, practical minimum)
  UPS efficiency: uniform 0.90 to 0.99 (LBNL 2024 Table 4.3, hyperscale); PDU loss 3% of input
               (Dayarathna et al. 2016)
  Chip temperature T_j: uniform 70 to 85 C (Ebrahimi et al. 2014: 85 C limit; ASHRAE 2021: cases 80-90 C)
  Air return T_air: uniform 30 to 40 C (Ebrahimi et al. 2014); liquid T_liq: uniform 45 to 60 C
               (ASHRAE W45 class, LBNL Table 4.3; Ebrahimi Table 8)
  Liquid cooled share in 2025: uniform 0.05 to 0.15 (Uptime 2024 cooling survey: DLC on few racks);
               growth 0.02 to 0.06 per year, cap 0.8 (our assumption)
  Capture fraction f_cap: uniform 0.6 to 0.9 (our assumption)
  Dead state T0: uniform 8.7 to 10.7 C about the Dublin Airport 1991-2020 mean of 9.7 C (Met Eireann)
  Best practice reference for avoidable destruction: PUE 1.10, heat supply 60 C
"""
import csv, json, collections, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
rng = np.random.default_rng(20261111)
N = 20000
K = 273.15
S = json.load(open(D('results/ireland_scoring.json')))
scores = np.array([p['s'] for p in S['pairs']])  # signed horizon scaled log errors

ED, BASE = 'AIRAA 2026-2035', 2024
M = {}; L = {}; H = {}
for x in csv.DictReader(open(D('data/eirgrid_gcs/ter_vintages.csv'))):
    if x['edition'].startswith(ED) and x['note'] == 'forecast' and x['ter_twh_ireland']:
        sc = x['scenario'].split()[0].lower(); y = int(x['year']); v = float(x['ter_twh_ireland'])
        {'median': M, 'low': L, 'high': H}[sc][y] = v
years = sorted(M)

cso = collections.defaultdict(lambda: collections.defaultdict(float))
for x in csv.DictReader(open(D('data/cso/mec02.csv'), encoding='utf-8-sig')):
    cso[x['Electricity Consumption']][int(x['Quarter'][:4])] += float(x['VALUE']) / 1000
oth = np.array([cso['Customers other than data centres'][y] for y in range(2015, 2026)])
d = np.diff(np.log(oth)); mu, sd = d.mean(), d.std(ddof=1)
ratio = np.clip(rng.normal(S['outcome']['ter_cso_ratio_mean'], S['outcome']['ter_cso_ratio_sd'], N), 1.0, None)

# thermodynamic parameters, one draw per sample path (held fixed across years along a path)
P = dict(
    pue0=rng.uniform(1.18, 1.36, N), dpue=rng.uniform(0.0, 0.01, N),
    eta_ups=rng.uniform(0.90, 0.99, N),
    Tj=rng.uniform(70, 85, N) + K, Tair=rng.uniform(30, 40, N) + K, Tliq=rng.uniform(45, 60, N) + K,
    phi0=rng.uniform(0.05, 0.15, N), beta=rng.uniform(0.02, 0.06, N),
    fcap=rng.uniform(0.6, 0.9, N), T0=rng.uniform(8.7, 10.7, N) + K)
PDU, PUE_BEST, TS_BEST = 0.03, 1.10, 60 + K


def q(a):
    return [float(v) for v in np.quantile(a, [0.05, 0.5, 0.95])]


def first_order(y, x, bins=20):
    """Correlation ratio Var(E[y|x]) / Var(y) with equal frequency bins of x."""
    edges = np.quantile(x, np.linspace(0, 1, bins + 1)); idx = np.clip(np.searchsorted(edges, x, side='right') - 1, 0, bins - 1)
    means = np.array([y[idx == b].mean() for b in range(bins)]); w = np.array([(idx == b).mean() for b in range(bins)])
    return float(np.sum(w * (means - y.mean()) ** 2) / y.var())


out = {}
for y in years:
    h = y - BASE
    ter = M[y] * np.exp(rng.choice(scores, N) * math.sqrt(h))
    other = oth[-1] * np.exp(mu * (y - 2025) + sd * math.sqrt(max(y - 2025, 0)) * rng.standard_normal(N))
    E = np.maximum(ter / ratio - other, 0)                                   # facility electricity, TWh
    # ---- energy analysis
    pue = np.maximum(P['pue0'] - P['dpue'] * max(y - 2025, 0), PUE_BEST)
    E_it = E / pue
    E_pc = E_it * (1 / (P['eta_ups'] * (1 - PDU)) - 1)                       # UPS and PDU losses
    E_pc = np.minimum(E_pc, E - E_it)
    E_cool = E - E_it - E_pc                                                # cooling and other infrastructure
    phi = np.clip(P['phi0'] + P['beta'] * max(y - 2025, 0), 0, 0.8)
    Ts = phi * P['Tliq'] + (1 - phi) * P['Tair']
    Q_rec = P['fcap'] * E_it                                                # recoverable heat, TWh
    dE_best = E_it * (pue - PUE_BEST)                                       # energy saving at best practice PUE
    # ---- exergy analysis (electricity is pure exergy; dead state T0)
    T0 = P['T0']
    D_pc, D_cool = E_pc, E_cool                                             # dissipated near ambient
    D_it = E_it * T0 / P['Tj']                                              # electricity to heat at chip temperature
    D_ht = E_it * T0 * (1 / Ts - 1 / P['Tj'])                               # chip to coolant heat transfer
    Ex_rej = E_it * (1 - T0 / Ts)                                           # exergy of heat in the coolant
    Ex_rec = P['fcap'] * Ex_rej                                             # recoverable heat exergy
    D_total = D_pc + D_cool + D_it + D_ht
    assert np.allclose(D_total + Ex_rej, E)                                 # exergy balance closes
    # avoidable destruction relative to best practice (PUE 1.10, heat supply 60 C)
    D_av_inf = E_it * (pue - PUE_BEST)
    D_av_ht = E_it * T0 * np.maximum(1 / Ts - 1 / TS_BEST, 0)
    D_av = D_av_inf + D_av_ht
    psi = Ex_rec / np.maximum(E, 1e-9)                                      # heat recovery exergy ratio
    o = dict(h=h, published=dict(low=L.get(y), median=M[y], high=H.get(y)),
             ter_calibrated=q(ter), dc_metered=q(E), pue=q(pue), E_it=q(E_it), E_pc=q(E_pc), E_cool=q(E_cool),
             heat_rejected=q(E), heat_recoverable=q(Q_rec), dE_best=q(dE_best),
             Ts_C=q(Ts - K), carnot=q(1 - T0 / Ts), Ex_in=q(E), D_pc=q(D_pc), D_cool=q(D_cool), D_it=q(D_it),
             D_ht=q(D_ht), Ex_rej=q(Ex_rej), Ex_rec=q(Ex_rec), D_total=q(D_total), D_avoidable=q(D_av),
             D_av_inf=q(D_av_inf), D_av_ht=q(D_av_ht),
             share=dict(D_pc=q(D_pc / E), D_cool=q(D_cool / E), D_it=q(D_it / E), D_ht=q(D_ht / E),
                        Ex_rej=q(Ex_rej / E), D_av=q(D_av / E)),
             psi=q(psi))
    if y in (2030, 2035):
        inputs = dict(demand=E, pue=pue, T_supply=Ts, f_cap=P['fcap'], T0=T0, T_chip=P['Tj'])
        o['sobol_first_Ex_rec'] = {k: first_order(Ex_rec, v) for k, v in inputs.items()}
        o['sobol_first_D_av'] = {k: first_order(D_av, v) for k, v in inputs.items()}
    out[y] = o
json.dump(dict(edition=ED, base=BASE, N=N, years=out), open(D('results/ireland_outlook_exergy.json'), 'w'), indent=1)
f = lambda v, n=1: f'{v[1]:.{n}f} [{v[0]:.{n}f}, {v[2]:.{n}f}]'
for y in (2025, 2030, 2035):
    o = out[y]
    print(y, 'E', f(o['dc_metered']), 'IT', f(o['E_it']), 'pc', f(o['E_pc'], 2), 'cool', f(o['E_cool'], 2), 'PUE', f(o['pue'], 3))
    print('    Ex: D_it', f(o['D_it']), 'D_ht', f(o['D_ht'], 2), 'D_inf', f(o['D_pc'], 2), '+', f(o['D_cool'], 2), 'Ex_rej', f(o['Ex_rej'], 2), 'Ex_rec', f(o['Ex_rec'], 2), 'psi', f(o['psi'], 3))
    print('    shares', {k: round(v[1], 3) for k, v in o['share'].items()}, 'D_av', f(o['D_avoidable'], 2), 'dE_best', f(o['dE_best'], 2))
    if 'sobol_first_Ex_rec' in o: print('    S1 Ex_rec', {k: round(v, 2) for k, v in o['sobol_first_Ex_rec'].items()}, '\n    S1 D_av', {k: round(v, 2) for k, v in o['sobol_first_D_av'].items()})
