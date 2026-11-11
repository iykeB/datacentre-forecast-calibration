"""Netherlands and Great Britain: (1) official forecasters' stated baseline vs metered outturn,
(2) score the NESO FES scenario ranges that are already observable, in levels and in growth
(growth removes scope differences between NESO and DESNZ).
Output: results/external_checks.json"""
import csv, json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = lambda *p: os.path.join(R, *p)
gb = {int(x['year']): float(x['twh_or_gwh']) for x in csv.DictReader(open(D('data/gb/desnz_datacentres.csv')))}
nl = {}
for x in csv.DictReader(open(D('data/nl_cbs/cbs_datacentres.csv'))):
    if x['gwh']: nl[int(x['year'])] = float(x['gwh']) / 1000   # later releases overwrite earlier
fes = collections.defaultdict(dict)
for x in csv.DictReader(open(D('data/gb/neso_fes_datacentres.csv'))):
    s = (x['source_sheet'] + x['series']).lower()
    if not x['series'].startswith('total'): continue
    fes[(x['edition'], x['scenario'])][int(x['year'])] = float(x['twh'])
out = dict(gb_metered=gb, nl_metered=nl, baseline=[], fes_scores=[])
# (1) baselines stated by the forecaster for a year that is now metered
for (ed, sc), v in fes.items():
    for y in (2020, 2021, 2022, 2023):
        if y in v and y in gb and y < int(ed):
            out['baseline'].append(dict(country='GB', source=f'NESO FES {ed}', year=y, stated=v[y], metered=gb[y], ratio=v[y] / gb[y]))
for src, y, pj in [('PBL KEV 2021', 2020, 8), ('PBL KEV 2025', 2023, 17)]:
    out['baseline'].append(dict(country='NL', source=src, year=y, stated=pj / 3.6, metered=nl[y], ratio=pj / 3.6 / nl[y]))
seen = set(); bl = []
for b in out['baseline']:
    k = (b['source'], b['year'])
    if k not in seen: seen.add(k); bl.append(b)
out['baseline'] = bl
# (2) FES ranges for years after publication that DESNZ now meters (2023, 2024)
for ed in ('2022', '2023', '2024'):
    scen = {sc: v for (e, sc), v in fes.items() if e == ed}
    b = int(ed) - 1
    for y in (2023, 2024):
        if y < int(ed): continue
        vals = [v[y] for v in scen.values() if y in v]
        if not vals: continue
        lv = dict(lo=min(vals), hi=max(vals), inside=min(vals) <= gb[y] <= max(vals))
        base_f = {sc: v.get(b) for sc, v in scen.items()}
        g = [v[y] / base_f[sc] for sc, v in scen.items() if y in v and base_f.get(sc)]
        gm = gb[y] / gb[b] if b in gb else None
        out['fes_scores'].append(dict(edition=ed, year=y, h=y - b, metered=gb[y], level=lv,
                                      growth=dict(lo=min(g), hi=max(g), metered=gm, inside=(min(g) <= gm <= max(g)) if gm else None) if g else None))
json.dump(out, open(D('results/external_checks.json'), 'w'), indent=1)
for b in out['baseline']: print('baseline', b['source'], b['year'], 'stated %.2f metered %.2f ratio %.2f' % (b['stated'], b['metered'], b['ratio']))
for s in out['fes_scores']: print('FES', s['edition'], s['year'], 'h', s['h'], 'metered %.2f' % s['metered'], 'level %.2f-%.2f in=%s' % (s['level']['lo'], s['level']['hi'], s['level']['inside']), 'growth', s['growth'] and ('%.3f-%.3f vs %.3f in=%s' % (s['growth']['lo'], s['growth']['hi'], s['growth']['metered'], s['growth']['inside'])))
