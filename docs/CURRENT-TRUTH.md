# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history
is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2186
(2026-08-23); behavioral and source evidence is current through s2185.

The detailed s2164–s2185 chain was migrated to
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) §43 during this maintenance
pass. This file is the compact operational state, not a second ledger.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio is still defaulted to the silent `Broke` stub. The Factor 5
  image arm is opt-in through `ROGUESQ_AUDIO_UCODE=1`; it is not default-on.
  The M5 plan is [`M5-AUDIO-PLAN.md`](M5-AUDIO-PLAN.md).
- s2162 fixed the unsigned PATCH `MEM_BU(0X1AD0, 0X80140000)` by using an
  S32-addressed KSEG0 value; the image arm then returned from
  `waitForAnyAudioSlot` and reached title/hangar. s2163's same-build retry
  selected `H-CinematicRegress`: unset/`=1` failed intermittently in the
  post-wait 640 cinematic while `=0` reached title/hangar. The default flip
  was reverted.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. Its host canary is inside the generated mix-buffer span;
  `canary_ok=0` is a probe field and does not gate completion, writeback, or
  DMA recording. MORT is a CPU speech asset, not a second RSP image.
- s2184 classified one completing image run as title/hangar-only: 5,841
  joins, a positive 640 phase control, zero 640 image joins, and zero
  overlap with six named physical words. s2185 independently confirmed
  that retail writes all six words, but only named the `0x2231EC` writer;
  five retail writer identities remain open. These results are scoped and
  do not authorize a guard, task rewrite, or default flip.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not active
work items.

1. **M5 A1 cinematic window; blocks default-on.** Obtain a fresh failing
   `ROGUESQ_AUDIO_UCODE=1` run with positive `[audtask-image-join]` count and
   a phase-gated 640 row at origin `0x00696100`. Parse join intervals against
   physical `0x25A580`, `0x0CA748`, `0x0C7B0C`, `0x165E40`, `0x0CDB58`, and
   `0x2231EC`. Do not add a port instrument, rebuild, mitigation, or default
   flip for this work unit.
2. **M5 drain in-loop tick A/B; parked.** s2125 selected
   `H-PumpIrrelevant` only at route scope. s2126–s2128 failed to put both
   drain arms in the target comparison despite positive controls. Resume
   only with a new renderer-recovery or ground-truth discriminator.
3. **M3 crash work.** Continue only as systematic idiom-class audits with
   a named discriminator. The dormant `slotDispatcherIter+872` class has
   7,659 clean hangar calls in its guarded run; no mitigation is authorized.
4. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
   because the oracle cannot screenshot the LLE path. Do not repeat the
   `0xD60` scan.
5. **Generated-symbol renaming sweep; closed.** s2149 closed the two-line
   overlay-move class and s2150 selected `H-LeftoverAllHolds` for leftover
   `fake_func_*` with ELF size `> 0xC`. The remaining generated names are
   the five parked/intentional holds `func_8000040C`, `func_800927B0`,
   `func_80092A54`, `func_80092CF0`, and `func_800E9AE0`. Do not re-census
   or invent names for them.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and independent-ground-truth requirements
are in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

Forced LLE is the route gate under the common wrapper. The accepted
four-arm table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title and
hangar, `01` reaches title only, and `10`/`00` reach neither. This is
recipe-level port evidence, not an explanation of audio or PCM. Menu spin
yield is a diagnostic route aid, not a default behavior change.

Route history is in `PROJECT-OVERVIEW.md` §§36–43. s2093–s2096 closed the
wrapper, task-thread, SP external-delivery, and guest-receive route at the
qualified recipe scope. s2111 superseded B40 as a route-admission cause at
that recipe; s2112 selected recipe timing for the unreproduced phase-7
origin split. Do not reopen the SP queue or B40 read-site census.

### M5 status, service, wait, AI, and MORT

The generated tree reaches both target phases. Direct service entry/exit and
the service gate/loop are live. The port observes the legitimate slot-0
sequence through the service store at `0x8009B7EC`, guest address
`0x80154620`, including `0x03 -> 0x00`. Retail independently observes the
same status-table cycle. Retail does not execute port crash labels
`0x8000B650`/`0x80095D54`; that is a PC-scope boundary, not permission to
change port wait or guard behavior.

s2122 is a normal-path hangar key-on contract at sampled scope: four valid
`0xC0` divides and a normal tail with no early-return guard hit. s2123
independently establishes that the completion-wait contract is live on the
qualified retail route. s2125 closed the pump's sampled route-admission
question. A10 is parked after three coverage-only pairs.

