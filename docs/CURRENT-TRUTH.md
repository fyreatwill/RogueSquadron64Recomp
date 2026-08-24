# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2302 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§46; the append-only ledger is authoritative for exact commands, counts, and
probe rows.

Maintained in Session 2328 (2026-08-24). Session 2303 was the maintenance
iteration that migrated durable s2263–s2302 history to §46, pruned closed
detail, and renumbered the active backlog. Session 2304 ran the M5
task→stage→PCM ordinal join; s2305 extended it to a corrected bounded
temporal join; s2306 extended it to a 45-second recurrence capture with a
per-destination payload-mismatch summary; s2307 extended that capture across
all retained target phases; s2308 added phase-scoped writer provenance and
discovered that the nonzero ring slots rotate between captures; s2309 added
retail whole-ring writer/value ground truth; s2311 added a title-phase writer
census alongside both active 512 target buckets; s2312 added both recurring
post-title 512 origins and found no phase-attributed writer rows in any of the
five distinct configured buckets.
Session 2313 added the two earlier 640 origins and again found no
phase-attributed writer rows, despite positive callback coverage in both.
Session 2315 added all six remaining VI origins and again found no
phase-attributed writer rows, despite positive callback coverage in every
bucket.
Session 2316 ran the ground-truth-first gate/task/wait checkpoint; the oracle
controls passed, but both port arms crashed before the required hangar phase.
Session 2317 repaired the route with the explicit keycode-36 schedule and
added the full gate/task/wait oracle attribution table; both port arms reached
hangar, while retail showed no target-phase gate or wait writer row.
Session 2318 expanded that table to all fifteen observed VI origins. The
oracle had positive coverage in every bucket, found earlier-origin gate and
task writers, and still found no wait-field writer; both port arms again
reached title and hangar with the complete contract markers.
Session 2319 added the existing `ROGUESQ_LOG_VI_CALLERS=1` table to the
explicit pair; both port arms reached title and hangar, while the independent
oracle again passed all fifteen buckets and found no wait-field writer. Task,
DMA, image-stage, and PCM controls stayed positive, but no valid port
`01/02/00` slot transition or descriptor row appeared; the only key-on row
had `idx=0xFFFFFFFF` and `armed=0`.
Session 2320 added physical watches for the five active-byte candidates. The
same-run oracle passed whole-RDRAM (`10329`), title/hangar, gate/task (`17`/
`108`), wait (`0`), and all fifteen phase buckets. Retail wrote four of the
five watched locations after arming, including named target-phase writers,
but every sampled status top byte was `00`; no `01/02` transition was
observed. Both port arms again reached hangar with no slot/descriptor row and
the sentinel key-on. This selects a zero-only retail status result at the
capture scope, while the phase-keyed writer/value join remains open.

Session 2321 added phase-keyed post-store rows for the fourteen named
active-byte writer PCs. The same-run oracle passed whole-RDRAM (`10329`),
title/hangar, gate/task/wait (`17/108/0`), and all fifteen phase buckets.
The target `0x006AB400:512` bucket had `24` requested-writer samples with
top-byte counts `00=21`, `01=0`, `02=0`, `03=1`, `3F=2`. The `54` samples
from those writers outside the target bucket had `00=46`, `01=3`, `02=3`,
`03=2`. Both port arms reached hangar with positive task/PCM controls but
zero slot/descriptor rows and sentinel key-on rows. This selects
`H-Retail-Earlier-Nonzero` at capture scope; it does not establish that the
earlier `01/02` values are active-slot status. Writer/value ownership is the
prior boundary; target status semantics and zeroing are now the next boundary.
Session 2322 added an opt-in bounded detail table to that same oracle path.
The valid capture produced `78` requested-writer rows: target
`0x006AB400:512` had `35` rows with top-byte counts `00=30`, `01=3`,
`02=2`; the other origins had `43` rows with `00=37`, `01=0`, `02=1`,
`03=3`, and `3F=2`. All five target `01/02` rows were at physical
`0x00154620`, written by `0x8009B214` or `0x8009B6F8`; the independent
target phase histogram named those same PCs. Both port arms reached hangar
with task/PCM controls, while slot allocation/byte/descriptor rows stayed
zero and key-on remained the sentinel. This selects target status presence
at capture scope and leaves status semantics/zeroing open.
Session 2323 added VI ordinal and sampled origin/width to the status poll and
ran the same staged pair with both status polling and writer detail enabled.
The oracle passed whole-RDRAM `10329`, title/hangar, gate/task/wait `17/108/0`,
all fifteen phase buckets, and `25` writes to `0x00154620`. The target word's
status poll showed three repeated `01 -> 02 -> 03 -> 00` cycles; detail rows
independently named `0x8009B214`/`0x8009B6F8` for `01/02` and
`0x8009B7CC`/`0x8009B7EC` for the later `03/00` stores. No competing word
showed a stable lifecycle; the two noisy tail words were high-entropy data.
This selects `H-Status-Cycle` at capture scope and closes the retail status
lifecycle boundary. Both port arms still reached hangar with task/PCM
controls but zero slot/descriptor rows and sentinel key-on rows. No runtime,
audio, gate, wait, slot, consumer, address, mitigation, or default behavior
changed.

Session 2324 ran the M5 Step 1 same-build stub/image checkpoint behind the
retail oracle. The oracle positive control reached `10329` whole-RDRAM writes,
title/hangar, gate/task/status watches `17/108/25`, all fifteen phase buckets,
and no wait-field writes. Both port arms reached title and hangar. The stub
produced `1442` task-ABI/DMA rows with no image DMA/stage rows; the image arm
produced `1155` task-ABI rows, `2368` image DMA ranges, `2367` joined
image-stage rows, and `518` successful `0x1328`/`Broke` returns with DMEM
changes. Only the image arm produced nonzero target payload rows, at
`0x167C50` (`60F910DE`, `nz=621`) and `0x167F50` (`7B70923A`, `nz=639`);
the latter independently joined both PCM source and consumer. The image
arm's other sampled PCM rows remained zero. Both arms still had zero
slot-allocation, slot-byte, descriptor, and voice/filter rows, while gate,
route, task-return, and SP-completion controls were positive. This selects
live image-RSP progress plus an unresolved downstream task/output-to-slot
contract gap at capture scope; it does not authorize a writeback, guard,
default, or key-on change.

Session 2325 ran the ground-truth-first task/output-to-consumer table. The
retail oracle passed whole-RDRAM `1346640`, title/hangar, gate/task/status
watches `17/108/25`, wait `0`, and named target task/output writers
`0x8008EB8C`, `0x8008EBBC`, and `0x80094648`. Both port arms reached hangar
with the same route controls. The stub had task ABI/DMA `1143/1143`, PCM
source/consumer `88/88`, and zero image-stage rows. The image arm had task
ABI/DMA `1140/1140`, `2305` DMA ranges, `2300` image joins, and target
summary `618` stage rows with two nonzero rows. Destination `0x168850`
(`2B9E9631`, `nz=621`) was stage-only; destination `0x168B50`
(`6ADD4218`, `nz=639`) had exact source/consumer events `6426/6427` with
source-before-consumer ordering. Neither arm emitted slot, descriptor,
voice/filter, or key-on rows. This selects `H-Destination-Role-Skew` at
capture scope, rules out a uniform image-stage-only result, and leaves the
destination-to-slot/key-on contract open. No runtime behavior changed.

