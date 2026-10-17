# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Maintained
at Session 5027; detailed historical evidence is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md)
and the per-session `docs/M5-S*.md` notes. Git history preserves prior wording.

## Headline

- **s5033:** Heap-guard census needs no new instrument: existing env-gated guard logs (alloc-tail-guard2/3/4, R1, coalesce) fire only on bad pointers. Recipe soak_queue/s5033_heap_guard_census.sh enqueued; verdict lands in SOAK-RESULTS.md. 0 fires = single-source (no fire control without a rebuild).
- **s5032 (unblock):** The s5031 "owner decision" block was re-scoped, not escalated. Its premise was stale (movz/movn DONE s4970; M4 accumulator CLOSED s5005/s5006). The MIPS GCC dependency is real (Apple clang has no MIPS target; installing is human-only) but gates only one disabled patch, so it is an OPEN NON-GATING dependency. Next unit: heap-guard need census (NEXT.md). Details: scratch/agent/UNBLOCK.md.

- **s5029:** Mission-route external-entry join (retail oracle vs port, same run,
  controls passed): retail reaches `0x00690400` and `0x00620400` with the voice-range
  PC watch live (1241 writer hits) yet `pc=0x800903F0` executes 0 times; the port also
  has 0 `s4534-jal` at that site. Retail-entry boundary is now closed for title, hangar
  AND mission (retail-design-dead consumer). Script: `scratch/agent/s5029_mission_external_join.sh`
  (+ `s5029_summarize.sh`; run via nohup, not the 600 s background cap).

- **s5027:** The next menu-overlay candidate, `0x800B3AFC`, passes the
  companion-address, exact `0x174` overlay-span, generated-body, and live-caller
  gates for `buildScaledFormatTextElement`. The regeneration helper now
  preserves `func_800B3AFC -> buildScaledFormatTextElement`. Evidence:
  `docs/RENAME-S5027-AUDIT.md`.

- **s5026:** The next menu-overlay candidate, `0x800B2630`, passes the
  companion-address, exact-span, and live-caller gates for
  `buildFormatMessageGlyphBuffer`. The generated snapshot was already named,
  so the only change was adding the regeneration-preserving entry to
  `tools/rename_generated_symbols.py`. Evidence:
  `docs/RENAME-S5026-AUDIT.md`.

- **s5025:** The generated-symbol sweep reopened when the companion added a
  semantic menu-overlay mapping for `0x800B3824`. The generated record has the
  same start address, exact `0x2D8` span, and a live caller, so
  `tools/rename_generated_symbols.py` now preserves
  `func_800B3824 -> buildLevelSelectTextTextures` across regeneration. No
  generated files or runtime behavior changed. Detailed evidence:
  `docs/RENAME-S5025-AUDIT.md`.

- **s5024:** The normal patch qualification remains unavailable because this
  host has only `mips-linux-gnu-as`; neither `mips64-elf-gcc` nor
  `mips-linux-gnu-gcc` is installed. A bounded build-system fix made
  `MIPS_GCC` and `MIPS_LD` explicit CMake cache overrides, so a future supplied
  compiler can be selected by exact path. Configure validation preserved the
  intended skipped-target behavior with missing paths; `PatchesLib` was not
  built and the runtime override remains disabled.

- **s5023:** Reconfiguring with the available macOS tools confirmed the normal
  patch path is omitted because `mips64-elf-gcc` is unavailable; only the MIPS
  assembler/linker are installed. `PatchesLib` therefore has no CMake target,
  and the requested build ends with `No rule to make target PatchesLib`. This
  is a toolchain blocker, not evidence against the s5022 ELF-reader fix; the
  runtime override remains disabled.

- **s5022:** N64Recomp's ELF reader now treats an absolute linker-defined
  symbol as a game reference symbol when the same name exists in the supplied
  function table. The exact assembly-only `allocateDisplayListBuffer` patch
  therefore recompiles successfully with its direct
  `findAndUnlinkSmallestEntry` call and preserves the `0xE8` span. The
  override remains disabled; no runtime behavior changed.

- **s5021:** The preserved generated snapshot contains the complete
  `allocateDisplayListBuffer` window. The assembly reconstruction now emits
  the exact `0xE8` span and matches its stack, branch-likely, queue-store, and
  return structure. N64Recomp rejects the faithful direct external `jal` form
  (`No function found for jal target: 0x8002221C`) and clears the output, so
  the override remains disabled; this is now an integration limitation, not a
  missing-source question. See `docs/M3-S5021-ALLOCATE-DL-INSTRUCTION-WINDOW.md`.

