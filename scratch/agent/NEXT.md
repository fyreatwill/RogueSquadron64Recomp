# NEXT work unit

HYPOTHESIS-ID: item-317-heap-dequeue-derived-ptr-guard-confirm

## s490 summary: item -316 closed 2/2; item -317 found, fixed (after catching and correcting a wrong
first attempt), 1st confirm clean, 2nd queued

Item -316's 2nd confirm soak (`s489_dl_alloc_propagation_confirm`) came back clean for item -316
itself (0 `dl-alloc-propagation-guard` fires) but its raw log showed four unrelated sibling guards
(`freelist-next-guard`, `generic-cache-guard`, `dl-list-append-rwrite-guard`,
`dl-list-reset-rnode-guard`) fire in sequence on the same corrupted pointer value right before a
SIGBUS in `heapFreeListDequeue` — the same "-312..-316" signature. Traced it: an unguarded
`ctx->r4` reload (from the free-list-cache-head global `0x801163B0`) feeds a derived pointer
(`ctx->r16 = ADD32(ctx->r4, 0x8)`) that's dereferenced unguarded 6 instructions later. **A first fix
attempt validated the wrong register** (`ctx->r4`, which turned out to have path-dependent meaning
at a shared control-flow label reachable from a second, unrelated branch) and fired 660,261 times in
one soak while its sibling guards stayed at 0 — caught by that exact mismatch, not by a crash.
Corrected to validate `ctx->r16` (the actually-dereferenced pointer) directly. Re-verified clean: 0
fires on the corrected guard, `hangarbay-entry` n=31 (positive control), crashed on the
already-catalogued `loadCutsceneAssetsByIndex+1860` family (unrelated). 2nd independent confirm
queued (`s490_heap_dequeue_derived_ptr_confirm.sh`, currently the only item in `soak_queue/`).

## IMPORTANT UPDATE (landed after s490 committed -- read this before anything else below)

A classification subagent dispatched during s490 kept running after the session closed and reported
back afterward. Hand-verified finding, already folded into `docs/CURRENT-TRUTH.md` item -317: **the
shipped `HEAP_DEQUEUE_DERIVED_PTR_GUARD` fix is CORRECT but INCOMPLETE.** `ctx->r16` (the exact
derived pointer just guarded at `0x8000D760`) is dereferenced at least 9 MORE times later in the same
`heapFreeListDequeue` function body, all still completely unguarded (approx. guest addrs `0x8000D794`,
`0x8000D7A0`, `0x8000D7AC`, `0x8000D7C8`, `0x8000D7E4`, `0x8000D7E8`, `0x8000D7F0`, `0x8000D7F8`), plus
a second-generation derived pointer (`ctx->r5 = ADD32(ctx->r16, 0X10)`) that likely propagates the same
gap even further downstream. It also found ONE more confirmed VULNERABLE site under the strict
same-function/same-register criterion: `funcs_4.c` reload `0x80012E94` -> derived `ctx->r18` at
`0x80012EF0` -> an 8-field unguarded struct-init block starting at guest `0x80012F14`. **Treat item
-317 as still OPEN, not closed**, regardless of what the queued confirm soak shows (a clean confirm on
the FIRST store's guard doesn't mean the other 9+ unguarded uses in the same block are safe -- they
share the same corrupted pointer and just haven't been hit yet in 300s of soak). This session's own
subagent explicitly flagged a structural blind spot in its scan (register-rename/global-round-trip
indirection, ~73/88 of the 184 reload sites use exactly this idiom) -- so treat "1 more vulnerable site"
as a floor, not a ceiling.

## This session's next work unit (supersedes the "if clean, mark CLOSED 2/2" instruction below given
the update above -- fold the confirm result in as evidence, but do NOT close item -317 on it alone)