Session 2326 ran the corrected ground-truth-first destination-to-slot/key-on
table. The retail oracle passed whole-RDRAM (`1341192` writes), title/hangar,
gate/task/status watches (`17/108/25`), wait (`0`), and the three named task
writers (`0x8008EB8C`, `0x8008EBBC`, `0x80094648`). Both port arms reached
title and hangar; VI-caller and audio-task ABI controls were positive in both.
The image arm's target phase had two nonzero stage rows at
`0x166750`/`0x300`/`60F910DE`/`nz=621` and
`0x166A50`/`0x300`/`7B70923A`/`nz=639`; both were stage-only with source and
consumer events `0/0`. The signed event table found zero post-stage
slot-allocation, slot-byte, slot-store, key-on, descriptor, or M5 key-on rows
for either destination. It did find pre-stage rows shared by both destinations:
five `slot-sb` stores, one sentinel `keyon-w40` row (`idx=0xFFFFFFFF`,
`armed=0`), and nineteen M5 key-on rows. Raw marker recount agrees with the
table. The filter/voice probe emitted no positive control, so this run does
not establish a filter/voice null. This selects
`H-Missing-Descriptor-Contract` at this capture scope, with the ordering
boundary still open: pre-stage lifecycle rows may belong to the same task or
to an earlier tick. No runtime, audio, gate, wait, slot, writeback, consumer,
address, mitigation, or default behavior changed.

Session 2327 ran the ground-truth-first task-ordinal pre/post join with the
required stub and image arms. The retail oracle independently passed whole-
RDRAM (`537360` writes), title/hangar VI coverage, task/output (`108`) and
gate (`17`) watches, wait (`0`), status (`23`), and the three target writer-PC
controls. Both port arms reached title and hangar with positive VI and task
controls. The image arm's target phase contained two nonzero stage rows for
audio ordinal `705`, at `0x166A50` (stage-only) and `0x166D50` (PCM source /
consumer `6456/6457`). Its signed table contained zero same-ordinal slot,
key-on, or descriptor rows. Instead, six active lifecycle events (five
`slot-sb`, one `keyon-w40`) occurred at deltas `-10..-3` before the target
stage and were stamped with the prior route ordinal `704` in phase 8; the
stub arm independently showed the same shape with prior ordinal `703` and no
target image rows. The task-ordinal table therefore selects
`H-PreEvents-EarlierTick` at this capture scope and rules out same-task
ownership of those pre-stage rows. This is a two-arm replication from one
instrumentation source; the filter/voice positive control remained absent in
both arms, so that null remains unevaluable. The route snapshot needed to be
made process-shared because SP receive and lifecycle calls run on different
host threads; this was diagnostic-only and changed no game behavior.

Session 2328 first caught a stale drain A/B because the launcher env var was
absent from generated `funcs_30.c`. After applying the existing s1993 fixup
gate, the oracle and both image tick arms qualified; their normalized target
lifecycle tables matched, selecting `H-DrainRedundant` at capture scope.

The current M5 boundary is the destination-to-slot consumer after task-ordinal
ownership. The qualified default
Factor 5 image arm reaches title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`; measured nonzero phase-10 slots have exact source and
consumer joins in some captures. Retail independently reaches both origins
and supplies a different task/output writer class. The latest C88 route
discriminator was coverage-invalid before title/hangar, so it provides no C88
or key-on verdict. The s2309 phase-gated table found the current port pair at
`0x168850`/`len=0x300`/`fnv=60F910DE`/`nz=621` and
`0x168B50`/`len=0x300`/`fnv=7B70923A`/`nz=639`. The first had exact source
and consumer events, then a same-destination image-DMA rewrite to
`F59C39C5`/`nz=0`; the second remained stage-only. Retail's whole-ring
watch wrote all `0x3000` bytes and its final snapshot had `12026` nonzero
bytes, forcing at least `506` nonzero bytes in the observed `0x168850` slot.
That aggregate/final-snapshot result still selects `H-PortOnlyZeroFill` at
its capture scope. The s2312 same-run title plus four 512 buckets found all
five distinct phase buckets empty for the sixteen retail slot writers, while
the lifetime writer control remained positive and all final slot snapshots
were nonzero. Session 2313 added `0x0066A500:640` and `0x00696100:640`; both
had positive VI coverage (`18` and `202`) but no phase writer-PC rows. This
selects `H-Retail-Earlier-Or-Unattributed` at capture scope across all seven
  configured buckets. Session 2314 added `0x0066AA00:640` and
  `0x00696600:640`; both had positive VI coverage (`139` and `219`) but no
  phase writer-PC rows. This extends `H-Retail-Earlier-Or-Unattributed` at
  capture scope across all nine configured buckets. The stage-only row and
  game-level legitimacy remain open. Session 2315 added
  `0x00000280:320` (`vi=2`), `0x006BA280:320` (`46`),
  `0x005D4500:640` (`121`), `0x0062C200:640` (`92`),
  `0x0062BD00:640` (`103`), and `0x00790800:1024` (`631`); all had zero
  phase writer-PC rows, while the lifetime writer controls and final
  snapshots stayed positive. This closes the observed VI-origin census and
  leaves the writer outside the configured phase buckets, or phase
  attribution incomplete, as the active boundary. No runtime behavior change
  is authorized.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu overlay explanation is closed.
- The qualified route uses `ROGUESQ_LLE_FORCE=1`,
  `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, and
  `ROGUESQ_LLE_SOLO=1`. Spin yield is environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name the writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0`
  selects the silent `M_AUDTASK` `Broke` stub for controls. The image arm does
  real DMEM work and generated DMA, then returns `Broke`; its host canary is
  probe data only. Stock `aspMain` is not the game's MusyX/Factor 5 contract,
  and MORT is a separate CPU speech asset.
- The default image arm is qualified through the same title/hangar route as
  the stub at the tested recipe scope. The measured output contract remains
  capture-dependent: s2306 had one exact source/consumer pair and one
  stage-only row, s2307 found two fixed-address payload mismatches, s2308
  found a rotated pair with exact nonzero publication followed by later
  image-DMA zero writes, and s2309 independently showed aggregate retail
  nonzero final data. In s2310 the current port pair was
  `0x166750`/`0x166A50`; both were stage-only and later zero-filled by
  image-DMA, while retail's lifetime slot writers were outside both
  `0x006AB400:512` and `0x006AB800:512` phase buckets. Thus
  `H-PortOnlyZeroFill` remains an aggregate/final-snapshot result, and
  `H-SlotRoleTimeSkew` is selected for target-phase polarity. No writeback,
  consumer, writer, slot, gate, guard, address remap, or default change is
  authorized.
- The s2312 retail writer census retained the title and both active 512
  buckets and added `0x00656400:512` and `0x00656800:512`. All sixteen
  lifetime slot writers remained positive at `0x800078EC` with `768` writes
  each, but none of the five distinct phase buckets had a writer-PC row; all
  sixteen final snapshots were nonzero.
- **s2313 — earlier 640-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each), all seven phase callback
  controls, and all sixteen nonzero final snapshots. The new
  `0x0066A500:640` and `0x00696100:640` buckets had `18` and `202` VI
  callbacks, respectively, but no phase writer-PC row; neither supplied the
  missing publication phase. The complete seven-bucket × seventeen-watch
  phase matrix was empty for writer PCs. The port's observed pair was
  `0x168850`/`0x168B50`, with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`, exact source/consumer events `11801/11802` and
  `11810/11811`, and later zero PCM events `11873/11874` and `11882/11883`;
  `0x168B50` also had a later zero image-stage event `11820`. This confirms
  the earlier-origin gap at capture scope and leaves writer attribution and
  game legitimacy open. No runtime or contract change was authorized.
