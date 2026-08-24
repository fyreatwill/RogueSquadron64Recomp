# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the append-only
ledger remains authoritative for exact commands, counts, and probe rows.
Maintained in Session 2227 (2026-08-23); behavioral and source evidence is
current through s2226. The s2198–s2226 archive is §44.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio is still defaulted to the silent `M_AUDTASK` `Broke` stub. The
  Factor 5 image arm is opt-in through `ROGUESQ_AUDIO_UCODE=1`; C88=`1` is
  also a diagnostic behavior arm. Stock `aspMain` is not the game's MusyX/
  Factor 5 contract, and MORT is a separate CPU speech asset.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. Its host canary is inside the generated mix-buffer span;
  `canary_ok=0` is probe data and does not gate completion, writeback, or DMA.
- s2220 matched the retail payload/polarity of `reapplyDisplayMode` at
  `0x8008EC88`: C88=`1` reaches service, slot completion, and nonzero PCM
  controls; forced zero does not. Keep this opt-in pending the remaining M5
  contract work.
- Retail key-on ground truth reaches the boundary and hangar, skips the eight
  watched divide PCs, and executes the alternate post-guard transfer path.
  The phase-keyed `$v0/$s1/$a0/$a2` tuple sets differ across both target
  origins and hangar. The port has positive normal-tail/slot behavior at four
  sites, but its 2048-entry first-target tuple rings still overflow six sites;
  tuple parity is not measured.
- The port's `ViState::field` is fixed at zero by default. Opt-in field,
  current-register, timing, and total-`VI` arms recover the two-origin target
  split, but the natural host publisher/cadence is unidentified. No such
  knob is default-on.

## Active backlog

Closed investigations are not active work items. The sequence is monotonic.

1. **M5 key-on tuple contract.** Expand the regeneration-safe port census
   ring from 2048 to 8192 entries per transfer PC, then compare one complete
   phase-keyed table against s2223's retail table. This is the next work unit
   in [`scratch/agent/NEXT.md`](../scratch/agent/NEXT.md). No key-on return,
   guard, task-field rewrite, default flip, or mitigation follows from the
   comparison automatically.
2. **M5 A1: identify the missing second-origin transition.** Retail's
   `__osViNext` context uses `framep` plus the selected current field to make
   both target origins. The port has the candidates but its natural field
   publisher is still unknown; all recovery knobs remain diagnostic-only.
3. **M5 drain in-loop tick A/B; parked.** s2125 selected `H-PumpIrrelevant`
   only at route scope, while s2126–s2128 failed to place both drain arms in
   the target comparison. Resume only with a new renderer-recovery or
   ground-truth discriminator.
4. **M3 crash work.** Resume only as a systematic idiom-class audit with a
   named discriminator. The dormant `slotDispatcherIter+872` class has 7,659
   clean hangar calls in its guarded run; no mitigation is authorized.
5. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
   because the oracle cannot screenshot the LLE path; do not repeat the
   `0xD60` scan.

Generated-symbol renaming is closed at the useful boundary: the remaining
names are the five parked/intentional holds
`func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, and
`func_800E9AE0`. Do not re-census or invent names for them.

## Durable boundaries

### Route and rendering

Factor 5 command mappings and independent-ground-truth requirements are in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

The accepted four-arm route table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11`
reaches title and hangar, `01` reaches title only, and `10`/`00` reach neither.
This is recipe-level port evidence, not an explanation of audio or PCM. Menu
spin yield is a diagnostic route aid, not a default behavior change.

### M5 audio, status, service, wait, AI, and MORT

The generated tree reaches both target phases. Direct service entry/exit and
the service gate/loop are live. The port observes the legitimate slot-0
sequence through the service store at `0x8009B7EC`, guest address
`0x80154620`, including `0x03 -> 0x00`; retail independently observes the
same status-table cycle. Retail not executing port crash labels
`0x8000B650`/`0x80095D54` is a PC-scope boundary, not permission to alter the
port wait or guard.

s2132–s2133 and s2152–s2153 close the sampled AI-status/queue boundary:
retail queues through `osAiSetNextBuffer`; the only status poll is the
in-function `__osAiDeviceBusy`, which does not return FIFO-full on the covered
title/hangar route, and the generated caller ignores v0. Do not change
`osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`.

s2135–s2140 close the sampled RSP-image/task/output edge:
`factor5b_rsp.toml` is the retail audio image, MORT speech is separate, task
fields match, and both retail and port write `data_ptr+0x100`. The image arm
is nontrivial but its sampled host output, PCM, and validated slot completion
were absent in s2219; s2220's C88 result supplies the current downstream
discriminator. The image arm remains opt-in.

s2218's Rice oracle passed its whole-RDRAM control, reached both target 640
origins, and found 17 writes from five PCs to the watched retail gate; its
capture did not expose every payload or the active writer for the other status
word. It also saw zero writes to `0x0014998A`, 13,319 writes to
`0x0014974C`, and all three watched task/AI callsites. This is ground-truth
capture, not authorization for a gate or task change.

### VI state and the second origin