1. Read the new `SOAK-RESULTS.md` line for `s490_heap_dequeue_derived_ptr_confirm` (the loop will
   have run it between iterations). Grep its `run.log` (NOT just the probe.sh summary line — it omits
   guard-tag detail) for `heap-dequeue-derived-ptr-guard` fires, sibling guard fires, `hangarbay-entry`
   count, and the `[CRASH]` tags. Fold into `docs/CURRENT-TRUTH.md` item -317 and `PORTING-STATE.md` as
   evidence for the FIRST store's guard specifically -- but do not mark item -317 CLOSED regardless of
   outcome; go straight to extending the guard per step 1a below.
1a. Extend `HEAP_DEQUEUE_DERIVED_PTR_GUARD` (or wrap the whole downstream block in one validity check
   right after the derived-pointer computation at `0x8000D744`, which is cleaner than guarding each of
   the 9+ individual stores separately) to cover every remaining unguarded `ctx->r16` use in
   `heapFreeListDequeue`, plus the `ctx->r5 = ADD32(ctx->r16, 0X10)` second-generation pointer and ITS
   downstream uses. Read the full block (`funcs_3.c`, guest `0x8000D744` through wherever `ctx->r16`/
   derived-from-r16 registers stop being used) directly before designing the fix -- don't trust the
   subagent's line list without a direct read, same discipline as always. Then fix the new `funcs_4.c`
   0x80012E94/0x80012EF0 site (separate, unrelated function, needs its own guard).
2. **Before trusting ANY fire count on a brand-new guard as "rare corruption, working as intended,"
   compare it against this session's sibling guards in the SAME run.** Every guard in this whole
   `-312..-317` lineage has historically fired 0-4 times per soak. A three-, four-, or five-digit fire
   count on a new guard while its siblings stay near 0 is not a bigger discovery — it is very likely a
   guard placement bug (checking a proxy register with path-dependent meaning, same mistake this
   session made and caught). Investigate the guard's OWN correctness before folding a high fire count
   into the ledger as evidence of anything.
3. If item -317 closes clean with nothing new surfaced: the deferred item from this session is the
   **control-flow-aware blanket sweep** of the other 183 sites sharing item -317's reload idiom
   (`ctx->r4 = MEM_W(ctx->r4, 0X63B0);`, `funcs_3.c`/`funcs_4.c`). This session's own classification
   subagent's first attempt FAILED its sanity check against the one known-true instance — do not
   reuse its raw tally. A correct sweep needs, PER SITE: (a) find every `ADD32`-derived-pointer
   register set from the reload, (b) find its first dereference, (c) **check whether the dereference
   site sits at or after a label that has ANOTHER `goto`/branch INTO it from elsewhere in the same
   function** (grep `goto L_<addr>` for every label between the reload and the dereference) — if so,
   trace what the derived register's base was on THAT alternate path before assuming the guard can
   validate the reload's own register; (d) validate the ACTUALLY-DEREFERENCED register directly, never
   an upstream proxy — this session's own correction is the template. Given the false-positive risk
   just demonstrated, do this INCREMENTALLY (a handful of sites at a time with a live-verify checkpoint
   comparing new-guard-fires against sibling-guard-fires) rather than a single 183-site blanket regex,
   unlike the s485 84-site precedent which didn't have this shared-label hazard to contend with.
4. If the confirm reveals something new instead: same standard as always — 2 direct source reads
   before proposing a fix, and this session's specific new rule (compare fire rate against siblings)
   before trusting a first live-verify.

## Regen/build/soak recipe (only needed if a new fix is designed — reading SOAK-RESULTS.md needs
neither)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for the expected counts, no errors, no SKIPPED lines other than the known-permanent
S392_H3A/H3B item -290 remainder) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule — see
`scratch/agent/soak_queue/s490_heap_dequeue_derived_ptr_confirm.sh` for the current full list, add
`ROGUESQ_LOG_<NEW_GUARD_NAME>=1` for whatever the new guard is named. **Live-verify BEFORE queueing
the 2nd confirm and BEFORE folding into the ledger** — this session's own near-miss (660K false-positive
fires) would have gone straight into the ledger as "1st confirm clean, 2nd queued" if the numbers
hadn't been checked against siblings in the same run.

## Soak queue status
1 item queued: `s490_heap_dequeue_derived_ptr_confirm.sh` (item -317's 2nd independent confirm).
