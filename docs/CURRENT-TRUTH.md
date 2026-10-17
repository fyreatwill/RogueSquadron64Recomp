# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5296 (2026-10-17). The
chronological ledger is `PORTING-STATE.md`; durable background belongs in
`docs/PROJECT-OVERVIEW.md`; per-topic evidence is in the `docs/M5-S*.md` and
`docs/RENAME-S*.md` audit files.

## Headline

The validated route boots through attribution, N64 logo, intro, Factor 5 logo,
title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
origins (`0x00690400` and later `0x00620400`, VI 512). Audio is active on the
qualified image route; the silent `ROGUESQ_AUDIO_UCODE=0` path is only a
control. Mission input reaches the game and changes the player vehicle state.

The retail mission-entry byte is written by `musyxMixActiveVoices`.
Session 5227 watched both strides in one run. Origins `0x00690400` and
`0x00620400` entered on `0x80195190 + i*0x88`; `0x00690800` and
`0x00620800` entered on `0x80190E50 + i*0x88`. On every live stride the
dominant offset-`0x22` store is `0x80090F3C` (`sb $zero`), after the
entry read in the same iteration. `0x80090F8C` stores the constant 1
and is the minority. Neither writes the port's `0x03`. The idle stride
of each origin has no writer. No guard. Audit:
`docs/REVISIT-S5227-BOTH-STRIDES.md`.

The renaming sweep is paused at `__osCurrentHandle = 0x80039150`. Every libultra/ABI
candidate from `cosf 0x8002B190` through `osRecvMesg 0x800331D0` (and the
companion-only `__osPfs*`/`osPi*`/`osMotor*` entries between) was classified as
an unmaterialized host-wrapper/ABI entry or already-synchronized: preserve the
ABI name, no body to rename. Per-candidate detail was archived to
`docs/PROJECT-OVERVIEW.md` ("Archived sweep log"); audits are `docs/RENAME-S5*-AUDIT.md`.

Session 5278's new-angle entry-tuple revisit ran port and retail arms in
parallel with whole-RDRAM controls and mission-origin gates. Both reached
`0x00690400` and `0x00620400`; retail's `0x8008FAAC` execution rows and the
port's bounded samples agreed on caller `0x800902CC`, `s0`/`s1`, `a0`, `a2`,
`a3`, and `v0` shape. This is two-source evidence against a distinct caller
population, but the dynamic `a1` buffer and the invalid host-hook `r31` leave
the full contract unresolved. Audit: `docs/REVISIT-S5278-ENTRY-TUPLE.md`.

Session 5279 corrected the M4 retail mid-task decode. In one qualified run,
all 572 512-wide graphics tasks (including 286 at the two hangar origins) had
at least one `0x8000` VACC lane mid-task, while all 572 had zero at task end.
The whole-RDRAM control and both VACC dump streams fired; the requested
`0x80033FCC` publication watch did not, so publication ordering remains
unevaluable. The prior zero-mid-task claim was a signed-16-bit decoder error,
not a runtime result. Audit: `docs/REVISIT-S5279-M4-ACCUMULATOR-AUDIT.md`.

Session 5280's corrected port capture reached title and hangar with the same
build/run. In hangar phase 5, 2,000 bounded mid-task rows included 18 rows
with an `0x8000` accumulator component, while 352 task-end rows had zero
`sat8000`. The cap concentrated mid-task rows in one repeatedly staged task,
so this is single-source qualitative port evidence only: it rules out “the
port never creates transient `0x8000`,” but does not establish retail-like
per-task prevalence or timing. Audit:
`docs/REVISIT-S5280-M4-PORT-MIDTASK.md`.

Retail-entry boundary (`fillSampleStreamRange 0x8008FAAC`): retail enters it
~145k-290k times while interior `0x800903F0` stays at zero (single-source
oracle, S5183/S5203). S5224 full histograms: retail modal offset-`0x22` byte
`0x00`, retail `0x03` count 0, port modal `0x03`. S5227 (both strides, all four
origins): the live-stride writer is `0x80090F3C` (constant 0) in
`musyxMixActiveVoices`, minority constant-1 at `0x80090F8C`; neither writes the
port's `0x03`. No guard. Audits: `docs/REVISIT-S5183-*`, `S5203-*`, `S5223..S5227-*`.

This file was compacted at S5245 (maintenance); history is in git.

Session 5296's new-angle M4 revisit reanalyzed the qualified retail RSM1/RSD1
capture. All 3,036,036 mid-task records and 6,533 end-task records passed
format/sequence controls; all 2,085 retail graphics tasks ended with zero
0x8000 lanes. Mid-task retail had 367,023 sampled 0x8000 lanes across 20+
populated sample PCs, led by 0x0B18/0x0B20/0x0B1C/0x0B34/0x0B14 rather than
one unique PC. The RSM1 sequence is a global sample ordinal, not a task ID, so
per-task prevalence and publication ordering remain unevaluable. This is
single-source retail provenance with an independent end-task control; no port
mitigation follows. Audit: `docs/REVISIT-S5296-M4-MID-PC-PROVENANCE.md`.

## Durable state

### M5 audio

- The image route produces nonzero PCM and passes title, hangar, and mission
  phase controls. AI byte order is corrected. The audio task is not currently
  a zero-output stub, although the MusyX/MORT compatibility work is not fully
  complete.
- Mission route joins show fresh audio ordinals and row-0 resets at the
  `0x00690400 -> 0x00620400` handoff. Treat this as route reinitialization,
  not grounds for filtering.
- The voice-render range fires in retail title/hangar, but exact consumer
  `0x800903F0` remains absent in retail. The port-only mixer overrun remains
  an internal boundary; do not add a guard without a writer explanation.
- First-teardown synth deregistration is fixed. The covered route does not
  reach `shutdownAudioEngine`; callback registration is not proof of shutdown.
- The M5 plan and its execution sequence are in `docs/M5-AUDIO-PLAN.md`.

### M3 and rendering

- M3 idiom audits are closed for the previously enumerated trap/break/syscall/
  cop0, unaligned and LL/SC/cache, division, float/FCSR, memory-width,
  indirect-call, self-walk, branch-likely, variable-shift, HI/LO, 64-bit
  shift, 32-bit multiply, and 64-bit mul/div classes. Do not repeat a class
  without new recompiler or provenance evidence.
- `movz`/`movn` support is complete in N64Recomp and fixup tooling.
- The Factor 5 runaway-DL cause is known: op `0xBD` loads overlay `0x2C`
  (ROM `0x27368`, destination `0x1DB0`) without a route. The splice effect
  remains parked.
