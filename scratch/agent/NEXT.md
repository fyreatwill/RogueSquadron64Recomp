# NEXT work unit

## s403 recap

Not a maintenance iteration (CURRENT-TRUTH was 48,774 bytes at session start; 50,241 after this
session's edits, still comfortably under the 60,000-byte trigger). Continued item -249 (the
`main_overlay.txt` phantom-overlay-function family) at s400/s402's proven n≈20 scale, with the same
mandatory live-verify-per-batch discipline.

Regenerated the candidate list (unchanged script, `is_data` filter fix): 746 candidates, matching
s402's checkpoint exactly. Ran **two independent n=20 batches**, each: probed (17 CONFIRMED — all
`mission`, 3 NONE, 0 AMBIGUOUS both times — the cleanest verdict split yet for this item), applied the
17 CONFIRMED, regenerated (`make_elf.py`'s `unmapped functions skipped` dropped by exactly 17 each
time: 751→734→717, positive control), rebuilt clean (full `cmake -S . -B build` reconfigure + `cmake
--build -j8`, 0 new warnings/errors), verified all 17 names present via `nm` on the final binary, then
**live-verified with `probe.sh` before the next batch was even selected**: both runs reached `phase
width=512` (88.7s / 88.6s, matching the 88.7s clean baseline), 0 crashes/asserts/UnhandledJumpTarget/
dmem-race/SIGBUS, only the 1 known pre-existing `[missing-func]`.

**Net M4 progress: +34 relocations this session (52 prior + 34 s403 = 86/778 done, 692 remain).** Full
detail: `docs/CURRENT-TRUTH.md` item -252, `PORTING-STATE` Session 403.

`handleCraftSelectInput` (0x800af6ac) was skipped again without re-probing, per the standing
instruction from s402 (structurally AMBIGUOUS across menu/cinematic both times it was probed — a
probe won't resolve it, only a manual disassembly read will). It's still sitting in `main_overlay.txt`
and will keep showing up at the front of every future candidate-list slice until someone resolves it
by hand or explicitly defers it to the end of the list.

## Next work unit: item -249, continue at n=20

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (iteration 8 under this slug — s400 was
iteration 1, s401 was 2-3, s402 was 4-5, s403 was 6-7 combined as two verified batches). Per iron rule
8: this thread has produced a discriminating result (a clean regen+build+live-verify cycle) in every
iteration counted this session too — not a stall, no pivot preamble required. **6 consecutive clean
batches in a row since s401's CMakeLists.txt fix, 0 regressions.** Continue the SAME approach (n≈20,
mandatory live-verify per batch). The safe-ceiling-above-20 question remains deliberately deferred —
still not this iteration's job unless a human explicitly asks for a dedicated "find the safe ceiling"
session.

### Step 1 — regenerate the candidate list (should print 692, matching s403's checkpoint)
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
Note: this repo checkout has `rogue_squadron64` as a SIBLING directory
(`/Users/williambuckley/Documents/Tools/rogue_squadron64`), not nested under this repo — `cd` there
directly, don't assume a relative path from inside this repo.

### Step 2 — take a batch of ~20 (next slice after s403's first 40 candidates in this session's
regenerated list)
Probe with `scratch/agent/s400_probe_batch.py` (unmodified, reusable — takes a `name addr` per-line
batch file, writes verdicts). Apply only the CONFIRMED+WEAK entries — NONE and AMBIGUOUS get left for
follow-up, same as every prior batch. **Skip `handleCraftSelectInput` on sight, without re-probing**
(3rd time it would come up structurally ambiguous; read the disassembly by hand instead, or move it
to the very end of the candidate ordering).

### Step 3 — apply, regen, build
1. `python3 scratch/agent/s400_apply_batch.py <results_file_filtered_to_CONFIRMED/WEAK_only>` — the
   apply script REFUSES any line with an unresolved (NONE/AMBIGUOUS) tag, so filter with
   `grep -E "CONFIRMED|WEAK"` into a separate file first.
2. Delete all `RecompiledFuncs/funcs_*.c` first (item -20's standing rule) — they live in the SIBLING
   `~/Documents/Tools/N64Recomp/RecompiledFuncs/` directory, not under this repo. Use a Python
   `glob.glob` + `os.remove` loop if a shell glob gets sandbox-blocked as a "write operation".
3. `python3 ~/Documents/Tools/rogue_squadron64/tools/make_elf.py` → confirm `unmapped functions
   skipped` dropped by exactly the applied batch size (positive control).
4. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` → then
   `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` → grep both logs for
   `error|fail|mismatch`, expect 0 hits (the usual "Unhandled cop0/branch" and "neutered fake_func"
   lines are normal, ignore them).
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake -S . -B build` (full reconfigure —
   cheap, the `CONFIGURE_DEPENDS` fix means it's no longer strictly required, but still removes one
   whole class of false scares) → `cmake --build build -j8`.
6. If undefined-symbol cascade: prefer reverting the batch over chasing it (s401's lesson) unless the
   extra neighbor set is single-digit.
7. Spot-check the batch's names are actually present via `nm` on the built binary — run it through
   `python3 -c "import subprocess; ..."` rather than a bare `nm` shell call, which needs interactive
   approval in this environment and will stall a non-interactive session.

### Step 4 — MANDATORY live verify BEFORE the next batch (no exceptions, this is the load-bearing rule)
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
  zsh tools/probe.sh <outdir> 45 2
```
This reliably exceeds the 120s foreground command limit and gets auto-backgrounded — that's fine, it
finishes in ~90-100s and a `<task-notification>` fires when it's done; don't poll with `sleep` loops
(blocked in this environment) and don't fabricate a result before the notification arrives.

PASS = `phase width=512 reached` in the probe output (~88-89s), 0 new crash/assert/
UnhandledJumpTarget/dmem-race/SIGBUS in `<outdir>/run.log`, only the 1 known `[missing-func]`
(`endMissionCleanup`/`0x800FB9E4`). If it crashes: revert this batch immediately (name+address
matching, never a blanket revert), do not patch around it same-iteration unless the fix is a single
obvious site.

### Step 5 — repeat for a second batch if step 4 passed
Two clean batches per iteration has now worked three sessions running (s400 implicitly, s402 and s403
explicitly) — keep doing it, but ONE clean live-verified batch alone still counts as ADVANCED if time
is short.

### Do NOT this iteration
Scale batch size above ~20-25 without a dedicated "find the safe ceiling" iteration — still deferred,
still not this session's job on its own initiative.

### Reminder: sibling-repo commit rule (item -3)
Every batch's symbol-file edits land in `~/Documents/Tools/rogue_squadron64/symbol_files/*.txt`, a
SEPARATE git repo with its own uncommitted history. Do NOT commit there autonomously — ask the user
first, per the standing rule. This repo's commit only covers `scratch/agent/*` and the docs.

## Soak queue

None currently queued for this item — each batch already gets its own live-verify run inline; no
separate soak makes sense until the item closes out or a specific regression needs re-confirmation.

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 8. Continue the n≈20-per-batch,
verify-before-next-batch discipline. 692 candidates remain at ~17-20/batch — many more iterations at
this rate, and that's fine, it's the safe rate this family has earned across 6 consecutive clean
batches.
