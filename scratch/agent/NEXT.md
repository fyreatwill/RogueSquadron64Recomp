# NEXT work unit (s1886)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F2AA4` (`0x800F2AA4`,
size `0x10`, `syms/rogue_squadron.syms.toml:1985`). After s1885 the
last-15 titles still include s1872's hangar/512 revisit, so this is
not a mandatory REVISIT.

s1872 parked hangar/512 as UNEVALUABLE (no port arm published
origin `0x006ab400` / `0x006ab800`). Do not reopen that window
without a `[phase] vi_width=512 origin=0x006AB400` log.

Preliminary peek: in `funcs_41.c`, the `RECOMP_FUNC void` block
immediately following `clearPendingChildNpc` (which ends at
`0x800F2AA0`/`0x800F2AA4` boundary) is `setObjectFlagBit4`. This
needs CONFIRMATION, not assumption — a naive `sed`/`grep` for the
substring `0x800F2AA4` can match a stray jal-target comment inside an
unrelated earlier function, not the actual prologue. Use the
`awk`-style pairing below (last `RECOMP_FUNC void` seen before the
line matching the exact prologue comment `// 0x800F2AA4:`) to get the
true occupant.

Competing hypotheses:

- H1 already-named: companion, generated headers/body/INL, and
  TOML already agree on one human name — confirm only.
- H2 TOML leftover: generated side already uses a human name
  (candidate: `setObjectFlagBit4`), TOML still `func_800F2AA4`
  — synchronize TOML.
- H3 invent: no trustworthy human name; leave `func_*`.

Exact commands:

```
# Confirm the true occupant of 0x800F2AA4 (avoid substring false match):
awk '/^RECOMP_FUNC void /{name=$0} /\/\/ 0x800F2AA4:/{print name; exit}' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_41.c

# Then verify non-collision and companion/funcs.h/INL agreement:
grep -rn 'func_800F2AA4\b' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.inl
grep -n "800F2AA4\|setObjectFlagBit4" mission_overlay.txt 2>/dev/null
grep -n "setObjectFlagBit4" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: every source already agrees; session title
  `confirmed the leftover … symbol`.
- H2 (expected, per neighbor peek above): synchronize TOML to
  the confirmed name; title `synchronized the … symbol`.
- H3: leave leftover; document why.

Do not start another hangar/512 LLE walk.
