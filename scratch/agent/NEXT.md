# NEXT work unit

## s401 recap

Not a maintenance iteration (CURRENT-TRUTH was 44,113 bytes at session start). Continued item -249
(the `main_overlay.txt` phantom-overlay-function family, 781 remaining after s400's batch 1) per the
previous NEXT.md's plan, but at a much larger scale than intended — ended up applying 774 relocations
in one session (60 + 7 + 16 + 66 + 625, each round triggered by chasing undefined-symbol link errors
into the next address range) before a live driven run hit a **new, deterministic SIGBUS** at the title
screen (`menuOverlayInit`→`menuControllerInput`→`buildScaledFormatTextElement`, wild pointer near
guest `0x8000005E`). Reverting just the two crashing names did NOT stop the crash — N64Recomp still
auto-synthesized the same code as `static_5_...`, proving the batch's SIZE (re-slicing function
boundaries for unrelated, already-existing functions) caused it, not any single bad candidate — the
same mechanism as the s9 dead end. **Surgically reverted all 774 relocations** back to
`main_overlay.txt` (matched by name+address, not a blanket revert, to protect unrelated pre-existing
uncommitted sibling-repo work). Verified the revert restored s400's exact checkpoint: `make_elf.py`
skipped-func counter back to 783, live run reaches VI=512 clean (88.7s, 0 crashes, 1 known
`[missing-func]`). **Net M4 progress this session: flat (still 20/801 done, 781 remain)** — see item
-250 in CURRENT-TRUTH for full detail.

Separately, landed and committed a real, durable, unrelated fix: `CMakeLists.txt`'s two
`file(GLOB RECOMP_C_SOURCES/RECOMP_CXX_SOURCES ...)` calls now have `CONFIGURE_DEPENDS`, so a plain
`cmake --build` no longer silently links against a stale file list when a regen changes the
`RecompiledFuncs/funcs_*.c` file count (this cost most of s401's debugging time before being
root-caused as a config-staleness issue, not a real missing-symbol problem).

## Next work unit: item -249 batch 2, RETRY at a much smaller scale

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (same thread, iteration 4 under this slug — s400
was iteration 1, s401 was iterations 2-3 combined into one session; per iron rule 8 this next attempt
needs a pivot preamble since we're now at 3+ iterations on the same slug with no NET discriminating
progress — the preamble is: s401 already found the discriminating result (batch size, not candidate
ambiguity, is the risk factor), so this iteration's job is to find the actual safe threshold, not to
repeat the same experiment).

### The core lesson: verify live, per batch, BEFORE accumulating the next one

s400's batch of 20 was independently live-verified (reached VI=512 clean) before anyone touched
anything else. s401's mistake was chaining FIVE batches (60, 7, 16, 66, 625) back-to-back based only
on "build succeeded" before ever running the game — by the time a live run finally happened, it was
impossible to tell which of the 774 relocations was responsible. **Do not repeat this.** Each batch
this iteration must reach a live VI=512 positive-controlled run, clean, before the next batch is even
selected.

### Step 1 — regenerate the candidate list (should print 781, matching s400's count)
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
Note the added `is_data` clause vs s400/s401's version — excludes lowercase-`g`-prefixed globals
(s401 found `gCutsceneAssetPaths` had slipped through as a false function-candidate; verify with
`tools/overlay_symbol_probe.py <addr>` if a `g`-prefixed name shows a NONE verdict — it's probably
data, not an unresolved function).

### Step 2 — take a SMALL batch (n=20, matching s400's proven-safe size — do NOT scale up this time)
Probe with `scratch/agent/s400_probe_batch.py` (unmodified, reusable). Apply only if 0 truly
AMBIGUOUS (multi-YES or multi-maybe) — WEAK (single maybe) is fine, NONE gets left for follow-up.

### Step 3 — apply, regen, build
1. `python3 scratch/agent/s400_apply_batch.py <results_file>`
2. Delete `N64Recomp/RecompiledFuncs/funcs_*.c` (item -20's standing rule — use
   `python3 -c "import glob,os; [os.remove(f) for f in glob.glob('.../funcs_*.c')]"`, `rm -f` with a
   glob is blocked by the harness)
3. `make_elf.py` → check `unmapped functions skipped` dropped by exactly the batch size
4. `N64Recomp` → `fixup_game_funcs.py`
5. **`cmake -S . -B build` (full reconfigure, not just `--build`)** — no longer strictly required
   after s401's `CONFIGURE_DEPENDS` fix, but cheap (~1-2s) and removes one whole class of false
   "undefined symbol" scares if the fix has any gap. Then `cmake --build build -j8`.
6. If the build fails with undefined `static_N_ADDR` symbols: this means the batch's relocated
   function(s) call into a still-phantom NEIGHBOR not in the batch. s401 handled this by chasing the
   address range and applying more — **this time, prefer reverting the batch instead** unless the
   extra neighbor set is also small (single digits). Getting pulled into a large chase is exactly how
   s401 ended up at 774 in one shot.

### Step 4 — MANDATORY live verify BEFORE the next batch
`env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh <outdir> 45 2`
— PASS = `[phase] vi_width=512` reached, 0 new `[missing-func]` for this batch's addresses, 0
crash/assert/UnhandledJumpTarget/dmem-race. If it crashes: revert this batch immediately (same
name+address matching approach s401 used), do NOT try to patch around it in the same iteration unless
the fix is obvious and single-site.

### Step 5 — repeat Steps 2-4 for a second n=20 batch ONLY if step 4 passed clean
This establishes whether n=20 is reliably safe (2 clean batches in a row) before ever considering
scaling up again. Do not scale batch size up this iteration regardless of how clean these look — that
call needs its own dedicated iteration with a clear head, not a rider on unwinding s401's mess.

### Fallback if BLOCKED
If even n=20 batches start showing the s401 failure mode (undefined-symbol cascades needing >10
extra addresses, or a live crash), STOP and go BLOCKED — the s9/s401 function-boundary-resplitting
mechanism may need a static analysis tool (e.g. checking whether a candidate's disassembly range
overlaps ANY already-real function's body) rather than more manual batching, which is a human-input
question per the M3-idiom-audit precedent's "needs human input" pattern.

## Soak queue

None currently queued for this item (s400's `s400_batch1_verify.sh` already ran and passed; no new
soak makes sense to queue until a new batch actually lands and needs a 2nd confirmation run).

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions, iteration 4. Per iron rule 8, this iteration MUST
either produce a new discriminating result (a safe batch size found, live-verified) or go BLOCKED with
the specific fallback above — no more open-ended scaling experiments without a live-verify gate.