- Native hangar artifacts (rim band, holo spikes, stale right edge) remain
  localized. M4 accumulator origin, pillar references, `0x1F0D74`, and odd PI
  DMA remain parked. The retail entry boundary's port join matches the
  retained caller and s0/s1/v0 constraints. Session 5224's full histograms
  make the `s0+0x22` difference quantitative: retail modal `0x00`, port
  modal `0x03`, retail `0x03` count 0. Both retail strides are live in
  one run, on opposite field origins; `0x80090F3C` writes constant 0
  to the live one after the entry read. Do not rename `bcmp_recomp` or
  `bzero_recomp` back to
  the unsuffixed libc names: those globals interpose libSystem and SIGSEGV
  in `RT64::GBIManager`.
- The Session 5147 retail page-writer revisit passed whole-RDRAM, hangar, and
  mission controls and found 1,026,749 writes to `0x1F0000:0x1F1000` with
  lifetime guest-PC attribution, dominated by `0x800078EC`. The oracle's
  hangar/mission phase writer tables remained empty even after a fixed rerun
  with `--phase-origin-watch`; retain this as single-source, phase-unqualified
  evidence and do not close the M4 page-reuse boundary. Audit:
  `docs/M4-S5147-PAGE-WRITER-AUDIT.md`.
- Session 5163 repaired that phase-attribution gap with the qualified cxd4 RSP
  route: whole-RDRAM and exact-PC controls passed, 595 hangar VI frames were
  observed, and 73,370 lifetime writes hit `0x1F0000:0x1F1000`. The
  phase-gated writer table attributed 8,912 hangar-page writes to
  `0x800078EC`, with the `0x800C7F08`…`0x800C801C` family also present. This
  selects retail-page-writer-is-hangar, but does not identify the port-side
  value origin or authorize a mitigation; it is single-source oracle evidence.
  Audit: `docs/M4-S5163-PAGE-WRITER-AUDIT.md`.

### Generated-symbol sweep

Sweep detail archived in `docs/PROJECT-OVERVIEW.md` ("Archived sweep log").
The `vi = 0x800391B0` candidate is typed `OSViContext` data of size `0x60`;
the bounded helper made zero edits, and the generated tree has only a data
fragment `nop` with no callable placeholder, declaration, overlay record, or
direct generated reference. Preserve the data name. Audit:
`docs/RENAME-S5277-AUDIT.md`.

Session 5281 classified `__osViCurr = 0x80039210` as already synchronized.
The bounded helper made zero edits; the companion map types it as
`OSViContext*`, and the generated tree has no callable body, placeholder,
declaration, overlay record, or direct reference at the address. Audit:
`docs/RENAME-S5281-AUDIT.md`. The next sweep candidate is
Session 5282 classified `__osViNext = 0x80039214` as already synchronized.
The bounded helper made zero edits; the companion map types it as
`OSViContext*`, and the generated tree has no callable body, placeholder,
declaration, overlay record, or direct reference at the address. Audit:
`docs/RENAME-S5282-AUDIT.md`. Session 5283 classified
`__osViDevMgr = 0x80039220` as already synchronized. The bounded helper made
zero edits; the companion map types it as `OSDevMgr` data of size `0x1C`, and
the generated tree has only a surrounding `nop` with no callable body,
placeholder, declaration, overlay record, or direct reference at the address.
Audit: `docs/RENAME-S5283-AUDIT.md`. The next sweep candidate is
`osViModeMpalLan1 = 0x80039240`. Session 5284 classified
`osViModeMpalLan1 = 0x80039240` as already synchronized. The bounded helper
made zero edits; the companion map types it as `OSViMode` data of size `0x50`,
and the generated tree has no callable placeholder, declaration, overlay
record, or direct reference at the address. Its apparent instruction lines
are part of the surrounding `__OSGlobalIntMask` data/fragment decode. Audit:
`docs/RENAME-S5284-AUDIT.md`. The next sweep candidate is
`osViModeNtscLan1 = 0x80039290`.
Session 5285 classified `osViModeNtscLan1 = 0x80039290` as already
synchronized. The bounded helper made zero edits; the companion map types it
as `OSViMode` data of size `0x50`, ending at `osViModePalLan1 = 0x800392E0`,
and the generated tree has no callable placeholder, declaration, overlay
record, or direct reference at the address. Its apparent instructions are
part of the surrounding `__OSGlobalIntMask` data/fragment decode. Audit:
`docs/RENAME-S5285-AUDIT.md`. The next sweep candidate is
`osViModePalLan1 = 0x800392E0`.
Session 5286 classified `osViModePalLan1 = 0x800392E0` as already
synchronized. The bounded helper made zero edits; the companion map types it
as `OSViMode` data of size `0x50`, ending at `osViModeTable = 0x80039330`, and
the generated tree has no callable body, placeholder, declaration, overlay
record, or direct reference at the address. Its apparent instructions are
part of the surrounding `__OSGlobalIntMask` data/fragment decode. Audit:
`docs/RENAME-S5286-AUDIT.md`. Session 5287 classified
`osViModeTable = 0x80039330` as already synchronized. The companion map
types it as `OSViMode[42]` data of size `0xD20`, ending at `0x80040050`, and
the generated tree has only a data-region `nop` with no callable body,
placeholder, declaration, overlay record, or direct reference. Audit:
`docs/RENAME-S5287-AUDIT.md`. The next sweep candidate is the first
unclassified companion record after `0x80040050`. Session 5288 classified
`getNpcContextByIndex = 0x8004013C` as already synchronized. The bounded
helper reported `already-synchronized` and renamed zero references in zero
files; the generated tree has the named declaration, call sites, and overlay
record, with no placeholder at the address. Audit:
`docs/RENAME-S5288-AUDIT.md`. Session 5289 classified
`getNpcContextField8 = 0x8004015C` as already synchronized. The bounded
helper reported `already-synchronized` and renamed zero references in zero
files; the generated tree has the named callable body, declaration, call
sites, and overlay record, with no placeholder or conflicting fragment.
Audit: `docs/RENAME-S5289-AUDIT.md`. The next sweep candidate is
`factor5RemoveListNode = 0x80098DE0`. Session 5290 classified
`factor5RemoveListNode = 0x80098DE0` as already synchronized. The bounded
helper reported `already-synchronized` and renamed zero references in zero
files; the companion map documents the named list-unlink callable, and the
generated tree has its named body in `funcs_26.c`, declaration, overlay record,
and callers, with no placeholder or conflicting fragment. Audit:
`docs/RENAME-S5290-AUDIT.md`. The next companion record is
`safeLookup3DSoundEntry = 0x80088D1C`.
Session 5291 classified `safeLookup3DSoundEntry = 0x80088D1C` as already
synchronized. The bounded helper made zero edits; the companion map documents
the named mutex-guarded 3D-sound lookup wrapper, and the generated tree has its
named body in `funcs_22.c`, declaration, overlay record, and callers, with no
placeholder or conflicting fragment. Audit:
`docs/RENAME-S5291-AUDIT.md`. The next companion record is
`initNpcSlotList = 0x8003E560`.
Session 5292 classified `initNpcSlotList = 0x8003E560` as already
synchronized. The bounded helper made zero edits; the companion map documents
the NPC free-list initializer, and the generated tree has its named body in
`funcs_8.c`, declaration, overlay record, and callers, with no placeholder or
conflict. Audit: `docs/RENAME-S5292-AUDIT.md`. The next companion record is
`allocateNpcSlot = 0x8003E5F8`.
Session 5293 classified `allocateNpcSlot = 0x8003E5F8` as already
synchronized. The bounded helper made zero edits; the companion map documents
the NPC free-list allocator, and the generated tree has its named body in
`funcs_8.c`, declaration, overlay record, and callers with no placeholder or
conflict. Audit: `docs/RENAME-S5293-AUDIT.md`. The next companion record is
`unregisterAndFreeNpcSlot = 0x8003E7D0`. Session 5294 classified
`unregisterAndFreeNpcSlot = 0x8003E7D0` as already synchronized. The helper
made zero edits; the generated tree contains the named body, declaration,
overlay record, and direct callers, with no placeholder or conflicting
fragment. Audit: `docs/RENAME-S5294-AUDIT.md`. The next companion record is
`reinsertNpcIntoSortedFreeList = 0x8003EC10`.
Session 5295 classified `reinsertNpcIntoSortedFreeList = 0x8003EC10` as
already synchronized. The bounded helper made zero edits; the generated tree
contains the named body, declaration, overlay record, and direct callers, with
no placeholder or conflicting fragment. Audit:
`docs/RENAME-S5295-AUDIT.md`. The next companion record is
`relinkNpcSlotToNewParentGroup = 0x8003EFDC`.
## Operational rules

- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 command or
  display-list behavior. The retail oracle is independent ground truth and
  requires whole-RDRAM, VI, and phase positive controls before a null matters.
- Batch all counters and A/B arms into one build/run. Phase-gate animated
  comparisons; run-lifetime zeroes are not evidence for later phases.
- A mitigation-shaped change must identify its writer and state whether the
  value is legitimate. A guard is not an explanation.
- Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
  cmake`. Generated behavior edits belong in fixup tooling or patches, not
  directly in generated C. Never reset, clean, checkout, or update a
  submodule; export submodule patches after any `lib/` edit.
- Run the game from `build/`, keep the ROM present, capture output to a file,
  and kill test processes with SIGKILL. Use the soak queue for repeat runs.
- The MIPS GCC toolchain is still absent, so PatchesLib qualification remains
  blocked; do not repeat that command until the toolchain is supplied.

## Parked and closed

- External retail-entry is qualified through title/hangar/mission on the Rice
  route; the old exact PC boundary is not a current target.
- The M4 accumulator boundary is closed at task-end granularity: hangar
  `0x8000` lane counts matched retail (port 0/1955, retail 0/576). A new
  retail cxd4 oracle run sampled mid-task state and found `0x8000` lanes in
  all 286 hangar tasks (all 572 512-wide tasks), while task-end remained zero.
  This is single-source retail evidence, not a port explanation; see
  `docs/REVISIT-S5279-M4-ACCUMULATOR-AUDIT.md`.
- Heap/copy/message-queue/PI-DMA and audited host-wrapper pointer classes are
  closed on the qualified keyed route with positive controls. Re-open only on
  a phase-qualified recurrence.
- The mission input thread is closed: stick state at `0x80130B88` reaches
  flight code; the player vehicle object at `0x80138458` moves normally.
- The s4296 A14 yield patch is present and guarded by
  `tools/check_a14_yield_patch.py`; the prior mission shutdown spin was traced
  to its missing generated patch, not a new audio diagnosis.

## Superseded conclusions worth retaining

- (s5129) "Retail has no mid-task `0x8000` VACC lane" was believable because
  the first decoder treated the signed `i16` dump as a positive `uint16`
  comparison. Re-read of the raw dump in s5279 shows `-32768`/`0x8000` in
  every 512-wide task; task-end remains zero. The old discriminator is
  superseded, and no mitigation is authorized.

- (s5247) "The old-commit bisect is blocked and the loop must stop" (s5246 BLOCKED.md). Believable because cp/ditto were denied headless; overturned because the clone is only needed after the queued HEAD arm fails, and a git worktree avoids cp.

- Earlier claims that M5 was fully closed were too broad: nonzero PCM proves
  route activity, not every audio contract.
- Earlier claims that the loop had no runnable target were overturned when a
  mission-qualified soak became available; use `scratch/agent/NEXT.md` and
  the soak queue rather than declaring a block from a stale backlog.
- The old exact retail-entry and stale-base voice theories are not current
  explanations. Their guarded/atomic/lock variants either remained live or
  were route-blocking; no value rewrite was authorized.
- A fully shared port entry contract, and a port that never enters
  `fillSampleStreamRange` on the mission origins, were both still open after
  the retail-only s5203 dump. Session 5223 refutes both: the port enters on
  `0x00690400` and `0x00620400` through `0x800902CC`. Session 5224 refutes
  the follow-on claim that those capped rows hid a modal `0x03`: every
  mission-origin hit has retail `0x03` = 0 and modal `0x00`. The port modal
  `0x03` is a real field difference. Session 5225 refutes the follow-on
  guess that the first three port `s0` samples were the addresses to watch.
  Its own "retail never enters with `s0=0x80195190`" was that run's census
  only. Session 5226 entered on exactly that stride, with the same modal
  `0x00` and `0x03` count 0. Its empty writer tables described the idle
  field, not the live byte: the watches were `0x80190E50` while the 0400
  census was `0x80195190`. Session 5227 refutes "the mission origins do
  not store offset `0x22`". Both strides are stored, each on the origin
  that names it, by constant 0 at `0x80090F3C`. That store is not the
  port's `0x03`. No guard yet.

`osSetEventMesg = 0x80033560` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has only the ABI declaration, a zero-size overlay record,
and five direct callers of the host wrapper, with no generated body or
placeholder at the companion address. Its nominal span to
`osSetIntMask = 0x80033630` is `0xD0`, with no body to validate. Preserve the
ABI name. Audit: `docs/RENAME-S5184-AUDIT.md`. The next candidate is now
`osSetIntMask = 0x80033630`. `osSetIntMask = 0x80033630` is now classified
as another unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and the generated tree has only the ABI declaration
and a zero-size overlay record, with no generated body or direct caller at
the companion address. Its nominal span to `osSetThreadPri = 0x800336E0` is
`0xB0`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5185-AUDIT.md`. The next candidate is now
`osSetThreadPri = 0x800336E0`.

