# NEXT work unit — M3: confirm/refute "voice+0x34 corruption is
uninitialized heap memory, not a corrupted write" (s114)

s113 closed both open hypotheses about a *write* mechanism (RSP ucode,
s112; computed-offset guest-C store, s113) with decisive source-level
refutations, no build/soak needed for either. It then found, as an
unplanned byproduct of the same audit, a well-supported new explanation
that doesn't involve a write bug at all. Read PORTING-STATE.md's Session
113 entry before doing anything else; this file only has the actionable
summary.

## Why this is the next work unit

Three independent static facts now agree that the `-0x664C` sample-stream
node's offsets `0x8`/`0x10` (the two fields `fillSampleStreamRange` sums
into the corrupted `devAddr`, per s103) are **never initialized by any
guest code**:

1. The node-claim path, `acquireSampleStreamBlock`, never touches
   `0x8`/`0x10`/`0x14` (s103).
2. The node allocator, `initSampleStreamBlockCache`
   (`funcs_23.c:12103`, guest `0x8008F858`), only ever writes `0x4` and
   `0x14` per node (s113) — never `0x8`/`0x10`.
3. No other file in the recompiled tree references the exact literal
   `-0X664C` at all (`grep -rl -- "-0X664C" RecompiledFuncs/*.c` returns
   only `funcs_23.c`, s113) — so there is no fourth function anywhere
   that could be the missing initializer.

Plus: `rs_malloc` (`funcs_0.c:2743`, the allocator these nodes come from)
has no `memset`/`bzero` call anywhere in its body — it does not zero
returned memory (s113).

Put together: `fillSampleStreamRange` reads `node->0x8`/`node->0x10` and
sums them into `devAddr` — but nothing ever wrote those fields. It's
reading whatever `rs_malloc` handed back: leftover contents of previously-
used heap memory. This would explain, with an actual mechanism instead of
a label, both of the two facts every prior hypothesis in this chain
(s85-s104) struggled to explain at once: the **structured, tag-like**
byte patterns in the corrupted values (s102's `"lg?r"`/`"wi?g"` — plausible
fragments of leftover asset-name/string data, not noise) and the **byte-
identical reproduction across independent runs/rebuilds** (s91/s93 — not a
race, just a deterministic function of asset-load heap history that is
itself deterministic per boot).

This is three static facts, not a runtime observation — strong, but not
yet the two-independent-runtime-lines bar this file's own rules ask for
before writing "confirmed" into CURRENT-TRUTH. One cheap, narrowly-
targeted log turns it into a runtime fact.

## What's confirmed (do not re-derive)

- Hypothesis (a) RSP MusyX ucode write path: **closed** (s112,
  `factor5_ucode_b` never called anywhere in `src/`).
- Hypothesis (b) computed-offset guest-C write to `voice+0x34`: **closed**
  (s113, exhaustive read of all 3 files referencing the voice-array
  base — every store terminates in a literal, non-0x34 offset).
- `initSampleStreamBlockCache` (`funcs_23.c:12103`): the `-0x664C` list's
  node allocator, `rs_malloc`s `count*0x18`-byte nodes, init loop at
  `funcs_23.c:12204-12228` writes only `0x4` (next-pointer) and `0x14`
  (data-buffer address, `base+n*0x600`) per node.
- `acquireSampleStreamBlock`'s node-claim path never touches
  `0x8`/`0x10`/`0x14` (s103) — already confirmed, don't re-derive.
- `fillSampleStreamRange` (`funcs_23.c:12473`, guest `0x8008FAAC`) computes
  `entry.devAddr = node->0x8 + node->0x10` (s103) and its own incoming
  arguments are already corrupted at function entry, matching the known
  `devAddr` pattern byte-for-byte (s104) — both facts stand, this session
  doesn't change them, it explains *why* they're true.
- `rs_malloc` (`funcs_0.c:2743`): no zeroing call in its body — confirmed
  by a full read of the function, not a guess.
- The `tickAudioChannel`/`musyx-gate1`/voice-trigger-chain investigative
  thread is retired (s110, 5 null sessions) — irrelevant to this question,
  do not resume it.
