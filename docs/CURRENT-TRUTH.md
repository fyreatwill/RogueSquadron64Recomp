# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5207 (2026-10-17). The
chronological ledger is `PORTING-STATE.md`; durable background belongs in
`docs/PROJECT-OVERVIEW.md`; per-topic evidence is in the `docs/M5-S*.md` and
`docs/RENAME-S*.md` audit files.

## Headline

The validated route boots through attribution, N64 logo, intro, Factor 5 logo,
title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
origins (`0x00690400` and later `0x00620400`, VI 512). Audio is active on the
qualified image route; the silent `ROGUESQ_AUDIO_UCODE=0` path is only a
control. Mission input reaches the game and changes the player vehicle state.

The current bounded work is the generated-symbol renaming sweep. The last
candidates, `cosf = 0x8002B190`, `osCreateMesgQueue = 0x8002B300`, and
`osCreateThread = 0x8002B330`, were already synchronized: `cosf` has its
generated body, exact `0x170` span, and 75 callers; the two libultra entries
are zero-size host-wrapper/ABI entries with 28 and 10 generated call sites.
`osDestroyThread = 0x8002B480` is also a zero-size host-wrapper/ABI entry with
one generated caller and no body to rename. `osDpGetCounters = 0x8002B590`
and `osDpSetStatus = 0x8002B5E0` are likewise host-wrapper/ABI entries: their
generated trees have no bodies or overlay records, with two ABI call sites
each. The preamble at `0x8002B5F0` is the same ABI-boundary case with no
generated caller. `__osException = 0x8002B600` is the same ABI-boundary case:
it has no generated body, overlay record, or direct generated caller. The
intervening
`__osRestoreInt = 0x8002C260` is likewise an ABI-boundary entry with an
overlay record of `rom_size = 0` and only one generated caller, with no body
to rename. `osMotorStart = 0x8002D570` was also classified as an
unmaterialized libultra/ABI entry: its generated tree has only the ABI
declaration, one caller, and a zero-size overlay record. The next candidate is
`_MakeMotorData = 0x8002D710`. That candidate is now classified as another
unmaterialized ABI entry: its helper audit made zero edits, and the generated
tree has no body, placeholder, overlay record, or direct caller. Its companion
span ends at `osMotorInit = 0x8002D88C`; preserve the ABI name. Audit:
`docs/RENAME-S5143-AUDIT.md`. `osMotorInit = 0x8002D88C` is also an
unmaterialized libultra/ABI entry: the helper reported `already-synchronized`,
and its generated tree has only the ABI declaration, four direct callers, and
a zero-size overlay record, with no body at the companion address. The next
candidate is now classified: `osPfsAllocateFile = 0x8002EBE0` is another
unmaterialized libultra/ABI entry. Its bounded helper reported
`already-synchronized`; the generated tree has only the ABI declaration, one
direct generated caller, and a zero-size overlay record, with no body at the
companion address. Its companion span to `__osPfsDeclarePage = 0x8002F064` is
`0x484`, but there is no generated body to rename. Preserve the ABI name.
Audit: `docs/RENAME-S5145-AUDIT.md`.
`__osPfsDeclarePage = 0x8002F064` is now classified as already correctly
named: its generated body and exact `0x264` overlay span are present, but the
generated tree has no independent caller. Preserve the ABI name. Audit:
`docs/RENAME-S5146-AUDIT.md`.
`__osClearPage = 0x8002F2C8` is likewise already correctly named: its
generated body and exact `0xC8` overlay span are present, with two generated
callers. The helper made no edits. Preserve the ABI name. Audit:
`docs/RENAME-S5148-AUDIT.md`.
`__osSumcalc = 0x8002F390` is also already correctly named: its generated body
ends at `0x8002F3E8`, exactly matching the `0x5C` span to `__osIdCheckSum` and
the overlay record; it has an independent caller at `0x800306B4`. The helper
made no edits. Audit: `docs/RENAME-S5149-AUDIT.md`.
`__osIdCheckSum = 0x8002F3EC` is likewise already correctly named: its
generated body ends at `0x8002F450`, exactly matching the `0x68` span to
`__osRepairPackId` and the overlay record. The generated tree has no
independent caller beyond the definition, so preserve the existing ABI name.
Audit: `docs/RENAME-S5150-AUDIT.md`.
`__osRepairPackId = 0x8002F454` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree search found no body or placeholder at the companion
address. Its companion span ends at `__osCheckPackId = 0x8002F86C`; preserve
the ABI name. Audit: `docs/RENAME-S5151-AUDIT.md`.
`__osCheckPackId = 0x8002F86C` is likewise an unmaterialized libultra/ABI
entry: the bounded helper reported `already-synchronized`, and the generated
tree has no body, placeholder, overlay record, or independent caller at the
companion address. Its companion span ends at `__osGetId = 0x8002FA04`;
preserve the ABI name. Audit: `docs/RENAME-S5152-AUDIT.md`.
`__osGetId = 0x8002FA04` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree search found no body, placeholder, overlay record, or
independent caller at the companion address. Its companion span ends at
`__osCheckId = 0x8002FC60`; preserve the ABI name. Audit:
`docs/RENAME-S5153-AUDIT.md`. `__osCheckId = 0x8002FC60` is now likewise
classified as an unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and the generated tree has no body, placeholder, or
independent caller at the companion address. Its companion span ends at
`__osPfsRWInode = 0x8002FD5C`; preserve the ABI name. Audit:
`docs/RENAME-S5154-AUDIT.md`. `__osPfsRWInode = 0x8002FD5C` is likewise an
unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and the generated tree has no body, placeholder,
overlay record, or independent caller at the companion address. Its requested
companion boundary is `0x8003007C`; preserve the ABI name. Audit:
`docs/RENAME-S5155-AUDIT.md`. `__osPfsSelectBank = 0x8003007C` is now
classified as another unmaterialized libultra/ABI entry: the helper reported
`already-synchronized`; the generated tree has no body or overlay record,
while five generated callers target an existing host wrapper that returns
`PFS_ERR_NOPACK`. Its requested companion boundary is `0x800303D0`; preserve
the ABI name. Audit: `docs/RENAME-S5156-AUDIT.md`. The next candidate is
`osPfsDeleteFile = 0x800300F0` is now likewise classified as an unmaterialized
libultra/ABI entry: the helper reported `already-synchronized`; the generated
tree has only the ABI declaration, one generated caller, and a zero-size
overlay record, with no generated body at the companion address. Its
companion boundary is `0x800303D0`; preserve the ABI name. Audit:
`docs/RENAME-S5157-AUDIT.md`. `__osPfsReleasePages = 0x800303D0` has now been
classified as already correctly named: its generated body and exact `0x248`
overlay span end at `0x80030618`, but the generated tree has no independent
caller. Preserve the ABI name. Audit: `docs/RENAME-S5158-AUDIT.md`. The next
`__osBlockSum = 0x80030618` is now also classified as already correctly named:
its generated body and exact `0xF8` overlay span end at `0x80030710`, and the
generated tree has two independent callers. Preserve the ABI name. Audit:
`docs/RENAME-S5159-AUDIT.md`. `osPfsFreeBlocks = 0x80030710` is now
classified as another unmaterialized libultra/ABI entry:
the bounded helper reported `already-synchronized`; the generated tree has
only the ABI declaration and a zero-size overlay record, with no body,
placeholder, or independent caller at the companion address. Its companion
boundary is `0x80030A70`; preserve the ABI name. Audit:
`docs/RENAME-S5160-AUDIT.md`. The next candidate is
`__osPfsGetStatus = 0x80030860` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree search found no body, placeholder, overlay record, or
independent caller at the companion address. Its companion span ends at
`__osPfsRequestOneChannel = 0x80030944`; preserve the ABI name. Audit:
`docs/RENAME-S5161-AUDIT.md`. The next candidate is now
`__osPfsRequestOneChannel = 0x80030944`.