`osSetThreadPri = 0x800336E0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has only the ABI declaration, a zero-size overlay record,
and two direct callers of the host wrapper, with no generated body or
placeholder at the companion address. Its nominal span to `osSetTimer =
0x800337C0` is `0xE0`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5186-AUDIT.md`. The next candidate is now `osSetTimer =
0x800337C0`.

`osSetTimer = 0x800337C0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. The generated tree has only the ABI
declaration, a zero-size overlay record, and one direct caller of the host
wrapper, with no generated body or placeholder at the companion address. Its
nominal span to `__osSiCreateAccessQueue = 0x800338A0` is `0xE0`, with no body
to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5187-AUDIT.md`. The next candidate is now
`__osSiCreateAccessQueue = 0x800338A0`. It is now classified as another
unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and independent generated-tree searches found no body,
placeholder, overlay record, or direct caller at the companion address. Its
companion span to `__osSiGetAccess = 0x800338F0` is `0x50`, with no body to
validate. Preserve the ABI name. Audit: `docs/RENAME-S5188-AUDIT.md`.
`__osSiGetAccess = 0x800338F0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal span to `__osSiRelAccess = 0x80033934` is
`0x44`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5189-AUDIT.md`. The next candidate is now
`__osSiRelAccess = 0x80033934`. `__osSiRelAccess = 0x80033934` is now
classified as another unmaterialized libultra/ABI entry: the bounded helper
reported `already-synchronized`, and independent generated-tree searches found
no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal companion span to `__osSiRawStartDma =
0x80033B20` is `0x1EC`, with no body to validate. Preserve the ABI name.
The helper also surfaced `sinf = 0x80033960` as already synchronized; that is
a separate libultra symbol. Audit: `docs/RENAME-S5190-AUDIT.md`. The next
candidate is now `__osSiRawStartDma = 0x80033B20`.

`__osSiRawStartDma = 0x80033B20` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal span to `__osSiDeviceBusy = 0x80033BD0` is
`0xAC`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5191-AUDIT.md`. The next candidate is now
`__osSiDeviceBusy = 0x80033BD0`.

`__osSiDeviceBusy = 0x80033BD0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree search found no body, placeholder, overlay record, or
direct generated caller at the companion address. Its nominal span to
`__osSiRawReadIo = 0x80033C00` is `0x30`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5192-AUDIT.md`. The next candidate is now
`__osSiRawReadIo = 0x80033C00`.

`__osSiRawReadIo = 0x80033C00` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal span to `__osSiRawWriteIo = 0x80033C50` is
`0x50`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5193-AUDIT.md`. The next candidate is now
`__osSiRawWriteIo = 0x80033C50`.

`__osSiRawWriteIo = 0x80033C50` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal span to `proutSprintf = 0x80033CA0` is `0x50`,
with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5194-AUDIT.md`. The next candidate is now
`proutSprintf = 0x80033CA0`. `proutSprintf = 0x80033CA0` is now classified as
already correctly named: its generated body and exact `0x24` overlay span
end at `0x80033CC4`, matching the companion `sprintf` entry, but the
generated tree has no independent caller. Preserve the ABI name. Audit:
`docs/RENAME-S5195-AUDIT.md`. The next candidate is now
`sprintf = 0x80033CC4` is now classified as already correctly named: the
companion symbol map, generated `sprintf_recomp` body, exact `0x5C` overlay
span, and many independent generated callers all agree. Preserve the ABI name.
Audit: `docs/RENAME-S5196-AUDIT.md`. The next candidate is now
`_VirtualToPhysicalTask = 0x80033D20`. `_VirtualToPhysicalTask` is now
classified as already correctly named: its generated body spans exactly
`0x11C` bytes from `0x80033D20` to `0x80033E3C`, matching the companion
symbol-map and overlay record, but the generated tree has no independent
caller. Preserve the ABI-semantic name. Audit:
`docs/RENAME-S5197-AUDIT.md`. The next candidate is now
`osSpTaskLoad = 0x80033E3C`. `osSpTaskLoad` is now classified as another
unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`; the generated tree has no body or placeholder at the
companion address, while the overlay record is zero-size and five generated
calls target the existing host wrapper. Its nominal span to
`osSpTaskStartGo = 0x80033FCC` is `0x190`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5198-AUDIT.md`. The next candidate is now
`osSpTaskStartGo = 0x80033FCC`.

`strchr = 0x80034744` is now classified as already correctly named: the
bounded helper reported `already-synchronized`; its generated body spans
exactly `0x4C` bytes to `0x80034790`, matching the overlay record, and six
independent generated callers agree. Preserve the ABI-semantic name. Audit:
`docs/RENAME-S5210-AUDIT.md`. `__osDequeueThread = 0x80034790` is now
classified as an unmaterialized libultra/ABI entry: the bounded helper
reported `already-synchronized`, and independent generated-tree searches
found no body, placeholder, overlay record, or direct caller at the companion
address. Its companion span ends at `__osTimerServicesInit = 0x800347D0`;
preserve the ABI name. Audit: `docs/RENAME-S5211-AUDIT.md`.
`__osTimerServicesInit = 0x800347D0` is now classified as another
unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and independent generated-tree searches found no body,
placeholder, overlay record, or direct caller at the companion address. Its
nominal span to `__osTimerInterrupt = 0x8003485C` is `0x8C`, with no body to
validate. Preserve the ABI name. Audit: `docs/RENAME-S5212-AUDIT.md`. The
next candidate is now `__osTimerInterrupt = 0x8003485C`.

`__osTimerInterrupt = 0x8003485C` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
independent generated-tree searches found no body, placeholder, overlay
record, or direct caller at the companion address. Its nominal span to
`__osSetTimerIntr = 0x800349D4` is `0x178`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5213-AUDIT.md`. The next candidate is now
`__osSetTimerIntr = 0x800349D4`.

