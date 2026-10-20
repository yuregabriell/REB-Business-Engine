#!/usr/bin/env bash
set -euo pipefail
export REB_DB_PATH="$(mktemp -d)/demo.sqlite3"
reb doctor
reb init "Lavandaria à porta" "Recolher, lavar e entregar roupa" --budget 300 --market Portugal
reb projects
reb finance --price 25 --variable 12 --fixed 200 --units 30 --cac 3