- **s2314 — companion 640-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each at `0x800078EC`), all nine
  configured phase buckets, and all sixteen nonzero final snapshots. The new
  `0x0066AA00:640` and `0x00696600:640` buckets had `139` and `219` VI
  callbacks, respectively, but no phase writer-PC row; the complete
  nine-bucket × seventeen-watch phase matrix was empty. This extends
  `H-Retail-Earlier-Or-Unattributed` at capture scope and rules out either
  companion origin plus shared/alternating publication. The current port pair
  was `0x167950`/`0x167C50`, with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`; the first had exact source/consumer events `11822/11823`,
  while the second remained stage-only. Later zero-payload rows occurred at
  image-stage events `11904`/`11834` and PCM events `11894/11895`/
  `11978/11979`. No runtime or contract change is authorized.
- **s2315 — remaining VI-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each at `0x800078EC`), all
  fifteen configured phase buckets, and all sixteen nonzero final snapshots.
  The new buckets had callbacks `2`, `46`, `121`, `92`, `103`, and `631` for
  `0x00000280:320`, `0x006BA280:320`, `0x005D4500:640`,
  `0x0062C200:640`, `0x0062BD00:640`, and `0x00790800:1024`, respectively;
  none had a phase writer-PC row. The complete fifteen-bucket × seventeen-
  watch phase matrix was empty. The current port pair was
  `0x168E50`/`0x169150`, with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`, stage events `9906/9908`, exact source/consumer events
  `9961/9962` and `9963/9964`, and later zero image-stage events `15317` and
  `10105` plus zero PCM source/consumer events `14274/14275` and
  `10030/10031`. This closes the observed VI-origin census and leaves
  writer attribution outside the configured buckets, or phase attribution
  incomplete, as the next M5 boundary. No runtime or contract change is
  authorized.
- **s2316 — gate/task/wait checkpoint was route-invalid.** The oracle passed
  whole-RDRAM (`10125` writes), title/hangar VI coverage, gate
  `0x000A0F50` (`17` writes), and task/output span
  `0x00141AD0:0x00141AF0` (`108` writes); the wait field
  `0x0001498A` had `0` writes. Both port arms reached title once but missed
  `512 @ 0x006AB400`, each ending in the existing
  `slotDispatcherIter+3508` / guest PC `0x80022160` crash family. The
  launcher also omitted the port gate/task contract env vars, so its zero
  `[m5-gate]` and related counts are not a valid port null. This selects
  `H-CoverageInvalid` and authorizes no gate, wait, status, slot, or
  mitigation change.
- **s2317 — repaired gate/task/wait checkpoint selects an outside-target
  writer boundary.** The dedicated explicit-route launcher passed syntax and
  ran one staged silent/image capture without rebuilding. Retail exited
  naturally with whole-RDRAM `10125`, title `633`, hangar `973`, gate-watch
  `17`, task/output-watch `108`, and wait-watch `0`. Its post-value table
  observed six gate samples (`0x00000000` ×4 and `0x01000000` ×2), 76
  task/output samples, and no wait samples. The title phase had gate rows
  without a writer PC and task/output writer `0x80094648` (`n=24`); the
  hangar phase had no writer PC for any of the three watches. Both port arms
  reached title and hangar and supplied positive contract activity: silent
  `[m5-gate]=1024`, `[m5-b40-route]=14`, PCM source/consumer `89/89`; image
  `[m5-gate]=1024`, `[m5-b40-route]=13`, image-stage `4408`, PCM
  source/consumer `88/88`. This selects `H-Gate-Wait-Outside-Target` at
  capture scope, with the task writer's title-phase role still separate; it
  rules out a target-phase oracle gate writer and target-phase wait writer in
  the two observed buckets, but does not distinguish an earlier observed
  origin from incomplete phase attribution. Both port processes later exited
  with the existing crash marker after reaching hangar; no runtime or
  contract change was made.
- **s2318 — all-origin gate/task/wait census selects an earlier writer.** The
  first direct run was coverage-invalid because the command session interrupted
  the still-running stub before hangar; the fixed PTY rerun passed the same
  controls. Retail exited naturally with whole-RDRAM `10125`, title `633`,
  hangar `979`, gate-watch `17`, task/output-watch `108`, wait-watch `0`, and
  fifteen positive phase buckets. Gate writer PCs appeared at earlier origins,
  including `0x006AB800:512` with `0x8008EB7C` and `0x8008EC88`; task writers
  also appeared there (`0x8008EB8C`, `0x8008EBBC`, and `0x80094648`). The wait
  watch had no writer PC or post-value sample. Both port arms reached title and
  hangar: silent `[m5-gate]=1024`, `[m5-b40-route]=14`, PCM `89/89`, and
  image `[m5-gate]=1024`, `[m5-b40-route]=13`, image-stage `4698`, PCM
  `88/88`. This selects `H-Earlier-Origin` at capture scope, rules out
  `H-Phase-Attribution-Gap` and `H-Task-Only`, and leaves writer legitimacy
  and slot/status progress open. No gate, wait, status, slot, consumer,
  address, or default change was authorized.
- **s2319 — slot/status table result.** The same-run oracle passed whole-RDRAM
  `10125`, title/hangar, all fifteen phase buckets, gate `17`, task/output
  `108`, and wait `0`. The stub and image both reached title/hangar. Stub
  controls were gate `1024`, route `14/28`, task ABI/DMA `1302/1302`, and
  PCM `89/89`; image controls were gate `1024`, route `13/25`, task ABI/DMA
  `1138/1138`, image-stage `4673`, DMA-range `2320`, and PCM `88/88`.
  `[vi-callers]` controls fired in both arms, but `[slot-alloc]`, `[slot-sb]`,
  and `[init-desc]` did not; the sole `[keyon-w40]` row in each arm was the
  sentinel index `0xFFFFFFFF` with `armed=0`. This selects `H-Task-Only` at
  capture scope and leaves independent retail active-byte writer attribution
  as the next boundary. No runtime, gate, wait, status, slot, consumer, or
  default change was authorized.
