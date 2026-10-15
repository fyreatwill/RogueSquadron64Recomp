# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Maintained
at Session 4942; detailed historical evidence is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md)
and the per-session `docs/M5-S*.md` notes. Git history preserves prior wording.

## Headline

- **s4964:** s4959 run3 valid (mission onset t=182 s, crash=0, pcm_nz 128/164). Keyed mission route now 3/3 valid, crash=0, PCM live. M5 plan steps 0-11 all closed; next is a mission-phase image-vs-silent (`ROGUESQ_AUDIO_UCODE=1/0`) A/B soak pair on the keyed route.

- **s4958:** first keyed route to a real mission: title (36,6) -> hangar 0x6AB400 -> ~5 A -> 0x6A2900 is a ~70 s LOADING phase (0x644D00, 0x62BD00, 0x696100) -> mission 0x620400/0x690400 at t=181, sustained 140 s, crash=0 (N=1). s4957's "model viewer" was this load. Recipe `scratch/agent/s4958_after_6a2900.sh`.

- **s4956:** keys sent from the title phase (36,6 x8/run, N=3) reach the hangar `0x006AB400` in 3/3 at ~58-66 s with VI advancing and crash=0, but never any mission origin. Hangar control passed; (36,6) does not launch a mission. The s4943 "mission" origins are probably the attract demo. Recipe: `scratch/agent/s4956_keyed_title.sh`.

- **s4954:** the 512 (0x690400) phase in the s4950 soaks is the ATTRACT DEMO: keys were only sent after it appeared and timing is identical across 5/5 runs (640@~76s, 512@~97s, title again ~4s later). Not a mission, not an abort. Real mission needs hangar + keys (s4943 route).

- **s4953:** `tools/vi_progress.py` over the s4950 logs: all 5 runs go title -> 640 -> 512 (0x690400, ~3-4 s, ~150-260 update_screens) -> title again; no run's VI progress halts. The 512 "mission" may be an attract demo or a port bounce-to-title (undiscriminated). Mission-phase row added to `docs/M5-AUDIO-PLAN.md`.

