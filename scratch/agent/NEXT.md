# NEXT work unit

HYPOTHESIS-ID: songtempo-table-guard-29c0

## s458 close-out: item -295 (next slice of item -292's `SONGTEMPO_TABLE_GUARD`) EXECUTED

`stepSongModulationLanes` (5 sites) built, live-verified, soaked-queued: 0 `songtempo-table-guard`
fires, 0 `dl-list-append-guard` fires (both match established 0-fires baselines), 0 `[CRASH]`
markers across the entire 300s schedule (clean run this time — no unrelated crash to file, unlike
s457). 19/43 total sites of item -292 now fixed, 4 of 6 reader functions done. Confirmation soak
queued to `scratch/agent/soak_queue/s458_songtempo_smod_confirm.sh`. Full detail:
`docs/CURRENT-TRUTH.md` item -295, `PORTING-STATE.md` Session 458.

## Priority 1: finish item -292's `SONGTEMPO_TABLE_GUARD` (24 sites remaining)

`updateSongTempoTickRate` (4), `tickScheduledSongEvents` (5), `stepSongPitchBendLanes` (5),
`stepSongModulationLanes` (5) — 19/43 total — are DONE and verified. The remaining 24 sites are the
same idiom (`0x29C0($reg)` → global `0x801529C0`, MusyX song-track pointer), in the last 2 reader
functions, both in `funcs_25.c`:
- `advanceSongRegion` (12 sites, ~539 lines)
- `stepActiveSongTracks` (12 sites, ~744 lines)

Do `advanceSongRegion` next (smaller of the two). Same method as all prior slices: **read the whole
function body first** (in `N64Recomp/RecompiledFuncs/funcs_25.c` — the live regenerated copy, not
the stale scratch/agent/s389_verify or s390_verify snapshots), identify each site's real bail
semantics (before-prologue → bare `return;`; inside an existing loop with its own exit
label/idiom → reuse that; past all loops, near the real epilogue → duplicate the epilogue) — do NOT
templatize blindly.

**Both `advanceSongRegion` and `stepActiveSongTracks` were flagged in earlier sessions' first-skim
as having an odd stack-frame mismatch** (prologue pushes more than the visible epilogue pops) —
worth checking for the recompiler's cross-function shared-tail-merge behavior (seen elsewhere as
`lvj_checkComplexObjectives`/`audioCompandS16`/`__OSGlobalIntMask`, CLAUDE.md) before trusting a
single simple bail-to-epilogue pattern; may need per-site individual verification rather than a
uniform template. This is the reason these two were saved for last — confirm the actual function
boundaries and epilogue shape by reading before assuming anything.

Standard pipeline once patches are written: verify regex anchors match exactly once each with a
standalone Python probe BEFORE touching `fixup_game_funcs.py` (catches typos before spending a
build cycle; also cross-check the raw `0X29C0` occurrence count in the function body matches the
expected site count) → raw regen (`make_elf.py` → delete stale `funcs_25.c` → `N64Recomp` →
`fixup_game_funcs.py` — audit the report counts against a direct grep, don't just trust the number)
→ `cmake --build` (run in background; it takes ~2 min) → `strings` sanity → live-verify
(`tools/probe.sh`, full 300s/250s-keys schedule, ALL passive guard env vars armed — copy the list
from `scratch/agent/soak_queue/done/s457_songtempo_readers_confirm...sh` or this session's
`s458_songtempo_smod_confirm.sh`) → queue confirmation soak → exit contract.

Note: `fixup_game_funcs.py` and `RecompiledFuncs/` in `~/Documents/Tools/N64Recomp` are untracked
local tooling (confirmed s458) — NOT part of this repo's `lib/` submodule tree (the
`lib/N64ModernRuntime/N64Recomp` submodule path has no working files checked out). No
`submodule-patches/export.sh` step applies to edits there.

Once `advanceSongRegion` and `stepActiveSongTracks` are both done, item -292 CLOSES (43/43 sites) —
write the closure the same way item -291/-293 were closed.

## Confirmed non-issues, do not re-investigate

`-0x25C0($s0)` (56 sites, `mallocCraftSelectionData`) and `-0x76E0($s0)` (46 sites, spread across
8 files) are compile-time-constant-based counter/scalar accesses (`lui $s0, 0x800D` then a 16-bit
counter store/load used in index arithmetic), not pointer dereferences — independently confirmed
by both s454 and s455.

Small/ubiquitous offsets (`0x0`, `0x4`, `0x8`, `0xC`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`...)
match hundreds of unrelated functions doing ordinary struct-field access — too broad to be a
distinct idiom class the way `-0x25A4`/`-0x5824`/`0x29C0` are (large, distinctive, concentrated in
a narrow subsystem). Don't re-run a plain frequency scan without the concentration filter
(`|offset| >= 0x1000`, small function count) — it just reproduces this noise.

`-0x23A8($reg)` → sibling global `0x8011DC58` (same `funcs_3.c`/`funcs_4.c` cluster as the now-
closed item -291, but each site's downstream write differs — no clean byte-identical shape found)
needs the same S392/S393-style per-site mechanistic classification before any patch, not a blanket
regex. Not started. ~111 non-canonical `-0x5824` sites (same global as item -291/-293, reached
through a non-adjacent load/deref pair with intervening code) also need per-site treatment, not
started.

**Wait-for-recurrence breadcrumb (passive, do not chase):** two independent single-occurrence
crashes in `submitSceneNodeRender`'s call subtree at the identical `hangarbay-entry` n=2600, from
s456's and s457's queued confirm soaks (different `last-guest-pc` each time — per the
crash-signature-blindness trap, item -200, not confirmed as one bug). If a 3rd occurrence lands
(same or different session), that's worth a dedicated idiom-class audit. s458's own run was clean
(0 crash) — does not add a 3rd data point.

## Process notes

Before starting: `ps aux | grep loop.sh` and `tail -20 scratch/agent/loop.log`, cheaply, once —
s454/s455 hit a real concurrent-process collision (both resolved, see CURRENT-TRUTH item
-291/-292); a fresh collision is unlikely but check anyway rather than assume it can't recur.

The account hit its monthly Claude spend limit multiple times earlier this session cycle
(`loop.log` shows repeated `HARD CAP reached` / `api_error_status: 429` entries) — if a future
iteration opens with an immediate 429, that's the same operational/billing condition recurring,
not a new bug to chase.

`cmake --build` takes ~2 minutes — always launch it as a background Bash command
(`run_in_background: true`) and continue other prep work (or just wait for the task-completion
notification) rather than foreground-polling it.
