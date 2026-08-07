# NEXT work unit

HYPOTHESIS-ID: songtempo-table-guard-29c0

## s456 close-out: item -291 (`DL_LIST_APPEND_GUARD`, 57 sites) is EXECUTED and CLOSED

Built, live-verified, soaked clean: 0 `[CRASH]` across a full 300s schedule, 0
`dl-list-append-guard` fires (matches the established 0-fires baseline for this whole guard-idiom
family — not an open question), `hangarbay-entry` reached n=3000. Confirmation soak queued to
`scratch/agent/soak_queue/s456_dl_list_append_confirm.sh`. Full detail: `docs/CURRENT-TRUTH.md`
item -293, `PORTING-STATE.md` Session 456.

## Priority 1: finish item -292's `SONGTEMPO_TABLE_GUARD` (39 sites remaining)

`updateSongTempoTickRate` (4/43 sites of the `0x29C0($reg)` → global `0x801529C0` MusyX
song-track-pointer idiom) is DONE and verified (s455). The remaining 39 sites are the same idiom,
in 5 more reader functions, all in `funcs_25.c`:
- `tickScheduledSongEvents` (5 sites, ~200 lines)
- `stepSongPitchBendLanes` (5 sites, ~279 lines)
- `stepSongModulationLanes` (5 sites, ~283 lines)
- `advanceSongRegion` (12 sites, ~539 lines)
- `stepActiveSongTracks` (12 sites, ~744 lines)

Do the two smallest (`tickScheduledSongEvents`, `stepSongPitchBendLanes`) next — same method as
`updateSongTempoTickRate`: **read the whole function body first**, identify each site's real bail
semantics (before-prologue → bare `return;`; inside an existing loop with its own exit label →
reuse that label; past all loops, near the real epilogue → duplicate the epilogue) — do NOT
templatize blindly, each function's control flow differs. The two largest (`advanceSongRegion`,
`stepActiveSongTracks`) are unusually large and their tail sections showed an odd stack-frame
mismatch on a first skim (prologue pushes more than the visible epilogue pops) — worth checking
for the recompiler's cross-function shared-tail-merge behavior (seen elsewhere as
`lvj_checkComplexObjectives`/`audioCompandS16`/`__OSGlobalIntMask`, CLAUDE.md) before trusting a
single simple bail-to-epilogue pattern; may need per-site individual verification rather than a
uniform template.

Standard pipeline once patches are written: raw regen (`make_elf.py` → `N64Recomp` →
`fixup_game_funcs.py` — audit the report counts against a direct grep, don't just trust the
number) → `cmake --build` → `strings` sanity → live-verify (`tools/probe.sh`, full
300s/250s-keys schedule, ALL passive guard env vars armed — copy the list from
`scratch/agent/soak_queue/done/s454_songtempo_confirm...sh` or this session's
`s456_dl_list_append_confirm.sh`, plus `ROGUESQ_LOG_SONGTEMPO_TABLE_GUARD=1`) → queue confirmation
soak → exit contract.

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

## Process notes

Before starting: `ps aux | grep loop.sh` and `tail -20 scratch/agent/loop.log`, cheaply, once — s454/
s455 hit a real concurrent-process collision (both resolved, see CURRENT-TRUTH item -291/-292); a
fresh collision is unlikely but check anyway rather than assume it can't recur. Also watch for a
delegated subagent reflexively delegating further instead of executing (happened s454/s455 per
NEXT.md's prior write-up) — if a subagent's report reads like a plan/promise rather than a
completed result, check actual repo state (`git log`, file mtimes) before trusting it.

The account hit its monthly Claude spend limit multiple times this session cycle (`loop.log` shows
repeated `HARD CAP reached` / `api_error_status: 429` entries around 10:17–11:33 today) before this
iteration's own invocation succeeded. This is an operational/billing condition, not a code issue —
if a future iteration opens with an immediate 429, that's the same condition recurring, not a new
bug to chase.
