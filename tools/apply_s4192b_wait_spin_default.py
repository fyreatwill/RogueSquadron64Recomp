"""Make the yielding wait spin (mode 2) the default for the A12 countdown wait.

Unset ROGUESQ_AUDIO_WAIT_NOPUMP -> 2 (yield to the real producer);
'0' -> old musyxSynthFrame pump (rollback); '1' -> blind spin (deadlocks).
ORIGIN: s4192 measured the pump hitting its 64-iteration ceiling with the
countdown unchanged (16 -> 16), i.e. it never wrote the countdown and the wait
fell through unsatisfied, while the yield arm saw the real producer take the
countdown 16 -> 0 after ~200 yields. The writer is the legitimate producer.
Patches the live funcs_24.c and the fixup template.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "N64Recomp"
OLD = "s_audiowait_pump_off = (e && e[0] && e[0] != '0') ? (e[0] == '2' ? 2 : 1) : 0; }"
NEW = "s_audiowait_pump_off = (!e || !e[0]) ? 2 : (e[0] == '0' ? 0 : (e[0] == '2' ? 2 : 1)); }"
for f, n in ((root / "RecompiledFuncs" / "funcs_24.c", 2), (root / "fixup_game_funcs.py", 1)):
    t = f.read_text()
    if NEW in t:
        print(f"{f.name}: already default-yield")
        continue
    if t.count(OLD) != n:
        raise SystemExit(f"{f.name}: expected {n} sites, got {t.count(OLD)}")
    f.write_text(t.replace(OLD, NEW))
    print(f"patched {f}")
