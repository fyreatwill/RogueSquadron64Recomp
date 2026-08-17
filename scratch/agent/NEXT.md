# NEXT work unit (s1823)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume leftover `fake_func_800ECE04`. Last-15 ledger titles after
s1822 still include the s1808 revisit (`selected H2 menuIn/mission
jal-sites`), so the 15-title all-sweep REVISIT gate does not fire.

Census leftover `fake_func_800ECE04` (`0x800ECE04`, size `0xC`).
Neighbor peek already: companion `mission_overlay.txt`, generated
`funcs.h` / `funcs_40.c` / overlay INL, and TOML already use
`fake_func_800ECE04`. Previous occupant is now
`dispatchSlotActionTwelveByGlobalId` (`0x800ECDDC`, `0x28`; s1822
synchronized) then this leftover. First insn `srl $v0, $t1, 4`;
then `addiu $v0, $v0, 0x9F`; last `multu $v0, $v1` at
`0x800ECE0C`. No generated `jal 0x800ECE04`. Next generated
occupant is `datItemActorNpcHandler` (`0x800ECE10`, `0x338`; first
insn `addiu $sp, $sp, -0x140`). TOML still leftover
`{ name = "func_800ECE10", vram = 0x800ECE10, size = 0x338 }`.
Companion comment: `func_800ECE10` deleted s432 as a
duplicate-symbol collision with `datItemActorNpcHandler`.

Competing hypotheses:

- H1: already synchronized — TOML, generated headers/body, overlay
  INL, and companion already agree on the leftover splat name with
  matching size (confirm only; no rename).
- H2: one or more sources still carry stale `func_800ECE04`.
  Companion already has `fake_func_800ECE04`. Do not invent a name
  and do not steal `datItemActorNpcHandler` for this 0xC span.
- H3: leftover splat, overlay collision, or size/boundary
  disagreement (`dispatchSlotActionTwelveByGlobalId` ends at
  `0x800ECE04`; generated next occupant is
  `datItemActorNpcHandler` at `0x800ECE10`). Leave the leftover
  name if this is a mid-function orphan (no prologue; next
  occupant has its own `addiu $sp`).
- H4: companion, generated body, TOML, or section-4 row is missing.

Exact commands (no game run):

```
# TOML + generated + overlay INL
grep -n '800ECE04\|fake_func_800ECE04\|func_800ECE04\|800ECE10\|func_800ECE10\|datItemActorNpcHandler' \
  syms/rogue_squadron.syms.toml \
  ../N64Recomp/RecompiledFuncs/funcs.h \
  ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
# generated body + callers
grep -n 'fake_func_800ECE04\|func_800ECE04\|jal         0x800ECE04' \
  ../N64Recomp/RecompiledFuncs/funcs_4*.c
# companion overlays
grep -n '800ECE04\|fake_func_800ECE04\|func_800ECE04\|800ECE10\|func_800ECE10\|datItemActorNpcHandler' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/*.txt
```

Then read the generated body: `srl $v0, $t1, 4` at `0x800ECE04`;
`addiu $v0, $v0, 0x9F`; `multu $v0, $v1` at `0x800ECE0C`. Classify
as leftover splat vs split first instruction of the next occupant.
Do not invent a name.

Expected splits:

- H1: all four sources already `fake_func_800ECE04` at size `0xC`.
  Confirm.
- H2: rename the stale `func_800ECE04` placeholder(s) only if a
  companion human name exists for this exact 0xC span (it does
  not — companion leftover is `fake_func_800ECE04`).
- H3: document the leftover/collision/size miss; leave the name.
- H4: fill the missing source or leave as `fake_func_*`.

Do not reopen the s1744 six-entry, s1760 jump-table, s1776
main-text, s1792 unwatched-caller, or s1808 jal/`prev_pc` Rice
recipes. The next 15-title REVISIT is the M4 accumulator
boundary, not another `submitGfxFrame` PC set.