The required 15-session sweep revisit ran a new retail function-entry gate.
With the whole-RDRAM and mission VI controls positive, retail entered
`fillSampleStreamRange = 0x8008FAAC` 145,268 times, while the old interior
site `0x800903F0` remained at zero; adjacent writer watches fired 1,205 times.
This is single-source evidence for `H-retail-branch-diff`, not a port
explanation: the containing function is live, but the previously watched
interior path is not. Preserve the boundary as open pending a second source
or a port-side join. Audit: `docs/REVISIT-S5183-RETAIL-FUNCTION-GATE.md`.

Session 5203 repeated that boundary with a bounded entry field dump. With the
whole-RDRAM and both mission VI controls positive, retail entered
`fillSampleStreamRange = 0x8008FAAC` 290,798 times, while exact interior
`0x800903F0` remained at zero. The entry dump retained 145,514 phase-gated
hits before its row cap; the interior dump retained zero. This is still
single-source oracle evidence for `H-retail-branch-diff`: it supplies entry
tuples for a future port-side join but does not identify a port writer or
prove a port defect. Audit: `docs/REVISIT-S5203-RETAIL-ENTRY-FIELDS.md`.

`__osPfsRequestOneChannel = 0x80030944` is now classified as another
unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and the generated-tree search found no body,
placeholder, overlay record, or direct caller at the companion address.
Its companion span ends at `__osGetOneChannelData = 0x80030A04`; preserve the
ABI name. Audit: `docs/RENAME-S5162-AUDIT.md`. The next candidate is now
`__osGetOneChannelData = 0x80030A04`.