- **s2320 — active-byte ground truth is zero-only after phase arming.** The
  same-run oracle passed whole-RDRAM `10329`, gate/task/wait `17/108/0`, title,
  hangar, and all fifteen phase buckets. The five watches recorded lifetime
  writes `25/0/87/6/86` for slots `0..4`; target-phase writer rows named
  `0x8009BBF0` and its `0x8009B170/174/178/214` family for slot 0,
  `0x800292E4` for slot 2, and `0x80022B1C` for slot 4. Slot 3 had two
  post-value samples from `0x80017DB0` but no phase-histogram row; slot 1 had
  none. Across all post-value samples after title/hangar, the aligned words'
  status top byte was `00` (lower fields varied), with no `01/02` sample.
  Both port arms reached title/hangar with task/PCM controls; neither emitted
  slot allocation, slot-byte, or descriptor rows, and each key-on row stayed
  at `idx=0xFFFFFFFF`, `armed=0`. This selects
  `H-Retail-Zero-Only-After-Arming` at capture scope, rules out the prior
  retail-active-byte null, and leaves the phase-keyed value join and port
  address/contract boundary open. No runtime or audio behavior changed.
- **s2321 — target status is absent, earlier requested writers are nonzero.**
  The ground-truth-first explicit pair passed whole-RDRAM `10329`, title and
  hangar, gate/task/wait `17/108/0`, and all fifteen phase buckets. The target
  `0x006AB400:512` post-store table had `24` requested-writer samples:
  `00=21`, `01=0`, `02=0`, `03=1`, `3F=2`. The `54` same-writer samples
  outside that target bucket had `00=46`, `01=3`, `02=3`, `03=2`.
  Target-phase named writers were `0x8009B7CC` (`0x036E4000`),
  `0x800292E4` (21 top-byte-zero values), and `0x80022B1C`
  (`0x3F800000` twice). Stub and image both reached hangar with positive
  task/PCM controls; slot allocation, slot-byte, and descriptor markers
  stayed zero, and each key-on marker was `idx=0xFFFFFFFF`, `armed=0`.
  This selects `H-Retail-Earlier-Nonzero` at capture scope and leaves the
  writer/value ownership and game-level status meaning open. No runtime,
  audio, slot, gate, wait, consumer, address, mitigation, or default change
  was made.
- **s2322 — target status writer/value ownership.** The same-run oracle
  passed whole-RDRAM `10329`, title/hangar, gate/task/wait `17/108/0`, and
  all fifteen phase buckets. The new detail table recorded `78` requested-
  writer samples. In the target `0x006AB400:512` bucket, top-byte counts were
  `00=30`, `01=3`, `02=2`; outside it they were `00=37`, `01=0`, `02=1`,
  `03=3`, `3F=2`. The five target `01/02` rows all addressed
  `0x00154620` and were owned by `0x8009B214`/`0x8009B6F8`; the target
  phase histogram independently recorded those writers. This refutes the
  s2321 target-absence result and the narrower earlier-only selection at
  this capture scope, but does not prove that the word is a complete slot
  lifecycle. Stub and image both reached hangar with task/PCM controls;
  slot allocation/byte/descriptor stayed zero and key-on remained
  `idx=0xFFFFFFFF`, `armed=0`. Both port processes then hit their existing
  post-hangar crash path. No runtime, audio, slot, gate, wait, consumer,
  address, mitigation, or default change was made.
- **s2323 — target status lifecycle.** The same-run oracle passed whole-RDRAM
  `10329`, title/hangar, gate/task/wait `17/108/0`, and all fifteen phase
  buckets. Its new status rows recorded `1469` status changes, including three
  target `0x00154620` cycles `01 -> 02 -> 03 -> 00` at width `512`; the target
  detail table had `24` rows and named `0x8009B214`, `0x8009B6F8`,
  `0x8009B7CC`, and `0x8009B7EC`. The other stable words were initial-zero,
  `00 -> 01`, or non-status values; slots 16/17 produced `717/716` noisy
  changes with hundreds of other top-byte values. This selects
  `H-Status-Cycle`, refutes `H-Status-Sticky` and
  `H-Status-Other-Word` at capture scope, and closes retail status/zeroing.
  Stub/image port arms reached hangar with gate `1024`, task ABI/DMA
  `1440/1440` and `1142/1142`, image-stage `4658`, PCM `91/91` and `88/88`,
  but slot allocation/byte/descriptor remained zero and key-on stayed at
  `idx=0xFFFFFFFF`, `armed=0`. The arms then hit the existing post-hangar
  crash/retention outcomes. No behavior change was authorized.
- The retail oracle is an independent witness. Its whole-RDRAM, title, hangar,
  width-aware target, and exact-PC controls must pass before a null is read.
  The oracle currently reaches attract/title/hangar, not a mission.
