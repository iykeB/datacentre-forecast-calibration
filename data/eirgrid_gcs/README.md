# EirGrid demand forecast vintages for Ireland (GCS 2015-2024 to AIRAA 2026-2035)

Built 11 Nov 2026. Each forecast is transcribed exactly as printed in the edition's appendix tables. Every value in `ter_vintages.csv` was then checked by script against the extracted text of the cited page. The garbled rows in GCS 2016, 2018 and 2019 were also checked against page images.

## Files

| File | Content |
|---|---|
| `ter_vintages.csv` | Ireland TER by edition, scenario and year (372 rows). Columns: `edition, scenario, year, ter_twh_ireland, source_table, page`, plus `printed_value, printed_unit, note`. |
| `dc_vintages.csv` | Data centre numbers (97 rows). Columns: `edition, scenario, year, quantity, unit, source_table, page`, plus `note`. |
| `*.pdf` / `*.txt` | Downloaded PDFs and the text extracted with `pdf2txt`. |

How the columns work:

- **`page`** is the 1-based PDF page index of the downloaded file (`pdf pN`), not the page number printed on the page. Printed page numbers are not used consistently across editions.
- **`ter_twh_ireland`**:
  - For the GCS 2015 and 2016 editions, the tables print TER in GWh. Those values are divided by 1000 here, and the printed GWh string is kept in `printed_value`.
  - For all other editions it is the printed TWh value. The `*` provisional marker is stripped and kept in `printed_value`.
- **`note`** flags the first row of each table. That row is a base or historical year, not a forecast.
- **`dc_vintages.csv`**:
  - `year` is left blank for quantities that the edition describes as "presently" or "at publication" without naming a year.
  - `quantity` keeps qualifiers such as "approximately" or "over" exactly as printed.

## Editions

| Edition | File | URL | Ireland TER tables | Basis of TER tables |
|---|---|---|---|---|
| GCS 2015-2024 | gcs2015.pdf | https://www.pleanala.ie/publicaccess/PCI/PCI1/PCI0001/03%20-%20EirGrid%20North%20South%20Interconnector%20Project%20Application%20File%20June%202015/AppPartOne/Volume%203B/4.%20Reference%20Material/3B_17)%20EirGrid%20and%20SONI%20(2015)%20All%20Island%20Generation%20Capacity%20Statement%202015-2024.pdf | A-1 / A-2 / A-3, GWh | "52-week year" |
| GCS 2016-2025 | gcs2016.pdf | https://cms.eirgrid.ie/sites/default/files/publications/Generation_Capacity_Statement_20162025_FINAL.pdf | A-1 / A-2 / A-3, GWh | "52-week year" |
| GCS 2017-2026 | gcs2017.pdf | https://cms.eirgrid.ie/sites/default/files/publications/4289_EirGrid_GenCapStatement_v9_web.pdf | A-1 / A-2 / A-3, TWh | Calendar year |
| GCS 2018-2027 | gcs2018.pdf (same file as ../pdf/a.pdf) | https://cms.eirgrid.ie/sites/default/files/publications/Generation_Capacity_Statement_2018.pdf | A-1 / A-2 / A-3, TWh | Calendar year, corrected to 366 days in leap years |
| GCS 2019-2028 | gcs2019.pdf (same file as ../pdf/b.pdf) | https://www.eirgrid.ie/site-files/library/EirGrid/EirGrid-Group-All-Island-Generation-Capacity-Statement-2019-2028.pdf | A-1 / A-2 / A-3, TWh | Calendar year, leap year corrected |
| GCS 2020-2029 | gcs2020.pdf (same file as ../pdf/c.pdf) | https://cms.eirgrid.ie/sites/default/files/publications/All-Island-Generation-Capacity-Statement-2020-2029.pdf | A-1 / A-2 / A-3, TWh | Calendar year, leap year corrected |
| GCS 2021-2030 | gcs2021.pdf | https://cms.eirgrid.ie/sites/default/files/publications/208281-All-Island-Generation-Capacity-Statement-LR13A.pdf | A-1 / A-2 / A-3, TWh | Calendar year, leap year corrected |
| GCS 2022-2031 (Part B of "Ireland Capacity Outlook 2022-2031", Oct 2022) | ico2022.pdf | https://cms.eirgrid.ie/sites/default/files/publications/EirGrid_SONI_Ireland_Capacity_Outlook_2022-2031.pdf | A1-1 / A1-2 / A1-3, TWh | Calendar year, leap year corrected |
| GCS 2023-2032 (Ten-Year GCS, Jan 2024) | gcs2023.pdf | https://cms.eirgrid.ie/sites/default/files/publications/19035-EirGrid-Generation-Capacity-Statement-Combined-2023-V5-Jan-2024.pdf | A1-1 / A1-2 / A1-3, TWh | Calendar year, leap year corrected |
| AIRAA 2025-2034 (Mar 2025; data freeze 30 Apr 2024) | airaa2025.pdf | https://cms.eirgrid.ie/sites/default/files/publications/AIRAA-2025-2034.pdf | A1.1 / A1.2 / A1.3, TWh | Calendar year, leap year corrected |
| AIRAA 2026-2035 (data freeze 30 Jun 2025) | airaa2026.pdf | https://cms.eirgrid.ie/sites/default/files/publications/AIRAA-2026-2035_Ireland.pdf | A2.1 / A2.2 / A2.3, TWh | Calendar year; historic values temperature corrected |

