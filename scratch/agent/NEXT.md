# NEXT work unit

## s399 recap

Not a maintenance iteration (`docs/CURRENT-TRUTH.md` was 40,131 bytes). Per s398's own
recommendation, picked up the M4 fallback candidate: item -6, "confirm the s53/s54 missing-func fix
at runtime."

**Result: the s54 "fix" was never real.** s54 added the 3 missing symbol names to
`mission_overlay.txt`, but they already existed at the same addresses in `main_overlay.txt` (copied
"from the existing main_overlay.txt entries" per s54's own log — that phrase undersold what it meant).
`make_elf.py` parses `main_overlay.txt` first and dedupes by name, so the `mission_overlay.txt`
copies were always shadowed; `main_overlay.txt`-sourced symbols get range-checked against `.text`
(not the overlay window), so the shadowing copies get silently dropped as phantom functions.
`strings build/roguesquadron.elf` (which s54 never ran) showed the 3 names absent, full stop.

**Fixed s399**: deleted the 3 dead-weight duplicate lines from `main_overlay.txt` (sibling repo,
uncommitted per the sibling-repo rule), regenerated the full pipeline (deleted all `funcs_*.c` first
per item -20's standing rule, then `make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake
build`, all clean), and verified 2/2 post-fix runs: the 3 target addresses fire 0/3 (were 3/3
pre-fix in the same-session control run), same VI=512/origin-0x00690400 phase reached both times,
0 other stability-counter regressions. **M4 item -6: CLOSED.**

**Bigger finding, NOT yet fixed**: the same bug class affects **~801-803 more functions** in
`main_overlay.txt` (make_elf.py's own `skipped_funcs` count) — a 4th address of this exact family
(`endMissionCleanup`, 0x800FB9E4) fired live during s399's own verification soak. Unlike the 3 just
fixed, **none of the 803 have a correct duplicate anywhere else** — each needs its true owning
overlay (mission/menu/cinematic — they share one VRAM range) determined before relocation. s9
already tried bulk `main_overlay.txt` moves and hit a dead end (splits the enclosing function,
SIGBUS) — the standing lesson is `tools/overlay_symbol_probe.py <0xADDR>`, one address (or one
small validated batch) at a time. Full detail: `docs/CURRENT-TRUTH.md` item -248,
`PORTING-STATE` Session 399.

## Next work unit: start the `main_overlay.txt` phantom-function fix (item -248)

**HYPOTHESIS-ID: m4-main-overlay-phantom-functions** (new thread, iteration 1 under this slug).

This is a big backlog (~803 functions), so the work unit is NOT "fix them all" — it's the first
probe batch, following s9's one-at-a-time-or-small-validated-batch lesson exactly.

### Step 1 — get the full candidate list with addresses
```
cd ~/Documents/Tools/rogue_squadron64/symbol_files && python3 -c "
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
This reproduces the ~801-803-entry list. Save it to `scratch/agent/s400_phantom_candidates.txt`.

### Step 2 — determine true overlay ownership for a small first batch (10-20 addresses)
Use `tools/overlay_symbol_probe.py <0xADDR>` (per s9's lesson) on the first 10-20 candidates to
determine which overlay (mission/menu/cinematic) each address actually belongs to. Do NOT guess
from the function name alone (`cinematicX`-named functions are a reasonable prior but not proof —
verify).

### Step 3 — competing hypotheses / discriminating measurement
- H1: most candidates are genuinely mission-overlay functions that were simply never migrated when
  `mission_overlay.txt` was split out (predicts: `overlay_symbol_probe.py` confirms mission-overlay
  residency for the large majority).
- H2: candidates are a mix across all 3 overlays roughly proportional to each overlay's size
  (predicts: probe results split across mission/menu/cinematic without one dominating).
- H3: some candidates are actually dead/unreferenced code (never called by anything reachable) and
  fixing them will show 0 runtime effect (predicts: cross-referencing JAL callers in RecompiledFuncs
  finds no caller for a subset).
Discriminator: the probe script's overlay-residency answer for the first batch, cross-referenced
with a JAL-caller grep in the current `RecompiledFuncs/*.c` for each candidate name/address.

### Step 4 — apply and validate the first batch
Move the batch's entries (with `overlay_symbol_probe.py`-confirmed addresses) into the correct
overlay symbol file, delete them from `main_overlay.txt`, regen (delete `funcs_*.c` first!), build,
and soak — watch specifically for `[missing-func]` on the batch's addresses going to 0, AND for any
NEW UnhandledJumpTarget/SIGBUS (the s9 failure mode) as the batch's positive/negative control pair.

### Fallback if this is BLOCKED or too slow to start this iteration
The M3 idiom-audit-exhausted question from s397/s398 is still separately open (needs human
reconfirmation per the USER DIRECTIVE) — this item -248 line of work is a legitimate, self-directed
M4 item that doesn't need that reconfirmation, so prefer it over going BLOCKED.

## Soak queue

`scratch/agent/soak_queue/s399_missingfunc_verify3.sh` — 3rd confirmation run of the s399 fix (2/2
already passed live this session; this is belt-and-suspenders, not blocking). Runs itself, exits
nonzero only if one of the 3 originally-target addresses regresses.

## Iteration budget

HYPOTHESIS-ID: m4-main-overlay-phantom-functions (new, iteration 1). The old
`m3-idiom-audit-next-family` slug is parked, not closed — it still needs human input per s397/s398
(CFG-aware tool / crash-driven fallback / explicit M3-mode-exit approval), unaffected by this
session's M4 work.
