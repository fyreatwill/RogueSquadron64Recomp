# NEXT work unit

## s400 recap

Not a maintenance iteration (CURRENT-TRUTH was 44,180 bytes at session start). Picked up item -248
(renumbered -249 this session) per NEXT.md's plan: the `main_overlay.txt` phantom-overlay-function
family, batch 1.

**What happened**: re-derived the 801-candidate list, probed the first 20 with
`tools/overlay_symbol_probe.py` (checks function-start prologue signature against all 3 overlays).
Result: 13 CONFIRMED (strict prologue match), 7 WEAK (jr-$ra-before match only), **0 AMBIGUOUS, 0
NONE** — every one of the 20 resolved to exactly one destination overlay (10 mission, 7 cinematic, 3
menu). Cross-checked a sample against `RecompiledFuncs/*.c` JAL callers — all live/reachable, not
dead code. Moved all 20 to their correct overlay file, deleted from `main_overlay.txt`. Regenerated
the full pipeline (`make_elf.py`'s own `skipped_funcs` counter dropped 803→783, exactly the 20
moved), rebuilt clean, then verified two independent ways: `strings roguesquadron.elf` shows all
20/20 names now present (the "build succeeded" trap from s54/s399 — checked anyway), and a live
driven run hit **0/20** `[missing-func]` for the batch, with a positive control (reached VI=512) and
0 new instability. Only 1 other `[missing-func]` fired (`0x800FB9E4`/`endMissionCleanup`, the same
known not-yet-fixed address s399 saw). Full detail: `PORTING-STATE` Session 400,
`docs/CURRENT-TRUTH.md` item -249.

**Batch tooling is reusable as-is**: `scratch/agent/s400_probe_batch.py` (probe + classify) and
`scratch/agent/s400_apply_batch.py` (move + regen-ready) both take a plain `name addr` list file and
need no changes for the next batch — just point them at the next slice of candidates.

**781 candidates remain.**

## Next work unit: batch 2 (and consider scaling batch size up)

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (same thread, iteration 2 under this slug).

### Step 1 — regenerate the candidate list (it shrinks as batches land)
```
cd rogue_squadron64/symbol_files && python3 -c "
import re
SYM_RE = re.compile(r'^(\w+)\s*=\s*(0x[0-9A-Fa-f]+)\s*;(.*)\$')
overlay_start = 0x800A5130
def load_names(path):
    names=set()
    for line in open(path, encoding='utf-8'):
        m = SYM_RE.match(line.strip())
        if m and 'defined:false' not in m.group(3): names.add(m.group(1))
    return names
other = load_names('mission_overlay.txt') | load_names('menu_overlay.txt') | load_names('cinematic_overlay.txt')
for line in open('main_overlay.txt', encoding='utf-8'):
    m = SYM_RE.match(line.strip())
    if not m: continue
    name, addr_s, comment = m.groups()
    if 'defined:false' in comment: continue
    is_data = (('type:' in comment and 'type:func' not in comment) or 'size:' in comment or 'name_end:' in comment or name.startswith('D_') or name.startswith('junk_'))
    if is_data: continue
    vram = int(addr_s,16)
    if vram >= overlay_start and name not in other:
        print(name, hex(vram))
"
```
Should print ~781. Take the NEXT slice (skip the 20 already done — they're no longer candidates
since they're now in their destination files, so this just works). Save to
`scratch/agent/s401_batch2.txt` (or reuse `s400_probe_batch.py`'s batch-file convention).

### Step 2 — decide batch size: 20 (repeat s400's size) or scale up (40-60)?
s400's batch of 20 had 0 ambiguous/unresolved candidates — better than the "one at a time" caution
s9's bulk-move dead end implied. Before committing to a bigger batch, do a quick gut-check: probe
40-60 addresses (Step 2 script from s400, just point at a bigger slice) and look at the AMBIGUOUS/
NONE rate. If it stays near 0%, apply the whole probed batch in one shot (same apply script, no
changes needed). If AMBIGUOUS/NONE starts showing up meaningfully (e.g. >10-15%), fall back to
applying only the CONFIRMED+WEAK subset and leave the rest for individual follow-up (don't guess).

### Step 3 — apply, regen, build, verify (identical to s400)
1. `python3 scratch/agent/s400_apply_batch.py <results_file>` (already refuses on unresolved tags)
2. Delete `N64Recomp/RecompiledFuncs/funcs_*.c` (item -20's standing rule)
3. `make_elf.py` -> check `skipped_funcs` dropped by exactly the batch size (positive control #1)
4. `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build . -j8`, all clean
5. `strings roguesquadron.elf | grep <batch names>` -> all present (positive control #2, the s54/s399
   lesson)
6. One live driven run (`tools/probe.sh`, `ROGUESQ_STUB_MISSING_FUNCS=1`, `PROBE_PHASE_WIDTH=512`,
   `PROBE_LEAVE_OK=1`) -> 0/<batch size> `[missing-func]` fires for the batch's addresses, positive
   control (VI=512 reached), 0 new UnhandledJumpTarget/dmem-race/defer-drop/assert.
7. Queue a 2nd confirmation soak to `scratch/agent/soak_queue/` (same shape as
   `s400_batch1_verify.sh` — copy and retarget the address list).

### Fallback if BLOCKED
If a batch surfaces an AMBIGUOUS case that genuinely can't be resolved by the probe script (e.g. a
function-start signature present in 2 overlays at the same address — plausible since all 3 share one
VRAM window), do NOT guess: leave that one address in `main_overlay.txt`, apply only the resolved
rest of the batch, and note the unresolved address(es) for a dedicated follow-up (maybe needs a
same-scene-loaded-overlay cross-check instead of a static disassembly check).

## Soak queue

`scratch/agent/soak_queue/s400_batch1_verify.sh` — 2nd confirmation run of s400's batch-1 fix (1/1
already passed live this session). Runs itself, exits nonzero if any of the 20 batch-1 addresses
regress.

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions (iteration 2 of this slug — s400 was iteration 1).
Plenty of room before iron rule 8's 3-consecutive-iteration budget check kicks in; this is a large,
well-understood, repetitive backlog, not a stuck investigation — each batch is a fresh discriminating
result (does relocation clear the address from `[missing-func]`), not a repeat of the same
inconclusive probe.
