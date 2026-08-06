# NEXT work unit

## s402 recap

Not a maintenance iteration (CURRENT-TRUTH was 46,912 bytes at session start). Retried item -249
(the `main_overlay.txt` phantom-overlay-function family) at s400's proven n≈20 scale, per s401's
fallback plan, with a **mandatory live-verify gate after every single batch** — the discipline s401
skipped. Regenerated the candidate list with the `is_data` filter fix (excludes lowercase-`g`-prefixed
globals): 778 candidates (down from 781, the 3 difference being the filter now correctly excluding
data symbols like `gCutsceneAssetPaths`).

Ran **two independent n=20 batches**, each: probed (0 truly AMBIGUOUS applied, NONE/AMBIGUOUS left for
follow-up), applied 16 CONFIRMED+WEAK entries, regenerated (`make_elf.py`'s `unmapped functions
skipped` dropped by exactly 16 each time — positive control), rebuilt clean, verified all 16 names
present via `nm` on the final binary, then **live-verified with `probe.sh` before the next batch was
even selected**: both runs reached `[phase] vi_width=512` (88.4s / 89.3s, matching the 88.7s clean
baseline), 0 crashes/asserts/UnhandledJumpTarget/dmem-race/SIGBUS, only the 1 known pre-existing
`[missing-func]`. Batch 1 happened to include `menuControllerInput`/`buildScaledFormatTextElement` —
the exact two names in s401's title-screen SIGBUS — and it relocated clean, reinforcing s401's
conclusion that batch **size** (not those symbols) caused that crash.

**Net M4 progress: +32 relocations this session (20 s400 + 32 s402 = 52/778 done, 746 remain).** Full
detail: `docs/CURRENT-TRUTH.md` item -251, `PORTING-STATE` Session 402.

One structurally-ambiguous holdout found twice now: `handleCraftSelectInput` (0x800af6ac) — multi-maybe
across menu/cinematic both times it was probed. Don't re-probe it again expecting a different answer;
next time it comes up, read the disassembly by hand (`tools/overlay_symbol_probe.py`'s prologue
heuristic is guessing, not proving, for this one) or just leave it for last.

## Next work unit: item -249, continue at n=20, OR use this session's clean 2/2 as grounds to try
## scaling batch size up (human call, not autonomous — see below)

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (iteration 6 under this slug — s400 was
iteration 1, s401 was 2-3, s402 was 4-5 combined as two verified batches in one session). Per iron
rule 8, this thread has now produced discriminating results in 3 of the last 3 iterations counted by
session (s400 positive, s401 negative-but-informative, s402 positive again) — not a stall, so no pivot
preamble required. Continue the SAME approach (n≈20, mandatory live-verify per batch) rather than
re-litigating batch size — that specific question (whether something between 20 and 774 is also safe)
was deliberately deferred here and needs a dedicated iteration with a clear head per s402's own
instruction, not a rider on this one.

### Step 1 — regenerate the candidate list (should print 746, matching s402's checkpoint)
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
    is_data = (('type:' in comment and 'type:func' not in comment) or 'size:' in comment or 'name_end:' in comment or name.startswith('D_') or name.startswith('junk_') or (name.startswith('g') and len(name) > 1 and name[1].isupper()))
    if is_data: continue
    vram = int(addr_s,16)
    if vram >= overlay_start and name not in other:
        print(name, hex(vram))
"
```

### Step 2 — take a batch of ~20 (next slice after s402's first 40 candidates)
Probe with `scratch/agent/s400_probe_batch.py` (unmodified, reusable). Apply only the CONFIRMED+WEAK
entries (0 truly multi-YES/multi-maybe AMBIGUOUS in the applied set) — NONE and AMBIGUOUS get left for
follow-up, same as s400/s402. If `handleCraftSelectInput` shows up again, skip it without re-probing
(see above).

### Step 3 — apply, regen, build (same recipe as s400/s402, now boringly repeatable)
1. `python3 scratch/agent/s400_apply_batch.py <results_file>`
2. Delete `N64Recomp/RecompiledFuncs/funcs_*.c` first (item -20's standing rule)
3. `make_elf.py` → confirm `unmapped functions skipped` dropped by exactly the applied batch size
4. `N64Recomp` → `fixup_game_funcs.py` → check for `error`/`fail`/`mismatch` in the output
5. `cmake -S . -B build` (full reconfigure — cheap, and the `CONFIGURE_DEPENDS` fix means it's no
   longer strictly required, but still removes one whole class of false scares) → `cmake --build
   build -j8`
6. If undefined-symbol cascade: prefer reverting the batch over chasing it (s401's lesson) unless the
   extra neighbor set is single-digit.

### Step 4 — MANDATORY live verify BEFORE the next batch (no exceptions, this is the load-bearing rule)
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
  zsh tools/probe.sh <outdir> 45 2
```
PASS = `[phase] vi_width=512` reached (~88-89s), 0 new crash/assert/UnhandledJumpTarget/dmem-race/
SIGBUS, only the 1 known `[missing-func]` (`endMissionCleanup`/`0x800FB9E4`). Also spot-check via `nm`
on the built binary that the batch's names are actually present (build success alone is not proof,
per the s54/s399/s401 lesson). If it crashes: revert this batch immediately (name+address matching,
never a blanket revert), do not patch around it same-iteration unless the fix is a single obvious site.

### Step 5 — repeat for a second batch if step 4 passed, same as s402
Two clean batches per iteration has now worked twice (s400 implicitly, s402 explicitly) — keep doing
it, but if you have any doubt about time budget, ONE clean live-verified batch alone still counts as
ADVANCED. Landing zero batches because you ran out of iteration budget mid-verify is worse than landing
one clean one and stopping.

### Do NOT this iteration
Scale batch size above ~20-25 without a dedicated "find the safe ceiling" iteration — s402 explicitly
deferred that question and it deserves its own hypothesis thread, not a casual bump because two batches
in a row looked easy.

## Soak queue

None currently queued for this item — each batch already gets its own live-verify run inline; no
separate soak makes sense until the item closes out or a specific regression needs re-confirmation.

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 6. Continue the n≈20-per-batch,
verify-before-next-batch discipline. 746 candidates remain at ~16-20/batch — this will take many more
iterations at this rate; that's fine and expected, it's the safe rate this family has earned.
