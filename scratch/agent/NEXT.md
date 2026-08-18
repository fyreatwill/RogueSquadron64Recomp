# NEXT work unit (s1973) — M3 slotDispatcherIter+872 SIGBUS class audit

HYPOTHESIS-ID: m3-dispatcher-sigbus-class

## What s1972 settled

`drainAudioAndFinalizeSpeechBuffer` was spinning on `anyAudioSlotActive` at
`L_800B24D4` (funcs_30.c) — the same host-yield-starvation class as menuInit and
menuInput. Adding the ROGUESQ_SPIN_YIELD gate (s1972 fixup in fixup_game_funcs.py
and funcs_30.c) resolved the spin in ~300k iters. Hangar now stable 180s / 48
frames / zero crashes with all three yield sites active. H-new-yield-needed
SELECTED. Class closed.

## Single next work unit

M3 systematic idiom-class audit: the recurring `slotDispatcherIter+872` SIGBUS at
`funcs_8.c:22810`. This is the generated prologue spill of guest `$sp` that
previous static audits exhausted without finding a reachable writer. The
class-audit approach (per the s282–s288 model):

1. Locate the exact spill site and the guest stack range it occupies.
2. Enumerate ALL generated prologue/epilogue instructions that store to the same
   guest stack address range (across all funcs_*.c files, not just the caller).
3. Classify each hit: can it race with slotDispatcherIter's frame? Prove dead or
   mark as guard candidate.
4. If a writer is found, name it with ORIGIN:. If the class is exhausted with no
   writer, close as "no static writer found" and move on.

Do NOT add a guard or mitigation until the writer is named.

## Competing hypotheses and discriminator

- H-stack-collision: another generated function's prologue writes to the same guest
  stack region during a concurrent slotDispatcherIter call.
- H-corruption-from-caller: the dispatched callee corrupts $sp before the spill
  address is read back, making the load see garbage.
- H-uninit-stack: the SIGBUS comes from a guest $sp that was never initialized to a
  valid host-mapped address, so the generated prologue store hits unmapped memory.

Discriminator: the spill address itself (computed from ctx->r29 at the prologue).
If the SIGBUS address is a well-formed N64 address that just has no host mapping,
H-uninit-stack is most likely. If it's a wild value far from any N64 range,
H-corruption-from-caller. If it's within another function's frame range, H-stack-collision.

## Exact commands

Find the dispatcher prologue spill site:
```sh
grep -n 'funcs_8.c:22810\|slotDispatcherIter\|0x8003E8DC' docs/CURRENT-TRUTH.md PORTING-STATE.md | tail -10
sed -n '22800,22830p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c
```

Get the guest PC and $sp range from the generated prologue:
```sh
grep -n 'slotDispatcherIter\|0x8003E8DC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c | head -5
```

Enumerate all stores to the same guest stack range across all funcs_*.c:
```sh
grep -n 'MEM_W.*ctx->r29\|MEM_W.*r29' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c | head -30
```

Positive control: verify the hangar is still reachable with current build:
```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1973_control 60 2
```
