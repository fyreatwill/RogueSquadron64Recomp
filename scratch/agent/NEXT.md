# NEXT work unit

HYPOTHESIS-ID: songtempo-table-guard-29c0

## s457 close-out: item -294 (next slice of item -292's `SONGTEMPO_TABLE_GUARD`) EXECUTED

`tickScheduledSongEvents` (5 sites) + `stepSongPitchBendLanes` (5 sites) built, live-verified,
soaked-queued: 0 `songtempo-table-guard` fires, 0 `dl-list-append-guard` fires (both match
established 0-fires baselines). 14/43 total sites of item -292 now fixed. Confirmation soak queued
to `scratch/agent/soak_queue/s457_songtempo_readers_confirm.sh`. Full detail: `docs/CURRENT-TRUTH.md`
item -294, `PORTING-STATE.md` Session 457.

**Also folded in, filed not chased:** the live-verify crashed at 113.5s on an unrelated signature
(`pc-symbol=heapFreeListDequeue+32596`/`submitSceneNodeRender+45220`, `last-guest-pc=0x8000d92c`,
`hangarbay-entry` n=2600) — 2nd crash in 2 consecutive sessions inside `submitSceneNodeRender`'s
call subtree at the identical `hangarbay-entry` n=2600 (previous one: item -291's own queued
confirm soak, `pc-symbol=submitSceneNodeRender+29928`, `last-guest-pc=0x80010874`). Different
`last-guest-pc` both times — per the crash-signature-blindness trap (item -200), do NOT assume
these are the same bug without checking further; they're two independent single-occurrence data
points in the same hot rendering call chain. Worth a dedicated audit if a 3rd occurrence lands.
Not a discriminating measurement for anything currently in flight — no action needed unless it
recurs.

## Priority 1: finish item -292's `SONGTEMPO_TABLE_GUARD` (29 sites remaining)

`updateSongTempoTickRate` (4 sites), `tickScheduledSongEvents` (5 sites), `stepSongPitchBendLanes`
(5 sites) — 14/43 total — are DONE and verified. The remaining 29 sites are the same idiom
(`0x29C0($reg)` → global `0x801529C0`, MusyX song-track pointer), in 3 more reader functions, all
in `funcs_25.c`:
- `stepSongModulationLanes` (5 sites, ~283 lines, `funcs_25.c:3136-3419`)
- `advanceSongRegion` (12 sites, ~539 lines, `funcs_25.c:3419-3958`)
- `stepActiveSongTracks` (12 sites, ~744 lines, `funcs_25.c:1913-2657`)

Do `stepSongModulationLanes` next — same method as the prior 3: **read the whole function body
first**, identify each site's real bail semantics (before-prologue → bare `return;`; inside an
existing loop with its own exit label or idiom → reuse that; past all loops, near the real
epilogue → duplicate the epilogue) — do NOT templatize blindly. Per s455's original scan, this
function shares `stepSongPitchBendLanes`'s per-lane outer-loop shape (same 0x24 stride / 0x900
bound structure), so its bail semantics should closely mirror `spbl1`-`spbl5`'s "abandon this
lane, advance to the next" pattern — but confirm by reading, don't assume.

`advanceSongRegion` and `stepActiveSongTracks` are unusually large and their tail sections showed
an odd stack-frame mismatch on a first skim (prologue pushes more than the visible epilogue pops)
— worth checking for the recompiler's cross-function shared-tail-merge behavior (seen elsewhere as
`lvj_checkComplexObjectives`/`audioCompandS16`/`__OSGlobalIntMask`, CLAUDE.md) before trusting a
single simple bail-to-epilogue pattern; may need per-site individual verification rather than a
uniform template. Do these two last.

Standard pipeline once patches are written: verify regex anchors match exactly once each with a
standalone Python probe BEFORE touching `fixup_game_funcs.py` (catches typos before spending a
build cycle) → raw regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` — audit the report
counts against a direct grep, don't just trust the number) → `cmake --build` → `strings` sanity →
live-verify (`tools/probe.sh`, full 300s/250s-keys schedule, ALL passive guard env vars armed —
copy the list from `scratch/agent/soak_queue/done/s454_songtempo_confirm...sh` or this session's
`s457_songtempo_readers_confirm.sh`) → queue confirmation soak → exit contract.

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

Before starting: `ps aux | grep loop.sh` and `tail -20 scratch/agent/loop.log`, cheaply, once —
s454/s455 hit a real concurrent-process collision (both resolved, see CURRENT-TRUTH item
-291/-292); a fresh collision is unlikely but check anyway rather than assume it can't recur.

The account hit its monthly Claude spend limit multiple times earlier this session cycle
(`loop.log` shows repeated `HARD CAP reached` / `api_error_status: 429` entries) — if a future
iteration opens with an immediate 429, that's the same operational/billing condition recurring,
not a new bug to chase.
