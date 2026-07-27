# NEXT work unit — M3: find the real `voice+0x0` (active-flag) writer (s116)

s115 **closed** the multi-session `voice+0x34`-writer question for good
(3rd independent line of evidence) and found a sharper, previously-unseen
open question in its place: what actually activates a voice (sets
`voice+0x0` nonzero)? Read PORTING-STATE.md's Session 115 entry before
doing anything else; this file only has the actionable summary.

## What's now closed — do not re-open or re-chase

- `voice+0x34` (the field `musyxRenderVoiceSamples` reads, that feeds
  `fillSampleStreamRange`'s corrupted `devAddr`) is uninitialized by
  design whenever a voice is never explicitly key-oned via
  `musyxInitVoiceFromSample`. Three independent lines of evidence, all
  now in the ledger: (1) s111 — the only literal write anywhere is
  `musyxInitVoiceFromSample`; (2) s113 — no computed-offset write to this
  field exists anywhere either; (3) s115 — the voice array's own
  allocator, `allocateSongChannelArray` (`funcs_23.c:10687`), zeroes only
  3 of 136 bytes per slot (`0x0`/`0x84`/`0x85`) and never touches `0x34`.
  Combined with s105-s110's 5-session-null finding that
  `musyxInitVoiceFromSample`'s entire call chain never fires (not even in
  a run that reached and survived the whole ~140s corruption window with
  a clean positive control on the surrounding MusyX system), this fully
  explains the ASCII-shaped, run-to-run-identical `do_rom_read`
  corruption as a deterministic uninitialized-heap read, not a race
  (closes s85's "shared corruption race" framing for good).
- **s114's framing of this as still-open ("s113's audit had a gap") was
  itself a misreading** of s113's own text — s113 never disputed that
  `musyxInitVoiceFromSample` writes `voice+0x34`; it only closed a
  *different*, narrower sub-question (no computed-offset write exists).
  Don't re-litigate this; it's a documentation-drift correction, not new
  evidence either way.
- Do not re-run the `-0x6908` literal-grep method (`grep -n
  "MEM_W(ctx->r[0-9]*, -0X6908)"`) to look for more writers — s111 and
  s113 both already ran it exhaustively for the field-write question, and
  it has a structural blind spot (see below) that makes running it again
  pointless.

## The real open question, and why it matters

`musyxMixActiveVoices` (`funcs_24.c:2477`, called 3x from `musyxSynthFrame`
— the confirmed-always-running per-VI-retrace driver, s101, unlike the
countdown-gated `tickAudioSequencerFrame` call sites) loops every voice
slot and only calls `musyxRenderVoiceSamples` (the function that reads
`voice+0x34`) when `voice+0x0 != 0` (`funcs_24.c:2587-2592`, `beq $v0,
$zero, L_80090F40` skips the call when the byte is zero). `voice+0x0` is
confirmed zeroed for every slot by `allocateSongChannelArray`'s init loop.
So in principle no voice should ever reach `musyxRenderVoiceSamples`
unless something else flips this byte to nonzero first.

The only writer of `voice+0x0 = 1` found this session is
`musyxTriggerVoiceAttack` (`funcs_24.c:6085`, guest `0x8009231C`) — and it
is a near-perfect match for the bug shape (it resets ADSR fields and the
rate half-word but **never touches `+0x34`**), but both of its call sites
(`funcs_23.c:4887` inside `tickAllAudioChannels`, `funcs_26.c:1573` inside
`startStreamedSampleVoice`/`serviceVoicePoolFrame`) are inside the two
chains s105-s110/s114 already proved fire 0/0 during every corrupting run.

**Yet `musyxRenderVoiceSamples` demonstrably does run every corrupting
soak** — it's the only path into `fillSampleStreamRange`, and
`musyx-dma-call`/`fill-range-args` have fired every session since s102.
So some voice's `+0x0` genuinely is getting set nonzero, by a writer
neither audit found.

**Why the prior audits missed it**: s111/s113 both worked by grepping for
functions that load the `-0x6908` global pointer *fresh*. Any function
that instead receives an *already-computed* voice-struct pointer as an
argument is invisible to that grep — and PORTING-STATE's own s111 entry
already flagged (in passing, never acted on) that `musyxRenderVoiceSamples`
and `musyxKeyOnVoice` themselves are exactly this category. Neither audit
went on to enumerate every other argument-receiving function and check it
for a `+0x0` write.

## The work unit

Pure source-read, no build/soak needed unless this dead-ends:

1. Find every function reachable from `musyxSynthFrame`'s always-running
   path (not gated behind the countdown divider) that takes a voice
   pointer as a parameter — start from `musyxMixActiveVoices`'s own body
   (does it call anything besides `musyxRenderVoiceSamples` per voice?)
   and from `musyxSynthFrame`'s other direct calls at the same 3 call
   sites as `musyxMixActiveVoices` (`funcs_24.c:3579/3713/3840`).
2. For each such function, check for a write to offset `0x0` off that
   voice pointer (not off a fresh `-0x6908` load).
3. If found: check whether that same function also sets `+0x34` (or
   calls something that does). If it does not, **that is the real fix
   site** — not `allocateSongChannelArray`, and not a blind zero-fill of
   `+0x34` (its true role as a stream/DMA-source address means 0 is not a
   confirmed-safe default; check what `musyxInitVoiceFromSample` treats
   as a "no sample" sentinel, if any, before picking a default).
4. If step 1-2 comes up empty after checking the obvious candidates,
   widen to: does `musyxKeyOnVoice` (already read s105, writes an
   unrelated RSP cmd-list struct — re-verify it truly never touches the
   CPU voice struct's `+0x0`) or `isAudioSlotActive`
   (`funcs_24.c:5731` — name suggests a query but worth a direct read,
   never done yet) turn out to be the actual activator.

## Do not

- Do not re-instrument or re-soak `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` /
  `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` / `ROGUESQ_LOG_STREAM_NODE_INIT=1`
  — all three questions they were built for are closed.
- Do not re-run the `-0x6908` literal-grep audit — it has a proven blind
  spot (argument-passed voice pointers) and running it again just
  reproduces the same false "exhaustive" result.
- Do not assume zeroing `voice+0x34` in `allocateSongChannelArray` is the
  fix without first finding the real activator and confirming what a
  "no sample assigned yet" state is supposed to look like — a guessed
  default could turn a crash into silent wrong behavior elsewhere.

## Housekeeping flagged, still not done

`docs/CURRENT-TRUTH.md` is ~118 KB, over 3x the ~35 KB target in
CLAUDE.md/ITERATION.md. Worth a dedicated compression work unit (migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md, prune
superseded detail) paired with a real experiment per ITERATION.md
(compressing docs alone does not count as an ADVANCED work unit).