`osRecvMesg = 0x800331D0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has only the ABI declaration and a zero-size overlay
record, with no body, placeholder, or direct generated caller at the
companion address. Its nominal span to `osSendMesg = 0x80033410` is `0x240`,
with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5181-AUDIT.md`. The next candidate is now `osSetEventMesg =
0x80033560`.

`osSpTaskStartGo = 0x80033FCC` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
independent generated-tree searches found no body or placeholder at the
companion address. Its overlay record is zero-size and five generated callers
invoke the host wrapper. Its nominal span to `bcopy = 0x80034010` is `0x44`,
with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5199-AUDIT.md`. The next candidate is now `bcopy = 0x80034010`.

`bcopy = 0x80034010` is now classified as already correctly named: its
generated body spans exactly `0x310` bytes to `0x80034320`, matching the next
companion entry, and it has one independent generated caller. Preserve the
ABI name. Audit: `docs/RENAME-S5200-AUDIT.md`. The next candidate is now
`__osSpDeviceBusy = 0x80034320`.

`__osSpDeviceBusy = 0x80034320` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
independent generated-tree searches found no body, placeholder, overlay
record, or direct caller at the companion address. Its companion span ends at
`__osSpRawStartDma = 0x80034350`, but no generated body exists to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5201-AUDIT.md`. The next candidate
is now `__osSpRawStartDma = 0x80034350`.

`__osSpRawStartDma = 0x80034350` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized` and
renamed zero references in zero files. Independent generated-tree searches
found no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal span to `__osSpSetPc = 0x800343E0` is `0x90`,
with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5202-AUDIT.md`. The next candidate is now
`__osSpSetPc = 0x800343E0`.