- **s5020:** Extended the disabled assembly-only `allocateDisplayListBuffer`
  probe through free-list expansion, dequeue, active-queue append, and
  bump-cursor publication. Assembly/link/N64Recomp all pass and emit the
  correct symbol, but the section is `0xCC` bytes versus the known original
  `0xE8` span. The port remains a structural H3 slice; no runtime behavior
  changed.

- **s5018:** Homebrew `mips-linux-gnu-as`/`ld` can assemble and link the
  existing patch layout: a temporary assembly override produced ELF32
  big-endian MIPS-II with `.recomp_patch` at `0x80801000`, and the in-tree
  `build/N64Recomp` consumed it successfully. This unblocks an assembly-only
  patch route, but no game behavior changed and MIPS C compilation remains
  unavailable.

- **s5019:** The first assembly-only heap-guard build exposed and fixed a
  stale patch symbol: `0x80007D74` is `allocateDisplayListBuffer`, not
  `func_80007D74`. Strict N64Recomp validation now passes and emits the host
  override. The bounded assembly slice is only 0x44 bytes versus the original
  0xE8-byte entry and omits queue publication, so it is not behaviorally
  faithful and remains disabled. The assembly route is viable; the slice is
  H3 (structural mismatch), not an explanation for a runtime defect.

- **s5000:** The independent retail/port boundary retry passed retail
  whole-RDRAM, title, and hangar controls and recorded 0 exact
  `0x800903F0` executions after 24,195,957 surrounding-range executions.
  The port reached title and `0x00620400` but not qualified hangar
  `0x006AB400`, so the join selects `H-route-mismatch`; no mitigation was
  added. See `docs/M5-S5000-EXTERNAL-BOUNDARY.md`.

- **s4999:** The bounded residual-symbol audit found no safe rename. `func_8000040C`
  has an exact `0x34` span and live callers but no semantic companion name;
  `func_800E9AE0` has an exact `0x114` span but remains address-coded in the
  companion and has no generated live caller. Neither generated symbol was
  changed. Evidence: `docs/RENAME-S4999-AUDIT.md`.

- **s4993:** The per-origin bad-row budget passed title, hangar, both mission
  origins, allocator and PCM controls (mission onset 181 s, PCM=149,
  crash=0, abort=0). It produced 2,602 bad rows, but only at pre-mission
  origins `0x006A2900` and `0x00644D00`; none occurred at mission origins
  `0x00690400` or `0x00620400`. The s4987 observation control fired 20 times
  at `0x00690400` with current `20/0x8018C720`. The same-origin bad-row join
  remains unevaluable, so no hypothesis or mitigation is selected.

- **s4995:** The regeneration-preserved ordinary-caller sample was added and
  built, but the validation recipe reached hangar and pre-mission origins only
  (`mission_onset_t=-1`; crash markers were present), so its s4540 arm and
  s4987 observations were pre-mission controls. It emitted no mission-origin
  sample rows. H-uninstrumented-reader, H-classifier-phase, and H-no-sample
  remain unevaluable; retry with a route-qualified mission recipe.

- **s4990:** The caller-boundary instrument passed all route controls and
  recorded `r31=0`, `r4=0x801724C0`, and guest `32/0x801714D0` on four bad rows,
  but those rows occurred only at origins `0x644D00` and `0x6A2900`; the
  mission-origin mixer/publication rows were current `20/0x8018C720`. Because
  the bad-row budget was run-lifetime capped, this run made no same-origin
  caller join and selected no hypothesis. The instrument is live; next is a
  per-origin bad-row budget, with no value rewrite or guard.

- **s4988:** Independent retail ground truth passed its whole-RDRAM positive
  control and wrote the voice pair at `0x801496F8/0x80149700` (dominant writer
  `0x800917C4`). The corrected, phase-scoped port provenance soak reached
  title, hangar, both mission origins, and PCM with crash=0/abort=0. In mission,
  allocator publication and mixer count/base observation both agreed on
  `count=20`, `base=0x8018C720`, while the four `s4540` bad rows still saw
  `count=32`, `base=0x801714D0`, `a0=0x801724C0`. This selects a stale/unjoined
  `s4540` path or caller propagation outside the instrumented mixer pair;
  it does not authorize a guard or rewrite.

- **s4987:** The narrow publication/observation lock preserved the qualified
  route (title, hangar, mission onset 180 s, s4579-A=9, PCM 146 rows,
  crash=0, abort=0) but left kind=bad=8 and pidma=0. This is a
  single-source refutation of this lock implementation as the missing
  handoff; it does not identify the writer of the stale diagnostic pair.

