"""M5 A15 de-stub: ROGUESQ_SPIN_YIELD defaults ON (unset/empty -> on; =0 -> off).

ORIGIN: the menuInit/menuInput/cinematicInit spins on anyAudioSlotActive never
yield, so the host VI/SI retrace in external_messages starves (hardware would
preempt the spin). Same starvation class as A11 (s4196-s4198). Patches the
generated RecompiledFuncs and the fixup_game_funcs.py templates.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "N64Recomp"
OLD = "(ye && *ye && *ye != '0') ? 1 : 0"
NEW = "(!ye || !*ye || *ye != '0') ? 1 : 0"
total = 0
for p in sorted(root.glob("RecompiledFuncs/*.c")) + [root / "fixup_game_funcs.py"]:
    lines = p.read_text().split("\n")
    n = 0
    for i, l in enumerate(lines):
        # only SPIN_YIELD sites: getenv("ROGUESQ_SPIN_YIELD") within the 3 preceding lines
        if OLD in l and any("ROGUESQ_SPIN_YIELD" in x for x in lines[max(0, i - 3):i]):
            lines[i] = l.replace(OLD, NEW)
            n += 1
    if n:
        p.write_text("\n".join(lines))
        print(p.name, n)
        total += n
print("total", total)