`__osSetTimerIntr = 0x800349D4` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
independent generated-tree searches found no body, placeholder, overlay
record, or direct caller at the companion address. Its nominal span to
`__osInsertTimer = 0x80034A48` is `0x178`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5214-AUDIT.md`. `__osInsertTimer =
0x80034A48` is now classified as another unmaterialized libultra/ABI entry:
the bounded helper reported `already-synchronized`, and independent
generated-tree searches found no body, placeholder, overlay record, or direct
caller at the companion address. Its nominal span to `__osSetCompare =
0x80034BD0` is `0x188`, with no body to validate. Preserve the ABI name.
Audit: `docs/RENAME-S5215-AUDIT.md`. The next candidate is now
`__osSetCompare = 0x80034BD0`. `__osSetCompare = 0x80034BD0` is now
classified as another unmaterialized libultra/ABI entry: the bounded helper
reported `already-synchronized`, and independent generated-tree searches found
no body, placeholder, overlay record, or direct caller at the companion
address. Its nominal span to `osViBlack = 0x80034BE0` is `0x10`, with no body
to validate. Preserve the ABI name. Audit: `docs/RENAME-S5216-AUDIT.md`. The
next candidate is now `osViBlack = 0x80034BE0`.

`osViBlack = 0x80034BE0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. The generated tree has only the ABI
declaration, two generated callers, and a zero-size overlay record, with no
body or placeholder at the companion address. Preserve the ABI name. Audit:
`docs/RENAME-S5217-AUDIT.md`. The next sweep candidate is the next named
entry after `osViBlack` in the companion symbol map. `osViGetCurrentField =
0x80034D90` is now classified as another unmaterialized libultra/ABI entry:
the bounded helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree has one call site but no body,
placeholder, header declaration, or overlay record at the companion address.
Its nominal span to `osCreateViManager = 0x80034DB0` is `0x20`, with no body to
validate. Preserve the ABI name. Audit: `docs/RENAME-S5218-AUDIT.md`.
The next sweep candidate is now `osCreateViManager = 0x80034DB0`.
`osCreateViManager = 0x80034DB0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. The generated tree has only the ABI
declaration, one generated caller, and a zero-size overlay record, with no
body or placeholder at the companion address. Its nominal span to
`osVirtualToPhysical = 0x80035120` is `0x170`, with no body to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5219-AUDIT.md`. The next sweep
candidate is now `osVirtualToPhysical = 0x80035120`. `osVirtualToPhysical`
is now classified as another unmaterialized libultra/ABI entry: the bounded
helper reported `already-synchronized` for it and the next in-range
`__osProbeTLB`, while renaming zero references in zero files. The generated
tree has the ABI declaration, seven generated callers, and a zero-size overlay
record, but no body or placeholder at the companion address. The primary
companion map places `osViSetEvent` at `0x80035260` (nominal span `0x140`),
but `__osProbeTLB = 0x800351A0` is the next bounded candidate. Preserve the
ABI name. Audit: `docs/RENAME-S5220-AUDIT.md`.

`__osProbeTLB = 0x800351A0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, header declaration, overlay record, or direct
generated caller at the companion address. Its nominal span to
`__osViSwapContext = 0x80035550` is `0x3B0`, with no body to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5221-AUDIT.md`.

`__osViSwapContext = 0x80035550` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, header declaration, overlay record, or direct
generated caller at the companion address. Its nominal span to `_Putfld =
0x80035960` is `0x410`, with no body to validate. Preserve the ABI name.
Audit: `docs/RENAME-S5222-AUDIT.md`.

`__OSGlobalIntMask = 0x80039110` is now classified as a data/fragment record:
the bounded helper reported `already-synchronized` and renamed zero
references. The companion map marks it as volatile data; the generated
function/overlay entry begins with invalid data at the address and spans
`0x4E10`, so it is not a callable placeholder. Preserve the name. Audit:
`docs/RENAME-S5270-AUDIT.md`.

`__osPiDevMgr = 0x80039130` is now classified as already synchronized: the
bounded helper made zero edits, and the generated tree contains only a `nop`
inside the preceding data/fragment decode, with no distinct callable body,
placeholder, declaration, overlay record, or direct generated caller at the
address. Preserve the existing data name. Audit: `docs/RENAME-S5272-AUDIT.md`.

`__osPiTable = 0x8003914C` is now classified as already synchronized: the
bounded helper made zero edits, and the companion is typed `OSPiHandle_s*`
data of size `0x4`. The generated tree contains only a `nop` immediately
before the next fragment, with no distinct callable body, placeholder,
declaration, overlay record, or direct generated caller at the address.
Preserve the existing data name. Audit: `docs/RENAME-S5273-AUDIT.md`.

`__osCurrentHandle = 0x80039150` is now classified as already synchronized:
the bounded helper made zero edits, and the companion is typed `OSPiHandle*`
data of size `0x8`. The generated tree contains no distinct callable body,
placeholder, declaration, overlay record, or direct generated caller at the
address; its apparent `lb`/`nop` entries are part of the surrounding
data/fragment decode. Preserve the existing data name. Audit:
`docs/RENAME-S5274-AUDIT.md`.

`__osSiAccessQueueEnabled = 0x80039170` is now classified as typed data: the
bounded helper made zero edits, and the companion declares `type:u32`. The
generated tree contains only a `nop` in the surrounding data/fragment decode,
with no callable body, placeholder, declaration, overlay record, or direct
generated reference. Preserve the data name. Audit:
`docs/RENAME-S5276-AUDIT.md`.

## Next steps (single monotonic backlog)

- **s5296:** The retail mid-task `0x8000` state is sampled across multiple RSP
  PCs, while the independent end-task stream remains zero. The RSM1 sequence
  cannot join samples to tasks, so the M4 publication/order boundary remains
  open. Add an explicit task serial to the cxd4 mid-task record and rerun the
  same qualified route, or obtain an equivalent task-keyed join. Do not add a
  mitigation or resume the generated-symbol sweep until this revisit is done.

- **s5293:** `allocateNpcSlot = 0x8003E5F8` is a named, already-synchronized
  callable NPC free-list allocator; the helper made zero edits and independent
  generated-tree inspection found its body in `funcs_8.c`, declaration, overlay
  record, and callers with no placeholder or conflict. No build or soak was
  warranted. Audit: `docs/RENAME-S5293-AUDIT.md`. The next bounded sweep unit
  is `unregisterAndFreeNpcSlot = 0x8003E7D0`, using the same helper plus
  independent companion/generated-tree inspection.

- **s5292:** `initNpcSlotList = 0x8003E560` is a named, already-synchronized
  callable NPC free-list initializer; the helper made zero edits and independent
  generated-tree inspection found its body in `funcs_8.c`, declaration, overlay
  record, and callers with no placeholder or conflict. No build or soak was
  warranted. Audit: `docs/RENAME-S5292-AUDIT.md`. The next bounded sweep unit is
  `allocateNpcSlot = 0x8003E5F8`, using the same helper plus independent
  companion/generated-tree inspection.

- **s5291:** `safeLookup3DSoundEntry = 0x80088D1C` is a named, already-synchronized
  callable 3D-sound lookup wrapper; the helper made zero edits and independent
  generated-tree inspection found its body, declaration, overlay record, and
  callers with no placeholder or conflict. No build or soak was warranted.
  Audit: `docs/RENAME-S5291-AUDIT.md`. The next bounded sweep unit is
  `initNpcSlotList = 0x8003E560`, using the same helper plus independent
  companion/generated-tree inspection.

- **s5290:** `factor5RemoveListNode = 0x80098DE0` is a named, already-synchronized
  callable list-unlink function; the helper made zero edits and independent
  generated-tree inspection found its body, declaration, overlay record, and
  callers with no placeholder or conflict. No build or soak was warranted.
  Audit: `docs/RENAME-S5290-AUDIT.md`. The next bounded sweep unit is
  `safeLookup3DSoundEntry = 0x80088D1C`, using the same helper plus independent
  companion/generated-tree inspection.