- **s4985:** The host-lock exclusion variant serialized the complete
  `allocateSongChannelArray` and `musyxMixActiveVoices` functions, but the
  armed validation did not reach the title control within its 150-second gate.
  It did fire one allocator positive-control entry (`s4579-A=1`) but had no
  title, mission, PCM, or crash marker. This makes the whole-function lock
  route-blocking/unevaluable; it does not select H-lock-required. Next is a
  narrower lock around publication and the paired observation only.

- **s4982:** The armed post-writer-fix mission soak reached the allocator and mission (ctl_arm=1, s4579A=9, onset 173 s) but still logged 4 `kind=bad` stale-base calls, with pidma=0 and crash=0. Writer ordering alone is insufficient; next is reader-side acquire/order qualification.

- **s4983:** The clean armed reader-acquire mission soak reached both mission origins (onset 175 s), with `ctl_arm=1`, `s4579A=9`, `bad=4`, `pidma=0`, crash=0, and abort=0. A fence after the ordinary count load did not change the stale-base signature; the remaining question is an atomic observation or lock, not route validity.
- **s4984:** The atomic voice-pair variant reached mission (onset 176 s), with `ctl_arm=1`, `s4579A=9`, `bad=8`, `pidma=0`, crash=0, abort=0, and 147 nonzero PCM rows. Acquire atomic loads/stores at the guest count/base locations did not close the stale pair; the next test is a lock-compatible handoff.

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
- s4984's atomic pair variant is regeneration-preserved by
  `tools/apply_s4984_atomic_voice_pair.py` and the vendored replay list. It
  uses host acquire loads and release stores for guest `0x80149700`/
  `0x801496F8`; the mission route remained qualified, but stale rows increased
  from 4 to 8 in this one run.

### M3 and rendering

- M3 idiom audits are closed for trap/break/syscall/cop0, unaligned and
  LL/SC/cache, integer division, float conversion/compare/FCSR, memory-width
  operations, indirect calls, self walks, branch-likely, variable shifts,
  HI/LO moves, 64-bit shifts, 32-bit multiplication, and 64-bit mul/div
  (s4975: 66 sites, 2 real, zero-divisor benign on arm64). Do not repeat a
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
- M4 accumulator boundary (closed s5006: hangar 0/1955 = retail 0/576; the 8 port 640-phase 0x8000 rows are ordinary values, no clamp shape), attached-mesh mission contract, hangar pillars,
  col-511 noise, `0x1F0D74`, and overlay-registration chunking are parked.
- Generated-symbol renaming is active again because the companion now supplies
  additional semantic mappings. s5025 qualified and preserved
  `func_800B3824 -> buildLevelSelectTextTextures`; continue one candidate at a
  time with the semantic-name, exact-span, and live-caller gates. The older
  s4999 no-safe-map result still applies to `0x8000040C` and `0x800E9AE0`.
- M3 patch-runtime qualification remains blocked on the MIPS GCC toolchain.
  s5023 independently confirmed that CMake omits `PatchesLib` when GCC is
  absent; the available assembler/linker are sufficient only for the
  assembly-only artifact.

## Superseded conclusions

- **s5007/s5009: "loop needs an owner decision; no runnable experiment"** — believable because every audited thread was closed and the s4993 per-origin budget had been run. Wrong because the mission-qualified s4994 sample was runnable via the soak queue; it had just never been enqueued (s5010).

- **s5001 “M4 accumulator witness needs a human-installed LLE RSP plugin”** -
  believable because the oracle README names `mupen64plus-rsp-hle` and s4689
  measured no accumulator/DMEM rows, and the s4514 cxd4 build was not carried
  forward. Refuted s5002: a built cxd4 dylib already exists in the maintained
  oracle tree and reached the hangar in s4514; exposing `VACC` is a local patch.
- **s4985 “a narrower publication/observation lock will close the stale-base
  calls”** - believable because it preserves exclusion only over the writer's
  base/count stores and the mixer's paired count/base loads, avoiding the
  route-blocking span of the whole-function mutex. Overturned by the
  same-run armed soak: title, hangar, mission, allocator, PCM, and no-crash
  controls all passed, but kind=bad=8 remained. This is single-source
  evidence against this lock placement; it does not prove which reader or
  writer produces the rows. No guard or value rewrite was added.

- **s4982 “a reader acquire fence will close the stale-base calls”** - believable because the writer now has a release fence after both base stores and before the legitimate count publication. Overturned by the clean same-route soak: allocator and mission controls passed, but the four `s4540` bad rows remained. The ordinary `MEM_HU` load plus fence is not an effective pair handoff; no guard or value rewrite was added.
- **s4983 “explicit atomic guest-memory observation will close the stale-base calls”** - believable because both publication sites and both mixer reads were changed to host acquire/release atomics at the exact guest locations. Overturned by the same-route armed soak: controls passed, but 8 stale rows remained. This leaves a lock-compatible handoff as the next discriminator; no guard or value rewrite was added.