s2198–s2204 moved the boundary from the guest swap caller to VI state.
Retail repeatedly reaches `0x00696100` and `0x00696600`; its target context
has field 0/1 respectively, and `framep` plus the selected field origin
produces the next origin. The port has matching framebuffer/mode candidates,
but its default selector chooses field 0, so it commits only the first target
origin. Same-built opt-in field-alternation and current-register arms recover
both origins.

s2200–s2216 rule out the obvious retail/port alternatives at their measured
scopes: retail's watched `osViGetCurrentField` returns zero on sampled target
rows; the port guest `comRegs.vCurrent` and `VI_V_CURRENT_LINE_REG` are also
fixed at zero; before-screen versus post-commit placement gives the same
target split; and `delta_total_vis` is one in all scheduler arms. The
legitimate natural host-register publisher and callback-versus-total-`VI`
cadence remain open. No VI recovery arm is default-on.

### Key-on branch state

s2221's port census is a positive normal-tail/slot result at sampled hangar
scope: four sites divide by `0xC0` with no guard hits and show `0x02 -> 0x00`
slot transitions; four sites have no entries. Retail independently reaches
the boundary and hangar. s2222's range witness proves that retail executes
the alternate interior path rather than simply missing instrumentation.
s2223's explicit width buckets show all eight transfer PCs in both target
origins and hangar, all eight divide PCs at zero, and phase-specific disjoint
tuple sets. s2225 showed the detail logger itself fires and reaches first
target, title, and hangar. s2226 expanded the port rings to 2048: hangar and
title had zero overflow, but six first-target rings remained capped and the
second target origin was absent. Expand the cap before interpreting parity.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, dormant slot-dispatch census, two-line overlay-move class, and leftover
`fake_func_*` size-`> 0xC` class are closed at their stated scopes. M3 resumes
only as an idiom-class audit or with a new discriminator. M4
accumulator/beam evidence rules out the old shade-lane theory but is not pixel
ground truth. Remaining `func_*` placeholders are semantic holds or
intentional non-sync entries.

## Superseded conclusions

Detailed reversals are archived in `PROJECT-OVERVIEW.md` §§26 and 35–44 and
remain in the append-only ledger. Operationally:

- “640 is a flaky crash,” missing-input, missing-wait-return, and unqualified
  PCM-null claims were believable while target rows were absent; same-run
  controls and the qualified LLE/spin recipe later reached both phases.
- The old title/hangar callback split and global zero-payload image-DMA claim
  were believable before joins carried guest-address/full-span identity and
  before a nonzero hangar task was sampled.
- Clean-stub, canary-poison, final-E50, uniform-gate, and host-isolator
  explanations were believable before complete task/consumer and
  writer-specific tables. Current controls show real image DMEM activity, a
  mixed retail gate, and sampled nonzero PCM joins; none authorizes a runtime
  change.
- The s2160 wait-slot crash was initially believable as a guest wait/slot
  defect. s2161 named retail's count-byte writers and matched it to an
  unsigned PATCH address; s2162 fixed the PATCH and reached title/hangar.
- The s2163 cinematic regression is not explained by NULL pointers, guessed
  KSEG0 addressing, missing `+0x50` or heap0 stores, a deterministic keyword
  hang, or retail absence from the transform/vec3 path. s2164–s2182 refuted
  each at its stated scope; the failure remains intermittent.
- s2190–s2197's missing second-origin cells and early caller mismatch were
  coverage/scope artifacts at their earlier boundaries. The later VI-context
  table moved the open question to the port's missing field publisher; do not
  add a writer guard or task rewrite.
- s2206's quiet `0x0066AA00` route was initially plausible as damage, but
  s2208's independent Rice trace observed the same legitimate origin.
- s2215's cadence selection is superseded by s2216: all measured
  `delta_total_vis` values were one, so callback versus total-`VI` cadence is
  unresolved.
- s2221's narrow retail nulls were a coverage-only observation. s2222–s2223
  show the alternate path and its phase-specific tuples; no key-on return
  change follows. s2224's coverage selection is superseded by s2225–s2226;
  the remaining cap artifact is a measurement limit, not a runtime defect.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35; s1880–s1949 is
§36; M5 archives through s2047 are §§37–38; the late route/fill boundary is
§39; s2080–s2108 is §40; B40 is §41; s2113–s2158 is §42; s2164–s2197 is
§43; and s2198–s2226 is §44. Exact commands, counts, failed retries, and
session headings remain in `PORTING-STATE.md`.

Selected hypotheses must not be widened from single-source or single-arm
observations. Do not re-flip the image default, guess S32 addressing, NULL-
skip, skip/allow `matchKeywordWithPriority` or its loads, disable
`NAN_CHECK`, add a wait/slot guard, or land a copyToRAM/CIMG writeback guard.
Do not treat last-guest-PC `0x8000834c` as the abort site.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical addresses and
  should be phase-gated by VI callbacks.
- A null is worthless without a same-run positive control. Batch all desired
  counters and every A/B arm in one build/run. Scope counters and log budgets
  to the relevant phase.
- Read `F5-UCODE-REFERENCE.md` before interpreting a Factor 5 display list.
  Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`,
  or `git reset --hard`. If `lib/` changes, export submodule patches in the
  same iteration.
- A mitigation is not an explanation. Name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a whole discriminating table and an
  outcome that selects among hypotheses. Repeated counters are not a work
  unit.
