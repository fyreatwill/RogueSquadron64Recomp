# NEXT work unit

HYPOTHESIS-ID: sibling-ptr-write-guard-23a8

## s459 close-out: item -296 (`-0x23A8` sibling-global audit) FOUND AND CLOSED, same session

Rule-8 mandatory pivot: s455/s457/s458 had all run `songtempo-table-guard-29c0` without closing
item -292 (24 sites remain). Rather than force a 4th consecutive iteration on that slug, this
session switched to a different, already-flagged-but-not-started M3 idiom-class audit: the
`-0x23A8($reg)` sibling global (`0x8011DC58`) item -291's own session (s454) had explicitly
scoped OUT of `DL_LIST_APPEND_GUARD` for lacking a clean byte-identical shape.

A fresh systematic re-scan found that assessment was only half right: the LOAD-TO-WRITE gap
really does vary site to site (no single blanket regex), but the WRITE shape itself, checked in
isolation, is uniform at 118/119 sites (`MEM_W(OFF, ctx->rN) = VAL;`). Patched all 119 sites via
individually-anchored literal patches (generated programmatically,
`scratch_s459_apply_patch.py`, N64Recomp repo, untracked), same "skip the write" remediation
precedent as `DL_LIST_APPEND_GUARD`/`FREELIST_NEXT_GUARD`. Full pipeline clean: regen/build/
`strings`/live-verify all green — 0 crash, 0 `sibling-ptr-write-guard` fires across a full
300s/250s-keys schedule. Confirmation soak queued to
`scratch/agent/soak_queue/s459_sibling_ptr_write_confirm.sh`. Full detail:
`docs/CURRENT-TRUTH.md` item -296, `PORTING-STATE.md` Session 459.

**This closes item -296 in the same session it was opened — no further action needed on this
hypothesis unless a future soak's `sibling-ptr-write-guard` fires (watch `submitSceneNodeRender`'s
10 sites specifically, per the breadcrumb note below).**

## Priority 1 (next iteration): resume item -292's `SONGTEMPO_TABLE_GUARD` (24 sites remaining)

Since this session's pivot fully closed the `-23A8` audit rather than leaving it half-finished,
`songtempo-table-guard-29c0` is no longer subject to rule 8's consecutive-iteration block —
resume it as the top priority next iteration. `updateSongTempoTickRate` (4), `tickScheduledSongEvents`
(5), `stepSongPitchBendLanes` (5), `stepSongModulationLanes` (5) — 19/43 total — are DONE and
verified. The remaining 24 sites are the same idiom (`0x29C0($reg)` → global `0x801529C0`, MusyX
song-track pointer), in the last 2 reader functions, both in `funcs_25.c`:
- `advanceSongRegion` (12 sites, ~539 lines)
- `stepActiveSongTracks` (12 sites, ~744 lines)

Do `advanceSongRegion` next (smaller of the two). Same method as all prior slices: **read the
whole function body first** (in `N64Recomp/RecompiledFuncs/funcs_25.c` — the live regenerated
copy), identify each site's real bail semantics (before-prologue → bare `return;`; inside an
existing loop with its own exit label/idiom → reuse that; past all loops, near the real epilogue
→ duplicate the epilogue) — do NOT templatize blindly.

**Both `advanceSongRegion` and `stepActiveSongTracks` were flagged in earlier sessions' first-skim
as having an odd stack-frame mismatch** (prologue pushes more than the visible epilogue pops) —
worth checking for the recompiler's cross-function shared-tail-merge behavior (seen elsewhere as
`lvj_checkComplexObjectives`/`audioCompandS16`/`__OSGlobalIntMask`, CLAUDE.md) before trusting a
single simple bail-to-epilogue pattern; may need per-site individual verification rather than a
uniform template.

Standard pipeline once patches are written: verify regex/literal anchors match exactly once each
with a standalone Python probe BEFORE touching `fixup_game_funcs.py` → raw regen (`make_elf.py` →
delete stale `funcs_*.c` via `os.remove`/`glob`, sandbox-safe → `N64Recomp` → `fixup_game_funcs.py`
— audit the report counts against a direct grep, don't just trust the number) → `cmake --build`
(background; ~2 min) → `strings` sanity → live-verify (`tools/probe.sh`, full 300s/250s-keys
schedule, ALL passive guard env vars armed — copy the list from
`scratch/agent/soak_queue/s459_sibling_ptr_write_confirm.sh`, this session's own recipe, which
is now the most complete list, and add `ROGUESQ_LOG_SONGTEMPO_TABLE_GUARD=1`) → queue
confirmation soak → exit contract.

Once `advanceSongRegion` and `stepActiveSongTracks` are both done, item -292 CLOSES (43/43 sites).

## Discriminating instrument now live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

10 of item -296's 119 sites are in `submitSceneNodeRender` — the same function named in items
-293/-294's still-open "wait-for-recurrence breadcrumb" (2 independent single-occurrence crashes
in its call subtree, s456/s457, different `last-guest-pc` each time, still not confirmed as one
bug per the crash-signature-blindness trap). If ANY future soak (this session's own queued
`s459_sibling_ptr_write_confirm`, or any later one with the env var armed) shows a
`sibling-ptr-write-guard` fire specifically at one of `submitSceneNodeRender`'s 10 sites, that's
new evidence connecting the breadcrumb to a found-and-guarded root cause — worth immediate
follow-up, breaking the "passive, do not chase" rule for that specific case. 0 fires (anywhere,
this session) does not clear `submitSceneNodeRender` generally — only these 10 specific sites.

## Confirmed non-issues, do not re-investigate

`-0x25C0($s0)` (56 sites, `mallocCraftSelectionData`) and `-0x76E0($s0)` (46 sites, spread across
8 files) are compile-time-constant-based counter/scalar accesses, not pointer dereferences —
independently confirmed by both s454 and s455.

Small/ubiquitous offsets (`0x0`, `0x4`, `0x8`, `0xC`, `0x10`, `0x14`, `0x18`, `0x1C`, `0x20`...)
match hundreds of unrelated functions doing ordinary struct-field access — too broad to be a
distinct idiom class. Don't re-run a plain frequency scan without the concentration filter
(`|offset| >= 0x1000`, small function count).

`-0x23A8($reg)` → sibling global `0x8011DC58`: **CLOSED s459** (item -296, 119/119 sites,
`SIBLING_PTR_WRITE_GUARD`) — no longer open work, do not re-scan.

~111 non-canonical `-0x5824` sites (same global as the closed item -291, reached through a
non-adjacent load/deref pair with intervening code) still need per-site treatment — NOT started,
lower priority than item -292's remaining 24 sites (smaller class, less concentrated). A future
idiom-class-audit iteration could take this up using the same "normalize downstream shape, check
for a WRITE-only uniform pattern even if the load-to-use gap varies" method item -296 validated
this session.

## Process notes

Before starting: `ps aux | grep loop.sh` and `tail -20 scratch/agent/loop.log`, cheaply, once —
concurrent-process collisions are rare but have recurred before (s454/s455).

`cmake --build` takes ~2 minutes — always launch it as a background Bash command
(`run_in_background: true`) and continue other prep work, or wait for the notification, rather
than foreground-polling. Same for `tools/probe.sh` live-verify runs (300s+): launch backgrounded,
use the Monitor tool or TaskOutput's blocking wait rather than manual `sleep`/polling loops.

The account hit its monthly Claude spend limit multiple times in an earlier session cycle
(`loop.log` shows `HARD CAP reached` / `api_error_status: 429` entries) — if a future iteration
opens with an immediate 429, that's the same operational/billing condition recurring, not a new
bug to chase.