- **s5289:** `getNpcContextField8 = 0x8004015C` is a named, already-synchronized
  callable NPC-slot accessor; the helper made zero edits and the generated
  tree contains its body, declaration, call sites, and overlay record. The
  next bounded sweep unit is `factor5RemoveListNode = 0x80098DE0`, using the
  same helper plus independent companion/generated-tree inspection. Audit:
  `docs/RENAME-S5289-AUDIT.md`.

- **s5285:** `osViModeNtscLan1 = 0x80039290` is typed `OSViMode` data of size
  `0x50` and already synchronized; the generated address is only part of an
  enclosing data/fragment decode. The next bounded sweep unit is
  `osViModePalLan1 = 0x800392E0`, using the same helper plus independent
  companion/generated-tree inspection. Audit: `docs/RENAME-S5285-AUDIT.md`.

- **s5284:** `osViModeMpalLan1 = 0x80039240` is typed `OSViMode` data of size
  `0x50` and already synchronized; the generated address is only part of an
  enclosing data/fragment decode. The next bounded sweep unit is
  `osViModeNtscLan1 = 0x80039290`, using the same helper plus independent
  companion/generated-tree inspection. Audit: `docs/RENAME-S5284-AUDIT.md`.

- **s5283:** `__osViDevMgr = 0x80039220` is typed `OSDevMgr` data of size
  `0x1C` and already synchronized; no generated callable placeholder or
  reference exists. The next bounded sweep unit is
  `osViModeMpalLan1 = 0x80039240`, using the same helper plus independent
  companion/generated-tree inspection. Audit: `docs/RENAME-S5283-AUDIT.md`.

- **s5282:** `__osViNext = 0x80039214` is typed `OSViContext*` data and already
  synchronized; no generated callable placeholder or reference exists. The
  next bounded sweep unit is the following companion record after
  `__osViNext`, using the same helper plus independent companion/generated-tree
  inspection. Audit: `docs/RENAME-S5282-AUDIT.md`.

- **s5281:** `__osViCurr = 0x80039210` is typed `OSViContext*` data and already
  synchronized; no generated callable placeholder or reference exists. Audit:
  `docs/RENAME-S5281-AUDIT.md`.

- **s5280:** The port capture reached the qualified hangar phase and found
  transient `0x8000` VACC components in bounded mid-task rows, with none at
  task end. Because the cap concentrated on one task, the next unit is a
  bounded per-task summary probe in the same hangar phase: count each task's
  mid-task `0x8000` presence and first/last stage, retain task-end state, and
  keep the phase positive control in the same run. Do not infer prevalence
  from the current 18/2,000 row count.

- **s5278:** The external retail-entry revisit found matching caller and
  bounded argument shape on both mission origins, with positive controls on
  both arms, but did not prove the dynamic `a1` or return contract. The
  sweep-scoped 15-session rule therefore requires the next unit to revisit
  the parked M4 accumulator boundary with a genuinely new angle, not resume
  generated-symbol classification.

- **s5277:** `vi = 0x800391B0` is typed `OSViContext` data of size `0x60` and
  already synchronized: the bounded helper made zero edits, and independent
  checks find only a data-fragment nop with no callable placeholder, header
  declaration, overlay record, or direct generated reference. Preserve the
  name; no build or soak. Audit: `docs/RENAME-S5277-AUDIT.md`. Because the
  recent 15-session census is sweep-scoped, the next unit is a new-angle
  external retail-entry boundary revisit, not another sweep candidate.

- **s5276:** `__osSiAccessQueueEnabled = 0x80039170` is typed `u32` data and
  already synchronized: the bounded helper made zero edits, and independent
  checks find only a nop/data fragment with no callable placeholder. Preserve
  the name; no build or soak. Audit: `docs/RENAME-S5276-AUDIT.md`. Next:
  classify `vi = 0x800391B0`.

- **s5274:** `__osCurrentHandle = 0x80039150` is already synchronized: the
  bounded helper made zero edits, and independent checks find typed pointer
  data with no callable placeholder. Preserve the name; no build or soak.
  Audit: `docs/RENAME-S5274-AUDIT.md`. Next: classify
  `__osSiAccessQueueEnabled = 0x80039170`.

- **s5275:** `__osPiAccessQueueEnabled = 0x80039160` is already synchronized:
  the bounded helper made zero edits, and independent checks find companion
  `type:u32` data plus only a nop/data fragment in the generated tree, with no
  callable body, header declaration, overlay record, or direct generated
  reference. Preserve the name; no build or soak. Next: classify
  `__osSiAccessQueueEnabled = 0x80039170`.

- **s5273:** `__osPiTable = 0x8003914C` is already synchronized: the bounded
  helper made zero edits, and independent checks find typed pointer data with
  no callable placeholder. Preserve the name; no build or soak. Audit:
  `docs/RENAME-S5273-AUDIT.md`. Next: classify
  `__osCurrentHandle = 0x80039150`.

- **s5272:** `__osPiDevMgr = 0x80039130` is already synchronized: the bounded
  helper made zero edits, and independent checks find only a `nop` in the
  preceding data/fragment decode, not a callable placeholder. Preserve the
  name; no build or soak. Audit: `docs/RENAME-S5272-AUDIT.md`. Next: classify
  `__osPiTable = 0x8003914C`.

- **s5271:** `__osMotorinitialized = 0x80039120` is already synchronized: the
  bounded helper made zero edits, and independent checks identify the companion
  as typed `u32` data of size `0x10` with no distinct generated callable body,
  placeholder, declaration, overlay record, or direct caller. Preserve the
  name; no build or soak. Audit: `docs/RENAME-S5271-AUDIT.md`. Next: classify
  `__osPiDevMgr = 0x80039130`.

- **s5270:** `__OSGlobalIntMask = 0x80039110` is already synchronized: the
  bounded helper made zero edits, and independent checks identify the
  companion as volatile data whose generated entry is data decoded as code.
  Preserve the name; no build or soak. Audit:
  `docs/RENAME-S5270-AUDIT.md`. Next: classify
  `__osMotorinitialized = 0x80039120`.
- **s5269:** `__osShutdown = 0x8003910C` is already synchronized: the bounded
  helper made zero edits, and independent checks identify it as a typed `u32`
  data symbol with no generated callable body, placeholder, declaration,
  overlay record, or direct generated caller. Preserve the name; no build or
  soak. Audit: `docs/RENAME-S5269-AUDIT.md`. Next: classify the companion data
  record `__OSGlobalIntMask = 0x80039110`.