Notes on the edition list:

- **Supporting file.** Also downloaded but not transcribed: `airaa2025_inputs.pdf`, the AIRAA 2025-2034 Input Assumptions for Ireland, from https://cms.eirgrid.ie/sites/default/files/publications/AIRAA-2025-2034-Input-Assumptions-Ireland.pdf.
- **No 2024-2033 edition exists.** AIRAA 2025-2034 (pdf p31) says that it "supersedes ... Generation Capacity Statement 2023-2032, published in January 2024". It describes itself as the first edition of the All-Island Resource Adequacy Assessment, the successor to the GCS.
- **2015 copy.** The GCS 2015-2024 PDF comes from the An Bord Pleanála copy of the North South Interconnector application (Volume 3B reference material). An EirGrid hosted copy was not found, because the cms.eirgrid.ie landing page returned no PDF link.
- **Earliest edition.** GCS 2015-2024 is the first edition that mentions data centres, in one sentence: "over 200 MW of demand" (pdf p8). GCS 2016-2025 is the first that builds its demand scenarios on data centre build-out.
- **AIRAA 2026-2035.** This is beyond the requested range (through 2025-2034). It is included because it is the latest edition.

## Median TER forecasts for 2024 and 2025 by edition (TWh, Ireland, as printed)

| Edition | 2024 | 2025 |
|---|---|---|
| GCS 2015-2024 | 30.179 (30,179 GWh) | not in horizon |
| GCS 2016-2025 | 32.934 | 33.480 |
| GCS 2017-2026 | 33.4 | 33.7 |
| GCS 2018-2027 | 39.4 | 39.9 |
| GCS 2019-2028 | 37.4 | 38.0 |
| GCS 2020-2029 | 36.5 | 37.2 |
| GCS 2021-2030 | 35.8 | 36.4 |
| GCS 2022-2031 | 37.5 | 38.5 |
| GCS 2023-2032 | 36.5 | 38.0 |
| AIRAA 2025-2034 | 35.8 | 37.7 |
| AIRAA 2026-2035 | 35.2 (historic, temperature corrected) | 37.2 |

## Historical and base year TER printed in each edition (Ireland)

Only the appendix tables print historical TER as numbers. All other historical TER appears only as unlabelled chart lines, which were not digitised. The first row of each table is the base year:

| Edition | Base row | Status as printed |
|---|---|---|
| GCS 2015-2024 | 2014 = 26,648 GWh (Median, Low); the High table prints 26,774 | Estimate: real data to Oct 2014, rest estimated (Fig 2-1 caption). 52-week year. |
| GCS 2016-2025 | 2015 = 27,425 GWh | Estimate: real data to Oct 2015 (Fig 2-3 caption). 52-week year. |
| GCS 2017-2026 | 2015 = 27.6 TWh (historical, all scenarios); 2016 = 28.2 / 28.1 / 28.3 (Median / Low / High) | 2016 is part estimate (real data to Oct 2016) but differs by scenario. |
| GCS 2018-2027 | 2017 = 28.8 | Base year; status not stated. |
| GCS 2019-2028 | 2018 = 29.8 | Base year; the provisional asterisk is shown only on Northern Ireland peaks. |
| GCS 2020-2029 | 2019 = 30.5* | "*Figure is provisional". |
| GCS 2021-2030 | 2020 = 30.8 | Base year; the caption has a provisional footnote but the row has no asterisk in the extracted text. |
| GCS 2022-2031 | 2021 = 31.7 | Base year. |
| GCS 2023-2032 | 2022 = 33.3 (Median, Low), 33.4 (High) | Footnote: "2022 data for Ireland ... consists of some assumed data". |
| AIRAA 2025-2034 | 2023 = 34.0 | Base year. |
| AIRAA 2026-2035 | 2024 = 35.2 | "Historic values are corrected for temperature". |

