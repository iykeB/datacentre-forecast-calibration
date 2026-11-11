# Netherlands: data centre electricity, outturn (CBS) and official outlooks

Retrieved 11 November 2026 with curl (TenneT pages through Chrome, since tennet.eu returns 403 to curl; the TenneT files themselves came by curl from TenneT's S3 host). Raw downloads are in `raw/` and `raw/forecasts/`.

## 1. `cbs_datacentres.csv` (metered outturn, every vintage)

Columns: release, year, gwh, total_gwh, share_pct, status, url.

Source: CBS maatwerk tables "Elektriciteit geleverd aan datacenters" (Statistics Netherlands, custom tables).

| release | maatwerk page | xlsx |
|---|---|---|
| 2020-12-14 | /nl-nl/maatwerk/2020/51/elektriciteit-geleverd-aan-datacenters-2017-2019 | publicatietabel_datacenters_elektriciteitsleveringen_2017_2019.xlsx |
| 2021-12-15 | /nl-nl/maatwerk/2021/50/elektriciteit-geleverd-aan-datacenters-2017-2020 | datacenters-elektriciteitsleveringen-2017-2020.xlsx |
| 2022-12-08 | /nl-nl/maatwerk/2022/49/elektriciteit-geleverd-aan-datacenters-2017-2021 | datacenters_elektriciteitsleveringen_2017_2021.xlsx |
| 2025-12-15 | /nl-nl/maatwerk/2025/51/elektriciteit-geleverd-aan-datacenters-2017-2024 | datacenters_elektriciteitsleveringen_2017_2024.xlsx |

The English news release (cbs.nl/en-gb/news/2025/51/...) gives the same figures as the 2025 table (5,100 GWh, 4.6 percent in 2024).

**No 2023 or 2024 edition exists.** I probed every week of 2023, 2024 and 2026 for the obvious URL pattern and found nothing. The 2025 table's notes say the 2020 publication was updated in 2022 and that the 2025 table updates that. No 2017 to 2025 edition has appeared yet. Going by the earlier pattern, one would be due in December 2026.

**Definition.** These are metered numbers: annual kWh delivered through the public grid to connections whose main activity is a data centre. The data come from the customer registers of TenneT, the regional DSOs and private networks. Connections were identified by operator name and other searches, and in 2025 also from the RVO energy efficiency reporting list (IT load of 500 kW or more). Data centres inside universities, hospitals and other organisations are excluded. Behind the meter generation is excluded, so net use can be understated.

**Status.** In each table the latest year is marked * (provisional). The other years carry no mark, and I record them as "final". CBS does not use the word "final" for them.

**Revisions.** 2017 went 1647, then 1648, then 1652 GWh. 2019 went 2740, then 2742, then 2747. 2020 went 3178 (provisional), then 3184. The 2021 value of 3730 did not change between the 2022 and 2025 editions. The 2020 edition split connections at 7.5 GWh. Later editions split at 10 GWh.

**share_pct** is the share CBS published in that release. Its denominator is total net national electricity consumption from the Elektriciteitsbalans as it stood when that release was made (8 Dec 2021, 31 Oct 2022 and 25 Nov 2025 vintages). The 2020 release gave no share of national consumption, only "2.7 percent of electricity delivered via the public grid" in 2019, so share_pct is blank for the 2020 release.

**total_gwh** is *not* vintage matched. It is CBS StatLine 84575NED "Netto verbruik (berekend)", table modified 30 Oct 2026, fetched by OData on 11 Nov 2026. It is also saved as `cbs_total_net_consumption_statline_84575NED.csv`, where 2024 and 2025 are "nader voorlopig". Historical vintages of the denominator were not recovered. Recomputing gwh/total_gwh therefore differs slightly from the published share_pct for older releases. For example, 2020 in the 2021 release is 2.85 percent published, while 3178/112434 gives 2.83 percent.

## 2. `nl_forecasts_datacentres.csv` (projections by edition)

Columns: edition, scenario, year, twh, source, url, plus original_value, original_unit and scope_note. PBL values are reported in PJ, and twh = PJ/3.6 (unit conversion only). Every value is copied from text, a table or a chart data label. Nothing was read off chart geometry or interpolated.

### PBL Klimaat- en Energieverkenning (KEV)
- KEV 2019, 2020, 2022, 2023: **no data centre number**. These editions only mention data centres qualitatively, within services floor area. The 2019 to 2025 tabellenbijlagen (ODS) contain no data centre rows, and nor do the 2024, 2025 and 2026 figure-data zips. The 2026 tabellenbijlage mentions data centres only in a footnote.
- KEV 2021: 8 PJ (2020), 12 PJ (2030).
- KEV 2024: 29 [22 to 39] PJ in 2030. The KEV 2024 text itself states no number. The value is quoted retrospectively in KEV 2025 (pdf p.65).
- KEV 2025: 17 PJ (2023, stated), 54 [36 to 87] PJ in 2030.
- KEV 2026: 21 PJ (2025), 56 [29 to 70] PJ in 2030.
- Scope: final electricity use of data centres within the services sector. The bracket is the KEV uncertainty range.

### Netbeheer Nederland (II3050 and successor scenarios), all in TWh
- II3050 edition 1 (Apr 2021): only an assumption of 1.8 GW and 16 TWh common to the 2050 scenarios, plus a sensitivity of 9 GW and 79 TWh in 2050. There is no year by year series. The year 2050 comes from the surrounding text.
- Scenario's investeringsplannen 2024 (20 Feb 2023): KA, ND and IA for 2025, 2030 and 2035 (Figure 12).
- II3050 edition 2 scenarios (30 Jun 2023): KA, ND and IA for 2030; DEC, NAT, EUR and INT for 2040 and 2050 (Figure 6).
- Scenario's editie 2025 (13 May 2025, errata Nov 2025): KM, EV, GB and HA for 2030, 2035, 2040 and 2050, plus reference 2019 and 2023 and KM 2025 (Figure 4.4.1, rounded integer labels).
- Verkenning Vertraagde Transitie (17 Apr 2026): VT for 2030, 2035, 2040 and 2050 from the text table. The chart labels on p.31 conflict slightly (20.0 vs 21 TWh in 2030), and their bar order is ambiguous in the extracted text, so the chart labels were not used.
- Scope: "Datacenters & ICT" (the data sector, including telecom and other ICT). This is wider than the CBS data centre definition. Their own 2019 reference is 4 TWh, made up of about 2.7 TWh data centres and 1.3 TWh other ICT per IP2024 footnote 21.
- Not found: a machine readable national scenario workbook. The editie 2025 regional dataset zip was not downloaded.

### TenneT
- Monitor Leveringszekerheid 2025 (Table B2-1): 2023 reference, then 2030, 2033 and 2035 by scenario.
- Monitor Voorzieningszekerheid 2026 dataset (`Scenario - Demand - Overview yearly.csv`): 2025 reference, then 2028, 2030, 2033 and 2035, high and low demand. As published, each year's low demand value equals the high demand value of the previous target year. This is flagged, not corrected.
- Monitor Leveringszekerheid 2024: data centres appear only in a chart (Figure B2-4), with no number in the text, so nothing was recorded. Earlier monitors were not checked.

## Caveats for the calibration paper
- CBS outturn (grid delivered, main activity data centres) and the Netbeheer "Datacenters & ICT" series differ in scope. They are not like for like.
- KEV and TenneT were not checked for whether they use the same boundary as CBS.
- Forecast "years" are scenario target years. The 2019 and 2023 values in the forecast documents are the documents' own reference values, not CBS vintages.