- **s5268:** `__osHwIntTable = 0x800390E0` is already synchronized: the
  bounded helper made zero edits, and independent checks identify it as a
  typed `u32` data symbol of size `0x14` with no generated callable body,
  placeholder, declaration, overlay record, or direct generated caller.
  Preserve the name; no build or soak. Audit:
  `docs/RENAME-S5268-AUDIT.md`. Next: inspect the next companion candidate
  after `0x80039100`.
- **s5267:** `__osContinitialized = 0x800390D0` is already synchronized: the
  bounded helper made zero edits, and independent checks identify it as a
  typed `u32` data symbol with no generated body, placeholder, declaration,
  overlay record, or direct generated caller. Preserve the name; no build or
  soak. Audit: `docs/RENAME-S5267-AUDIT.md`. Next: classify
  `__osHwIntTable = 0x800390E0`.
- **s5266:** The bounded helper rechecked `_Putfld = 0x80035960` over
  `0x80035960..0x80035FD0`; it made zero edits and reported
  `already-synchronized`. Independent inspection found the named companion,
  full 0x670-byte generated body, header declaration, overlay record, and
  generated caller. This duplicates s5259 because the prior next-step pointer
  was stale; preserve the name. Audit: `docs/RENAME-S5266-AUDIT.md`. Next:
  classify companion data symbol `__osContinitialized = 0x800390D0`.
- **s5265:** `osWritebackDCacheAll = 0x80035930` is already synchronized: the bounded helper made zero edits, and independent checks show the defined companion symbol, ABI declaration, zero-size generated overlay record, and two direct callers, but no generated callable body or placeholder. Preserve the ABI name; no build or soak. Audit `docs/RENAME-S5265-AUDIT.md`. Next sweep candidate: `_Putfld = 0x80035960`.
- **s5264:** `osYieldThread = 0x80037510` is already synchronized: the bounded helper made zero edits, and independent checks show the defined libultra symbol, no generated placeholder/body/overlay record, 20 direct ABI callers, and the companion `INCLUDE_ASM` boundary. Preserve the ABI name; no build or soak. Audit `docs/RENAME-S5264-AUDIT.md`. Next sweep candidate: `osWritebackDCacheAll = 0x80035930`.
- **s5263:** `_Litob = 0x80037270` is already synchronized: the bounded helper made zero edits, and independent companion/generated-tree checks show the defined symbol, exact named body, declaration, overlay record, and three direct callers. No build or soak. Next sweep candidate: `osYieldThread = 0x80037510` (audit `docs/RENAME-S5263-AUDIT.md`).
- **s5262:** `_Ldtob = 0x80036B90` is already synchronized: the bounded helper made zero edits, and the companion/generated trees independently show the defined symbol, exact named body, declaration, overlay record, and direct caller. Adjacent `lldiv` and `ldiv` entries were also already synchronized. No build or soak. Next sweep candidate: `_Litob = 0x80037270` (audit `docs/RENAME-S5262-AUDIT.md`).
- **s5261:** `_Genld = 0x80036620` is already synchronized: the bounded helper made zero edits, and the companion/generated trees independently show the defined symbol, exact named body, declaration, overlay record, and direct caller. The adjacent `0x80036B88` pure return stub is separately named `noopHandler_80036B88`. No build or soak. Next sweep candidate: `_Ldtob = 0x80036B90` (audit `docs/RENAME-S5261-AUDIT.md`).
- **s5260:** `_Printf = 0x80035FD0` is already synchronized: the bounded helper made zero edits, and the companion/generated trees independently show the defined symbol, exact named body, declaration, overlay record, and direct caller. No build or soak. Audit `docs/RENAME-S5260-AUDIT.md`.
- **OPEN DEPENDENCY (unblock s5250):** the hangar-route baseline needs host load1 < 2 (the queued recipe self-skipped at 5.20; not ours to kill). The host-load discriminator therefore remains unevaluated. Do not retry until the load gate is met.
- **s5258:** librecomp/ultramodern RDRAM-index class audited (~60 sites): rsp.cpp all masked, pi DMA guarded, flash dead, `__osRdbSend` size guard added (lib patch exported). Static, single-source. Next: s5250 baseline soak when host load1<2, else M5 step or retail-entry revisit.
- **s5257:** rt64 guest-sized host-buffer audit is exhausted: rdp/tmem/texture/f3dfactor5 (s5255), hle/gbi memcpy (s5256), RSP matrix/viewport/mode/matrix-id stack push/pop (s5257, all bounded; assert-only paths still index in range). All static, single-source; no overturned conclusions. Next: s5250 baseline soak when host load1<2, else an M3 idiom-class audit outside rt64 (librecomp/ultramodern shim RDRAM pointer arithmetic).
- **s5250 status:** src cleared: s5235 save-guard and task_ptr guard both 0 fires; noguard arm 0/3 hangar (load 10-12). Remaining H-host-load vs H-lib-patch; discriminator = baseline recipe at host load<2, else lib-patch bisect.
- **s5249 status:** HEAD arm ran: 0/3 hangar, 0 crash (load avg 5-9). Old-src arm queued (soak_queue/s5249_old70a56647_arm.sh); tools/bisect_worktree.sh now symlinks scratch/N64Recomp + build/factor5_ucode so the worktree builds.
- **s5248 status:** HEAD arm (soak_queue/s5246_head_arm_loadlog.sh) still not run. Old-commit arm is now one command: `tools/bisect_worktree.sh 70a56647 build` (worktree works headless; build step untested; arm = old src + CURRENT lib). Only behaviour-changing deltas since 70a56647: main.cpp task_ptr range early-return and the s5235 save-guard (lib); rest is diagnostics/ TO_PTR mask (refuted s5242).
- **s5247 status:** the s5246 clone block was premature (the clone is only needed if the HEAD arm fails, and that arm has not run). First fold soak_queue/s5246_head_arm_loadlog (pass => host load/time-of-day; fail => old-commit arm via `git worktree add scratch/wt_70a56647 70a56647` with lib/ symlinked, untested; cp/ditto stay permission-denied headless). Archived: scratch/agent/BLOCKED.resolved.s5246-bisect-clone.md. No new measurement.
0g. (s5243) s5242 A/B: BOTH mask arms failed nohangar (CRASH=0), so the TO_PTR mask is not the cause (two arms agree; load avg ~6.7 so flake not excluded). Recipe delta vs passing s5099 = five ROGUESQ_LOG_*GUARD* env flags. Queued soak_queue/s5243_envflag_ab.sh (A = s5099 env control, B = A + guard flags). Read its SOAK-RESULTS line first; outcome map in scratch/agent/NEXT.md.
0g. (s5244) s5243 env-flag A/B: control arm A (exact s5099 env) FAILED nohangar, so the log flags are refuted and the s5240 mask is un-implicated (both s5242 arms failed). The route stall is host load/time-of-day or an un-marked lib patch (s5235/36/39). Divergence marker (single-source): slot pool 'first 0 populated' vs s5099's 4 at t=6.6s, then stuck at origin 0x6DD280. Decisive control if the HEAD arm fails: build 70a56647 end-to-end (clone or worktree, see NEXT.md). Until then the 0d mask and the s5229-s5240 guards are UNVALIDATED against the hangar route.
0f. (s5242) s5240 mask soak FAILED the route (nohangar t=205, no CRASH). A/B arms queued: soak_queue/s5242_maskon.sh vs s5242_maskoff.sh (binaries build/RS64_maskon / RS64_maskoff). Read both SOAK-RESULTS lines first: on-fail+off-pass => revert TO_PTR mask (H-mask); both pass => flake; both fail => bisect s5229-s5240 / host load. Until resolved the 0d mask is UNVALIDATED.
0e. (s5241) Queued soak scratch/agent/soak_queue/s5240_to_ptr_mask_regress.sh to check the 0d mask for regression (clean = crash=0, mission_onset ~174s). Read its SOAK-RESULTS.md line first next iteration; if clean, resume M5 audio plan. No conclusion overturned this session.