- Generated-symbol renaming is closed at the useful boundary. Do not recensus
  or invent names for the five remaining placeholders:
  `func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, and
  `func_800E9AE0`.

## Latest evidence

- **s2325 — rotating image destinations split stage-only from exact PCM.** The
  same-run retail oracle passed whole-RDRAM `1346640`, title/hangar,
  gate/task/status `17/108/25`, wait `0`, and the named target task/output
  writers. Stub and image both reached hangar. Stub task ABI/DMA was
  `1143/1143` with no image-stage rows and PCM source/consumer `88/88`.
  Image task ABI/DMA was `1140/1140`, with `2305` DMA ranges and `2300`
  image joins. In target phase, the destination table had two nonzero rows:
  `0x168850`/`0x300`/`2B9E9631`/`nz=621` was stage-only, while
  `0x168B50`/`0x300`/`6ADD4218`/`nz=639` matched source event `6426` and
  consumer event `6427` in order. This selects `H-Destination-Role-Skew`
  at capture scope. Slot, descriptor, voice/filter, and key-on controls were
  zero in both arms; no writeback, address remap, or default change is
  authorized.

- **s2324 — image RSP is live; downstream slot contract remains open.** The
  same-run oracle passed whole-RDRAM `10329`, title/hangar, gate/task/status
  writes `17/108/25`, and all fifteen phase buckets; wait remained `0`.
  Both port arms reached the target phase. The stub had task ABI/DMA
  `1442/1442`, image-stage `0`, PCM source/consumer `91/91`, all-zero PCM,
  and no slot/descriptor rows. The image had task ABI/DMA `1155/1155`,
  image-stage `2367` joined rows, DMA-range `2368`, `518` successful
  `0x1328` returns, and PCM source/consumer `88/88`; exactly one target
  source/consumer tuple was nonzero (`0x167F50`, `7B70923A`, `nz=639`),
  alongside a stage-only nonzero row at `0x167C50` (`60F910DE`, `nz=621`).
  Neither arm emitted slot allocation, slot-byte, descriptor, or voice/filter
  rows. This is two independent port lines (task/DMA/exit and image-stage/
  PCM joins) plus the retail oracle control: the image arm is no longer a
  silent stub, but its downstream slot/key-on contract is still missing. No
  runtime or default change was authorized.

- **s2318 — earlier-origin gate/task writers are present.** The valid PTY
  rerun passed the independent oracle controls: whole-RDRAM `10125`, title
  `633`, hangar `979`, gate `17`, task/output `108`, wait `0`, and all fifteen
  phase buckets positive. Gate writer PCs occurred at earlier origins,
  including `0x006AB800:512` (`0x8008EB7C`, `0x8008EC88`), and task writer PCs
  occurred there as well (`0x8008EB8C`, `0x8008EBBC`, `0x80094648`); no wait
  writer or post-value sample occurred. Stub and image both reached title and
  hangar with `[m5-gate]` `1024` and PCM joins `89/89` and `88/88`; the image
  also emitted `4698` image-stage rows. This selects `H-Earlier-Origin` at
  capture scope and leaves slot/status progress and writer legitimacy open.

- **s2319 — task-only progress without a valid slot transition.** The valid
  same-run oracle passed whole-RDRAM `10125`, title `632`, hangar `964`, gate
  `17`, task/output `108`, wait `0`, and all fifteen phase buckets. Its phase
  table still showed earlier gate/task writers, including `0x8008EB7C`,
  `0x8008EC88`, `0x8008EB8C`, `0x8008EBBC`, and `0x80094648`; no wait writer
  or wait post-value existed. Stub and image both reached target phases with
  positive task/PCM controls; image had `2320` DMA-range and `4673`
  image-stage rows. The port slot/key-on table had no allocation, slot-byte,
  or descriptor rows, and its only key-on row was `idx=0xFFFFFFFF`,
  `armed=0`. This selects `H-Task-Only` at capture scope, rules out
  `H-CoverageInvalid`, and does not prove a game-level absence of slot writes
  because the independent oracle did not yet watch the active-byte ring.

- **s2316 — gate/task/wait capture was coverage-invalid.** The oracle
  completed with whole-RDRAM `10125` writes, title/hangar VI coverage, gate
  writes `17`, task/output-span writes `108`, and wait-field writes `0`.
  Silent and image port arms each produced one title phase but no
  `0x006AB400:512` phase; both ended at `slotDispatcherIter+3508` with guest
  PC `0x80022160`. The launcher’s port contract logging was not enabled, so
  its zero gate/task marker counts are unusable. No gate/wait or runtime
  change is authorized.

- **s2315 — all remaining VI origins remain unattributed.** The same-run
  oracle/port capture passed whole-RDRAM `10000`, title/hangar, ring writes
  `12288`, all sixteen lifetime `0x800078EC` slot-writer controls (`768`
  each), all fifteen phase callback buckets, and all sixteen nonzero final
  snapshots. The new origin callback counts were
  `0x00000280:320=2`, `0x006BA280:320=46`, `0x005D4500:640=121`,
  `0x0062C200:640=92`, `0x0062BD00:640=103`, and
  `0x00790800:1024=631`; all fifteen buckets had zero phase writer-PC
  rows. The port pair was `0x168E50`/`0x169150`, with nonzero stage
  `2B9E9631/621` and `6ADD4218/639`, exact joins `9961/9962` and
  `9963/9964`, then later zero image-stage events `15317`/`10105` and zero
  PCM source/consumer events `14274/14275` and `10030/10031`. This selects
  `H-Retail-Earlier-Or-Unattributed` at capture scope and authorizes no
  writeback, consumer, writer, slot, gate, guard, address-remap, or default
  change.

- **s2314 — companion 640-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each), all nine phase callback
  controls, and all sixteen nonzero final snapshots. The new
  `0x0066AA00:640` and `0x00696600:640` buckets had `139` and `219` VI
  callbacks but no phase writer-PC rows; all nine bucket × seventeen-watch
  phase cells were empty. The current port pair was
  `0x167950`/`0x167C50` with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`; the first matched source/consumer `11822/11823`, the
  second was stage-only, and later zero rows were observed at image-stage
  events `11904`/`11834` and PCM events `11894/11895`/`11978/11979`.
  This selects `H-Retail-Earlier-Or-Unattributed` at capture scope and
  authorizes no runtime or contract change.

- **s2313 — earlier 640-origin retail writer census.** The same-run capture
  passed whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`,
  all sixteen lifetime writer controls (`768` each), all seven phase callback
  controls, and all sixteen nonzero final snapshots. The new
  `0x0066A500:640` and `0x00696100:640` buckets had `18` and `202` VI
  callbacks, respectively, but no phase writer-PC row; the complete
  seven-bucket × seventeen-watch phase matrix was empty. The port's observed
  pair was `0x168850`/`0x168B50`, with stage FNV/nz `2B9E9631/621` and
  `6ADD4218/639`, exact source/consumer events `11801/11802` and
  `11810/11811`, and later zero PCM events `11873/11874` and `11882/11883`;
  `0x168B50` also had later zero image-stage event `11820`. This confirms the
  earlier-origin gap at capture scope and authorizes no runtime or contract
  change.

- **s2312 — retail writer earlier-origin gap.** The same-run capture passed
  whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`, all
  sixteen lifetime writer controls (`768` each at `0x800078EC`), nonzero
  final ring and slot snapshots, port title/hangar, and 45-second retention.
  The five distinct phase buckets had positive VI callbacks but no
  phase-attributed writer rows: `0x00790400:1024=631`,
  `0x006AB400:512=1895`, `0x006AB800:512=2386`,
  `0x00656400:512=2258`, and `0x00656800:512=1767`. This selects
  `H-Retail-Earlier-Or-Unattributed` and rules out both new post-title
  origins plus coverage invalidity at this capture scope.

  The current port pair was `0x166D50`/`0x300`/`60F910DE`/`nz=621` and
  `0x167050`/`0x300`/`7B70923A`/`nz=639`. The first was stage-only at event
  `9472`, with later zero PCM events `13497/13498` and image-stage event
  `13551`. The second matched source/consumer events `9572/9573` after stage
  event `9474`, then later emitted zero image-stage events `9577/9642` and
  zero PCM events `9637/9638`. No contract or runtime change was authorized.

- **s2311 — retail writer other-phase result.** The same-run capture passed
  whole-RDRAM `10000`, title/hangar VI coverage, ring writes `12288`, all
  sixteen lifetime writer controls (`768` each), title/target phase callback
  controls (`632`/`2735`/`1536`), port title/hangar, and 45-second retention.
  The `0x00790400:1024`, `0x006AB400:512`, and `0x006AB800:512` writer-PC
  buckets were all empty; all sixteen final slot snapshots were nonzero.
  The VI trace showed recurring post-title 512 origins `0x00656400` and
  `0x00656800` (25 and 44 callbacks in the retained trace), so this selects
  `H-RetailOtherPhase` and leaves the two-origin split for the next census.
  The current port pair was `0x169150`/`0x166450`, both `len=0x300`, with
  stage FNV/nz `2B9E9631/621` and `6ADD4218/639`. Each had an exact source
  and consumer match at events `9704/9705` and `9706/9707`, followed by
  zero-payload source/consumer rows at `9776/9777` and `9778/9779` and
  later zero image-stage rows at `9781` and `9788`. No contract, writer,
  slot, consumer, or mitigation change was authorized.

