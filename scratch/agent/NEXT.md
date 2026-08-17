# NEXT work unit (s1874)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F2310` (`0x800F2310`,
size `0xE8`). After s1873 the last-15 titles still include
s1872's hangar/512 revisit, so this is not a mandatory REVISIT.

s1872 parked hangar/512 as UNEVALUABLE (no port arm published
origin `0x006ab400` / `0x006ab800`). Do not reopen that window
without a `[phase] vi_width=512 origin=0x006AB400` log.

Companion `mission_overlay.txt` and generated headers/body/INL
already name `isVectorInConeWriteDistance`; TOML still leftover
`func_800F2310`. First insn `addiu $sp, $sp, -0x40`; last
`jr $ra` / `addiu $sp, $sp, 0x40` at `0x800F23F0` /
`0x800F23F4`. Next already-named occupant is
`computeTurnAxisTowardTarget` at `0x800F23F8`.

Competing hypotheses:

- H1 already-named: companion, generated headers/body/INL, and
  TOML already agree on one human name — confirm only.
- H2 TOML leftover: generated side already uses
  `isVectorInConeWriteDistance`; TOML still `func_800F2310` —
  synchronize TOML (and any remaining generated leftover).
- H3 invent: no trustworthy human name; leave `func_*`.

Exact commands:

```
# Size, first/last insn, neighbor, leftover vs named occupancy.
# Compare companion mission_overlay.txt, generated headers/body/INL,
# and syms/rogue_squadron.syms.toml. Do not invent a name.
```

Expected splits:

- H1: every source already agrees; session title
  `confirmed the leftover … symbol`.
- H2: synchronize TOML (and leftovers) to the existing human
  name; title `synchronized the … symbol`.
- H3: leave leftover; document why.

Do not start another hangar/512 LLE walk.
