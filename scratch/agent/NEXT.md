# NEXT work unit

HYPOTHESIS-ID: item-317-funcs4-buildorientedfacegeometry-r18-provenance

## s491 summary: item -317's own remainder CLOSED (1st confirm clean, 2nd queued); funcs_4.c sibling
site traced far enough to know it needs its own dedicated investigation, deferred not guessed at

s490 fixed the FIRST unguarded derived-pointer write in `heapFreeListDequeue` (`funcs_3.c`, guest
`0x8000D760`) but a post-session classification pass found 9+ MORE unguarded uses of the same
`ctx->r16` pointer later in the same function, plus a second-generation `ctx->r5 = ADD32(ctx->r16,
0X10)` pointer. **s491 direct-traced the whole downstream span (guest `0x8000D75C`-`0x8000D8A8`)
and confirmed it's a single straight-line block with exactly one external entry point** (the
`L_8000D75C` label, reached only by the two paths s490 already characterized) — so the fix widened
the EXISTING check to `goto L_8000D8A8` (skip the entire rest of the block, an existing label,
itself pure arithmetic) instead of adding 14 more per-site checks. `ctx->r5` needed no separate
check (small constant offset from an already-validated base, same convention as -312..-316).
Build-verified clean, live-verified: **0 fires on the guard, 0 fires on any of ~20 sibling guard
families**, `hangarbay-entry` n=31 (positive control), crashed on the already-catalogued
`BREADCRUMB6`/`buildPositionAndCallTransformHelper` near-zero-pointer family (unrelated, filed
since s273). 2nd independent confirm queued
(`scratch/agent/soak_queue/s491_heap_dequeue_blockskip_confirm.sh`).

## This session's next work unit: trace `ctx->r18`'s full provenance in `buildOrientedFaceGeometry`
(`funcs_4.c`) before designing a guard — do NOT reuse the `heapFreeListDequeue` fix shape blindly

The `funcs_4.c` site s490's subagent flagged (reload `0x80012E94` → derived `ctx->r18` at
`0x80012EF0` → an 8-field unguarded struct-init block from `0x80012F14`) is **structurally different
from `heapFreeListDequeue`'s `ctx->r16`, not a simple copy-paste of the same fix**:

1. `ctx->r18` ($s2) in `buildOrientedFaceGeometry` is a GENERAL-PURPOSE register reassigned from at
   least 6 different sources spread across the function (`ADD32(ctx->r4,0)`, `ADD32(ctx->r7,0)` x4,
   `ADD32(ctx->r18,0X8)` chained twice, at guest addresses spanning roughly `0x80012750`-`0x80012EF0`)
   — nothing like `heapFreeListDequeue`'s single derived-once pointer.
2. It has its OWN separate multi-path shared-label hazard: a `goto L_80012F08` at guest `0x80012E24`
   (reached from a branch well BEFORE the local `0x80012EF0` computation) lands on the SAME tail
   label the `0x80012EF0` fallthrough path also reaches. **Confirmed by direct read**: `ctx->r18` is
   already READ at guest `0x80012E1C` (`ctx->r3 = ADD32(ctx->r18, 0X20)`), which is BEFORE its "own"
   computation at `0x80012EF0` in program order — so on the `goto`-in path, `ctx->r18` carries a
   value from much earlier in the function, not the local `0x80012E94` reload chain at all. This is
   the exact same "shared label, different provenance per path" shape that bit s490's FIRST (wrong)
   fix attempt.

**Do the same full-provenance trace s490/s491 did for `heapFreeListDequeue`, applied to this
function**, before writing any patch:
1. Read the WHOLE `buildOrientedFaceGeometry` function (funcs_4.c, starts at guest `0x80012E0C`-ish
   region backward through its true start — grep `RECOMP_FUNC void buildOrientedFaceGeometry` for the
   opening line; it's a large function, likely 800+ lines / several hundred guest instructions).
2. For EVERY assignment to `ctx->r18`, note its source and which control-flow region it dominates.
3. For the SPECIFIC target (the `0x80012EF0`→`0x80012F14`-onward struct-init block), enumerate every
   `goto`/branch that can reach it and trace `ctx->r18`'s value on EACH path back to its most recent
   assignment on that path — same discipline as s490's correction (validate the register ACTUALLY
   dereferenced, on ALL paths that reach the dereference, never assume one path's provenance covers
   another).
4. Once every path's `ctx->r18` provenance is known, design the check placement: if all paths
   converge at a single label before the first deref (like `heapFreeListDequeue`'s `L_8000D75C`),
   validate there once, block-skip style. If they DON'T converge cleanly (possible here, given
   `ctx->r18` is reused this heavily), per-path or per-site checks may be unavoidable — that's fine,
   just don't assume the block-skip shape transfers without re-verifying the entry-point topology.
5. Before trusting the FIRST live-verify's fire count: compare it against sibling guards in the same
   run (s490's rule). A three-, four-, or five-digit fire count while siblings sit at 0 means the
   check is validating the wrong register on some path — go back to step 3, not to the ledger.
6. If this closes clean: the deferred wider-183-site blanket sweep (item -317's other open scope,
   needs control-flow- and register-rename-aware tooling per s490/s491's own methodology, not a
   repeat of s490's failed textual-proximity scan) becomes the next candidate, or a fresh
   frequency-scan angle, or wait for a new breadcrumb (both `lui`+`lw` and `lui`+`sw` idiom classes
   are structurally dry at the >=20-site tier per s488).

## Regen/build/soak recipe
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for expected counts, no errors, no SKIPPED lines other than the known-permanent
S392_H3A/H3B item -290 remainder) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule — see
`scratch/agent/soak_queue/s491_heap_dequeue_blockskip_confirm.sh` for the current full list, add
`ROGUESQ_LOG_<NEW_GUARD_NAME>=1` for whatever the new guard is named. Live-verify BEFORE queueing a
2nd confirm and BEFORE folding into the ledger.

## Soak queue status
1 item queued: `s491_heap_dequeue_blockskip_confirm.sh` (item -317's own-remainder fix, 2nd
independent confirm).