0e. (s5239) lib/ non-rsp.cpp raw rdram[] index class CLOSED (1 unsafe site: rt64_gbi_f3dfactor5.cpp:1023 texture dump could read 31 B past 8 MB, now masked; sp.cpp/pi.cpp/heap.cpp/f3dfactor5:194 proved safe; static-only, single-source). No overturned conclusions. Next: census of unchecked `TO_PTR` (ultra64.h:42) users in ultramodern/librecomp, else resume sweep at `_Putfld`.
0d. (s5238) src/main memcpy/memset/rdram+base class CLOSED (47 hits classified; all masked/constant-gated/checked; no guard needed; static-only, single-source). Next: another idiom class (e.g. lib/ rt64 host buffer sizes) or resume sweep.
0c. (s5237) src/main upstream_compat.cpp raw rdram[] index class CLOSED (3 diagnostic sites masked to 0x7FFFFF; static-only, single-source). Next: resume M5 plan or another idiom class.
0d. (s5240) TO_PTR (ultra64.h:42) index masked to 0x7FFFFF: 73-site class bounded at the macro (build-only, single-source; census partly inferred). Next: mission soak to confirm no regression; else M5/rename.
0b. (s5236) rsp.cpp raw rdram[] index-mask class CLOSED (8 diagnostic sites clamped to 0x7FFFFF; static-only, single-source). Signed-vs-unsigned base class was already closed s5094-s5100. Prior: s5235 PI/EEPROM guest length/offset class closed. Next: raw rdram[]/memcpy index audit in src/main debug threads, or resume M5 plan.
0a. (s5234) Host-wrapper guest-pointer-arg class CLOSED (osDpGetCounters + rs64_m5_port_task_load guarded; rest constant-gated/already checked). Next: another class or resume sweep.
0. (s5233) rdram byte/halfword swizzle class CLOSED and lint-enforced (`tools/lint_rdram_reads.sh`, clean; 2 rsp.cpp s4221 probe lambdas fixed). Next M3 class: pick another by grep, or resume sweep.
1. (s5232) Swizzle-fix ledger re-check CLOSED: no CURRENT-TRUTH/M5-plan claim cites the 45 fixed probe readers
   (grep, single-source). M5 plan steps 0-11 are qualified; next is an M3 idiom-class audit or the paused sweep.
1b. The retail-entry thread is closed (s5229: census byte-swizzle bug).
   Re-open the "external retail-entry boundary" only with a new angle
   not built on the s5223-s5228 byte census. Otherwise resume M5 audio
   de-stubbing per `docs/M5-AUDIO-PLAN.md`. The sweep stays paused at
   `_Genld = 0x80036620`. Plan: `scratch/agent/NEXT.md`.
2. If a new M5 step is selected, write its design and validation row in
   `docs/M5-AUDIO-PLAN.md` before changing runtime behavior.
3. When MIPS GCC is supplied, configure and qualify `PatchesLib`; record
   generation, compile, and link outcomes in the ledger.

## Evidence index

Use `PORTING-STATE.md` for session detail, `docs/PROJECT-OVERVIEW.md` for
archived durable history, `docs/M5-AUDIO-PLAN.md` for the audio sequence, and
the per-session audit/soak paths named above. The next iteration must read
this file, `scratch/agent/NEXT.md`, and the tail of
`scratch/agent/SOAK-RESULTS.md` before acting.

## s5229 resolution (SUPERSEDES the s5223-s5228 "port entry byte 0x03" thread)

The port's "modal 0x03 entry byte" was a CENSUS BUG, not a port divergence.
The `rs64_s5223_entry_join` read used `rdram[phys]` without the `^3`
byte swizzle that `MEM_B` applies, so it sampled guest byte +0x21 (the
field `sb` at 0x80090780 writes, legitimately 3), not +0x22. It was
believable because every earlier check (stride, coverage, store census)
used guest addresses correctly and only the one raw read was wrong; the
retail oracle reads physical bytes properly, so the two sides were never
reading the same byte. With the read fixed (s5229 run, byte-granular
last-writer shadow `rs64_s5229_*` in main.cpp): origin 0x00690400 entry
byte is 00 x76339, 01 x289 of 76649 (matches retail 00/01); last patched
writer is `0x80090F3C` (match 76317) or `0x80090F8C` (match 288). Residue
about 0.04%: pc=0 rows (record never written by a patched store) and a
handful of mismatches (unhooked SD/swl/swr/host write); not pursued.
No port divergence at the mission entry boundary; nothing to guard.
Lesson: any raw `rdram[...]` byte read in a census must apply `^3`.

## s5230 note (raw rdram[] reads)
19 hand-composed word reads in main.cpp/upstream_compat.cpp were byte-reversed (no `^3`); fixed via
`src/main/rs64_rdram_peek.h` (use it for ALL host probe reads). Logged words from the probes named in
PORTING-STATE s5230 predating this are suspect (single-source) until re-read. Remaining single-byte
`rdram[x]` reads: s5231 classified all; 26 more unswizzled byte reads fixed (hashes/dumps over byte-permuted data were wrong).
- **s5253 (unblock):** s5252 block re-scoped (route 3). NEXT = offline rt64 guest-sized-host-buffer audit; host-load dependency for the s5250 baseline remains open.

- s5254: rt64 guest-sized host-buffer leads 1,3,6 guarded (light index, VI screenFb bytes, SHADOW2 size); 2/4 are PROT_NONE faults, 5 dead. Uncovered: tmem, texture upload, f3dfactor5 vertex/matrix. Baseline soak s5250 still load-gated.
- **s5255:** rt64 TMEM row-skip `+=` overflow (rt64_rdp.cpp:797) fixed to `=`; tmem/texture/f3dfactor5 audit closed (static, single-source; no run, host load 7+).
