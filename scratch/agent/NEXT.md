# NEXT work unit (s1967) — hangar hologram-beam visual artifact, first discriminator

HYPOTHESIS-ID: hangar-hologram-beam-artifact

s1966 closed the generated-symbol renaming sweep to 57 genuine holdouts (RE
required or deliberate holds — see `docs/CURRENT-TRUTH.md` "Current state"
and `PORTING-STATE.md` s1966). It is no longer a metadata-sync target; do
not resume `tools/sweep_scan_candidates.py` expecting more free wins.

Per `tools/agent/ITERATION.md`'s strategic priority: M5 is closed, M3 is
parked pending a new idiom-class discriminator, and the sweep is now
closed too — so this session's work unit comes from
`docs/CURRENT-TRUTH.md` "Active investigation and ranked next steps" #1,
the hangar visual artifacts, since it needs the least new tooling (a
capture already exists) among the remaining items.

## What's already captured

`scratch/agent/soak_results/s1949_menu_input_yield_20260818-021858/f_001_000.0.png`
(same frame reproduced in `s1950_hangar_yield_repro_20260818-022703/`) is
the SELECT LEVEL / AMBUSH AT MOS EISLEY hangar screen — the first live
hangar frame this campaign has ever captured (s1949, `ROGUESQ_SPIN_YIELD=1`
+ eleven-Start recipe). Looking at it directly: the holographic light-cone
beneath the floating X-wing hologram has two jagged blue triangle spikes
poking up through the cone surface, breaking its silhouette — plus the
cone's own edge looks faceted/torn rather than a clean gradient wedge.
This matches CURRENT-TRUTH's prior description ("geometry cracks, blue
tris, hologram layering") well enough to treat as the same artifact
family, though no prior session had actually looked at the pixels before
now — s1950 only confirmed the window didn't lengthen, it didn't examine
the frame.

**Window is short: ~4s / 1 frame before the `filterVoiceSampleBlock+220`
SIGBUS (known family, do not chase as a single crash — CURRENT-TRUTH #2).**
Any new capture needs the same yield recipe and will hit the same wall;
budget for exactly one frame per run.

## Competing hypotheses (need refinement before instrumenting)

1. **Depth/blend ordering.** The hologram beam is alpha-blended geometry;
   if RT64's HLE gets the RDP blend-mode or z-compare setup wrong for
   this specific draw (or the port omits a `G_RENDERMODE` edge the
   original hardware/LLE handles), the spike shapes could be triangles
   from the beam cone rendering front-to-back instead of correctly
   blended/culled.
2. **Vertex/triangle-winding corruption**, same family as the already-
   audited M4 shade-lane and `L_17F0` restage work (`docs/CURRENT-TRUTH.md`
   "Durable boundaries" M4 accumulator) — but that thread's evidence was
   VI-640-attribution-LLE and explicitly `y8000_any=0` on the hangar
   window; this would be a NEW instance in a screen that thread never
   evaluated. Do not assume it's the same bug without independent evidence
   from this specific draw call.
3. **Legitimate retail behavior misread as an artifact.** The N64 original
   may render this cone as a faceted, non-smooth shape by design (holo-
   projector aesthetic) and what looks like "cracks" is just N64-era low
   triangle count at emulator upscale. Rule this out FIRST — it is the
   boring explanation and costs nothing: check `tools/oracle/README.md`
   for whether the retail ROM under mupen64plus can reach this exact
   hangar screen (oracle currently reaches "boot and attract only" per
   CURRENT-TRUTH — if the hangar menu is out of reach there, this
   hypothesis can't be checked directly and should be labeled unresorlvable
   pending oracle extension, not silently assumed false — do not treat it
  as unresolvable without checking).

## Discriminating measurement to design before instrumenting

Before writing any capture code: name what result would select which
hypothesis. Candidates:
- If the oracle CAN reach this screen (check first, cheaply): a
  side-by-side RDP command dump of the beam-cone draw call, retail vs
  port, discriminates H1 vs H3 directly (same triangles == H3 legitimate;
  different blend/z state == H1).
- If the oracle cannot reach it: dump the RDP triangle stream for this
  specific draw (reuse the `L_17F0` / `0xD60` command-buffer
  instrumentation pattern from the M4 accumulator work, `docs/CURRENT-
  TRUTH.md` Durable boundaries) restricted to the hangar-menu overlay
  entry, single frame, and check triangle winding/vertex Z against what
  `docs/F5-UCODE-REFERENCE.md` says this ucode can legitimately emit for
  a translucent fan/cone primitive. A malformed or degenerate triangle
  (duplicate vertices, inverted winding) selects H2; a spec-valid triangle
  stream with a blend-mode mismatch selects H1.

This is genuinely a **new discriminator design task**, not a "run the
existing recipe" task — per the iteration contract, do not build an
instrument until you can name what each outcome would prove.

## Do not repeat

- Chasing hangar SIGBUS `filterVoiceSampleBlock+220` (`0x8000834c`) as a
  single crash — known family, only revisit as a complete idiom-class
  audit (CURRENT-TRUTH #2).
- Re-walking VMADH/VGE / `0xD60` / ovl20 for Y=`0x8000` — that thread is
  closed (H-never-live, `docs/CURRENT-TRUTH.md` Durable boundaries M4
  accumulator). This is a DIFFERENT symptom (visual, not the Y=0x8000
  accumulator question) even though it may share instrumentation.
- Defaulting `ROGUESQ_SPIN_YIELD` on.
- Resuming the generated-symbol sweep as if it still had a large
  resolvable backlog — it doesn't (57 left, all RE/hold).
- Cross-run A/B on this scene without phase-gating — the hangar window is
  ~4s of animating content, exactly the case iron rule 2 forbids comparing
  by stopwatch.
- If this hypothesis doesn't pan out or can't be instrumented in one
  session, the fallback per `tools/agent/ITERATION.md` strategic priority
  is the REVISIT: re-attempt the external retail-entry boundary or M4
  accumulator boundary (`docs/CURRENT-TRUTH.md` Next steps / Durable
  boundaries) with a genuinely new angle — not another sweep session.