- **s4985 “a host mutex around both complete functions will close the stale-base calls”** - believable because it provides exclusion across allocator publication and mixer observation. Not selected: the same armed recipe did not reach the title positive control, despite one allocator entry, so the whole-function lock is route-blocking/unevaluable. This does not refute a narrower publication/observation lock; no value guard or rewrite was added.

- **s4981 expected "writer reorder closes the race"** - believable because the
  source fix moved the legitimate count publication after allocation and added
  a release fence. Overturned by the same-run armed validation: allocator
  control and 9 array-control rows fired, yet 4 stale-base calls remained.
  This selects a reader-side ordering defect; no guard or value rewrite was
  added.

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

## RESOLVED (s5050) - s5049 clobber of N64Recomp/RecompiledFuncs
The s5049 in-place regen (tools/agent/regen_n64recomp.sh, still disabled) destroyed the live tree, but it is RESTORED and verified: N64Recomp/scratch_s4970_live (Oct-13 copy) + replay of post-s4970 scripts (scratch/agent/s5050_replay.sh, s5050_s5037.sh) compiles to byte-identical __text for 51/51 funcs_*.c vs the surviving build/libRecompiledFuncs.a (scratch/agent/s5050_compare.py). funcs.h/lookup.cpp/recomp_overlays.inl identical to the clobbered copies. The clobbered tree is kept at N64Recomp/RecompiledFuncs.s5049-clobbered. cmake --build is safe again (it recompiles ~5 files whose mtimes the replay touched; code identical). Never regen in place; "live tree is unreproducible" was wrong: backup + ordered apply_s* replay reproduces it.

## Next steps (single monotonic backlog)

> s5047: queued soak s5047_route_flake_hostload (2 back-to-back runs, per-key rc + host load). Read SOAK-RESULTS first: both pass = host-load flake (H1); both fail = rebuild with s5038 census / s5039 lib hook compiled out (H2) else H3 build staleness. Host load avg was 7.2 (Chrome/REAPER) at s5047.

- **s5044 note:** s5043 refuted 'GUARD2 dropped' as the cause of the poison-arm route stall; the only remaining recipe delta vs s5037 is ROGUESQ_FREE_CENSUS=1 (4/4 census runs stalled, 3/3 non-census reached mission; single-source). Do not combine census with keyed-route soaks. Poison arms re-queued as s5044_*_nocensus.

**s5041 (top):** double-free census (rs_free/rs_malloc shadow set) clean on the mission route: 0 doubles in >=16K frees, force control 16384/16384. Next: poison-on-free read-after-free probe (NEXT.md).
**s5040:** mq census class closed on keyed route (jam never called under force; setevent control fired). Next: use-after-free readers after audited frees (scratch/agent/NEXT.md).

**s5030 (top, supersedes the s5027 rename item):** The generated-symbol renaming
sweep is CLOSED. Measured on the current N64Recomp/RecompiledFuncs tree: 2 of the
~1,548 s1487 placeholders remain (`func_8000040C`, `func_800E9AE0`) and both already
have `tools/rename_generated_symbols.py` entries (the tree just predates the mapping);
all 14 remaining menu-overlay companion candidates 0x800B32F4..0x800B4048 are already
generated under their companion names (N64Recomp reads the symbol files). Adding more
helper entries is a no-op. The next unit must be M5 / M3 / retail-entry work, or a
human decision on the missing MIPS GCC toolchain (s5023). Gate script:
`scratch/agent/s5030_rename_gate.py LO HI`.

**s5027 (top):** The next bounded rename candidate is the next newly mapped
menu-overlay symbol. Apply the same independent companion-address, exact-span,
and live-caller gates before adding it to
`tools/rename_generated_symbols.py`; reject stale, split, or callerless
records. Keep runtime and patch qualification unchanged.

**s5025 (completed):** `func_800B2630 -> buildFormatMessageGlyphBuffer` passed
all gates and is now explicit in the regeneration helper. The snapshot was
already synchronized, so no generated code or runtime behavior changed.

