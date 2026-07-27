# NEXT work unit — M3: find what writes/corrupts `voice+0x34` (s115)

s114 ran the discriminating instrument s113 proposed
(`ROGUESQ_LOG_STREAM_NODE_INIT=1`) and got a clean, twice-reproduced
result: the `-0x664C` sample-stream nodes read all-zero at allocation
time. Read PORTING-STATE.md's Session 114 entry before doing anything
else; this file only has the actionable summary.

## Why this reopens (not closes) the investigation

s113 claimed hypothesis (b) — "a literal-offset write to `voice+0x34`
exists in guest C" — was exhaustively refuted (an audit of all 3 files
referencing the voice-array base, claiming every store terminates in a
literal non-0x34 offset). **That claim was wrong.** s114 re-read
`N64Recomp/RecompiledFuncs/funcs_24.c:5866-5881` directly (not via
subagent) and found a literal `MEM_W(0X34, ctx->r4) = ctx->r3;` write
inside `musyxInitVoiceFromSample` — one of the 12 functions s113's own
list names as audited. This is not a new discovery: it's the exact
writer s105 already found and instrumented
(`ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`, still armed in the current build),
which s113 simply overlooked while re-auditing the same file.

Combined with s104's already-established mechanism — every
`fillSampleStreamRange` node-claim unconditionally recomputes
`node->0x8` from that function's own `a1`/`a3` arguments (already proven
corrupted at entry, byte-for-byte matching the known `devAddr` pattern)
— s114's all-zero-at-allocation result needs no new mechanism to explain
it: nodes start zero, the first real claim overwrites them with
already-corrupted data. **The chain closes cleanly back to "what
corrupts the value at `voice+0x34`" — exactly the question s105-s110
spent 5 sessions on before parking it (s110), and s111-s113 spent 3
sessions on before wrongly believing they'd closed it.**

## What's confirmed (do not re-derive)

- `initSampleStreamBlockCache`'s node-init loop writes all-zero into
  `0x8`/`0x10` at allocation (s114, 32/32 positive control, reproduced
  twice in one session). This is a real, replicated runtime fact, not
  single-source within this session — though it is the only session to
  have measured it.
- `fillSampleStreamRange`'s claim/eviction paths (`L_8008FCD8`/
  `L_8008FD48`/`L_8008FDB8`) unconditionally recompute `node->0x8` from
  the function's own already-corrupted `a1`/`a3` arguments (s104) — this
  is why allocation-time zero and read-time corruption don't conflict.
  Do not re-instrument this; it's a closed loop, not a gap.
- `musyxInitVoiceFromSample` (`funcs_24.c:5753`, guest `0x80092128`)
  writes `voice+0x34 = sampleDesc+0x4` via a literal offset (confirmed
  twice now: s105's read, s114's independent re-read). Base/stride
  (`G_BASE-0x6908` + `voiceIdx*0x88`) matches `musyxRenderVoiceSamples`'s
  own indexing by 3 independent field offsets (s105) — this is very
  likely the right function, not a coincidental match.
- `musyxInitVoiceFromSample`'s own instrument
  (`ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`) has fired **0/0 across two
  independent soaks**: s105 (full soak through hangar-flight death,
  ~140s+hold) and s114 (fresh cold-boot-through-title soak). Still not a
  positive control in either direction — this is a wide null, not a
  refutation. Do not soak a third time with only this flag and hope for
  a different outcome; that would be the 3rd non-discriminating attempt
  on the exact same instrument (ITERATION.md rule 8) — redesign first.
- Its two call sites (`funcs_22.c:3667`, `funcs_26.c:1418`) build
  `sampleDesc` fresh right before the call: one from a fixed global
  scratch address (`G_BASE-0x5358`, conditionally `-8`), the other from
  a small on-stack buffer populated from local registers (`$s1`-`$s6`)
  (s105). Neither traced further yet.