- **s2310 — per-slot retail polarity and dual-512 phase control.** The
  initial capture passed whole-RDRAM, title/hangar, ring-wide, all sixteen
  slot watches, port title/hangar, and 45-second retention, but its single
  `0x006AB400:512` writer bucket had no entries. The fixed rerun added
  `0x006AB800:512` in the same recipe. Both phase buckets were active
  (`1535` and `2720` VI callbacks), and the lifetime positive control
  attributed all sixteen `768`-byte slot watches (`768` writes each) to
  retail PC `0x800078EC`; neither 512 bucket contained a writer entry.
  The corrected run's current port pair was `0x166750`/`0x166A50`, with
  stage events `9740/9742`, FNV/nz `60F910DE/621` and
  `7B70923A/639`, respectively. Both were stage-only in the port join;
  later zero rows were events `9882/9884`, writer kind image-DMA, PC `0`,
  callsite `0x8008EE84`. Retail final snapshots for those exact slots were
  nonzero (`750/768`), FNV `E5CF803C`, and `753/768`, FNV
  `E611A9A8`. This selects `H-SlotRoleTimeSkew` for target-phase
  polarity, rules out a target-phase retail zero conclusion, and does not
  prove target-phase retail nonzero publication because its phase writer arm
  was a valid zero. No contract change or mitigation is authorized.

- **s2309 — retail whole-ring polarity.** The required oracle preflight and
  same-run capture passed the whole-RDRAM positive control, title/hangar VI
  origins, ring watch, an active phase bucket, the lifetime ring writer, and
  the final ring snapshot; the
  port reached title/hangar and retained 45 seconds. The port's current
  phase-10 pair was `0x168850` (`60F910DE`, `nz=621`) and `0x168B50`
  (`7B70923A`, `nz=639`). The first had exact source/consumer events
  `10804/10805`, then same-destination zero rows beginning at event `10881`;
  the last writer was image-DMA (`writer_pc=0`, callsite `0x8008EE84`). The
  second was stage-only. Retail wrote all `12288` bytes in
  `0x166450..0x169450` through `0x800078EC`; its final ring snapshot had
  `12288` bytes and `12026` nonzero. A `0x300` target slot leaves at most
  `11520` nonzero bytes outside itself, so at least `506` bytes of the exact
  `0x168850` slot were nonzero. This selects aggregate `H-PortOnlyZeroFill`
  and
  refutes slot rotation for the observed pair. The result does not prove
  game intent and authorizes no writeback or mitigation.

- **s2308 — dynamic-slot writer provenance.** The initial driver capture was
  postprocessing-invalid because it stopped the oracle before its shutdown
  summaries and used non-portable AWK hex bounds. The corrected same-run
  capture passed the retail whole-RDRAM control (`10,000`), title/hangar
  origins, both target-range write summaries (`768` each), and a phase writer
  histogram; the port reached title/hangar and retained 45 seconds. The
  complete ring table found that the nonzero phase-10 pair had rotated to
  `0x167C50` (`2B9E9631`, `nz=621`) and `0x167F50` (`6ADD4218`, `nz=639`).
  Stage events `9386/9388` were followed by exact source/consumer events
  `9467/9468` and `9469/9470`, respectively. Subsequent rows at those same
  destinations were `F59C39C5`/`nz=0`; their writer snapshots were
  `writer_kind=image-dma`, `writer_pc=0`, callsite `0x8008EE84`, with the
  image-DMA write sequence advancing after the exact pair. This is a
  single-source port result that rules out an image-publication gap and a
  ring-role mismatch for the observed pair; it established the port-side
  image-DMA zero-fill behavior but not its retail polarity or game intent.
  The independent oracle confirms active retail writes in the watched PCM
  ring and target phase, but its fixed two-slot controls did not cover the
  dynamically selected `0x167F50` pair; s2309 supplied the missing whole-ring
  evidence.

- **s2307 — cross-phase payload tuple mismatch.** The fixed same-run capture
  passed retail whole-RDRAM `10,000`, title/hangar, and all three target
  writer-PC controls, and the port reached title/hangar with 45-second
  retention. Its two nonzero phase-10 stage rows were
  `0x167650`/`0x300`/`2B9E9631`/`nz=621` and
  `0x167950`/`0x300`/`6ADD4218`/`nz=639`. The cross-phase table retained
  `1,251` width-512/`0x006AB400` PCM rows and found zero exact source or
  consumer matches for either stage row. An independent raw-log recount found
  `38` same-destination PCM rows for `0x167650` and `40` for `0x167950`, all
  `F59C39C5`/`nz=0`; the postprocessor summary independently reported
  `19/19` and `20/20` source/consumer mismatches. This selects
  `H-PayloadTupleMismatch` for the observed rows, rules out
  `H-CrossPhaseExact` at this scope, and does not authorize a contract change.

- **s2306 — recurrence and destination payload summary.** The fixed same-run
  capture passed retail whole-RDRAM `10,000`, title/hangar, and all three
  target writer-PC controls; the port reached title/hangar and retained 45
  seconds after hangar. Its two nonzero phase-10 rows both matched exact DMA:
  `0x168550`/`0x300`/`60F910DE`/`nz=621` remained without exact source or
  consumer in the retained phase, while `0x168850`/`0x300`/`7B70923A`/`nz=639`
  matched both at ordinal `+12` with valid ordering. The per-destination table
  reported `stage-only` for the first and exact source/consumer for the
  second, plus one same-destination zero-payload mismatch flag for each
  endpoint on the second. This selects `H-StageUnconsumed` at the observed
  phase scope and leaves cross-phase attribution open.

- **s2305 — bounded temporal task→stage→PCM join.** The same-run retail
  whole-RDRAM `10,000`, title/hangar, and target writer-PC controls passed, as
  did the port title/hangar gates. Both nonzero phase-10 stage rows had exact
  DMA (`2/2`). The `0x166450`, `0x300`, `2B9E9631`, `nz=621` row had no exact
  source or consumer tuple within `±64` or anywhere in the retained phase;
  native joining reported `stage-only`. The `0x166750`, `0x300`, `6ADD4218`,
  `nz=639` row matched source and consumer ordinal `12` (`delta=+12`) with
  DMA-before-source and source-before-consumer; native joining reported
  `stage-consumer-match`. This selects `H-StageUnconsumed` for the observed
  pair, rules out `H-OrdinalWindowTooNarrow` for the first row, and does not
  authorize a contract or mitigation change.

