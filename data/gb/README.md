# Great Britain: data centre electricity, outturn (DESNZ) and NESO FES projections

Retrieved 11 November 2026 with curl, using the GOV.UK content API, the NESO data portal CKAN API and NESO document downloads. Raw files are in `raw/` and `raw/neso/`.

## 1. `desnz_datacentres.csv` (outturn)

Columns: year, twh_or_gwh, unit, method_note, url, plus share_of_gb_grid_consumption_pct and n_datacentres_operational.

Source: DESNZ, Energy Trends June 2026 special feature article, "Data centre electricity consumption in Great Britain, 2020 to 2024", published 30 June 2026. These are Official Statistics in Development.
- Article PDF: https://assets.publishing.service.gov.uk/media/6a3e9f25da47783d87723bf2/Data_centre_electricity_consumption_in_Great_Britain__2020_to_2024.pdf
- Data tables (xlsx): https://assets.publishing.service.gov.uk/media/6a3e9f32eaee00074150f678/Data_centre_electricity_consumption_in_Great_Britain__2020_to_2024.xlsx. An ODS version also exists; it was not downloaded.
- Values come from Table 2 (GB row, TWh at full workbook precision), Table 3 (share, multiplied by 100 here) and Table 1 (count).

**Definition.** These are metered numbers. Meter level grid consumption (the same data as the DESNZ subnational electricity statistics) was matched *manually* to a list of identified data centres. The list started from a DSIT dataset and was extended from operator and industry websites. There are 242 matched data centres; 259 were identified and 17 could not be matched. In the PDF text extraction these counts appear as 2423 and 2594 because footnote markers 3 and 4 run into the numbers.

**Scope.** Colocation, managed hosting and hyperscale data centres. Enterprise (in house) data centres are excluded. Grid consumption only. Great Britain only, so Northern Ireland is excluded.

**Caveats** (from the article):
- Possible undercount of small sites, and of the 17 unmatched sites.
- Possible overcount where offices share a building.
- NESO FES 2025 (page 110) quotes 7.6 TWh for 2023 from capacity and utilisation assumptions, against 4.1 TWh metered here.
- ND-NEED gives 2.6 TWh for England and Wales in 2023, against 4.1 TWh here.
- DESNZ plans an update in 2027 that adds 2025.
- In DUKES, data centres sit inside "Post and telecommunications" (table 5.2).
- The 2024 GB grid total quoted in the article is 249.2 TWh.

## 2. `neso_fes_datacentres.csv` (FES projections by edition)

Columns: edition, scenario, year, twh, source_sheet, url, plus series and year_basis.

Workbooks: FES Data Workbooks from https://www.neso.energy/publications/future-energy-scenarios-fes/fes-documents:
- 2020: document/173806
- 2021: document/199971
- 2022: document/263876
- 2023: document/283061
- 2024: document/321051
- 2025: document/364551

The ED1 CSVs from the NESO data portal (2023, 2024, 2025) were also saved and agree with the workbooks.

**By edition:**
- **FES 2020 and FES 2021: data centres are not separated.** I searched every sheet and shared string for "data centre"/"datacentre"/"hyperscale"/"server" and found nothing. Data centre demand is inside commercial demand, so these editions have no rows.
- **FES 2022:** ED1 has two rows, "GB Customer Demand: Commercial Data Centres - Direct Transmission Customers" and "... - Distribution System Customers". Both are recorded. NESO publishes no total for 2022. The row labelled "computed sum of ED1 components" is plain addition of the two rows, done here. Chart EC.C.07 is *net additional* demand (dedicated capacity growth minus displaced on premises computing). NESO says it does not match the ED1 totals. It is included as a separate series and should not be compared with outturn.
- **FES 2023 and FES 2024:** the same two ED1 rows, plus a NESO total in charts EC.M (2023) and EC.P (2024), "Total electricity demand for data centres". That total equals the sum of the two ED1 rows (checked: 754 + 2846 = 3600 for 2020 in FES 2023, and 1215 + 3785 = 5000 for 2023 in FES 2024).
- **FES 2025:** a single ED1 row, "Data Centre Demand", and chart F.47. Both are recorded, and they agree.
- The FES 2023 data centre trajectories from 2024 onwards are identical to FES 2022's (for example Consumer Transformation is 5.76 TWh in 2024 in both). Only the history (2020 to 2023) changed.
- Scenarios by edition:
  - 2022 and 2023: Consumer Transformation, System Transformation, Leading the Way, Falling Short, plus a Five Year Forecast.
  - 2024: Holistic Transition, Electric Engagement, Hydrogen Evolution, Counterfactual, plus a Five Year Forecast.
  - 2025: Holistic Transition, Electric Engagement, Hydrogen Evolution, Falling Behind, plus a Ten Year Forecast.

**Year basis caveat.** ED1 labels its rows "Annual [Fiscal]" with year headers. In 2022 to 2024 these are Excel dates of 1 January. The chart sheets label the same numbers by calendar year (the chart value for year Y equals the ED1 value for year Y). So it is unclear whether year Y is calendar Y or fiscal Y/Y+1. The year is recorded as labelled.

**Scope caveat.** The early years in each FES edition are NESO's own estimates, not metered outturn. For example FES 2025 gives 7.4 TWh for 2023, against 4.13 TWh metered by DESNZ, so FES history and DESNZ outturn differ substantially.

Not downloaded: the FES 2025 main report PDF, so NESO's page 110 figure of 7.6 TWh for 2023 is as quoted by DESNZ and was not verified.
