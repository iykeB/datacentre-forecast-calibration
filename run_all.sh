#!/bin/sh
# Reproduce every result, figure and the manuscript from the raw data in data/.
# Requires Python 3.12 with requirements.txt; tectonic for the PDF (optional).
set -e
cd "$(dirname "$0")"
PY=${PY:-python3}
$PY code/risk1_definitions.py > results/risk1_definitions.txt
$PY code/score_and_calibrate_ireland.py
$PY code/external_checks_nl_gb.py
$PY code/outlook_and_exergy_ireland.py
$PY code/make_figures.py
echo "done: results/, figures/, manuscript/manuscript.pdf"