- The hangar-tick-family guard program (5 classes) is closed pending a
  free positive control — do not re-soak it in isolation.
- `fixup_game_funcs.py` is still not idempotent — full ELF regen before
  every fixup run, run it exactly once per regen.

## The work unit

1. **Land one instrument, following the existing `_fill_range_args_patch`
   pattern** (`N64Recomp/fixup_game_funcs.py:922`, targets
   `RECOMP_FUNC void fillSampleStreamRange(...)`'s header with a regex,
   same style as `_stream_tag_patch`/`_musyx_dma_call_patch`). New patch
   should target `initSampleStreamBlockCache`'s header
   (`RECOMP_FUNC void initSampleStreamBlockCache\(uint8_t\* rdram, recomp_context\* ctx\) \{`)
   and insert a log statement **inside the per-node init loop**
   (`L_8008F8FC`, right after the existing `0x4`/`0x14` stores at
   `funcs_23.c:12205-12216`), reading the node's raw `0x8`/`0x10` fields
   *before this function ever writes anything else to them* (it doesn't,
   confirmed above — this read is genuinely "as rs_malloc handed it
   back"). Gate on a new env var, e.g. `ROGUESQ_LOG_STREAM_NODE_INIT=1`,
   same on/off caching idiom as every existing gate in this file
   (`s_..._enabled < 0` → check `getenv` once). Log: node index, node
   address, raw `MEM_W(0x8, node)`, raw `MEM_W(0x10, node)`. Cap the log
   (e.g. first 32 nodes) — this only runs once per cache init, so a cap
   is generous, not restrictive.
2. **Positive control is automatic**: the function runs exactly once at
   MusyX init with a known node count (already used to size the
   `rs_malloc` call). The log should fire exactly that many times. If it
   fires 0 times, the instrument didn't land where intended; that is a
   build/patch bug, not a null result.
3. **Regen order**: `make_elf.py` → `N64Recomp` → `fixup_game_funcs.py`
   (once) → `cmake --build`. Verify via `grep -c` on the regenerated
   `funcs_23.c` that the patch landed exactly once before building.
4. **Soak once, discriminating outcome named up front**: if the logged
   `0x8`/`0x10` values are already non-zero at allocation time (before
   any consumer has run), and especially if any of them decode to the
   same tag-like ASCII shapes s102 characterized (`"lg?r"`/`"wi?g"` or
   similar), that's direct runtime confirmation of "uninitialized heap
   memory read as data," turning this from a well-supported static
   hypothesis into a closed root cause. If they read as all-zero, the
   "never initialized" static claim was still right but `rs_malloc`
   apparently does return zeroed memory in practice (e.g. first-ever use
   of fresh heap pages) — in which case the corruption must appear
   *later*, between allocation and `fillSampleStreamRange`'s read, and
   the next step becomes finding what reuses this heap region in between
   (a genuine second mechanism, not the same one).

## Do not

- Do not re-search for a computed-offset or RSP-ucode write path — both
  closed (s112, s113).
- Do not re-derive `acquireSampleStreamBlock`'s or
  `initSampleStreamBlockCache`'s already-confirmed field lists.
- Do not resume the `tickAudioChannel`/voice-trigger-chain (retired
  s110).
- Do not re-soak the five hangar-tick-family guarded classes in
  isolation.
- Do not run `fixup_game_funcs.py` more than once per ELF regen.
- Do not cite `ra=0x00000000`, or re-open "random/race/stomp" framings
  for the `devAddr` corruption pattern itself (refuted s92) — this
  session's hypothesis is compatible with "deterministic," not a
  reopening of the race framing.

## Housekeeping flagged, not this session's job either

`docs/CURRENT-TRUTH.md` is well over the ~35KB target in CLAUDE.md/
ITERATION.md (now larger after s113's addition). Flagged for many
sessions running without action — worth a dedicated compression work
unit (migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md, prune superseded detail — especially the now-closed
hangar-tick-family guard narration, the now-closed RSP-ucode detour, and
the now-closed computed-offset-write detour) paired with a real
experiment per ITERATION.md (compressing docs alone does not count as an
ADVANCED work unit).
