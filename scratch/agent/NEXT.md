# NEXT work unit (s1887)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F2AB4` (`0x800F2AB4`, size
`0x10`, `syms/rogue_squadron.syms.toml:1986`). After s1886 the
last-15 titles still include s1872's hangar/512 revisit, so this is
not a mandatory REVISIT.

s1872 parked hangar/512 as UNEVALUABLE (no port arm published
origin `0x006ab400` / `0x006ab800`). Do not reopen that window
without a `[phase] vi_width=512 origin=0x006AB400` log.

Preliminary peek: in `funcs_41.c`, the `RECOMP_FUNC void` block
immediately following `setObjectFlagBit4` (which ends at
`0x800F2AA4`/`0x800F2AB4` boundary) is `clearObjectFlagBit4`. This
needs CONFIRMATION, not assumption — a naive `sed`/`grep` for the
substring `0x800F2AB4` can match a stray jal-target comment inside an
unrelated earlier function, not the actual prologue. Use the
`awk`-style pairing below (last `RECOMP_FUNC void` seen before the
line matching the exact prologue comment `// 0x800F2AB4:`) to get the
true occupant.

Competing hypotheses:

- H1 already-named: companion, generated headers/body/INL, and
  TOML already agree on one human name — confirm only.
- H2 TOML leftover: generated side already uses a human name
  (candidate: `clearObjectFlagBit4`), TOML still `func_800F2AB4`
  — synchronize TOML.
- H3 invent: no trustworthy human name; leave `func_*`.

Exact commands:

```
# Confirm the true occupant of 0x800F2AB4 (avoid substring false match):
awk '/^RECOMP_FUNC void /{name=$0} /\/\/ 0x800F2AB4:/{print name; exit}' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_41.c

# Then verify non-collision and companion/funcs.h/INL agreement:
grep -rn 'func_800F2AB4\b' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.inl
grep -n "800F2AB4\|clearObjectFlagBit4" mission_overlay.txt 2>/dev/null
grep -n "clearObjectFlagBit4" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl
```

Expected splits:

- H1: every source already agrees; session title
  `confirmed the leftover … symbol`.
- H2 (expected, per neighbor peek above): synchronize TOML to
  the confirmed name; title `synchronized the … symbol`.
- H3: leave leftover; document why.

Do not start another hangar/512 LLE walk.

IMPORTANT navigation note (s1886): the bash tool's working directory
persists across calls in this harness. A command that `cd`s into
`/Users/williambuckley/Documents/Tools/N64Recomp` to run the `awk`
census leaves subsequent commands running from that directory unless
you explicitly `cd` back to
`/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp` before
any `git` command. Verify with `pwd` before `git status`/`git commit`.
