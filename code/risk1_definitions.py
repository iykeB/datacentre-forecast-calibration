"""Risk 1: reconcile EirGrid TER and data centre MVA with CSO metered data."""
import csv, collections
r=[x for x in csv.DictReader(open('data/cso/mec02.csv',encoding='utf-8-sig'))]
A=collections.defaultdict(lambda: collections.defaultdict(float))
for x in r: A[x['Electricity Consumption']][int(x['Quarter'][:4])]+=float(x['VALUE'])/1000
dc,tot=A['Data centres'],A['All metered electricity consumption']; oth=A['Customers other than data centres']
# TER as reported later (first row of each edition, outcome estimate)
TER={2014:26.648,2015:27.6,2017:28.8,2018:29.8,2019:30.5,2020:30.8,2021:31.7,2022:33.3,2023:34.0,2024:35.2}
print('year  CSO_total  TER  TER/CSO  CSO_dc  CSO_other  dc_share')
for y in range(2015,2026):
    t=TER.get(y); print(y, f'{tot[y]:6.2f}', f'{t:5.1f}' if t else '  -  ', f'{t/tot[y]:.3f}' if t else '  -  ', f'{dc[y]:5.2f}', f'{oth[y]:6.2f}', f'{100*dc[y]/tot[y]:4.1f}%')
print('\nGrowth decomposition of CSO metered total since each base year (share of total growth due to data centres):')
for b in (2015,2017,2018,2019,2020,2021,2022):
    dT=tot[2024]-tot[b]; dD=dc[2024]-dc[b]; print(b,'->2024: total +%.2f TWh, data centres +%.2f TWh (%.0f%%)'%(dT,dD,100*dD/dT))
print('\nEirGrid stated data centre (+NTL) demand, MVA x 8.76 h/1000 at load factor 1, vs CSO metered:')
for lab,y,mva in [('GCS22 assumed',2022,600),('GCS23 end 2022',2022,734),('AIRAA25',2023,867),('AIRAA26',2024,959)]:
    e=mva*8.76/1000; print(f'{lab:15s} {y}: {mva} MVA -> {e:.2f} TWh vs CSO {dc[y]:.2f} TWh (ratio {e/dc[y]:.2f})')