## Caveats for scoring forecasts against outturn

1. **Definition of TER.** Every edition defines TER as sales grossed up for transmission and distribution losses, plus an estimate of self-consumption by self-generating sites (about 2-3% of TER). TER is not transmission demand and not CSO metered consumption. To score against CSO MEC02 data or EirGrid system demand, an adjustment for losses and self-consumption is needed.
2. **Year basis.**
   - The 2015 and 2016 editions print TER "for a 52-week year".
   - From 2017 the tables use calendar years. From 2018 they are explicitly corrected to 366 days in leap years.
   - AIRAA 2026-2035 temperature corrects its historic rows. Earlier editions do not say whether the base row is temperature corrected.
3. **Scope of the data centre category changes:**
   - 2016 and 2017: data centres only.
   - 2018: "large energy users" (mainly data centres).
   - 2019 and 2020: "data centres and large industrial users".
   - 2021: "data centres and new large energy users".
   - 2022 onwards: "data centres and new technology loads". Footnote 14 of the 2022 edition says these were previously called "new large energy users".
4. **Units and baselines of the data centre capacity numbers:**
   - Capacities are in MVA, except GCS 2021-2030 Table 2, which prints MW.
   - The additions are measured from different baselines:

     | Edition | Baseline |
     |---|---|
     | GCS 2019 | 400 MVA "currently built" |
     | GCS 2020 | 450 MVA "currently built" |
     | GCS 2021 | 520 MW "currently built" |
     | GCS 2022 | 600 MVA "assumed for 2022" |
     | GCS 2023 | 734 MVA "existing demand by end of 2022" |
     | AIRAA 2025-2034 | 867 MVA "2023 demand" |
     | AIRAA 2026-2035 | 959 MVA "2024 demand" |

   - These baselines are demand estimates. They differ from the much larger contracted capacity figures (1,000 to 2,400 MVA), which are recorded separately.
   - In GCS 2017 and 2018, the High scenario is printed as an increment on top of the Median.
5. **Inconsistent data centre shares within one edition:**
   - GCS 2021-2030: 23% (summary) versus 27% (Figure 10, which includes large energy users), both for 2030.
   - AIRAA 2025-2034: 31% (Part A) versus 29% (section 4.2.8), both for 2030.
   - AIRAA 2026-2035, Figure 4.8: the shares are of sector totals (36.52 TWh in 2026, 46.30 TWh in 2035). These totals are below the median TER in Table A2.1 (39.0 and 49.2), so they appear to exclude losses. Those two shares were read from the page image because they are not in the text layer.
6. **Printed inconsistencies, kept as printed and not corrected:**
   - GCS 2016-2025 Table A-2: Ireland Low plus Northern Ireland Low does not equal the printed all-island Low, for example 27,761 + 8,968 is not 36,873 in 2016. The Ireland column was checked against the page image.
   - GCS 2018-2027: the High 2018 value (29.0) is below the Median (29.5) and the Low (29.4).
7. **Garbled text extraction.** Three rows came out scrambled in the extracted text. They were transcribed from rendered page images:
   - GCS 2018 Median 2027 = 40.7
   - GCS 2019 Median 2028 = 40.2
   - GCS 2020 Median 2029 = 40.7 (from the text, which reads "2029 40.7 1.9%")
8. **Not extracted.** No numbers were estimated. These are left out:
   - Values that appear only in charts: historical TER series, data centre build-out curves, and the sector stacked bars, except the printed percentage labels listed above.
   - Data workbooks: the 2022 and later editions have separate Excel workbooks, which were not downloaded.
   - Values that were not printed.