s2132–s2133 plus s2152–s2153 close the sampled AI-status/queue boundary:
retail queues through `osAiSetNextBuffer`; the only status poll is the
in-function `__osAiDeviceBusy`; on the covered title/hangar route it never
returns FIFO-full; and the generated caller ignores v0. Do not change
`osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`.

s2135–s2140 close the sampled RSP-image/task/output edge:
`factor5b_rsp.toml` is the retail audio image, MORT speech is separate,
task fields match, and both retail and port write `data_ptr+0x100`.
s2138/s2139/s2151 close the MORT remaining-class reference decode. None of
these results defaults the image arm or rewrites task fields.

s2154–s2158 close the canary location/effect and host-isolator questions:
the canary lies in the mix buffer, is log/storage only, and the only live
image-arm isolation is the `ROGUESQ_AUDIO_UCODE` dispatch in
`get_rsp_microcode`. s2159 closed the named blocker census as policy-only;
s2160–s2163 then showed why the policy remains opt-in: the pre-S32 wait fault
was fixed, but the same-build image arm still has intermittent cinematic
regressions. The full pointer, heap, transform, NaN, and image-DMA chain is
archived in `PROJECT-OVERVIEW.md` §43.

The stock `aspMain` contract is not the game's MusyX contract. C88 testing
selected reversed-or-suppressing polarity at sampled port gate scope; no
blanket gate flip is authorized.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, dormant slot-dispatch census, two-line overlay-move class, and
leftover `fake_func_*` size-`> 0xC` class are closed at their stated scopes.
M3 resumes only as an idiom-class audit or with a new discriminator. M4
accumulator/beam evidence rules out the old shade-lane theory but is not
pixel ground truth. Remaining `func_*` placeholders are semantic holds or
intentional non-sync entries.

## Superseded conclusions

Detailed reversals are archived in `PROJECT-OVERVIEW.md` §§26 and 35–43 and
remain in the append-only ledger. Operationally:

- “640 is a flaky crash,” missing-input, missing-wait-return, and
  unqualified PCM-null claims were believable while target-phase rows were
  absent. Same-run controls and the qualified LLE/spin recipe later reached
  both phases.
- The old title/hangar callback split and global zero-payload image-DMA
  claim were believable before joins carried guest address/full-span
  identity and before a nonzero hangar task was sampled.
- Clean-stub, canary-poison, final-E50, uniform-gate, and host-isolator
  explanations were believable before complete task/consumer and
  writer-specific tables existed. Current controls show real image DMEM
  activity, a mixed retail gate, and sampled nonzero PCM joins; they do not
  authorize a runtime change.
- The s2160 wait-slot crash was initially believable as a guest wait/slot
  defect. s2161 named retail's count-byte writers and matched the fault to an
  unsigned PATCH address; s2162 fixed that PATCH and reached title/hangar.
- The s2163 cinematic regression is not explained by NULL pointers,
  guessed KSEG0 addressing, missing +0x50 or heap0 stores, a deterministic
  match-keyword hang, or retail absence from the transform/vec3 path:
  s2164–s2182 independently refuted each at its stated scope. The failure
  remains intermittent and unresolved.
- s2184's title/hangar-only image-DMA result is a completing-run result, not
  a universal claim. s2185's retail writer run proves target writes exist,
  but incomplete per-target attribution leaves the failing image join as
  the next discriminator.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is §36; M5 archives through s2047 are §§37–38; the late
route/fill boundary is §39; s2080–s2108 is §40; B40 is §41; and the
s2113–s2158 contract/MORT/AI/canary archive is §42. The s2164–s2185
pointer, failure, and image-DMA archive is §43. Exact commands, counts,
failed retries, and session headings remain in `PORTING-STATE.md`.

Selected hypotheses must not be widened from single-source or single-arm
observations. In particular, do not re-flip the image default, S32-address
by guess, NULL-skip, skip/allow `matchKeywordWithPriority` or its loads,
disable `NAN_CHECK`, add a wait/slot guard, or land a copyToRAM/CIMG
writeback guard. Do not treat last-guest-PC `0x8000834c` as the abort site.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm
  its whole-RDRAM positive control first; watches are physical addresses and
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
- A mitigation is not an explanation. Name the writer, state legitimacy,
  and add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a whole discriminating table and an
  outcome that selects among hypotheses. Repeated counters are not a work
  unit.