`__osSpSetStatus = 0x80034420` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has no body, placeholder, overlay record, or direct
generated caller at the companion address. Its nominal span to
`__osSpGetStatus = 0x800344D0` is `0xB0`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5205-AUDIT.md`. `__osSpGetStatus =
0x800344D0` is now classified as another unmaterialized libultra/ABI entry:
the bounded helper reported `already-synchronized`, and independent
generated-tree searches found no body, placeholder, overlay record, or direct
generated caller at the companion address. Its nominal span to
`osStartThread = 0x800344E0` is `0x10`, with no body to validate. Preserve the
ABI name. Audit: `docs/RENAME-S5206-AUDIT.md`. The next candidate is now
`osStartThread = 0x800344E0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has no body or placeholder at the companion address. It
contains only the ABI declaration, a zero-size overlay record, and 12 calls
to the existing host wrapper. Its nominal span to `osStopThread = 0x80034630`
is `0x150`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5207-AUDIT.md`. The next candidate is now
`osStopThread = 0x80034630`.

`__osGetOneChannelData = 0x80030A04` is now classified as another
unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and the generated tree has no body, placeholder,
overlay record, or direct caller at the companion address. Its nominal span to
the next companion entry, `osPfsInitPak = 0x80030AA0`, is `0x9C`, but no body
exists to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5164-AUDIT.md`. The next candidate is now
`osPfsInitPak = 0x80030AA0`.

`osPfsInitPak = 0x80030AA0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`; the
generated tree has one direct caller and a zero-size host-wrapper record, but
no generated body or placeholder at the companion address. Its nominal span
to `osPfsChecker = 0x80030D40` is `0x2A0`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5165-AUDIT.md`. The next candidate is now
`osPfsChecker = 0x80030D40`.

`osPfsChecker = 0x80030D40` is now classified
as another unmaterialized libultra/ABI entry: the bounded helper reported
`already-synchronized`, and the generated tree has no body, placeholder,
overlay record, or direct caller at the companion address. Its nominal span
to `osPfsIsPlug = 0x800317A0` is `0xA60`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5166-AUDIT.md`. The next candidate is now
`osPfsIsPlug = 0x800317A0`.

`osPfsIsPlug = 0x800317A0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has no body, placeholder, overlay record, or direct
generated caller at the companion address. Its nominal span to
`__osPfsRequestData = 0x80031940` is `0x1A0`, with no body to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5167-AUDIT.md`. The next candidate
is now `__osPfsRequestData = 0x80031940`.

`__osPfsRequestData = 0x80031940` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has no body, placeholder, overlay record, or direct caller
at the companion address. Its nominal span to `__osPfsGetInitData =
0x80031A10` is `0xD0`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5168-AUDIT.md`.

The former next candidate, `__osPfsGetInitData = 0x80031A10`, is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree searches found no body, placeholder, overlay record, or
direct caller at the companion address. Its nominal span to
`__osPfsGetNextPage = 0x80031AE0` is `0xD0`, with no body to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5169-AUDIT.md`. The next candidate
is now `__osPfsGetNextPage = 0x80031AE0`.

`__osPfsGetNextPage = 0x80031AE0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree search found no body, placeholder, overlay record, or
direct caller at the companion address. Its nominal span to
`osPfsReadWriteFile = 0x80031BDC` is `0xEC`, with no body to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5170-AUDIT.md`. The next candidate
is now `osPfsReadWriteFile = 0x80031BDC`.

`osPfsReadWriteFile = 0x80031BDC` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`; the
generated tree has only its ABI declaration and three generated callers, with
no body or placeholder at the companion address. Its zero-size overlay record
has offset `0x3179C`; the companion boundary is `osPfsRepairId = 0x80032000`.
Preserve the ABI name. Audit: `docs/RENAME-S5171-AUDIT.md`. The next candidate
`osPfsRepairId = 0x80032000` is now likewise classified as an unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated tree has no body, placeholder, or overlay record at the
companion address, only one ABI call site. Its companion boundary is
`osPfsFindFile = 0x80032260`; preserve the ABI name. Audit:
`docs/RENAME-S5172-AUDIT.md`. The next candidate is now
`osPiStartDma = 0x80032420`.

`osPfsFindFile = 0x80032260` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`; the
generated tree has two direct callers and a zero-size overlay record, but no
generated body or placeholder at the companion address. Its nominal span to
`osPiStartDma = 0x80032420` is `0x1C0`, with no body to validate. Preserve the
ABI name. Audit: `docs/RENAME-S5173-AUDIT.md`.