**s5023 (top):** The normal `PatchesLib` target is not present after a clean
reconfigure because `mips64-elf-gcc` is unavailable on this host; only
`mips-linux-gnu-as/ld` are installed. The patch-runtime qualification is
blocked until a MIPS GCC toolchain is supplied. Do not substitute the
assembly-only artifact for this test or enable the override. Once GCC is
available, rerun `cmake -S . -B build -DMIPS_TOOLCHAIN_DIR=<toolchain>`, then
`cmake --build build --target PatchesLib -j2`; successful generation and
compilation selects the normal-path hypothesis, while a generated relocation
failure selects the residual-artifact hypothesis.

**s5022:** The exact-span assembly now passes N64Recomp after the ELF
reader integration fix for absolute linker aliases that match game reference
symbols. The next bounded unit is to build the normal patch pipeline with the
C implementation excluded only for this validation, confirm the generated
host artifact is accepted by the CMake target, and keep the runtime override
disabled until that artifact-level integration is qualified.

**s5021 (completed):** The recovered generated snapshot and reconstructed assembly
now agree on the complete `0x80007D74..0x80007E58` window and exact `0xE8`
span. The remaining bounded unit is an N64Recomp integration fix for the
faithful direct call to `findAndUnlinkSmallestEntry` at `0x8002221C`; the
current tool reports no function for that external `jal` and clears output.
Keep the override disabled until the exact assembly is consumable, and do not
replace the direct call with an indirect sequence merely to satisfy the tool.

**s5020 (superseded):** The missing source artifact was not yet located; this
is superseded by s5021's preserved generated snapshot and exact reconstruction.

**s5019:** The assembly-only patch pipeline and corrected symbol identity
are qualified, but the first bounded slice is structurally incomplete (0x44
bytes emitted versus the original 0xE8-byte entry). The next bounded unit is
to hand-port the remaining original `allocateDisplayListBuffer` control flow
and queue stores in assembly, then compare its disassembly and generated host
function to the known 0x80007D74–0x80007E58 path. Keep it disabled until the
full path matches; the missing MIPS C compiler still blocks compiling
`patches/heap_guards.c` directly.

**s5020 (top):** Obtain or reconstruct the missing recovered instruction window
for `allocateDisplayListBuffer` (`0x80007D74..0x80007E58`) before extending the
assembly probe again. Compare its branch targets and every memory store with
`patches/heap_guard_asm.S`; a source-backed exact `0xE8` span selects faithful
assembly coverage, while absent or ambiguous source leaves this M3 route
blocked. Do not enable the override or pad the function to match size.

**s5012 (top):** The mission-qualified s4994 sample ran validly (mission_onset_t=173, arm=1, crash=0): 32 of 32 mission-origin s4540 caller rows were current-base `0x8018C720`, 0 stale `0x801714D0`; with s4993 (0 bad rows at mission origins) this closes the mission-phase `kind=bad` thread. No runnable M5 unit remains; next eligible work is a genuinely new M3 idiom class or a new witness for the parked retail/M4 boundaries. Declaring M5 done stays an owner call, non-gating.

**s5010 (top):** The s5007/s5009 "BLOCKED on owner decision" was refuted: running the queued mission-sample soak needs no human decision (the s4994-instrumented binary is already built). Enqueued `soak_queue/s5010_s4540_mission_sample.sh`; next unit is consuming its verdict (NEXT.md). Declaring M5 done stays an owner question but is non-gating.

**s5007 (top):** All priority threads are closed or parked; loop is BLOCKED on an owner decision (scratch/agent/BLOCKED.md). Only live defect: mission-phase `kind=bad` voice-index reads (H-lock-required); s4985 lock attempt was route-unevaluable.

**s5000 (top):** The external-retail retry is route-mismatched: retail reached
the qualified phases and remained absent at `0x800903F0`, but the port did not
reach qualified hangar. Keep this question parked until a new port route
reaches `0x006AB400`; no mitigation was added.

**s4999 (prior):** The residual generated-symbol audit found no safe rename. The
`0x8000040C` entry has a live caller and exact span but no semantic companion
name; `0x800E9AE0` has an exact span but no semantic companion name or
generated live caller. The local inferred/mechanical rename entries do not
meet the gates. No generated file, mapping, or behavior was changed. Detailed
evidence: `docs/RENAME-S4999-AUDIT.md`. The symbol sweep is closed pending a
new mapping source; next eligible work is a genuinely new M3 class or the
parked external-retail/M4 boundary only if a new witness exists.

**s4998 (prior):** The complete register-target indirect-call audit closed the
remaining non-`$ra` M3 dispatch class: 113 `LOOKUP_FUNC(ctx->rN)` sites split
into 42 memory-derived, 3 arithmetic-derived, 11 other, and 57 locally
unresolved callback/data-as-code sites; the independent census found 177/177
jump-table `switch_error` defaults and 114 `$zero` sites in known data regions.
No silent lowering or reachable malformed dispatch was found, and the runtime
log search found no CPU missing-function marker. No guard or recompiler change
is authorized. M3 is parked pending a new class or witness; the next eligible
unit is the generated-symbol-renaming sweep after its required last-15-session
preflight.

