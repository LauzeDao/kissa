#!/usr/bin/env bash
# Schnelle Prüfungen vor dem Image-Build: Shell-Syntax, TOML, JSON(C), Desktop-Dateien.
# Läuft in der Pipeline vor "podman build" und lokal mit: bash tools/check.sh
set -euo pipefail
cd "$(dirname "$0")/.."
fail=0

for f in build_files/build.sh system_files/usr/bin/kissa system_files/usr/bin/pandasay system_files/usr/share/kissa/bashrc-kissa.sh; do
  if bash -n "$f"; then echo "ok   bash  $f"; else echo "FAIL bash  $f"; fail=1; fi
done

while IFS= read -r f; do
  if python3 -c 'import sys,tomllib; tomllib.load(open(sys.argv[1],"rb"))' "$f"; then echo "ok   toml  $f"; else echo "FAIL toml  $f"; fail=1; fi
done < <(find system_files -name '*.toml')

while IFS= read -r f; do
  # JSONC: Zeilen-Kommentare entfernen, dann als JSON prüfen
  if python3 -c 'import sys,json,re; json.loads(re.sub(r"(?m)^\s*//.*$","",open(sys.argv[1],encoding="utf-8").read()))' "$f"; then
    echo "ok   json  $f"; else echo "FAIL json  $f"; fail=1; fi
done < <(find system_files -name '*.json' -o -name '*.jsonc')

# Plasma-Layout-Skripte (JavaScript) – nur Syntax, wenn node vorhanden ist
if command -v node >/dev/null; then
  while IFS= read -r f; do
    if node --check "$f" 2>/dev/null; then echo "ok   js    $f"; else echo "FAIL js    $f"; fail=1; fi
  done < <(find system_files -name '*.js')
fi

exit $fail