- **s4949 (unblock):** the s4948 "owner decision" block was refuted: movz/movn defect is dormant (2 of 149 sites "reachable", both data-as-code; do_break exits loudly, no hit recorded). Next unit is a mission-route soak, not a human decision.
- **s4946:** solo vs duo image-arm VI pacing identical (mission entry #5738/#5744/#5735 at ~96.8s); concurrency does not explain the s4944 flip-count gap. M5 plan steps 0-11 all closed.

- **s4944:** Image-vs-silent aux-store A/B qualified (title+mission in both arms, crash=0, same final VI #9600). All four aux stores fire in both arms with identical value structure — H-contract-gap refuted, H-route-only supported. The silent arm emits ~11x more mission synth-frame rows at equal VI count (single run; AI-drain pacing suspected, untested). Recipe: `scratch/agent/s4944_aux_ab.sh`.

- **s4943:** One production image arm reached title (`0x00790400`) and both
  mission origins (`0x00690400`, `0x00620400`) with crash=0 and aux-store rows
  in both phases; hangar control absent (driver keyed on first VI-512). The
  s4942 VI-640 stall is intermittent, not a build defect (cf. s4794 2/5).
- **s4941:** The qualified Rice oracle reached title (`0x00790400`, VI 1024)
  and hangar (`0x006AB400`, VI 512), with whole-RDRAM and all three target
  controls firing. The aligned `0x00149700:0x00149704` watch produced repeated
  field rows at `pc=0x800917C4`, effective address `0x80149702`, in both title
  and hangar buckets. This selects H-alignment-boundary over no retail write or
  phase-route mismatch; it is single-source oracle evidence, and no rewrite or
  filter was added.
- **s4939:** The phase-gated retail/port join reached the title phase on both
  sides and the port witness recorded all four `musyxSynthFrame` stores in the
  retail order. Retail controls fired for whole RDRAM and the other target
  stores, but the exact retail watch for odd-byte `0x80149702` stayed empty;
  the port arm produced 256 capped title rows. The join is unresolved because
  the missing retail destination may be an oracle watch boundary. No value
  rewrite or filter was added.
- **s4942:** The same-build image/silent auxiliary-store A/B was unevaluable on
  this checkout: both the old LLE recipe and a no-LLE Rice/HLE retry reached
  VI-640 (`0x0066A500`) but neither reached title or hangar. The task, PCM,
  and auxiliary rows therefore select no A1 hypothesis. The route wrapper and
  rebuilt binary are retained for a route-qualified retry.
- **s4937:** Static ownership lookup identifies `0x80149702` as the MusyX
  double-buffer toggle and `0x80149988/8A` as synth output/countdown state.
  `0x800A1778` has no named companion symbol; its only current reference is
  the adjacent store in `musyxSynthFrame`. This selects route-family state
  over render/input state, but does not establish the field's exact meaning.
  No mitigation is authorized. See `docs/M5-S4937-RETAIL-AUX-OWNERSHIP.md`.
- **s4936:** A corrected retail store-site capture passed whole-RDRAM and VI
  controls and found stable auxiliary destinations `0x80149702`,
  `0x80149988/8A`, and `0x800A1778`; the independent type-2 task decoder was
  `0/8192`. This selects auxiliary-store ownership, single-source.
- **s4935:** Retail writer `0x80091784` executed 12,077 times with auxiliary
  context (`s0=0x80149470`, rotating small `s1`, mission `a1=0x142/a2=2`),
  while the independent type-2 decoder at `0x80033FCC` remained zero. This is
  an auxiliary writer, not yet an OSTask-publication proof.
- **s4934–s4933:** The writer fires at hangar and both mission origins, but
  the old task-entry watch remains zero. The current question is attribution
  and field ownership, not whether the route exists.

## Durable state

### M5 audio

- Audio is active, not a zero-output stub: nonzero PCM and corrected AI byte
  order are qualified on the current route. M5 plan: `docs/M5-AUDIO-PLAN.md`.
- The qualified route reaches attribution, N64 logo, intro, Factor 5 logo,
  title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
  (`0x00690400`, VI 512; later `0x00620400`). Retail mission qualification
  passed whole-RDRAM/VI controls and reached both mission origins (s4932).
- The s4927–s4930 mission joins show fresh audio route ordinals and row-0
  resets across the `0x00690400 -> 0x00620400` handoff, with PCM activity.
  This is legitimate port-side route reinitialization, not a basis for a
  guard or skip; retail ordinal parity is unclaimed.
- Retail/port task-family class matches (`0x80149470`, type 2), while retail
  publishes mostly `data_size=2` and port mostly `1`; s4887 closed this as a
  cadence difference. The s4933–s4937 writer/auxiliary captures supersede the
  old assumption that `0x80091784` is the task publication site.
- The voice-render range fires in retail title and hangar, but exact consumer
  `0x800903F0` remains absent (s4897). Treat this as an internal boundary, not
  as route absence and not as authorization for filtering.
- First-teardown synth deregistration is named and fixed (s4890). The covered
  route does not reach `shutdownAudioEngine` (s4894); callback registration
  rows do not prove shutdown execution. Synth `+5808` idle title/hangar crash
  family is closed by the default pause fix (s4786).
- Current default stability: title/hangar longevity is qualified; mission
  route captures have advanced counters and zero crash/abort markers in the
  cited runs. Judge future runs by phase controls, never wall-clock alone.
- The s4939 auxiliary-store witness is regeneration-preserved in the fixup
  template and records the four store sites with phase, order, value, and
  `s0/s1`; its title controls passed, while the requested hangar phase was not
  reached by the driven port capture.
- The s4941 retail watch-boundary run confirms that the odd byte is written by
  the retail store at `0x800917C4`; exact one-byte watch nulls are therefore a
  watch-boundary artifact, not evidence that the field is unwritten.

### M3 and rendering

- M3 idiom audits are closed for trap/break/syscall/cop0, unaligned and
  LL/SC/cache, integer division, float conversion/compare/FCSR, memory-width
  operations, indirect calls, self walks, branch-likely, variable shifts,
  HI/LO moves, 64-bit shifts, and 32-bit multiplication. Do not repeat a
  class without new recompiler or provenance evidence.
- Conditional moves remain a genuine recompiler defect: all 179 generated
  `movz`/`movn` sites emit `do_break`; one reachable nonzero-destination site
  is identified, and s4842 attributes it to missing N64Recomp operation
  support. No generated-file hand edit or runtime guard is authorized.
- Factor5 runaway-DL cause is known: op `0xBD` loads overlay `0x2C` (ROM
  `0x27368`, destination `0x1DB0`) without a route, restarting the task.
  Runaways occur in VI-640 and much of mission; splice effect remains parked.
- Native port hangar artifacts (rim band, holo spikes, right-edge stale data)
  remain localized. M4 accumulator origin, pillar references, `0x1F0D74`, odd
  PI DMA, and external retail-entry are parked pending a genuinely new
  discriminator.

### Operational constraints

- Retail oracle watches physical addresses and require whole-RDRAM, VI, and
  phase controls before any null is interpreted. Use `docs/F5-UCODE-REFERENCE.md`
  for Factor5 command semantics.
- Batch all counters and A/B arms in one build/run; phase-gate animated
  comparisons. A mitigation-shaped change requires an `ORIGIN:` naming the
  writer and stating whether its value is legitimate.
- Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
  CMake`; generated functions are not hand-edited for behavior. If `lib/`
  changes, export submodule patches in the same iteration. Never use
  submodule update, checkout, clean, or hard reset. Kill runs with SIGKILL.

## Parked and closed

- VI-640 crash families and broad guard classes: no reproducible current
  failure; any recurrence needs phase state plus process/display/load context.
- External retail-entry: Rice route is qualified through title/hangar but the
  old exact PC is absent; do not repeat without a new route or PC discriminator.
- M4 accumulator boundary, attached-mesh mission contract, hangar pillars,
  col-511 noise, `0x1F0D74`, and overlay-registration chunking are parked.
- Generated-symbol renaming is exhausted at the available snapshot: only
  `func_8000040C` and `func_800E9AE0` remain without a candidate satisfying
  companion mapping, live caller/body, and exact-span gates.
- M3 patch-runtime qualification remains blocked on the MIPS GCC/LD toolchain.

## Superseded conclusions

- **s4959 "BLOCKED: multi-minute recipes cannot be waited on inside an iteration"** - believable because foreground sleep/polling is blocked and the Stop hook fired six times mid-run. Overturned by the unblock iteration: the soak queue (ITERATION.md, 600 s cap per recipe, verdicts in SOAK-RESULTS.md) is the intended mechanism; the x3 script was just too long for it. Split into soak_queue/s4959_mission_run{1,2,3}.sh. Mission stability is still unmeasured.

- **s4950 "5/5 reached mission" (0x690400, VI-512)** - believable because the phase appeared after scripted keys and had a distinct width/origin. Overturned s4954 (script ordering + deterministic timing) and s4955 (3/3 solo run, hangar control absent): it is the attract demo, not player-mission evidence.

- s4950's "5/5 reached mission" (and its `stalled=1` stall grep) was refined by s4953: `stalled=1` appears at every phase, and the 512 phase is only ~3-4 s before return to title, so it is not established as a player mission. Believable because the origin 0x690400 matched the retail mission origin.

- s4934's “writer attribution” was refined by s4935–s4937: `0x80091784` is
  real mission-phase auxiliary activity, not yet an OSTask publisher.
- s4940's phase-route-mismatch selection was overturned by s4941: the same
  aligned watch with the qualified Rice route reached title and hangar and
  captured the target store. The earlier null remained valid only for its
  pre-route run.
- s4893's claim that the route reached `shutdownAudioEngine` was overturned by
  s4894's kind-0 entry and kind-2 return markers; only kind-1 registration rows
  occurred.
- The apparent port retrace burstiness was overturned by s4901: two
  `update_screen` calls represented one true origin change; port pacing is
  steady at two retraces per origin versus retail one.
- The early `+9668` bus error was our own unsigned diagnostic address bug,
  fixed with `S32()` (s4696); older recipes arming that probe are suspect.
- “M5 is fully closed” was too broad: nonzero PCM proves route activity, not
  task-contract, ownership, wait-gate, safety-exit, or MORT correctness.

## Next steps (single monotonic backlog)

**s4973 (top):** s4972 soaks never ran (zsh ${0:A:h...} bug, rc=2 in 0 s). Requeued as soak_queue/s4972r_vi640_idle_a.sh (5 idle runs; verdict in soak_results/s4972r_a/summary.txt, seen640=1 is the positive control). 0/5 stall => close the VI-640 wall; any stay640 => reproduced stall, investigate phase-gated.

**s4971 (prior):** VI-640 boot stall NOT reproduced (4/4 idle/loaded arms exit at 48-50 s, loadavg up to 39; no positive control, so not proof it is gone). H-load unsupported. Route wall is not currently observable; next: N>=10 repeat in soak queue to bound the rate, else treat as closed.

**s4970 (prior):** movz/movn DONE: N64Recomp now emits them (submodule-patches/n64recomp-movz-movn.patch), live tree patched by tools/fixup_movz_movn.py (census 179/179 do_break -> 0/179), build 0 errors, title+hangar smoke crash=0 (scratch/agent/s4970_smoke.sh). Live RecompiledFuncs is not reproducible from fixup_game_funcs.py alone (many apply_s*.py layers). Remaining pivot target: VI-640 route wall.

**s4969 (top):** the s4968 block was not an owner decision; re-scoped. Next unit is movz/movn support in N64Recomp via scratch regen (engineering-only, dormant defect, no runtime change expected); see NEXT.md.

**s4968 (prior):** long hold CLEAN (alive to 586 s, crash=0, PCM nz>0); M5 closed. Mandatory pivot has no remaining target; BLOCKED, see scratch/agent/BLOCKED.md.

**s4967 (prior):** Step 10 was already qualified at s4857, so the only open M5 item is a long mission hold. `soak_queue/s4967_mission_image_long.sh` is enqueued (image arm, ~310 s hold, cap 600 s); no verdict yet. Clean => long-hold qualified, then pick an M3 idiom-class audit; crash/stall => name the writer (rule 11). See NEXT.md.

**s4966 result (prior):** mission image-vs-silent A/B (s4964_mission_{image,silent}) both crash=0 abort=0 over ~320 s, onset t=183 vs 186 s; image pcm_nz_rows=131, silent 0 (controls valid, n=1/arm). H-stable-both: the audio image is not the mission-stability factor on the keyed route. Next: take the next unqualified row of M5-AUDIO-PLAN's execution sequence (Step 10 host PCM consumer / longer mission hold); see NEXT.md.

**s4965 (superseded by s4966):** recipes enqueued; now consumed.

**s4963 result (superseded by s4964):** s4959 run1/run2 VALID: mission (0x690400) at t=186/185 s held to 314 s, crash=0 abort=0, pcm_nz_rows 151/153 of 168 (n=2, keyed route). Run3 still queued: consume its SOAK-RESULTS line, then take the next unfinished step of M5-AUDIO-PLAN's execution sequence.

**s4962 note:** s4959 run1/run2 verdicts (rc=1) are INVALID — recipes ran under /bin/bash with zsh-only `${0:A:h}`, empty ROOT; fixed by zsh self-re-exec, all three re-queued.
**s4960 next (top; still unrun at s4961):** consume the verdicts of the three queued soaks scratch/agent/soak_queue/s4959_mission_run{1,2,3}.sh (SOAK-RESULTS.md, soak_results/s4959_mission_run*/keys*.log); do not babysit or rerun. rc=137 = timeout, not a result. Then add the mission-phase row to docs/M5-AUDIO-PLAN.md.

**s4958 next (superseded by s4960 above; recipe unchanged):** repeat the keyed route N=3 with mission-phase audio/PCM counters (see NEXT.md). Older, resolved by s4958: **s4957:** hangar keycode sweep (15 keys: A/B/Start/D-pad) never reaches a mission (0x690400/0x620400 = 0); the 5th A leaves to the 0x6A2900 model viewer. Input delivery works. Next: find the mission-launch state/flag (see scratch/agent/NEXT.md), try keys inside the viewer.

**s4955 next (top):** s4955 solo N=3 run confirmed the 512/0x690400 phase is the attract demo (bounces to title 3-5 s after onset; hangar 0x6AB400 never reached, keys sent only after 512 appeared). Next: rerun with keys sent at the TITLE phase (~50 s, origin 0x790400), hangar 0x6AB400 as control, then judge mission stability; see NEXT.md.

**s4954 next (superseded by s4955 above):** resolved as demo. Next: M5 plan row for the keyed route (title->hangar->mission) with the s4943 recipe; see NEXT.md.

**s4952: unblocked** - s4951 scope question re-scoped to NEXT.md (VI-progress metric from s4950 logs, then mission-phase M5 row). stalled=1 is not a VI640 indicator. Declaring the milestone done remains an owner decision.

0. **s4945 note:** s4944's "~11x more synth frames per VI" is a witness artifact (aux-store row cap resets per origin flip; rows/flip 32.8 image vs 30.8 silent; flips 49 vs 512). The arms are equivalent per flip; the image arm just presents fewer flips (cause undiscriminated, single-source offline).

1. **Completed — s4939:** perform the phase-gated retail/port join for
   `0x800A1778`, `0x80149702`, and `0x80149988/8A`, using whole-RDRAM and VI
   controls plus port `musyxSynthFrame`/`aspTask=0x80149470` controls. Match
   store order, values, and cadence in one table. The title-phase arm is
   unresolved because retail `0x80149702` was absent and the port did not reach
   hangar. No rewrite or filter was added.
2. **Completed — s4941:** repeat the aligned retail watch with the qualified
   Rice route and verified Start presses. The aligned watch and field-aware
   rows identified the legitimate `0x800917C4` store in title and hangar;
   exact odd-byte watch nulls are closed as a boundary artifact. Do not add a
   rewrite, filter, or port instrument for this field.
3. **Next:** run the A1 image/silent auxiliary-store A/B concurrently with
   title + mission origins as controls (route qualified by s4943); relaunch any
   arm that stalls at VI-640 rather than reading it as a null.
4. Execute the next named M5 contract edge from `docs/M5-AUDIO-PLAN.md` with
   one same-build validation arm and its rollback arm. Before changing
   behavior, choose a writer/consumer boundary whose positive control can
   reach title and hangar and whose outcome distinguishes a real contract gap
   from route-only progress.
5. Revisit M3 only as a complete idiom-class audit with a new discriminator;
   conditional-move recompiler support is a separate engineering task.
6. Revisit external retail-entry or M4 only with a genuinely new oracle route,
   PC, or RSP witness; otherwise keep them parked.
7. Resume symbol renaming only after the required last-15-session preflight
   shows it is not a REVISIT and a new mapping source exists.

## Evidence index

The detailed s4822–s4937 headline history and older backlog are archived in
`docs/PROJECT-OVERVIEW.md`; per-run evidence is in the session-specific M5/M3
notes and `PORTING-STATE.md`. The next iteration must read `scratch/agent/NEXT.md`
and the tail of `scratch/agent/SOAK-RESULTS.md` before acting.

- s4947: aux-store A/B thread closed; arms identical on [phase] transitions (6 each), pacing, rows/flip. Not a lead.
- s4948: all tiers closed or unevaluable; BLOCKED for owner decision (see scratch/agent/BLOCKED.md).

### s4950 update
Mission-route soak (solo, N=5): 5/5 reached origin 0x690400, 0 do_break hits, 0 crashes (single-source, small N). VI640-stall rate still undetermined: vi-fs-decision lines carry stalled=1 late in every run, needs a phase-gated count, not a raw grep.