**s4995 (prior):** The new ordinary s4540 caller sample is live and regeneration-preserved, but the s4984 retry reached hangar and pre-mission origins only (`mission_onset_t=-1`), with no mission-origin rows. The s4540 arm and s4987 observations fired, proving the instrument, but their pre-mission phase cannot discriminate the hypotheses. This thread is parked after the mandatory pivot; its mission-origin zero remains unevaluable. ORIGIN: legitimate writer is `allocateSongChannelArray`; this remains an observation/propagation boundary, not a value-rewrite target.

**s4984 (prior):** The explicit atomic count/base loads and release stores reached mission (onset 176 s) with `ctl_arm=1`, `s4579A=9`, `bad=8`, `pidma=0`, crash=0, abort=0, and PCM positive control 147. H-atomic-observation is refuted for this implementation; H-lock-required remains.

**s4981 (prior):** Armed soak s4980 showed the count-before-base race LIVE (`[s4540-call] kind=bad` s0=30 count=32 against the old 18-voice base; ctl_arm=1). Root cause: the s147 reorder never reached the live funcs_23.c. Fixed by `tools/apply_s4981_count_after_base.py` (applied, replay-registered, built). Verification showed the route and allocator were live, but the reader still logged 4 bad calls; see s4982.

**s4980 (prior):** Default soaks since s4959 never armed the env-gated S45xx instruments (0 `[s4539-entry] kind=arm` lines), so their zero `kind=bad`/`pi.cpp` hits are uninterpretable; 6 uninstrumented mission runs had 0 CRASH. Armed recipe queued (`soak_queue/s4980_armed_mission_a.sh`), verdict decides close vs source fix (NEXT.md).

**s4979 (top):** Retail-entry boundary CLOSED as design-dead. Two-source offline check (`tools/voice_kind_crosscheck.py`, no new run): (a) port `[init-desc]` rows are retail-consistent — 11,444 rows, only descs `0x8013ACA0` (d04 top nibble 0xB -> flag set, kind 3) and `0x8011C820` (d04 `0x801B2C60`, nibble 8 -> flag clear, kind 0); init (`0x80092234-0x80092268`) sets flag bit0 only when `(d04&0xF0000000)!=0x80000000`; (b) retail also inits kind-0 voices from `0x8011C820` (ra `0x800980f4`) and their next renders show flag v0=0 at `0x800901C0`, so they never reach `0x800901CC/0x800903F0`. H1 (init skipped) and H2 (stray ASCII store) refuted; the port reaches 0x800903F0 only via s4577/s4578's mixer index past the 18-voice array (count stored before `rs_malloc`, base after) into name-string memory. Not a retail boundary; no guard added.
**s4978:** Retail branch census: 0x800903F0 is design-dead in retail. Flagged voices always have `+0x6D==3` (241,308 hits); the `+0x6D==0` branch at 0x80090358 has 0 hits. The port reaches it, so port voice records carry kind 0 with the flag set, a state retail never makes. Next: port-side histogram of `+0x6D` and its writers (NEXT.md).

**s4977 (prior):** M3 idiom census EXHAUSTED: mfc1/dmfc1 width (4 dmfc1/dmtc1 sites, all $zero), sltiu sign (2 negative-imm sites, data-as-code, semantics correct), jr non-ra (176 $v0 jump tables; 12 $zero data-as-code; ~14 LOOKUP_FUNC uninspected) all benign. Next: REVISIT external retail-entry with a new angle (see NEXT.md).

**s4976 (top):** ldc1/sdc1 alignment class closed: 12/2644 misaligned-offset sites, all data-as-code; LD/SD are 32-bit pairs so arm64 cannot fault. Remaining M3 candidates: mfc1/dmfc1 width, sltiu, jr non-ra.

**s4975 (prior):** 64-bit mul/div class closed (see M3 list). Remaining unexamined M3 candidates: ldc1/sdc1 alignment, cvt rounding modes, mfc1/dmfc1 width, sltiu, jr non-ra. Then resume backlog item 3/4.

**s4974 (top):** s4972r soak consumed: 5/5 runs seen640=1 (positive control) and exit640@48s, bad=0. With s4971 (4/4) that is 0/9 VI-640 stalls vs s4794's 2/5; Fisher p~0.1, so not proven gone but not reproducible. VI-640 route wall CLOSED as non-observable (re-open only on a stay640 line in any future soak, since all recipes now arm seen640). Next: M3 census of idiom classes NOT in the closed list (see NEXT.md).