`osPiStartDma = 0x80032420` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`; the
generated tree has the ABI declaration, four direct generated callers, and a
zero-size overlay record, but no generated body or placeholder at the
companion address. Its nominal span to `osPiGetCmdQueue = 0x80032530` is
`0x110`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5174-AUDIT.md`. `osPiGetCmdQueue = 0x80032530` is now likewise
classified as an unmaterialized libultra/ABI entry: the bounded helper
reported `already-synchronized`, and the generated tree has no body,
placeholder, or overlay record at the companion address. Its nominal span to
`osCreatePiManager = 0x80032560` is `0x30`, with no body to validate.
Preserve the ABI name. Audit: `docs/RENAME-S5175-AUDIT.md`. The next candidate
is now `osCreatePiManager = 0x80032560`.

`osCreatePiManager = 0x80032560` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`; the
generated tree has one direct caller and a zero-size overlay record, but no
generated body or placeholder at the companion address. Its nominal span to
`osCartRomInit = 0x800326F0` is `0x190`, with no body to validate. Preserve the
ABI name. Audit: `docs/RENAME-S5176-AUDIT.md`. `osCartRomInit = 0x800326F0`
is now likewise classified as an unmaterialized libultra/ABI entry: the
bounded helper reported `already-synchronized`; the generated tree has only
the ABI declaration and a zero-size overlay record, with no body, placeholder,
or direct generated caller at the companion address. Its nominal span to
`osGetThreadPri = 0x80032FB0` is `0x8C0`, with no body to validate. Preserve
the ABI name. Audit: `docs/RENAME-S5177-AUDIT.md`. The next candidate is now
`osGetThreadPri = 0x80032FB0`.

`osGetThreadPri = 0x80032FB0` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`; the
generated tree has only the ABI declaration and a zero-size overlay record at
offset `0x32B70`, with no body, placeholder, or direct generated caller at the
companion address. Its nominal span to `osPiRawStartDma = 0x80033090` is
`0xE0`, with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5178-AUDIT.md`. The next candidate is now
`osPiRawStartDma = 0x80033090`.

`osPiRawStartDma = 0x80033090` is now classified as another unmaterialized
libultra/ABI entry: the bounded helper reported `already-synchronized`, and
the generated-tree search found no body, placeholder, overlay record, or
direct caller at the companion address. Its nominal span to
`osPiRawReadIo = 0x80033170` is another unmaterialized libultra/ABI entry:
the bounded helper reported `already-synchronized`, and the generated tree
has no body, placeholder, overlay record, or direct generated caller at the
companion address. Its nominal span to `osRecvMesg = 0x800331D0` is `0x160`,
with no body to validate. Preserve the ABI name. Audit:
`docs/RENAME-S5180-AUDIT.md`. The next candidate is now
`osRecvMesg = 0x800331D0`.

This maintenance iteration compacted the previous 611-line state file. The
removed historical narrative remains recoverable in git; durable conclusions
were retained below or in the project overview.

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
  DMA remain parked. The retail entry boundary now has a new single-source
  branch-difference result, but its port-side value origin remains open.
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

- Continue one companion entry at a time only when semantic name, exact body
  span, and a live generated caller support a rename.
- Host wrappers and zero-span entries retain their `_recomp` ABI names. A
  rename helper result of `already-synchronized` is a no-change result, not a
  runtime issue.
- `__osGetSR = 0x8002C230` is another companion-only libultra entry: the
  helper, generated-tree search, and overlay table show no generated body or
  caller, so its ABI name is preserved. Audit: `docs/RENAME-S5132-AUDIT.md`.
- `__osLeoAbnormalResume = 0x8002CBA4` is another companion-only libultra
  entry: the bounded helper reports `already-synchronized`, and the generated
  tree has no body, overlay record, or caller. Its companion span is `0xE8` to
  `0x8002CC8C`; preserve the ABI name. Audit:
  `docs/RENAME-S5136-AUDIT.md`.
- `__osLeoResume = 0x8002CC8C` is another companion-only libultra entry: the
  bounded helper reports `already-synchronized`, and the generated tree has no
  body, overlay record, or caller. Its companion span is `0xEC` to
  `0x8002CD80`; preserve the ABI name. Audit:
  `docs/RENAME-S5137-AUDIT.md`.
- `osEPiRawStartDma = 0x8002CD80` is another unmaterialized libultra entry:
  the bounded helper reports `already-synchronized`, and the generated tree
  has only an ABI declaration plus a zero-size overlay record, with no body or
  caller. The companion next-entry boundary is `0x8002CFB0`; preserve the ABI
  name. Audit: `docs/RENAME-S5138-AUDIT.md`.
- `osLeoDiskInit = 0x8002CFB0` is another unmaterialized libultra entry: the
  bounded helper reports `already-synchronized`, and the generated tree has no
  body, declaration, overlay record, or caller. The companion next-entry
  boundary is `0x8002D370`; preserve the ABI name. Audit:
  `docs/RENAME-S5139-AUDIT.md`.
- `osMapTLBRdb = 0x8002D370` is another unmaterialized libultra entry: the
  bounded helper reports `already-synchronized`, and the generated tree has no
  body, declaration, overlay record, or caller. The companion next-entry
  boundary is `0x8002D3D0`; preserve the ABI name. Audit:
  `docs/RENAME-S5140-AUDIT.md`.
- `osMotorStop = 0x8002D3D0` is another unmaterialized libultra entry: the
  bounded helper reports `already-synchronized`; the generated tree has only
  an existing ABI declaration, four wrapper call sites, and a zero-size
  overlay record, with no body at the companion address. The companion next
  entry is `osMotorStart = 0x8002D570`; preserve the ABI name. Audit:
  `docs/RENAME-S5141-AUDIT.md`.
- `osMotorStart = 0x8002D570` is another unmaterialized libultra entry: the
  bounded helper reports `already-synchronized`; the generated tree has only
  its ABI declaration, one wrapper call site, and a zero-size overlay record,
  with no body at the companion address. The companion next entry is
  `_MakeMotorData = 0x8002D710`; preserve the ABI name. Audit:
`docs/RENAME-S5142-AUDIT.md`.
- `_MakeMotorData = 0x8002D710` is another unmaterialized libultra/ABI entry:
  the bounded helper reports `already-synchronized`; the generated tree has
  no body, placeholder, overlay record, or direct caller. The companion next
  entry is `osMotorInit = 0x8002D88C`; preserve the ABI name. Audit:
  `docs/RENAME-S5143-AUDIT.md`.
- `__osPfsReleasePages = 0x800303D0` has a generated body and exact `0x248`
  overlay span ending at `0x80030618`, but no independent generated caller;
  the helper reports `already-synchronized`, so preserve the existing ABI
  name. Audit: `docs/RENAME-S5158-AUDIT.md`.
- `__osBlockSum = 0x80030618` has a generated body and exact `0xF8` overlay
  span ending at `0x80030710`, plus two independent generated callers; the
  helper reports `already-synchronized`, so preserve the existing ABI name.
  Audit: `docs/RENAME-S5159-AUDIT.md`.
- `osPfsFreeBlocks = 0x80030710` is another unmaterialized libultra/ABI entry:
  the bounded helper reported `already-synchronized`; the generated tree has
  only the ABI declaration and a zero-size overlay record, with no body,
  placeholder, or independent caller at the companion address. Its companion
  boundary is `0x80030A70`; preserve the ABI name. Audit:
  `docs/RENAME-S5160-AUDIT.md`.
- `__osPfsRequestOneChannel = 0x80030944` is another unmaterialized
  libultra/ABI entry: the bounded helper reported `already-synchronized`, and
  the generated tree has no body, placeholder, overlay record, or direct
  caller at the companion address. Its companion boundary is
  `__osGetOneChannelData = 0x80030A04`; preserve the ABI name. Audit:
  `docs/RENAME-S5162-AUDIT.md`.
- `__osGetOneChannelData = 0x80030A04` is another unmaterialized libultra/ABI
  entry: the bounded helper reported `already-synchronized`, and the
  generated tree has no body, placeholder, overlay record, or direct caller at
  the companion address. Its nominal span to `osPfsInitPak = 0x80030AA0` is
  `0x9C`, but no body exists to validate. Preserve the ABI name. Audit:
  `docs/RENAME-S5164-AUDIT.md`.
- `osPfsAllocateFile = 0x8002EBE0` is another unmaterialized libultra/ABI
  entry: the bounded helper reported `already-synchronized`, and the
  generated tree has only its ABI declaration, one direct caller, and a
  zero-size overlay record, with no body at the companion address. The
  companion next entry is `__osPfsDeclarePage = 0x8002F064`; preserve the ABI
  name. Audit: `docs/RENAME-S5145-AUDIT.md`.
- `__osPfsDeclarePage = 0x8002F064` has a generated body and exact `0x264`
  overlay span ending at `0x8002F2C8`, but no independent generated caller;
  the helper reports `already-synchronized`, so preserve the existing ABI
  name. Audit: `docs/RENAME-S5146-AUDIT.md`.
- `__osClearPage = 0x8002F2C8` has a generated body and exact `0xC8` overlay
  span ending at `0x8002F390`, plus two generated callers; the helper reports
  `already-synchronized`, so preserve the existing ABI name. Audit:
  `docs/RENAME-S5148-AUDIT.md`.
- `__osSumcalc = 0x8002F390` has a generated body and exact `0x5C` overlay
  span ending at `0x8002F3EC`, plus an independent generated caller at
  `0x800306B4`; the helper reports `already-synchronized`, so preserve the
  existing ABI name. Audit: `docs/RENAME-S5149-AUDIT.md`.
- `__osIdCheckSum = 0x8002F3EC` has a generated body and exact `0x68` overlay
  span ending at `0x8002F454`; the helper reports `already-synchronized`, and
  the generated tree has no independent caller. Preserve the existing ABI
  name. Audit: `docs/RENAME-S5150-AUDIT.md`.
- `__osCheckPackId = 0x8002F86C` is another unmaterialized libultra/ABI entry:
  the bounded helper reported `already-synchronized`, and no generated body,
  placeholder, overlay record, or independent caller exists at the companion
  address. Its next companion boundary is `__osGetId = 0x8002FA04`; preserve
  the ABI name. Audit: `docs/RENAME-S5152-AUDIT.md`.
- `__osGetId = 0x8002FA04` is another unmaterialized libultra/ABI entry: the
  bounded helper reported `already-synchronized`, and no generated body,
  placeholder, overlay record, or independent caller exists at the companion
  address. Its companion boundary is `__osCheckId = 0x8002FC60`; preserve the
  ABI name. Audit: `docs/RENAME-S5153-AUDIT.md`.
- `__osCheckId = 0x8002FC60` is another unmaterialized libultra/ABI entry:
  the bounded helper reported `already-synchronized`, and the generated tree
  has no body, placeholder, or independent caller at the companion address.
  Its companion boundary is `__osPfsRWInode = 0x8002FD5C`; preserve the ABI
  name. Audit: `docs/RENAME-S5154-AUDIT.md`.
- `__osPfsRWInode = 0x8002FD5C` is another unmaterialized libultra/ABI entry:
  the bounded helper reported `already-synchronized`, and the generated tree
  has no body, placeholder, overlay record, or independent caller at the
  companion address. Its requested companion boundary is `0x8003007C`; preserve
  the ABI name. Audit: `docs/RENAME-S5155-AUDIT.md`.
- `__osPfsSelectBank = 0x8003007C` is another unmaterialized libultra/ABI
  entry: the helper reported `already-synchronized`; the generated tree has
  no body or overlay record, and five generated callers target the existing
  host wrapper returning `PFS_ERR_NOPACK`. Its companion boundary is
  `0x800303D0`; preserve the ABI name. Audit:
  `docs/RENAME-S5156-AUDIT.md`.
- `osPfsDeleteFile = 0x800300F0` is another unmaterialized libultra/ABI
  entry: the helper reported `already-synchronized`; the generated tree has
  only the ABI declaration, one generated caller, and a zero-size overlay
  record, with no generated body at the companion address. Its companion
  boundary is `0x800303D0`; preserve the ABI name. Audit:
  `docs/RENAME-S5157-AUDIT.md`.
- `osPfsInitPak = 0x80030AA0` is another unmaterialized libultra/ABI entry:
  the helper reports `already-synchronized`; the generated tree has one
  direct caller and a zero-size host-wrapper record, but no generated body or
  placeholder at the companion address. Its nominal span to
  `osPfsChecker = 0x80030D40` is `0x2A0`, with no body to validate. Preserve
  the ABI name. Audit: `docs/RENAME-S5165-AUDIT.md`.
- `osPfsChecker = 0x80030D40` is another unmaterialized libultra/ABI entry:
  the bounded helper reported `already-synchronized`, and the generated tree
  has no body, placeholder, overlay record, or direct caller at the companion
  address. Its nominal span to `osPfsIsPlug = 0x800317A0` is `0xA60`, with no
  body to validate. Preserve the ABI name. Audit:
  `docs/RENAME-S5166-AUDIT.md`.
- Recent classifications: `bcmp` and `bzero` were renamed with exact spans;
  EEPROM/controller entries through `__osPackReadData` were classified as
  host wrappers or ABI boundaries. Audits are `docs/RENAME-S5106-AUDIT.md`
  through `docs/RENAME-S5135-AUDIT.md`.

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
  retail cxd4 oracle run sampled mid-task state and found 0/289 hangar tasks
  with a `0x8000` lane (0/577 across all 512-wide tasks). This is
  single-source retail evidence, not a port explanation; see
  `docs/REVISIT-S5129-AUDIT.md`.
- Heap/copy/message-queue/PI-DMA and audited host-wrapper pointer classes are
  closed on the qualified keyed route with positive controls. Re-open only on
  a phase-qualified recurrence.
- The mission input thread is closed: stick state at `0x80130B88` reaches
  flight code; the player vehicle object at `0x80138458` moves normally.
- The s4296 A14 yield patch is present and guarded by
  `tools/check_a14_yield_patch.py`; the prior mission shutdown spin was traced
  to its missing generated patch, not a new audio diagnosis.

## Superseded conclusions worth retaining

- Earlier claims that M5 was fully closed were too broad: nonzero PCM proves
  route activity, not every audio contract.
- Earlier claims that the loop had no runnable target were overturned when a
  mission-qualified soak became available; use `scratch/agent/NEXT.md` and
  the soak queue rather than declaring a block from a stale backlog.
- The old exact retail-entry and stale-base voice theories are not current
  explanations. Their guarded/atomic/lock variants either remained live or
  were route-blocking; no value rewrite was authorized.

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

## Next steps (single monotonic backlog)

1. Resume the companion sweep with `osStopThread = 0x80034630`, whose next
   candidate follows from its bounded symbol-map span, one entry per iteration
   now that the last-15 preflight remains broken by the retail revisit. The
   retail entry boundary remains open only for a port-side join. The M4 page
   writer is phase-attributed on the retail route, but its port-side value
   origin remains open.
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