- **s2302 — C88 route coverage.** Retail passed whole-RDRAM `10,000`, title,
  hangar, and all-eight transfer-PC controls. Port C88=0 reached the initial
  `640 @ 0x00696100`, emitted positive fingerprint rows, settled at
  `route_state=2`, `b40=1`, `key_on=0`, and bus-crashed at guest PC
  `0x8000834C` before title/hangar. The required hangar gate withheld C88=1.
  This is `H-CoverageInvalid` at recipe scope; it does not select a C88 route,
  pointer/data, branch-state, key-on return, or mitigation.
- **s2304 — task→stage→PCM ordinal join.** The fixed capture passed retail
  whole-RDRAM `10,000`, title/hangar, and target writer-PC controls, and the
  port reached title/hangar. Its complete nonzero phase-10/hangar table had
  two image-stage rows (`0x168E50`/`0x169150`, `0x300`, `nz=621/639`). Both
  matched exact same-ordinal DMA tuples; neither matched a same-ordinal PCM
  source or consumer (`2/2`, `0/2`, ordering `NA`). Native image joining
  independently reported both as `stage-only`. Its exact two-row result is
  retained for that capture, but s2305 found a different phase-10 pair with
  one complete temporal join; the `0/2` same-ordinal result is not a
  route-wide output conclusion.
- **s2301 — task/output sequence.** The fixed retail capture passed whole-RDRAM
  `10,000`, title, hangar, and `1,530` width-aware target VI rows. The retained
  sequence had `48` sentinel rows from `0x80094648`, then adjacent same-tuple
  rows from `0x8008EB8C` and `0x8008EBBC` at
  `0x141AD0 = 0x120E0000`; the independent writer histogram matched `48/1/1`.
  This selects `H-SharedSequence` at the measured span. A shorter control run
  had no target rows and was treated as coverage-invalid.
- **s2291–s2300 — retail boundary.** Retail metadata can publish the same
  destination pointer and `0x300` length as a port image tuple, but the retail
  payload-producing writer class differs from the port Factor 5 image-DMA
  edge. Retail writes all 16 candidate `0x300` slots from `0x166450` through
  `0x169150` via `0x800078EC`; none is written in the hangar target phase.
  The independent task/output span `0x141AD0:0x141AF0` instead exposes the
  target writer family `0x8008EB8C`, `0x8008EBBC`, and `0x80094648`. Sentinel
  filtering, phase latching, and the extended sequence capture resolved the
  row-cap artifacts but did not assign semantic roles. This selects
  `H-RetailDifferentWriter` plus `H-SharedSequence` at their measured scopes.
- **s2290 — default image arm.** Corrected explicit keycode-36 Start delivery
  and a hangar gate qualified both the silent stub and default image arms.
  The default target window contained nonzero image payloads with `nz=621` and
  `nz=639`; the stub had no image-stage rows. This qualifies the default at
  recipe scope, not a new writer or mitigation.
- **s2287–s2289 — retail route.** Independent retail controls passed and
  retail executed the equivalent initial-640 slot route (`110` iterator,
  `2` inner, `5` batch rows), while the exact port crash PCs were absent.
  This closes the narrow hypothesis that retail omits slot dispatch, without
  identifying the port callback/list state.
- **s2283–s2286 — A1 route.** Four-arm and corrected two-wave VI matrices
  passed their positive controls but failed in the same initial width-640
  route before either target origin. Logger removal changed the crash PC but
  did not restore coverage. These are route-invalid/route-intrinsic recipe
  observations, not VI-publisher or audio-writer conclusions.
- **s2272 — qualified output.** A corrected staggered pair kept both arms
  qualified through title/hangar. Two nonzero phase-10 rows each matched PCM
  source and consumer tuples with source-before-consumer ordering and no
  stage-only or ordering-violation rows. Earlier paired failures were
  route-invalid and do not overturn this result.

## Active backlog

Closed investigations are not active work items. This is the single monotonic
sequence; #1 is the next work unit.

1. **M5 audio de-stubbing — active.** `docs/M5-AUDIO-PLAN.md` is the design
   gate and inventories the live stubs, traps, gates, and validation sequence.
   s2327 selected `H-PreEvents-EarlierTick`: the image task and PCM contract
   are live, but the observed slot/key-on rows belong to the prior audio route.
   s2328's corrected A/B applied the existing s1993 gate and found both image
   arms qualified with identical normalized target lifecycle rows. The gate
   remains default-on; the image arm remains the qualified default.
2. **M5 destination-to-slot/key-on contract — active.** The corrected drain
   A/B does not explain the missing post-ordinal slot consumer: both image
   arms still have zero same-ordinal slot/key-on/descriptor rows. Use a new
   destination-role discriminator; do not add writeback, guards, slot values,
   or defaults.
3. **M5 task/output contract — closed at the current discriminator.** s2325
   supersedes the undifferentiated task/output gap with
   `H-Destination-Role-Skew`; revisit only if the destination-to-slot table
   cannot classify the split. Retail status/zeroing is independently closed.
4. **M5 A1 second-origin transition — parked.** Resume only with a new
   discriminator that restores `0x00696100`/`0x00696600` coverage; do not
   repeat the failed four-arm/two-wave matrix.
5. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator; do not chase a single recurring crash.
6. **Hangar visual artifact — parked.** Malformed-triangle H2 and consumer
   mode H1 are refuted. H3 is unavailable because the oracle cannot
   screenshot the LLE path; do not repeat the capped `0xD60` scan.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route table selects `LLE_UNGATED=1, LLE_SOLO=1`: the `11` arm
reaches title and hangar, `01` reaches title only, and `10`/`00` reach neither.
Menu spin yield is a diagnostic route aid, not a default behavior change.
Factor 5 command mappings and independent-ground-truth requirements live in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null.

### M5 audio and image output

`docs/M5-AUDIO-PLAN.md` inventories the active audio stubs, traps, gates, and
the incremental task→DMA→service→slot→voice→PCM validation sequence. Direct
service entry/exit, the service gate/loop, and the task/AI boundary are live
on the port. Retail now independently matches a complete slot-0
`01/02/03/00` status cycle at `0x00154620`, with nonzero stores by
`0x8009B214`/`0x8009B6F8` and later `03/00` stores named by detail rows.
The port still has no valid slot/descriptor/key-on transition, so this closes
retail lifecycle semantics but not the port key-on contract. MORT
speech is separate from Factor 5 RSP audio. The complete
s2315 retail census found positive callback coverage but no phase-attributed
`0x800078EC` writer row in any of fifteen observed VI-origin buckets. The
s2316 ground-truth gate/task/wait checkpoint passed its oracle controls, but
both port arms crashed before hangar and its port contract logging was not
enabled. The s2317/s2318 repaired pair restored both port hangar phases. s2318
found earlier-origin retail gate/task writers, including the shared
`0x8008EC88` writer class, but no wait-field writer. s2319 found task/DMEM/
DMA/PCM progress without a valid port slot transition; s2320 found lifetime
and target-phase writes to four of five candidate active bytes, but all
sampled status top bytes were zero and the port remained at its sentinel
key-on with no slot/descriptor rows. s2321 phase-keyed the named writers and
found target top-byte counts `00=21`, `01=0`, `02=0`, `03=1`, `3F=2`, while
earlier-origin samples included `01=3` and `02=3`. The next boundary is
s2322's detail join then found target top-byte counts `00=30`, `01=3`,
`02=2`, with all five target nonzero-status rows at `0x00154620` owned by
`0x8009B214`/`0x8009B6F8`; the independent target histogram named both.
s2323's phase-keyed status poll then recorded three complete target cycles and
the detail table named `0x8009B7CC`/`0x8009B7EC` for the `03/00` tail. The next
boundary is the port destination-role-to-slot contract. s2324's same-build
checkpoint now proves the image arm performs real DMEM/DMA work and can
produce a nonzero PCM join, but still records no port slot/descriptor/voice
transition. s2325 splits the rotating target destinations into one stage-only
row and one exact source/consumer row, but still finds no port slot/descriptor/
voice/key-on row. No gate, wait, status, slot, writeback, or default change is
authorized.