**s4973 (prior):** s4972 soaks never ran (zsh ${0:A:h...} bug, rc=2 in 0 s). Requeued as soak_queue/s4972r_vi640_idle_a.sh (5 idle runs; verdict in soak_results/s4972r_a/summary.txt, seen640=1 is the positive control). 0/5 stall => close the VI-640 wall; any stay640 => reproduced stall, investigate phase-gated.

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
3. **Completed — s4944/s4964:** run the A1 image/silent auxiliary-store A/B concurrently with
   title + mission origins as controls (route qualified by s4943); relaunch any
   arm that stalls at VI-640 rather than reading it as a null.
4. **Partly done — s5003 (capture only):** patch the already-built cxd4 LLE RSP
   (`rs64-oracle/src/mupen64plus-rsp-cxd4`, global `VACC[3][N]`) to dump
   accumulator + DMEM, run with `tools/oracle/rdplog` and positive controls
   (title VI 1024 non-empty, hangar `0x006AB400` reached, dump non-zero on a
   known F5 task), then compare the first accumulator publication against the
   port. Do not rewrite or guard any value. Keep the patch diff under `tools/oracle/`.
   s5003 landed the patch (`tools/oracle/patches/cxd4-rsp-dump.md`) and the
   recipe `scratch/agent/s5003_cxd4_dump.sh`; capture `scratch/agent/s5003/rsp.dump`
   passed all controls (6536 records = 2089 gfx + 4447 audio; gfx count equals
   2089 rdp rows; VACC non-zero in 5603; VI 1024 and 512@0x6ab800 reached).
   s5004 retail baseline: 0/576 hangar gfx tasks end with any VACC lane == 0x8000 (also 0 in every other phase); refutes retail-also-saturates, single-source until the port side is compared.
   **s5005 CLOSED (two-source):** the port's task-end accumulator (`ROGUESQ_LOG_M4_END`,
   fixup 10b, `tools/m4_end_table.py`) at hangar 512 (phase ord 5) is 0/1955 tasks with
   any 0x8000 lane, nz>0 in 1955/1955 (positive control) - same as retail 0/576. The
   end-of-task accumulator is NOT the carrier of the hangar Y=0x8000; M4 accumulator
   thread closed at task-end granularity (mid-task not examined). Residual lead: port
   640 phase (ord 3) has 8/1281 tasks with an accl 0x8000 lane vs retail 640 0/425
   (likely a legitimate 48-bit value; unclassified). Capture: scratch/agent/s5005_port_end_acc.sh.
5. Revisit M3 only as a complete idiom-class audit with a new discriminator;
   conditional-move recompiler support is a separate engineering task.
6. Revisit external retail-entry only with a recipe that reaches the qualified
   port hangar phase; otherwise keep it parked.
7. Resume symbol renaming only after the required last-15-session preflight
   shows it is not a REVISIT and a new mapping source exists.
8. **Next:** when a MIPS GCC compiler is supplied, configure with explicit
   `-DMIPS_GCC=... -DMIPS_LD=...` paths and build `PatchesLib`; classify
   generation/compile success, target omission, or relocation/symbol failure.
   Until then, do not repeat the blocked qualification command.

## Evidence index

The detailed s4822–s4937 headline history and older backlog are archived in
`docs/PROJECT-OVERVIEW.md`; per-run evidence is in the session-specific M5/M3
notes and `PORTING-STATE.md`. The next iteration must read `scratch/agent/NEXT.md`
and the tail of `scratch/agent/SOAK-RESULTS.md` before acting.

- s4947: aux-store A/B thread closed; arms identical on [phase] transitions (6 each), pacing, rows/flip. Not a lead.
- s4948: all tiers closed or unevaluable; BLOCKED for owner decision (see scratch/agent/BLOCKED.md).

### s4950 update
Mission-route soak (solo, N=5): 5/5 reached origin 0x690400, 0 do_break hits, 0 crashes (single-source, small N). VI640-stall rate still undetermined: vi-fs-decision lines carry stalled=1 late in every run, needs a phase-gated count, not a raw grep.

- Open owner-level options (not blockers, s5008): (a) declare M5 done, set new target; (c) supply symbol-mapping source for rename sweep. Mission-phase kind=bad voice reads: per-origin budget ALREADY RUN (s4993): 0 bad rows at mission origins vs 2,602 pre-mission, same-run control passed; only open arm is the s4994 mission-origin caller sample, which needs a mission-qualified recipe (s4995 never reached mission).