- The tickAudioChannel/voice-trigger call-chain mapping (s105-s110) is
  retired as a *blind repro* target (5 null sessions) but its call-graph
  findings are still valid, reusable facts: `soundMacroOpPlaySampleKeymap`
  (funcs_22.c, called from `tickAudioChannel`, funcs_23.c:3081, itself
  called only from `tickAllAudioChannels`) and
  `startStreamedSampleVoice` (funcs_26.c, called from
  `serviceVoicePoolFrame`, which has **zero** static/address-taken
  references anywhere in `RecompiledFuncs/*.c` — an indirect-call site,
  same shape as `musyxSynthFrame`'s caller before s101 found it).
- Hypothesis (a) RSP MusyX ucode write path: still closed (s112,
  unrelated to this — `voice+0x34` is written by real guest C, not RSP
  code).
- `fixup_game_funcs.py` is still not idempotent — full ELF regen before
  every fixup run, run it exactly once per regen.

## The work unit — pick ONE of these two angles, not both

**Angle (a) — resolve the `musyxInitVoiceFromSample` null via the call
graph, not another blind soak.** Before touching env vars or code:
source-read whichever of `serviceVoicePoolFrame`'s or
`tickAllAudioChannels`' own callers/gates would explain a permanent 0/0 —
e.g. does `serviceVoicePoolFrame`'s indirect caller even get resolved
under `ROGUESQ_STUB_MISSING_FUNCS=1` (could it silently no-op if
unresolved)? Is there a countdown/gate (like the `musyxSynthFrame`
gate-1 countdown s108 found) upstream of `tickAudioChannel` that could
explain zero *new* key-ons across 140+ seconds of continuous music? If
source-reading surfaces a concrete "this gate is closed and here's why"
answer, that's a clean discriminating result with no build needed. If it
surfaces a *different* candidate call path instead, redirect there.

**Angle (b) — trace `sampleDesc`'s origin one level up, bypassing the
need for a positive control entirely.** Read `funcs_22.c:3667`'s and
`funcs_26.c:1418`'s call sites and the code that populates
`G_BASE-0x5358`/the `$s1`-`$s6` stack buffer immediately before each
call. If one of the two call sites is provably dead (e.g. its own caller
is never reached, mirroring how s112 killed the RSP-ucode branch), that
narrows to one live source — then check *that* source's own derivation:
does it ever read a name/tag/string field into what should be a
sample-rate-shaped value? This can produce a decisive result via pure
source-read, no soak required, which is cheaper and matches the
"boring/source-first" rule.

Prefer (b) if the source read is tractable in one sitting — it can close
the loop without needing a positive control at all. Fall back to (a),
and only then to a new instrument/soak, if (b) dead-ends.

## Do not

- Do not re-run `ROGUESQ_LOG_STREAM_NODE_INIT=1` again — confirmed
  twice, all-zero, closed.
- Do not re-soak `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` alone a third time
  hoping for a different fire count — redesign (angle a) or bypass
  (angle b) first, per rule 8.
- Do not re-open hypothesis (a) (RSP ucode write) — closed s112,
  unaffected by this session's findings.
- Do not re-run `fixup_game_funcs.py` more than once per ELF regen.
- Do not trust a "closed" claim in CURRENT-TRUTH/PORTING-STATE about a
  file-wide audit without spot-checking at least one named function
  yourself first — s113's closure of hypothesis (b) was wrong, and the
  gap sat undetected for one full session.

## Housekeeping flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~116 KB, over 3x the ~35 KB target in
CLAUDE.md/ITERATION.md, and grew further this session. Worth a dedicated
compression work unit (migrate durable mechanism/architecture material
to PROJECT-OVERVIEW.md, prune superseded detail — the now-retracted s113
closure narration is a good first prune candidate once s115+ settles
the real answer) paired with a real experiment per ITERATION.md
(compressing docs alone does not count as an ADVANCED work unit).
