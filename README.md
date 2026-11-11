# Data centre electricity outlooks against metered outcomes: Ireland, the Netherlands and Great Britain

This dataset accompanies the paper "Calibrating Data Centre Electricity Demand Outlooks Against Metered
Outcomes: A Decade of Grid Operator Forecasts and the Waste Heat Exergy Bound" (B.I. Simeon).

It is, to our knowledge, the first machine readable collection of every Irish grid operator demand outlook
edition from 2015 to 2026, each value traced to its source table and page, together with the metered
outcomes needed to score them.

## Contents
| Path | What it holds |
|---|---|
| `data/eirgrid_gcs/ter_vintages.csv` | Total electricity requirement of Ireland, Low/Median/High, by edition and target year (11 editions: GCS 2015-2024 to AIRAA 2026-2035); source table, PDF page, printed value and unit |
| `data/eirgrid_gcs/dc_vintages.csv` | Data centre and large energy user quantities stated in each edition (MVA, MW, share of TER) |
| `data/cso/mec02.csv` | CSO table MEC02: metered electricity of data centres and other customers, quarterly 2015Q1 to 2025Q4 |
| `data/nl_cbs/` | CBS data centre electricity, four releases (2017 to 2024); national consumption; Dutch forecasts (PBL KEV, Netbeheer Nederland, TenneT) |
| `data/gb/` | DESNZ metered data centre electricity 2020 to 2024; NESO FES data centre demand, editions 2022 to 2025 |
| `code/` | Analysis: scoring, conformal recalibration, external checks, calibrated outlook, national energy and exergy analysis (parameter sources in the header of outlook_and_exergy_ireland.py), figures |
| `results/` | JSON results quoted in the paper |

Each `data/*/README.md` lists source URLs, definitions and caveats (for example the change of the data
centre category between EirGrid editions, and calendar versus 52 week years in 2015 and 2016).

## Reproduce
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PY=.venv/bin/python ./run_all.sh
```
Python 3.12; NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2. All random draws use fixed seeds; results are
identical across runs.

## Licence and sources
Code: MIT. Compiled tables and documentation: CC BY 4.0. The underlying statistics remain the property of
their publishers (CSO, CBS, DESNZ, NESO, EirGrid and SONI, PBL, Netbeheer Nederland, TenneT) and are reused
under each publisher's open data or reuse terms, which users should check before redistribution.
Source reports are not redistributed; their URLs are in the READMEs.

## Cite
Please cite both the paper and this dataset (see CITATION.cff).