- s5011: s5010 mission-sample soak route-unevaluable (mission_onset_t=-1; updateHangarBayScene crash). Retry queued as s5012; no conclusion on stale32/cur20.

## s5034 addendum — heap-guard census
s5033 soak: guard2/3/4, r1, coalesce guards fired 0 times on title->hangar->mission (onset 170s), no crash. Single-source (no fire control yet). MIPS toolchain no longer gates heap-guard work. Fire-control env ROGUESQ_FORCE_ALLOC_TAIL_GUARD2 is in fixup_game_funcs_vendored.py but unbuilt.

s5035: guard2 force-control fired (93 lines, 1 site 0x800079AC) on the same route -> s5033 guard2 zero is a valid two-source null (guard is not load-bearing on title->hangar->mission). guard3/4/coalesce/r1 still single-source nulls. Metal toolchain absent: rebuild via scratch/agent/s5034_build.sh (touches shader artifacts, then cmake). Live guard2 patch: tools/apply_s5034_guard2_force.py.

s5036: guard3/guard4 log-only force controls (ROGUESQ_FORCE_ALLOC_TAIL_GUARD3/4) built into 190 live blocks (tools/apply_s5036_guard34_force.py, in RS64_REPLAY); soak `s5036_guard34_force_control` enqueued. r1 guard env has NO generated site (null by construction); coalesce site's `[coalesce-next]` log is its control. Verdict pending -> NEXT.md.
s5036 result: heap-guard census CLOSED. Mission route (onset 174 s, crash=0): guard3 force fired 7752x at 4 drain-mesh sites, coalesce site reached 256x; no guard ever tripped => guards are live-but-silent, not load-bearing there. guard4: 0 passes under force (unreached; shares guard3's generator, no own control = single-source on wiring). r1: no generated site.

## s5037 addendum — copy-primitive guard
memcpy_recomp/bcopy_recomp now carry a host range/length guard (tools/apply_s5037_copy_guard.py; FORCE control env ROGUESQ_COPY_GUARD_FORCE). Census soaks s5037_copy_guard_{default,force} enqueued; verdict pending. Next: consume them (NEXT.md).

## s5038 addendum — copy-guard class closed; message-queue census built
s5037 soaks (mission_onset 170/174s, crash=0, 1.1M lines each): force arm cg=16 (positive control fired), default arm cg=0 => no memcpy/bcopy with wild length or non-RDRAM span on the keyed title->hangar->mission route (two-source, same recipe). Class closed there; other routes unexercised. Next: s5038 log-only message-queue structure census in osSendMesg_recomp/osRecvMesg_recomp (ROGUESQ_MQ_CENSUS, control ROGUESQ_MQ_CENSUS_FORCE); soaks s5038_mq_census_{default,force} enqueued; expect force mq=16, default mq=0 closes the class (osJamMesg has no host wrapper, uncovered).
s5038 result: force mq=16 (control), default mq=0, crash=0 on the keyed route => message-queue structure class closed there (osJamMesg uncovered). Next: use-after-free reads after audited frees.

- s5042: read-after-free poison probe (ROGUESQ_FREE_POISON, tools/apply_s5042_free_poison.py) built; on/off soaks queued, verdicts pending (see NEXT.md).
- s5043: s5042 arms stalled before hangar because the recipe dropped GUARD2 (vs s5037); corrected arms s5043_poison_{off,on}_g2 queued.
- (s5045) s5044 no-census arms stalled nohangar too: FREE_CENSUS refuted; s5045 control rerun of s5037 queued to separate route flake from binary regression (NEXT.md).

- (s5048) s5047 both runs nohangar (keys rc=0, load 4-7); pre-s5038 upstream_compat.cpp rebuild also stalls => mq census/lib hook refuted. Left: host load vs generated-code staleness; next = clean s5037 worktree rebuild (NEXT.md).

## s5046 addendum — keyed route regression (open)
Since s5042, the keyed title->hangar recipe (s5037 default) stalls: after title (phase 4, 1024/0x790400) the game goes to 640/0x696100 screens, never hangar 512/0x6AB400 (working s5037 reached hangar t=91, mission t=174). 6 straight failures (s5042-s5046). Refuted as cause: s5041/s5042 hooks (hook-free rebuild s5046 stalls identically; script tools/revert_s5041_s5042_hooks.py, dropped from RS64_REPLAY), save file (unchanged), poison/census/GUARD2 arms. Open: host load / stopwatch-driven keys vs s5038-s5040 mq census + lib weak hook. All free-poison / census-derived conclusions in s5041-s5045 entries remain valid only for phases up to title. Next: see scratch/agent/NEXT.md.
