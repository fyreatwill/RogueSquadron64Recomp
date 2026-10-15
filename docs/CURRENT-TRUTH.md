# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Maintained
at Session 4941; detailed historical evidence is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md)
and the per-session `docs/M5-S*.md` notes. Git history preserves prior wording.

## Headline

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
3. **Next:** execute the next named M5 contract edge from
   `docs/M5-AUDIO-PLAN.md` with one same-build validation arm and its rollback
   arm. Before changing behavior, choose a writer/consumer boundary whose
   positive control can reach title and hangar and whose outcome distinguishes
   a real contract gap from route-only progress.
4. Revisit M3 only as a complete idiom-class audit with a new discriminator;
   conditional-move recompiler support is a separate engineering task.
5. Revisit external retail-entry or M4 only with a genuinely new oracle route,
   PC, or RSP witness; otherwise keep them parked.
6. Resume symbol renaming only after the required last-15-session preflight
   shows it is not a REVISIT and a new mapping source exists.

## Evidence index

The detailed s4822–s4937 headline history and older backlog are archived in
`docs/PROJECT-OVERVIEW.md`; per-run evidence is in the session-specific M5/M3
notes and `PORTING-STATE.md`. The next iteration must read `scratch/agent/NEXT.md`
and the tail of `scratch/agent/SOAK-RESULTS.md` before acting.
