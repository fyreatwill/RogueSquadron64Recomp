#!/usr/bin/env python3
"""Score an s743 overlay-24 route soak against the s740 baseline."""
import re
import sys
from collections import Counter
from pathlib import Path

s740 = {
    "uj": 2931,
    "uj_fa92": 1009,
    "ovl4": 1033,
    "ovl12": 155960,
    "sec2_rows": 64,
    "sec2_match": 3,
    "sec2_active": 0,
    "rdpfs_last": 3948,
    "crash": 0,
}

path = Path(sys.argv[1] if len(sys.argv) > 1 else "")
if not path.is_file():
    raise SystemExit(f"usage: {sys.argv[0]} <run.log>")
text = path.read_text(errors="replace")

uj_tgts = re.findall(r"Unhandled jump target (0x[0-9A-Fa-f]+)", text)
uj_imem = [int(t, 16) & 0xFFFF for t in uj_tgts]
uj_oob = sum(1 for a in uj_imem if a < 0x1000 or a >= 0x2000)
uj_in = len(uj_imem) - uj_oob
uj_ovl12win = sum(1 for a in uj_imem if 0x1DB0 <= a <= 0x1FE0)
uj_ovl24win = sum(1 for a in uj_imem if 0x12A0 <= a < 0x1384)
top = Counter(f"0x{a:04X}" for a in uj_imem).most_common(8)

def count_res(res: str) -> int:
    return len(re.findall(rf"\[ovl-route\].*res={res}", text))

ovl4 = count_res("0x04")
ovl12 = count_res("0x0C")
ovl24 = count_res("0x24")
ovl28 = count_res("0x28")
other12 = len(re.findall(r"via=l1298-other", text))
crash = len(re.findall(r"\[CRASH\]", text))

sec2 = re.findall(r"\[e9-prov\] task=(\d+) scope=sec2 .* match=(\d+) .* "
                  r"frame=push:(\d+),pop:(\d+),resume:(\d+).* "
                  r"dl06=push:(\d+),complete:(\d+),open:(\d+)", text)
sec2_reset = re.findall(
    r"\[e9-prov-reset\] task=(\d+) scope=sec2 reset=(\d+) active=(\d+).*"
    r"ovl12=(\d+) ovl12_ret=(\d+)(?: ovl24=(\d+) ovl24_ret=(\d+) ovl28=(\d+) "
    r"l1298_12a0=24:(\d+),other:(\d+))?",
    text)
ctrl = re.findall(r"\[e9-prov\] task=(\d+) scope=control .* "
                  r"dl06=push:(\d+),complete:(\d+),open:(\d+) "
                  r"l12a0=direct:(\d+),overlay:(\d+)", text)

rdpfs = [int(x) for x in re.findall(r"\[vi-fs-decision\].*rdpFs=(\d+)", text)]
defer = len(re.findall(r"\[defer-drop\]", text))

print(f"log={path}")
print(f"CRASH={crash} (s740 {s740['crash']})")
print(f"UJ={len(uj_tgts)} oob={uj_oob} imem={uj_in} ovl12win={uj_ovl12win} "
      f"ovl24win={uj_ovl24win} (s740 UJ={s740['uj']} fa92={s740['uj_fa92']})")
print("UJ top", top)
print(f"[ovl-route] 04={ovl4} 0C={ovl12} 24={ovl24} 28={ovl28} "
      f"l1298-other={other12} (s740 04={s740['ovl4']} 0C={s740['ovl12']})")
print(f"sec2 e9-prov rows={len(sec2)} match>0="
      f"{sum(1 for r in sec2 if int(r[1]) > 0)} (s740 {s740['sec2_match']}/64)")
print(f"sec2 reset rows={len(sec2_reset)} active!=0="
      f"{sum(1 for r in sec2_reset if int(r[2]) != 0)} "
      f"(s740 {s740['sec2_active']})")
if sec2_reset:
    print("sec2 reset first", sec2_reset[0])
    print("sec2 reset last", sec2_reset[-1])
    warm = [r for r in sec2_reset if r[5] not in (None, "")]
    if warm:
        print("sec2 last ovl24/28/l1298",
              f"ovl24={warm[-1][5]} ovl24_ret={warm[-1][6]} ovl28={warm[-1][7]} "
              f"l1298_24={warm[-1][8]} other={warm[-1][9]}")
print(f"control rows={len(ctrl)}")
for row in ctrl[:4]:
    print(" control", row)
if rdpfs:
    print(f"rdpFs first={rdpfs[0]} last={rdpfs[-1]} last64={rdpfs[-64] if len(rdpfs)>=64 else rdpfs[0]}"
          f" (s740 last={s740['rdpfs_last']})")
print(f"defer-drop={defer}")

live24 = ovl24 > 0
live28 = ovl28 > 0
uj_collapse = len(uj_tgts) < s740["uj"] // 2
other_hit = other12 > 0
print("VERDICT_INPUTS "
      f"live24={int(live24)} live28={int(live28)} uj_collapse={int(uj_collapse)} "
      f"other12a0={int(other_hit)}")
