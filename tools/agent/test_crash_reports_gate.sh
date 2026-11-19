#!/bin/zsh
# s7664: tools/crash_reports.py rc contract as stop_gate.sh uses it (1 = NEW report, 0 = all PLANT/DIAG/FOLDED).
cd "$(dirname "$0")/../.." || exit 2
fail=0
python3 tools/crash_reports.py --selftest >/dev/null || { echo "FAIL selftest"; fail=1; }
D=$(mktemp -d)
mk() { python3 - "$D/$1" "$2" "$3" <<'PY'
import json,sys
p,tn,syms=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
b={'exception':{'type':'EXC_BAD_ACCESS','signal':'SIGSEGV'},'faultingThread':0,'usedImages':[{'name':'RogueSquadron64Recomp'}],
   'threads':[{'name':tn,'frames':[{'symbol':s,'imageIndex':0} for s in syms]}]}
open(p,'w').write('{}\n'+json.dumps(b))
PY
}
mk RogueSquadron64Recomp-2026-11-20-000001.ips 'SP Task Thread' 'rs64_s7523_status_read,factor5_ucode_b'
python3 tools/crash_reports.py --since 2026-11-13 --dir "$D" --ledger /dev/null >/dev/null; rc=$?
[ $rc = 0 ] || { echo "FAIL diag-only dir rc=$rc (want 0)"; fail=1; }
mk RogueSquadron64Recomp-2026-11-20-000002.ips 'Gfx Thread' 'initVec4TripletFromArgs,cinematicSplineWalkerNpcHandler'
python3 tools/crash_reports.py --since 2026-11-13 --dir "$D" --ledger /dev/null >/dev/null; rc=$?
[ $rc = 1 ] || { echo "FAIL new report rc=$rc (want 1)"; fail=1; }
L=$(mktemp); echo "folded RogueSquadron64Recomp-2026-11-20-000002 (test arm)" > "$L"
python3 tools/crash_reports.py --since 2026-11-13 --dir "$D" --ledger "$L" >/dev/null; rc=$?
[ $rc = 0 ] || { echo "FAIL folded rc=$rc (want 0)"; fail=1; }
python3 tools/crash_reports.py --since 2026-11-21 --dir "$D" --ledger /dev/null >/dev/null; rc=$?
[ $rc = 0 ] || { echo "FAIL --since rc=$rc (want 0)"; fail=1; }
rm -rf "$D" "$L"
[ $fail = 0 ] && echo "test_crash_reports_gate: PASS 5/5" || { echo "test_crash_reports_gate: FAIL"; exit 1; }