s2326 adds the first signed pre/post destination-to-slot table. Its two target
destinations are both stage-only in this capture. Their shared pre-stage rows
include five `musyxRenderVoiceSamples` slot stores and one unarmed sentinel
key-on row; no corresponding post-stage row exists. Because the filter/voice
probe's positive control did not fire, voice/filter absence remains
unqualified. The result selects `H-Missing-Descriptor-Contract` only for the
observed capture and leaves same-task ownership of the pre-stage rows open.
s2327's task-ordinal join assigns those rows to the prior audio route, not the
target task; the remaining question is the missing post-ordinal
destination-to-slot consumer, not a writeback or guard. s2328's corrected
drain-tick A/B independently gated the existing injection (`en=1` versus
`en=0`); both image arms retained title/hangar, task/DMA/image/PCM and guest
receive controls, with two target rows, zero same-ordinal lifecycle rows, and
the same prior-route lifecycle signature. This selects `H-DrainRedundant` at
capture scope and leaves the destination-role boundary open.

The image arm changes DMEM, completes, and emits generated DMA. Qualified
phase-gated captures show a rotating mixed output contract: s2306 had one
stage-only row and one source/consumer join at ordinal `+12`, s2307 found two
fixed-address zero-payload mismatches, s2308 found a nonzero pair with exact
source/consumer publication followed by later same-destination image-DMA
zero rows, and s2309 found a retail polarity mismatch for the observed
physical pair. The image-stage and port-side zero writers are known;
`H-PortOnlyZeroFill` is selected at that capture scope, while game-level
legitimacy and the stage-only row remain open. The silent arm's PCM boundary
is separately qualified but all-zero. Retail writes corresponding field
spans and a different task/output span. This is a measured contract
boundary, not permission to add a copyToRAM/CIMG writeback, writer guard,
slot guard, consumer change, or address remap.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-`VI` arms recover the
split, but the natural host publisher and cadence are unidentified. The A1
matrices were route-invalid and do not select any VI arm.

### Key-on, M3, and M4

Retail reaches the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with divisor
`0xC0` and no guard hits. Exact `(origin,width,PC)` tuple buckets differ in
both directions. A qualified port pointer/source/state witness exists, but
retail raw addresses vary and the common target window for a full join is
not currently restored. The `-0x25A4` pointer-chase, six-site PIC,
ten-site audio-slot, slot-dispatch, two-line overlay-move, and leftover
`fake_func_*` size-class audits are closed at their stated scopes.

## Superseded conclusions

The following were believable before qualified route and independent controls,
but are superseded at their measured scopes:

- The old overlay/menu explanation, “640 is intrinsically flaky,” missing
  input/wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- s2190–s2197 second-origin/caller explanations that were coverage artifacts;
  the open boundary is host VI-state publication/cadence.
- s2228 detail-ring and s2242–s2259 image/pair crash splits as intrinsic
  image or writer defects; they are intermittent route-load observations.
- s2283/s2284 A1 matrices as evidence against a particular VI publisher;
  both lacked target-origin coverage.
- s2288's stub-first route conclusion as a default/audio-null result; s2290
  supplied explicit input and qualified both arms.
- The logger-removal explanation from s2286; removing the logger changed
  timing/PC but did not restore the target route.
- s2320's broad `H-Retail-Zero-Only-After-Arming` result. It was believable
  because the valid capture's generic post-value samples all had top byte
  `00`, but s2321's requested-writer table found `01/02` values outside the
  target bucket. The narrower target-phase zero result remains valid; the
  broad zero-only conclusion is superseded by `H-Retail-Earlier-Nonzero`.
- s2321's target-phase absence and `H-Retail-Earlier-Nonzero` selection. It
  was believable because that valid run had `24` target rows with no `01/02`
  values and `54` earlier-origin rows containing them. s2322's same-recipe
  capture recorded five target `01/02` rows at `0x00154620`, owned by
  `0x8009B214`/`0x8009B6F8`, with an independent target phase histogram for
  the same writers. The new target-presence result does not establish a
  complete `01/02/00` slot lifecycle.
- s2304's two-row `0/2` same-ordinal PCM gap as a route-wide output result;
  s2305's corrected guest-address normalization and independent native join
  found one `+12` source/consumer pair in a different observed tuple class.
- s2307's fixed `0x167650`/`0x167950` addresses as stable target slots;
  s2308's complete ring table observed the nonzero pair at
  `0x167C50`/`0x167F50` instead.
- s2308's port-only zero-fill observation as evidence of retail-normal
  polarity; s2309's independent whole-ring snapshot shows nonzero data in
  the observed physical slot at the same capture scope.
- s2309's claim that its phase writer histogram proved retail target-phase
  polarity. Its log had active phase VI coverage but no
  `writer-pc-phase ... pc=` rows; only the lifetime ring writer was
  positive. s2310's corrected dual-512 run reproduced that distinction. The
  s2309 aggregate whole-ring/final-snapshot evidence remains valid, but it
  cannot establish target-phase publication.
- s2311's `H-RetailOtherPhase` selection was a candidate-gap result based on
  two unmeasured post-title origins. s2312 measured both with positive VI
  controls and no phase writer rows, so that selection is superseded by
  `H-Retail-Earlier-Or-Unattributed`; the earlier 640-origin gap remains open.
- s2322's open status-lifecycle boundary was believable because its detail
  table established target `01/02` ownership but not a return to zero. The
  s2323 status poll observed three target `01 -> 02 -> 03 -> 00` cycles and
  the detail table named the later `03/00` writer pair, so retail lifecycle
  semantics are now closed; the port-side slot/key-on gap remains separate.
- s2324's undifferentiated downstream task/output gap was believable because
  it had one stage-only nonzero row and one occasional exact PCM join but no
  destination-polarity table. s2325's same-run target table found one
  stage-only destination and a different destination with exact source and
  consumer events, so the active conclusion is the narrower
  `H-Destination-Role-Skew` at capture scope.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical addresses and must
  be phase-gated by VI callbacks.
- A null is worthless without a same-run positive control. Batch every arm and
  counter in one build/run, scope budgets to the phase, and use VI gates rather
  than elapsed time for animated scenes.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
