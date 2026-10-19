#!/usr/bin/env python3
"""Generate lldb-wrapped multi-boot plume soak recipes (s5589) from the s5587 hold recipe."""
import sys, pathlib
root = pathlib.Path(__file__).resolve().parents[2]
src = root / "scratch/agent/soak_queue/done/s5587_plume_hold_d_20261019-150224.sh"
for tag in sys.argv[1:]:
    t = src.read_text()
    t = t.replace("s5587_plume_hold_d", f"s5589_plume_lldb_{tag}").replace("N=1", "N=3")
    t = t.replace('./RogueSquadron64Recomp) > "$G"',
                  '/usr/bin/lldb -b -o "process handle SIGSEGV -s true -n true -p true" -o "process handle SIGBUS -s true" -o run -o "bt all" -o "register read" -o quit -- ./RogueSquadron64Recomp) > "$G"')
    head, tail = t.split("for i in $(seq 1 40); do\n      grep -aqiE")
    t = head + "for i in $(seq 1 5); do\n      grep -aqiE" + tail
    t = t.replace("ALIVE_AT_+120", "ALIVE_AT_+15")
    t = t.replace("s5584: LLE-trio title boots HELD 120 s", "s5589: 3 LLE-trio title boots under lldb, held 15 s")
    t = t.replace("pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true\nbad",
                  "pkill -KILL -x lldb >/dev/null 2>&1; pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true\nbad")
    t = t.replace('kill -KILL "$gp" 2>/dev/null || true\n',
                  'kill -KILL "$gp" 2>/dev/null || true; pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true\n')
    t = t.replace("grep -aqiE 'CRASH|SIGSEGV|fatal' \"$G\" && { echo",
                  "grep -aqE 'stop reason = (EXC_BAD|signal SIGSEGV)|CRASH' \"$G\" && { echo")
    out = root / f"scratch/agent/soak_queue/s5589_plume_lldb_{tag}.sh"
    out.write_text(t); out.chmod(0o755)
    print(out)
