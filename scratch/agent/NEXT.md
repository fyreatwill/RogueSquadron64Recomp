# NEXT work unit

HYPOTHESIS-ID: item-317-step3-183-site-blanket-sweep

## s493 was a MAINTENANCE iteration (CURRENT-TRUTH.md compaction)

s493 ran Step 0 of ITERATION.md (CURRENT-TRUTH.md was over the 60,000-byte trigger) and compacted it
from 60,657 to 41,025 bytes (net -200 lines by `git diff --numstat`), migrating the full s488-492
item -316/-317 narrative to `docs/PROJECT-OVERVIEW.md` §21. No experiment ran this session. Read
PROJECT-OVERVIEW §21 if you need the full derivation behind item -317 (registers, addresses, fire
counts, the s490 methodology lesson) — CURRENT-TRUTH.md itself now only carries the compact pointer.

## This session's work unit: item -317 step 3, the 183-site blanket sweep

Item -317 steps 1 (`heapFreeListDequeue`) and 2 (`funcs_4.c` `buildOrientedFaceGeometry`) are both
FULLY CLOSED, 2/2 independent confirms each. The only open scope in the entire -312..-317 lineage is
**step 3**: the wider ~183-184-site population of the same reload idiom
(`ctx->rL = MEM_W(ctx->rL, 0X63B0);`, the free-list-cache-head global at `0x801163B0`) across
`funcs_3.c`/`funcs_4.c`, of which only 2 sites (steps 1 and 2) have been directly traced and fixed so
far.

**Why this needs new tooling, not more manual traces**: s490's own naive textual-proximity classifier
(a subagent scan) mis-scoped its very first flagged site — it could not detect a shared-control-flow-
label hazard where the same register has different provenance depending on which of two paths reaches
it, which is exactly what made s490's first fix attempt false-positive 660,261 times in one soak
before live-verify caught it. A blanket sweep at this scale needs a **scripted, control-flow-aware
tracer** (Python, alongside the prior `scratch_s465_*`/`scratch_s482_*` scan scripts in N64Recomp) that,
for each site:
1. Traces the register actually DEREFERENCED forward from the reload (not just the reload's own
   target register) to find every real dereference.
2. For each dereference, traces backward through every control-flow path that can reach it, and
   confirms every path has consistent, already-validated provenance for that register — not just the
   textually-nearest guard.

**Positive control before trusting it at scale**: the tracer must correctly flag BOTH already-known-bad
sites (step 1's `heapFreeListDequeue` `0x8000D760` and step 2's `funcs_4.c` `0x80012F14` struct-init
block) as vulnerable, AND correctly clear a manually-verified sample of benign sites (e.g. the four
existing sibling guards on step 2's own path that read `ctx->r2`/`ctx->r3` and never touch the
free-list-derived pointer) — before it is trusted to classify the remaining ~181 sites.

**Scope this as its OWN work unit** (tool-building), not a single guard fix — it may take more than
one iteration. If it proves too large for one session, checkpoint the tracer script + its positive-
control results in `scratch/` and hand off via NEXT.md rather than guessing at unverified sites.

**Fallback if step 3 tooling is judged too large for this iteration**: either (a) a fresh
frequency-scan angle — both `lui`+`lw` and `lui`+`sw` are structurally dry at the >=20-site tier per
s488/s476 — or (b) the M5 lead-check cadence (last checked s488, due after 3+ more sessions have
passed, i.e. now due), or (c) wait for a 7th lineage instance to surface organically via a soak crash,
as items -316→-317 and -317 step 2 both did.

## Regen/build/soak recipe
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for expected counts, no errors, no SKIPPED lines other than the known-permanent
S392_H3A/H3B item -290 remainder; the script now REFUSES a second run on already-patched files via
its own `RS64_FIXUP_APPLIED` marker — regenerate from scratch if you need to re-run it) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (NOT `~/Documents/Tools/N64Recomp/build`
— that's the recompiler CLI's own build and silently no-ops) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule. Live-verify BEFORE queueing a 2nd confirm and BEFORE folding
into the ledger.

## Soak queue status
Empty (last item, `s492_oriented_face_derived_ptr_confirm.sh`, ran clean and moved to done/).
