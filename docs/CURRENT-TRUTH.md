# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background and archived lineages are in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
exact run recipes and evidence remain in the append-only ledger and scratch
artifacts. This file is intentionally compact and is the required pre-work
read.

Current maintenance marker: Session 3196 (2026-08-29).

Session 3197 advanced the generated-symbol sweep by classifying the invalid
data-decoded split at `0x800A2924` as `data_gap_800A2924`. The regeneration-
safe helper synchronized the generated body, header, and overlay registration;
no runtime behavior changed. Evidence:
`scratch/agent/s3197_generated_symbol_rename.md`.

Session 3196 advanced the generated-symbol sweep by classifying the invalid
data-decoded split at `0x800A2790` as `data_gap_800A2790`. The regeneration-
safe helper synchronized the generated body and header; no runtime behavior
changed. Evidence: `scratch/agent/s3196_generated_symbol_rename.md`.

Session 3195 advanced the generated-symbol sweep by classifying the invalid
data-decoded split at `0x800A2558` as `data_gap_800A2558`. The regeneration-
safe helper synchronized the generated body and header; no runtime behavior
changed. Evidence: `scratch/agent/s3195_generated_symbol_rename.md`.

Session 3194 advanced the generated-symbol sweep by classifying the invalid
data-decoded split at `0x800A23BC` as `data_gap_800A23BC`. The regeneration-
safe helper synchronized the generated body, header, and callsite; no runtime
behavior changed. Evidence:
`scratch/agent/s3194_generated_symbol_rename.md`.

Session 3193 advanced the generated-symbol sweep by classifying the invalid
data-decoded split at `0x800A2218` as `data_gap_800A2218`. The regeneration-
safe helper synchronized the generated body, header, and callsite;
no runtime behavior changed. Evidence:
`scratch/agent/s3193_generated_symbol_rename.md`.

Session 3192 ran the M5 Step 1 same-build image-versus-silent qualification.
The independent retail oracle passed its whole-RDRAM positive control and
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` before the
port arms launched. Both port arms then passed the dispatch selector control
(`real_ucode=0` versus `1`) and reached only pre-title VI 640
(`0x0066A500`); neither reached title or hangar before the harness killed the
pair. Consequently target-phase task/DMA/service/slot/voice/PCM nulls are
unevaluable, selecting `H-BothPreTarget`; no audio behavior or mitigation is
authorized. Evidence: `scratch/agent/s3192_m5_step1_contract_pair.md`.

Session 3191 advanced the generated-symbol sweep by classifying the invalid
data-decoded split at `0x800A2114` as `data_gap_800A2114`. The regeneration-
safe helper synchronized the generated body, header, and overlay registration;
no runtime behavior changed. Evidence:
`scratch/agent/s3191_generated_symbol_rename.md`.

Session 3190 advanced the generated-symbol sweep by classifying the split
record at `0x80045024` as `data_gap_80045024`: its body starts at an internal
label below the record address, has no callable prologue, and has no companion
symbol. The regeneration-safe helper mapping synchronized the body, header,
and overlay registration; no runtime behavior changed. Evidence:
`scratch/agent/s3190_generated_symbol_rename.md`.

Session 3189 advanced the generated-symbol sweep by mapping the invalid
unconditional-jump split at `0x80029270` from `static_3_80029270` to
`data_gap_80029270`. The generated body, declaration, and overlay registration
were synchronized; no companion semantic symbol or generated callsite exists.
Evidence: `scratch/agent/s3189_generated_symbol_rename.md`.

Session 3188 advanced the generated-symbol sweep by mapping the invalid
two-instruction split at `0x8009D8BC` from `static_3_8009D8BC` to
`data_gap_8009D8BC`. The generated body and header now agree; the record has
no callable prologue or companion semantic symbol, so this is a mechanical
data-gap name only. Evidence: `scratch/agent/s3188_generated_symbol_rename.md`.

Session 3187 synchronized the remaining stale generated reference for
`0x800027B8`: the generated body is `data_gap_800027B8`, and the helper
renamed its `funcs.h` declaration and overlay-table entry from
`fake_func_800027B8`. No runtime behavior changed.

Session 3186 completed the bounded generated-symbol sweep for
`0x801B0000..0x801C0000`. The required-rename helper selected zero generated
references and returned its expected no-rename error; independent searches
found no placeholder occurrence or definition in the interval, and the
companion symbol files had no record there. The only textual generated-tree
hit was an unrelated jump comment outside the function-address interval. The
band is closed without a semantic rename. Evidence:
`scratch/agent/s3186_generated_symbol_sweep.md`.

Session 3185 revisited the external retail-entry boundary with a new
independent oracle census of `bufferArbiterProducerScanWait` (`0x8000BF60`)
alongside `bufferArbiterProducerMark` (`0x8001BCE4`). The whole-RDRAM control
fired 10,000 times and the retail route reached title `1024 @ 0x00790400`
and hangar `512 @ 0x006AB400`. The wait routine executed in both target
phases, with predecessors `0x800C5CEC` (title) and `0x800B24E8` (hangar);
ProducerMark remained dominated by `0x8000C628`. This selects
`H-wait-route` and refutes `H-mark-only` for the tested retail route. It is
single-source oracle evidence only: no port arm ran and no port mismatch is
proved. Evidence: `scratch/agent/s3185_retail_producer_wait/RESULTS.md`.

Session 3184 completed the bounded generated-symbol sweep for
`0x801A0000..0x801B0000`. The required-rename helper selected zero generated
references and returned its expected no-rename error; independent searches
found no placeholder occurrence or definition in the interval, and the
companion symbol files had no record there. The band is closed without a
semantic rename. Evidence:
`scratch/agent/s3184_generated_symbol_sweep.md`.

Session 3183 completed the bounded generated-symbol sweep for
`0x80190000..0x801A0000`. The required-rename helper selected zero generated
references and returned its expected no-rename error; an independent
generated-definition search found no placeholder body in the interval. The
band is closed without a semantic rename. Evidence:
`scratch/agent/s3183_generated_symbol_sweep.md`.

Session 3182 completed the bounded generated-symbol sweep for
`0x80180000..0x80190000`. The required-rename helper selected zero generated
references and returned its expected no-rename error; an independent
generated-definition search found no placeholder body in the interval. The
band is closed without a semantic rename. Evidence:
`scratch/agent/s3182_generated_symbol_sweep.md`.

Session 3181 completed the bounded generated-symbol sweep for
`0x80170000..0x80180000`. The required-rename helper selected zero generated
references and returned its expected no-rename error; an independent
generated-definition search found no placeholder body in the interval. The
band is closed without a semantic rename. Evidence:
`scratch/agent/s3181_generated_symbol_sweep.md`.

Session 3180 completed a bounded generated-symbol sweep across two concrete
data-gap records. The regeneration helper renamed `static_3_80007064` to
`data_gap_80007064` and `fake_func_800AE3E4` to `data_gap_800AE3E4`; the latter
is the first two COP1 instructions before the named body at `0x800AE3EC`.
Generated header/body/overlay references were synchronized. This is a
source-only naming change with no runtime behavior change. Evidence:
`scratch/agent/s3180_generated_symbol_rename.md`.

Session 3179 completed the bounded generated-symbol sweep for
`0x80160000..0x80170000`. The required-rename helper selected zero generated
references and returned its expected no-rename error; an independent
generated-definition search found no placeholder body in the interval. The
band is closed without a semantic rename. Evidence:
`scratch/agent/s3179_generated_symbol_sweep.md`.

Session 3178 completed the bounded generated-symbol sweep for
`0x80150000..0x80160000`. The companion census selected two ambiguous/fake
records and three already-synchronized symbols; the required-rename helper
changed zero references and returned its expected no-rename error, while an
independent generated-definition search found no placeholder body in the
interval. The band is closed without a semantic rename. Evidence:
`scratch/agent/s3178_generated_symbol_sweep.md`.

Session 3177 completed the bounded generated-symbol sweep for
`0x80140000..0x80150000`. The companion census visibly selected
`0x80149470 aspTask` as already synchronized; the required-rename helper
changed zero references and returned its expected no-rename error, while an
independent generated-definition search found no placeholder body in the
interval. The band is closed without a semantic rename. Evidence:
`scratch/agent/s3177_generated_symbol_sweep.md`.

Session 3176 completed the bounded generated-symbol sweep for
`0x80130000..0x80140000`. The companion census visibly classified the
selected records as already synchronized or ambiguous/fake; the required-
rename helper changed zero references and returned its expected no-rename
error, while an independent generated-definition search found no placeholder
body in the interval. The band is closed without a semantic rename. Evidence:
`scratch/agent/s3176_generated_symbol_sweep.md`.

Session 3175 completed the bounded generated-symbol sweep for
`0x80120000..0x80130000`. The companion census visibly classified
already-synchronized and ambiguous/fake records; the required-rename helper
changed zero references, and an independent generated-definition search found
no placeholder body in the interval. The band is closed without a semantic
rename. Evidence: `scratch/agent/s3175_generated_symbol_sweep.md`.

Session 3174 completed the bounded generated-symbol sweep for
`0x80110000..0x80120000`. The companion census selected only synchronized or
ambiguous/fake records; the required-rename helper changed zero references,
and an independent generated-definition search found no placeholder body in
the interval. The band is closed without a semantic rename. Evidence:
`scratch/agent/s3174_generated_symbol_sweep.md`.

Session 3173 completed the bounded generated-symbol sweep for
`0x80100000..0x80110000`. The companion census found no stale semantic
function name, but the generated snapshot contained the invalid-data tail
`static_4_801096D8`; the regeneration helper now maps it to
`data_gap_801096D8`, and the external generated header/body/overlay table
contain two new-name references with no old-name references. The interval is
closed without runtime behavior change. Evidence:
`scratch/agent/s3173_generated_symbol_sweep.md`.

Session 3172 completed the bounded generated-symbol sweep for
`0x800F0000..0x80100000`. The companion census selected only already
synchronized or ambiguous/fake records; the required-rename helper changed
zero references, and the independent generated-definition check found no
stale placeholder definition in the interval. The band is closed without a
semantic rename. Evidence:
`scratch/agent/s3172_generated_symbol_sweep.md`.

Session 3171 completed the bounded generated-symbol sweep for
`0x800E0000..0x800F0000`. The helper classified 16 selected records as
already synchronized or ambiguous/fake, changed zero references, and the
independent generated-definition check found no stale placeholder definition
in the interval. The band is closed without a semantic rename. Evidence:
`scratch/agent/s3171_generated_symbol_sweep.md`.

Session 3170 completed the bounded generated-symbol sweep for
`0x800D0000..0x800E0000`. The companion census classified two records as
ambiguous/fake and found all other candidates already synchronized. The
required-rename helper changed zero references, and the independent generated
placeholder check found no placeholder definitions in the interval. The band
is closed without a semantic rename. Evidence:
`scratch/agent/s3170_generated_symbol_sweep.md`.

Session 3169 completed the bounded generated-symbol sweep for
`0x800C0000..0x800D0000`. The companion census found no stale generated
placeholder with a semantic rename: all callable-shaped candidates were
already synchronized, while fake/data records were ambiguous or already
mechanically named. The required-rename control reported zero changed
references and the band is closed without a new rename. Evidence:
`scratch/agent/s3169_generated_symbol_sweep.md`.

Session 3168 completed the bounded generated-symbol sweep for
`0x800B75D0..0x800C0000`. Every companion-qualified candidate was already
synchronized; the only remaining placeholder in the band,
`fake_func_800B89F4`, is explicitly fake/data and remains unchanged. The
helper changed zero references, closing this band without a new semantic
rename. Evidence: `scratch/agent/s3168_generated_symbol_sweep.md`.

Session 3167 completed a bounded M3 audit of `musyxMixActiveVoices`'s complete
`0x88`-stride voice-record access class. All six indexed accesses share the
same loop index; `initN64RspMixer` clamps the published voice count to `0x20`,
and the mixer loop proves indices `0..31`. Three reachable callers were
enumerated. Companion symbol metadata and the companion ELF independently
confirm the named bodies and addresses. This selects `H-M3-Proven`; no guard,
audio behavior, or generated source changed. Evidence:
`scratch/agent/s3167_m3_musyx_mix_active_voices_audit.md`.

Session 3166 completed a bounded generated-symbol sweep pivot. The external
generated snapshot had one remaining callable-shaped placeholder at
`0x800B75C4`; companion metadata classifies its 12-byte record as a
non-callable mission-overlay fragment between named bodies. The regeneration
helper now maps `fake_func_800B75C4` to `data_gap_800B75C4`, and the project
symbol table plus generated header/body/overlay table were synchronized. The
three-reference helper run changed exactly those generated records; ambiguous
placeholder records were not touched. This is source-only and does not alter
runtime behavior.

Session 3165 completed the bounded static M3 audit of the
`musyxStoreVoiceAdsrParams` voice-index producer edge. The sole callsite loads
the owning record's `+0x67` byte without a local range check; the complete
generated writer inventory found no connected record-relative `+0x67` writer or
recovered indirect/data producer. Companion metadata independently confirms
the named caller/callee and `0x88` voice-slot layout. This selects
`H-M3-Unclassified`, not proof of a retail-invalid index; no guard or audio
behavior change is authorized. Evidence:
`scratch/agent/s3165_m3_musyx_store_voice_index_producer_audit.md`.

Session 3164 completed the bounded static M3 audit of the unresolved
`stopVoicesByHandle` handle producer edge. All four direct callers load the
same linked-list node `+0x8` field; the sole identified writer is
`allocVoiceHandleNode:0x80086518`, which copies unconstrained `$a3`. No direct
or recoverable indirect dispatch edge to the allocator was found. Companion
symbol metadata and the companion ELF independently confirm the named bodies
and addresses. This selects `H-HandleUnclassified`: not proof of a retail
invalid handle, and no guard or audio behavior change is authorized. Evidence:
`scratch/agent/s3164_m3_stop_voices_handle_producer_audit.md`.

Session 3163 completed the bounded static M3 audit of
`musyxTriggerVoiceAttack`'s complete voice-indexed `0x88`-stride access set.
Both reachable callers were enumerated: the tick caller's 32-entry loop proves
`0..31`, while the streamed caller passes `stopVoiceByKey`'s result with only a
local `!= -1` check. Session 3162 independently proves that producer returns
`0..31` or `-1`, but the callee itself masks to 16 bits and checks only the
`0x801496F8` base pointer. The class selects `H-M3-Unclassified` from
generated control flow plus companion symbol/ELF metadata. No guard, audio
behavior, generated source, build, or run changed. Evidence:
`scratch/agent/s3163_m3_musyx_trigger_voice_attack_audit.md`.

Session 3162 completed the bounded static M3 producer audit for
`stopVoiceByKey`'s result. Its sole generated caller is
`startStreamedSampleVoice`; the result comes from `allocateSynthVoice`, which
scans `D_80141AD0`. The complete generated writer inventory shows both writers
validate `<0x21` and otherwise store `0x20`, proving successful results are
`0..31` and failure is `-1`. This selects `H-M3-Proven` from generated control
flow plus companion symbol/ELF metadata and closes that producer edge. No
guard, audio behavior, generated source, build, or run changed. Evidence:
`scratch/agent/s3162_m3_stop_voice_by_key_producer_audit.md`.

Session 3161 completed the bounded static M3 audit of
`musyxTriggerVoiceAttack`'s voice-indexed `0x88`-stride record accesses. The
tick caller is range-proven through the companion's 0x20-channel array, but
the streamed caller passes `stopVoiceByKey`'s result with only a `!= -1`
check; the available producer flow does not prove `0..63`. This selects
`H-M3-Unclassified` from generated control flow plus independent companion
symbol metadata. No guard, audio behavior, generated source, build, or run
changed. Evidence: `scratch/agent/s3161_m3_musyx_trigger_voice_attack_audit.md`.

Session 3160 closed the bounded generated-symbol sweep lead for
`0x800A0000..0x800B0000`. Fourteen placeholders remain: thirteen
`static_3_*` records have generated bodies and one generated caller each but
no companion semantic name, and `0x800AE3E4` is explicitly a companion
`fake_func_*` record. The bounded rename helper selected zero new mappings.
This selects `H-AmbiguousFragments` from the generated snapshot plus the
independent companion symbol files; no placeholder or runtime behavior was
changed. Evidence: `scratch/agent/s3160_generated_symbol_census.md`.

Session 3159 reopened the regeneration-safe generated-symbol sweep for a
bounded callable batch. The external generated snapshot had two exact
companion matches that were not in the rename table: `static_5_800AF6AC` is
`handleCraftSelectInput`, and `static_4_800E9B10` is
`initObjectAnimAndDetail`. Each has a generated body and direct caller, and
the companion symbol files independently provide the names and addresses.
The rename helper now carries both mappings, while the external snapshot's
header, bodies, and callsites were synchronized. This is source-only and
does not change runtime behavior. Evidence:
`scratch/agent/s3159_generated_symbol_rename.md`.

Session 3158 completed the bounded static M3 audit of
`musyxStoreVoiceAdsrParams`'s voice-indexed `0x88`-stride record accesses.
The current generated tree has one reachable caller, which passes a byte
loaded from `s5+0x67` without a local `<64` proof, and the callee has four
independent stores with no index check. `allocateSongChannelArray` supports
the `0x801496F8` base/stride interpretation but does not establish the
caller-byte bound. This selects `H-M3-Unclassified` from generated control
flow plus companion symbol metadata; the existing base-pointer guard remains
unchanged and no audio or runtime behavior changed. Evidence:
`scratch/agent/s3158_m3_musyx_store_voice_adsr_audit.md`.

Session 3157 completed the bounded static M3 audit of
`musyxInitVoiceFromSample`'s voice-indexed `0x88`-stride record accesses.
There are two distinct reachable callers: the sound-macro path passes an
incoming `$a0` with no local `<64` proof, while the streamed path passes a
`stopVoiceByKey` result whose available source does not establish the callee's
exact 64-slot bound/lifecycle. The callee's KSEG0 base guard proves only the
`0x801496F8` voice-array base, not the masked 16-bit index. This selects
`H-M3-Unclassified` from generated control flow plus independent companion
symbol metadata; no guard, audio, or runtime behavior changed. Evidence:
`scratch/agent/s3157_m3_musyx_init_voice_index_audit.md`.

Session 3156 completed the bounded static M3 audit of the final 12
`stepActiveSongTracks` readers of `D_801529C0` (`0x801529C0`). All 12 guest
PCs are distinct reachable sites in one function with one epilogue; none is
lowering-only. The sole writer is `tickAllActiveSongs:0x80096D88`, which
publishes `0x8014AA00+s2` before the caller's `stepActiveSongTracks` call, and
the producer's bounded eight-slot loop keeps the value in KSEG0 RDRAM. This
selects `H-M3-Proven` from generated control flow plus independent companion
symbol/ELF metadata and closes item -292's 43/43 reader inventory. No guard,
audio, or runtime behavior changed. Evidence:
`scratch/agent/s3156_m3_step_active_song_tracks_audit.md`.

Session 3155 completed the bounded static M3 audit of the complete
`musyxStopVoice` computed-record `+0x1` producer edge. `s6` starts at zero,
the call precedes its increment, and the only four stores to the loop-count
byte are the two display-mode setters. Each validates `< 0x21` and otherwise
stores `0x20`, proving the call argument is `0..31`. This selects
`H-M3-ValidProducer` from generated control flow plus independent companion
metadata; no guard or audio change is authorized. Evidence:
`scratch/agent/s3155_m3_musyx_stop_voice_index_producer.md`.

Session 3154 completed a bounded static M3 audit of the complete
`musyxStopVoice` computed-record `+0x1` store. The sole generated call passes
`tickAllAudioChannels`'s `s6`; the callee's KSEG0 base check dominates, but
the available callsite flow does not provide a dominating `<0x20` proof.
This selects `H-M3-UnclassifiedProducer` as single-source static evidence,
not proof of a retail-invalid index, and authorizes no guard or audio change.
Evidence: `scratch/agent/s3154_m3_musyx_stop_voice_offset_audit.md`.

Session 3153 ran the prescribed same-build Step 6 policy pair for 30 seconds.
The default and explicit `ROGUESQ_DRAIN_INLOOP_TICK=1` arms both reached the
pre-title VI 640 phase and each emitted eight shade-DMA control rows, but
neither emitted the `[drain-inloop-gate]` positive-control line. Therefore the
policy values are unevaluable: this run does not select default-off versus
policy-bypassed, and it does not authorize any audio, wait, slot, voice, or
PCM conclusion. Evidence: `scratch/agent/s3153_m5_step6_policy_qualification.md`.

Session 3152 completed the Step 6 M5 de-stub policy change. Runtime startup
now centralizes the default for `ROGUESQ_DRAIN_INLOOP_TICK` as unset → `0`,
while preserving an explicit environment value for the control arm. The
regeneration-side `fixup_game_funcs.py` contract now also enables the injected
drain tick only for explicit `=1`; unset and `=0` skip it. The target builds
successfully and the fixup passes Python compilation. This is a source/build
qualification of policy application, not proof of a valid audio task, slot,
voice, or PCM contract. The status-03 wait hatch and all guest writers remain
unchanged.

Session 3151 completed the bounded producer-edge census for
`allocVoiceHandleNode`. The generated call graph and project dispatch metadata
contain no direct call, `jal`, function-pointer table entry, or `get_function`
lookup for `0x80086450`; only the declaration, body, overlay registration, and
symbol record remain. The companion symbol file and ELF symbol table confirm
the body independently, but the available host disassembler cannot decode the
MIPS ELF. This selects `H-HandleIndirectOnly` as a single-source static
classification of an unrecovered producer edge, not proof of a retail invalid
handle. No guard or runtime behavior changed. Evidence:
`scratch/agent/s3151_m3_alloc_voice_producer_edge.md`.

Session 3150 completed the bounded M3 handle-writer audit for
`stopVoicesByHandle`. All four callers load the same linked-list node `+0x8`
field, ruling out a caller/field mismatch. The sole identified voice-node
`+0x8` writer is `allocVoiceHandleNode` at `0x80086518`, which copies
unconstrained `$a3`; its node-allocation counter is separate from the stored
handle. No direct generated callsite to this allocator is present, so the
producer edge cannot establish `0..0x1F`. This selects
`H-HandleUnbounded` as a single-source static contract classification, not
proof of a retail invalid value. No guard or runtime behavior changed.
Evidence: `scratch/agent/s3150_m3_stop_voices_handle_writers.md`.

## Current state

The native port builds and boots. With the validated spin-yield route and
Factor 5 LLE-only path it reaches attribution, the N64 logo, intro cinematic,
star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`). Hangar visuals still have geometry/color artifacts. Yield is
default-off. Audio is not production-complete: the Factor 5 image task is the
qualified audio arm, while the `musyx_stub`/Broke path is the silent control.

Recent M5 route captures stop at pre-title VI 640 (`0x0066A500`), although
independent retail runs pass a whole-RDRAM positive control and reach title and
hangar. Therefore target-phase audio/task/DMA/service/slot/voice/MORT/PCM
nulls from those port captures are unevaluable. No audio gate, wait, voice
guard, output destination, or VI behavior may be changed without a named
legitimate writer and an ordering edge.

Session 3141 resolved the source block locally: the companion project already
has a non-stripped generated ELF at
`/Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf`.
Its symbol table contains the exact retail bodies for `osViSetMode`
(`0x800352D0`, `0x70`) and `__osViSwapContext` (`0x80035550`, `0x360`). The
companion C files remain `INCLUDE_ASM` stubs, but this ELF is generated from
the retail ROM/symbol inputs and is explicitly consumable by N64Recomp. The
prior source block was therefore a missed local artifact, not a human-only
dependency. No runtime behavior changed.

Session 3142 decoded both local ELF bodies and selected a new publication
edge. `__osViSwapContext` contains the known origin store at `0x80035788` and
width store at `0x80035798`, then the distinct post-width VI-register store at
`0x800357A8`. A corrected independent retail oracle run passed the
whole-RDRAM positive control (10,000 writes), reached title 1024 and hangar
512, and executed all three PCs in the target-phase streams. This selects
`H-ELFExposesNewEdge` from two sources (ELF decode and retail attribution); no
port, audio, or route behavior changed. Evidence:
`scratch/agent/s3142_m5_retail_elf_boundary.md`.

Session 3143 added the phase-scoped host witness immediately after the
`VI_WIDTH_REG` write, corresponding to retail ELF edge `0x800357A8`. In one
controls-positive port capture it emitted 8 all-width edge controls, while
the existing VI-context and host voice-audit controls emitted 8 and 1 rows.
The port reached only pre-title `640 @ 0x0066A500`, with zero title `1024`,
hangar `512`, or target-edge rows and no crash/abort. This selects
`H-AudioRouteStillBlocked`; target parity and downstream audio nulls remain
unevaluable, and no audio, route, or VI behavior changed. Evidence:
`scratch/agent/s3143_m5_port_vi_edge.md`.

The earlier callable-placeholder sweep was believed closed after the known
`func_0x...` and ambiguous-fragment review, but Session 3159 found two
`static_*` callable records outside that inventory. The active sweep now
continues only for exact companion-qualified callable matches; the
`0x800A0000..0x800B0000` lead is exhausted and ambiguous fragments remain
preserved. The next active engineering prerequisite is a new retail-grounded
M5 boundary once the current M3 idiom audit queue is exhausted.

Session 3145 tested the block's claimed dependency instead of accepting it on
precedent. The documented LLE-only/spin-yield/autopilot route was run directly
from the current Debug binary with the existing phase control. Host input
controls fired eight times, and the port reached only VI 640 at
`0x0066A500`; the 1024 phase gate timed out after 60 seconds. The suspected
`ROGUESQ_M4_Y8000_WIDTH=512` setting is probe-only: source inspection shows it
changes the M4 logging width and cannot change route control flow. The dirty
submodules contain existing broad patches but no selected route arm. This
provides a same-run port line of evidence that the M5 target-phase dependency
is real for the current recipe, while not identifying its upstream cause.
The work was re-scoped to a bounded M3 idiom-class audit; no runtime behavior
was changed. Evidence: `scratch/agent/unblock_route_probe_20260828/`.

Session 3146 completed a bounded M3 NULL-plus-offset audit for the six original
nonzero-offset dereferences through `slotDispatcherIter`'s slot pointer
(`0x8003E944`–`0x8003E9D8`). The pointer is loaded from the global slot table,
tested nonzero at `0x8003E93C`, and remains unchanged through each listed
access; the `+0x1A` stores are legitimate age-field writers in the same
function. The complete static table selects `H-M3-Proven` for this class and
adds no guard or runtime behavior. Evidence:
`scratch/agent/s3146_m3_slot_pointer_audit.md`.

Session 3147 completed the bounded `slotDispatcherInner` slot-pointer audit.
The complete function-body enumeration found five guest sites (`+0x14` at
`0x8003EA60`, `0x8003EAC4`, and `0x8003EAEC`; `+0x18` at `0x8003EAF8`; and
`+0x04` at `0x8003EB48`). All five use the stable `$a0`/`$s1` slot record.
The five generated callers pass their freshly initialized `$s0` record after
inserting it into the global slot table via `popNpcSlotFromTail`; the repeated
host blocks are delay-slot lowering of one guest store. This selects
`H-M3-Proven` for the class: no unclassified reachable dereference or guard
site was found, and no runtime behavior changed. Evidence:
`scratch/agent/s3147_m3_slot_inner_audit.md`.

Session 3148 completed the bounded derived heap/list-pointer audit for the
same function, covering all 30 guest `MEM_*` sites through the record and its
`0x44`/`0x48` links between `0x8003EAE0` and `0x8003EBF8`. The record pointer
is either a nonzero selected global head or the result of the `0x204C`
allocation path. Every nullable list link is tested before use, including
the branch-likely predecessor store and the final unlink loads; the byte
table addresses are interior offsets under the record's initialized index
invariant. This selects `H-M3-Proven` for the complete class and provides no
basis for a guard or mitigation. Static evidence only; no build or runtime
behavior changed. Evidence:
`scratch/agent/s3148_m3_slot_inner_derived_audit.md`.

Session 3149 audited the complete `stopVoicesByHandle` body and all four direct
callsites. The linked-list head, node links, and matched-node `+0xC` access
have local null/data-flow edges. The handle is only masked to 8 bits before a
`0x17C`-stride access into the 32-record active voice table; no local or
caller-side proof bounds it to `0..0x1F`. This selects `H-M3-Unclassified` for
the handle-to-record-index contract. It is single-source static evidence: no
runtime run or guard was added. Evidence:
`scratch/agent/s3149_m3_stop_voices_by_handle_audit.md`.

Session 3144 could not run the queued M5 paired qualification. The required
route change is not present: the current state still records the port stopping
at pre-title VI 640, and the working tree exposes no selected upstream route
change to apply. Repeating the qualification would produce only the already
unevaluable pre-title rows. This blocks the iteration pending a human-selected
route change or an equivalent new retail-grounded boundary; it does not
authorize audio, route, VI, gate, wait, voice, destination, or output changes.
The read-only repository-state check is this iteration's evidence.

Session 3136 completed a bounded generated-symbol synchronization for the
mission-overlay body at `0x800E9AE0`: the external generated declaration and
overlay table now use the companion-qualified name
`func_mission_overlay_800E9AE0`, matching the already-renamed body and the
companion's exact address/overlay record. The two deliberately preserved
ambiguous `fake_func_*` fragments were not changed. This is source-only and
does not alter runtime behavior.

Session 3137 completed a bounded generated-symbol rename for entry address
`0x8000040C`. Its body takes an address and length, advances in 16-byte
steps, and stores two zero doublewords per step; the companion tree's libc
`bzero` placement independently supports the clearing semantics. The rename
`func_8000040C` → `clearMemory16ByteBlocks` was propagated by the regeneration
helper, generated header/body/overlay table, and project TOML. This is
source-only and does not alter runtime behavior.

Session 3138 ran the first M5 Step 1 paired qualification after the prescribed
retail-boundary census again found no defensible new handoff PC. One build
carried image and silent arms concurrently for 90 seconds. Both passed the
dispatch and host-boundary controls and reached pre-title VI 640
(`0x0066A500`), but neither reached title 1024 or hangar 512. The requested
downstream task/service/slot/voice/PCM tags had no usable positive rows, so
their nulls are unevaluable and no audio contract edge is selected. This
selects `H-RouteBlocked` for this route; audio behavior remains unchanged.
Evidence: `scratch/agent/s3138_m5_step1_qualification.md`.

Session 3139 reran the prescribed independent static census for pending VI
state, descriptors, VI setters, swap context, and origin publication. The
available companion executable bodies remain `INCLUDE_ASM` stubs, while the
project tree contains only existing declarations, symbol records, comments,
and already-closed probes. No new transition-capable retail instruction or
restored generated body was found. This selects `H-SourceInsufficient` and
rules out another oracle or port-instrument build for this unit. Single-source
static evidence; no runtime behavior changed. Evidence:
`scratch/agent/s3139_m5_retail_static_census.md`.

## Latest evidence

Session 3116's independent retail-oracle boundary capture passed the
whole-RDRAM positive control and reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. The post-init execution range
`0x8001B7B8:0x8001BB6C` fired throughout the run, including target phases,
but did not provide direct VI-mode-write attribution. This refutes the range
as the missing 640-to-1024 writer while proving it is live. Combined with
Session 3115, the writer remains outside both watched ranges or in a later
handoff. This is single-source oracle evidence; it does not authorize a port
change.

Session 3112 synchronized the mechanically classifiable generated records
`0x800B2628`, `0x800B42BC`, and `0x800B89F4` as `data_gap_*` where appropriate,
and synchronized the stale generated `0x800B42BC` name. No runtime behavior
changed. Session 3110/3111 retail boundary watches passed the positive control
and reached title/hangar, but the `selectAndApplyViMode` plus descriptor-helper
range never executed during the 640→1024 transition. The missing writer is
outside the already watched direct `osViSetMode` callsites and helper range.
These are single-source oracle qualifications; they select an unenumerated
writer but do not identify it.

Session 3117's static audit identified guest PC `0x800C2984` in
`runMenuModelViewerScreen` as a new request-stage handoff: it calls
`requestViFeatureChange(0x11)`, whose first store is the pending word at
`0x80128E90`. This is outside the closed direct `osViSetMode` callsites and
selector range. It is a candidate boundary only; no runtime behavior changed
and retail attribution is still required.

Session 3118's independent retail-oracle capture passed the whole-RDRAM
positive control (10,000 visible writes and 10,000 additional counted writes),
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and executed
`0x800C2984` exactly once at 3.3s during the already-live 640 phase
(`0x0066A500`). It did not execute at the 640-to-1024 transition or in title
or hangar. This rejects the candidate as the target-phase publication
boundary; it is a pre-title request-stage event whose relationship to the
missing writer remains unresolved. This is single-source oracle evidence.

Session 3119's complete static audit of the five remaining
`requestViFeatureChange` callers classified them as mission/cutscene or menu
maintenance, cinematic/player-record teardown, and post-transition hangar
work. None is a target-phase 640-to-1024 publication handoff; the hangar call
is explicitly after `beginSceneRenderFrame`. This selects
`H-AlreadyEnumerated` for this caller family and moves the next retail probe to
the unenumerated handoff between the pending request-mask store and VI
descriptor publication. This is static evidence only and does not identify
the writer. Evidence: `scratch/agent/s3119_m5_vi_request_callers.md`.

Session 3120 corrected the M5 task-contract arm identity in the runtime:
`run_task` now treats an unset `ROGUESQ_AUDIO_UCODE` as the default real
`factor5_ucode_b` image, matching `get_rsp_microcode`; only an explicit `0`
selects `musyx_stub`. The target builds successfully. No game soak was run in
this environment, so downstream phase rows remain unevaluable.

Session 3121's independent retail oracle passed the whole-RDRAM positive
control (18,055 writes), reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`, and watched the pending VI range, all four game VI records, the
final record, and selector bytes in one run. No title-phase write occurred to
the selector or record ranges. The pending range's title rows were only the
known per-frame `0x8001BA80/0x8001BA88` writers; request/clear edges were live
in the 640 and hangar controls. This selects a deferred/outside-consumer
publication boundary for the next retail probe. It is single-source oracle
evidence and does not identify the writer or authorize a port change.

Session 3122's independent retail oracle passed the whole-RDRAM positive
control (10,000 callbacks), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the untested libultra consumer range
`0x80034F38:0x800356AC`. At the 640-to-1024 transition it executed
`viMgrMain` and entered `__osViSwapContext` (`0x80035550`) with the new
`0x00790000` context immediately before the VI trace reported `0x00790400`.
The consumer range was live (1,675,531 executions; 4,604 context swaps).
This selects `H-ConsumerHandoff` and rejects the candidate-set form of
`H-OutsideConsumer`; `__osViNext`'s optional join was empty and is
unevaluable. The result is single-source retail evidence: it authorizes a
port-side parity probe but no behavior change.

Session 3123 built the existing port-side VI consumer probe and ran the
validated spin-yield/F5-LLE image arm for 120 seconds. Its all-width positive
control fired 8 rows, and the consumer committed width 640 continuously, but
the port never reached target width 1024 or hangar width 512. The capture
therefore selects `H-PortConsumerAbsent` only at the route's observed target
phase: no target-phase consumer row exists because the port stopped at 640.
It does not distinguish a missing consumer from an upstream route stop. This
is single-source port evidence; no behavior change is authorized.
Evidence: `scratch/agent/s3123_vi_consumer_capture/run.log`.

Session 3124 ran the paired, phase-keyed M5 route qualification with the
corrected image arm and silent control in one build/window. Both arms passed
the same-run positive controls (nine VI-context control rows and the host
voice-audit control), each dispatched 2,944 audio tasks, and each reached VI
640 but neither reached title 1024 or hangar 512. Image rows identified
`factor5_ucode_b`; silent rows identified `musyx_stub`. This selects
`H-BothPreTarget`: target-phase audio/task/DMA/service/slot/voice/MORT/PCM
nulls remain unevaluable and no audio behavior change is authorized. This is
single-source port evidence; it does not identify the upstream route blocker.
Evidence: `scratch/agent/s3124_m5_route_qualification/summary.txt`.

Session 3125's independent retail oracle passed the whole-RDRAM positive
control (10,000 callbacks), reached title `1024 @ 0x00790400` at 17.3s and
hangar `512 @ 0x006AB400` at 38.4s, and the fixed phase-gated run recorded
post-consumer execution rows in both target buckets (including
`0x800356F4` at title and `0x800358E8` at hangar). The range also reported
3,724,111 hits overall. This rejects a retail-side stop immediately after
`__osViSwapContext` but does not identify the port's pre-target divergence.
This is single-source retail evidence and authorizes an exact phase-gated port
parity probe, not a behavior change.
Evidence: `scratch/agent/s3125_m5_retail_post_consumer/oracle_phase.log`.

The strongest route boundary remains the independent comparison: retail
reaches title at 1024 and hangar at 512, while the recent same-build port
capture issues only widths 320, 2, 640, and 640 and remains at VI 640. The
port's audio-arm dispatch controls are positive in earlier qualified runs,
so a zero target-phase audio row is not evidence of absent dispatch.

Session 3126's phase-gated port parity probe passed both same-run controls:
the VI-context control fired 8 rows and the host voice-audit control fired
once. The port still issued only the pre-title 640 origin and produced zero
rows from the retail-live `0x800356AC:0x80035B00` range; it reached neither
title nor hangar, with no crash or abort. This selects `H-PortConsumerAbsent`
at the observed route, while leaving the upstream pre-640 divergence
unidentified. The range watch is sampled at the existing VI-commit accessor,
so it is not evidence that the full range was executed when the breadcrumb
was stale. This is single-source port evidence; no behavior change is
authorized. Evidence: `scratch/agent/s3126_m5_post_consumer_port/run.log`.

Session 3127's independent retail oracle passed the whole-RDRAM positive
control (10,000 writes), reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`, and watched exact guest PC `0x800356A8`, the final instruction
before the previously qualified `0x800356AC:0x80035B00` continuation. The
candidate executed zero times overall, including both target phases. This
rejects it as the immediate pre-consumer handoff and selects
`H-RetailBoundaryAbsent`; the port divergence remains unexplained. This is
single-source retail evidence and does not authorize a port change.
Evidence: `scratch/agent/s3127_m5_retail_preconsumer/oracle.log`.

Session 3128's independent retail oracle passed the whole-RDRAM positive
control (10,000 visible writes), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the distinct origin-publication instruction
`0x80035788` inside `__osViSwapContext`. The instruction is the store to
`VI_ORIGIN_REG`; the previously watched `0x80035798` is the subsequent width
store. The candidate executed 2,569 times overall and fired in both target
phases, with title `v0=0x00790000` and hangar `v0=0x006AB000`. This selects
`H-NewStaticHandoff` and authorizes a port-side parity probe at the origin
publication edge. It is single-source retail evidence and does not authorize
an audio or route behavior change. Evidence:
`scratch/agent/s3128_m5_retail_origin_publish/AUDIT.md`.

Session 3129's port-side parity probe instrumented the host equivalent of the
retail `0x80035788` origin publication: `update_vi` immediately before its
`VI_ORIGIN_REG` store. The same run emitted eight bounded origin-publication
control rows, eight VI-context control rows, and one host voice-audit control.
It reached only pre-title VI 640 (`0x0066A500`), emitted zero target
publication rows, and reached neither title nor hangar; no crash or abort was
observed. This selects `H-PortPublicationAbsent` for the observed route and
places the divergence upstream of the VI consumer/publication edge. It does
not identify the upstream writer, and no audio or route behavior changed.
This is single-source port evidence. Evidence:
`scratch/agent/s3129_m5_origin_publish/run.log`.

Session 3130's independent retail oracle passed the whole-RDRAM positive
control (10,000 writes), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the newly audited direct `osViSetMode`
callsite `0x8001BC28` in `selectAndApplyViMode`. The candidate executed zero
times overall, including both target phases. This rejects that selected-mode
callsite as the retail target-phase handoff and leaves the upstream boundary
unidentified. This is single-source oracle evidence; no port behavior changed.

Session 3131's independent retail oracle passed the whole-RDRAM positive
control (10,000 callbacks), reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and watched the upstream callsite `0x800186C0` (the
`jal 0x8001BB6C` into `selectAndApplyViMode`). The candidate executed zero
times overall, including both target phases. This rejects that caller as the
retail target-phase handoff and leaves the upstream boundary unidentified.
This is single-source oracle evidence; no port behavior changed. Evidence:
`scratch/agent/s3131_m5_retail_186c0/oracle.log`.
Evidence: `scratch/agent/s3130_m5_retail_bc28/AUDIT.md`.

Session 3132's bounded caller/data-flow census found no hidden caller of
`freeRenderSubsystemResources` in the available generated snapshot, companion
tree, project symbols, or registration artifacts. The wrapper's only
represented call edge is `0x800186C0 → selectAndApplyViMode`; its complete body
only frees five resources, selects/copies a mode descriptor, calls
`osViSetMode`, and waits on the video queue. This selects H-AlreadyEnumerated
and supplies no new retail PC. It rules out another caller in this wrapper
chain but does not identify the upstream 640-to-1024 handoff. Static,
single-source evidence; no build, run, or behavior change.
Evidence: `scratch/agent/s3132_m5_vi_caller_audit.md`.

Session 3133's available-text census of the pending word,
selector/descriptor candidates, named VI helpers, and consumer/publication
symbols found no game-side writer/reader body or new transition-capable
instruction. The companion libultra bodies are `INCLUDE_ASM` stubs and the
matching generated-function snapshot is absent from the workspace. This
selects `H-StaticInsufficient`, rules out a static PC selection for this unit,
and leaves the M5 route blocker unresolved. Single-source static evidence; no
runtime behavior changed. Evidence:
`scratch/agent/s3133_m5_pending_descriptor_audit.md`.

Session 3134 repeated the prescribed companion-tree and project-tree census
for the pending VI word, selector/descriptor candidates, named VI helpers,
and the known consumer/publication PCs. It found only existing declarations
and probes: no restored generated body or disassembly, and no new
transition-capable retail PC outside the closed candidate sets. This selects
`H-StaticInsufficient` again and leaves the M5 route blocker unresolved.
This is single-source static evidence; it authorizes no port probe or
behavior change. Evidence:
`scratch/agent/s3134_m5_upstream_source_census.md`.

Session 3135 reran the exact bounded census across the companion and project
trees. Matches remained limited to existing declarations, symbol entries,
and existing probes/references; no restored generated body, disassembly, new
transition-capable retail PC, or new pending-to-descriptor edge appeared.
This selects `H-StaticInsufficient` again and leaves the M5 route blocker
unresolved. Static, single-source evidence; no build, run, port probe, or
behavior change. Evidence:
`scratch/agent/s3135_m5_upstream_source_census.md`.

Session 3140 reran the exact source-restoration census before any build. The
companion `osViSetMode` and `__osViSwapContext` bodies remain `INCLUDE_ASM`
stubs; project matches remain existing declarations, symbol records, comments,
and closed probes. No new transition-capable retail instruction or generated
body was found, so this selects `H-SourceInsufficient` and does not authorize
another oracle watch, port instrument, or audio change. This repeats the
source limitation after the candidate set was exhausted; the M5 boundary is
blocked pending equivalent instruction-level source. Single-source static
evidence: `scratch/agent/s3140_m5_retail_source_census.md`.

## Next steps

Priority is maintenance, then M5 de-stubbing, then systematic M3, then the
generated-symbol sweep. Maintenance and M5 design are complete. Session 3192
qualified the dispatch arms but again found both port arms stopped at VI 640,
so M5 target-phase qualification is blocked until a route change produces
title or hangar controls. The selected M3 class is closed; with the M5 route
boundary blocked, the next work unit is the bounded generated-symbol sweep.
Do not remove the status-03 wait hatch.

1. **M5 route reachability — obtain a route-change direction.** Session 3192
   ran the prescribed Step 1 pair: both image and silent arms reached only VI
   640 despite a retail oracle control reaching title and hangar. Do not repeat
   this pair. A human-selected upstream route change or equivalent new
   retail-grounded source is required before Step 1 can produce target-phase
   audio evidence.

2. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   After item 1 changes the route, rerun the existing same-build pair with
   `ROGUESQ_AUDIO_UCODE=0/1`, `ROGUESQ_LOG_ALL=1`, and phase gating. The image
   arm must show nonzero DMEM/DMA, `Broke`, SP completion, and downstream
   service/slot/PCM joins; the silent arm remains the no-write control.

3. **M3 crash work — audit the next bounded idiom-class inventory entry.**
   Session 3158 audited `musyxStoreVoiceAdsrParams`: its one reachable caller
   passes a byte-loaded index without a local `<64` proof, and all four
   indexed stores remain unclassified. Session 3157 audited
   `musyxInitVoiceFromSample`: its two reachable callers
   and two independently formed voice-slot pointers remain unclassified
   because the sound-macro index has no local `<64` proof and the streamed
   allocator/lifecycle edge does not establish the callee's exact bound. The
   `slotDispatcherIter`, `slotDispatcherInner`, and
   `musyxStopVoice` computed-record classes and item -292's 43-site
   `SONGTEMPO_TABLE_GUARD` reader inventory are closed by Sessions 3146–3156.
   Session 3164 audited the `stopVoicesByHandle` producer edge: all four
   callers use the same node `+0x8`, while the sole identified writer copies
   unconstrained `$a3` and no direct or recoverable indirect allocator edge
   was found. This selects `H-HandleUnclassified`, not a retail-invalid-value
   finding; no guard is authorized. Session 3162 closes the `stopVoiceByKey`
   producer edge as `H-M3-Proven` (`0..31` or `-1`) after auditing its complete count-byte
   writer set. Select the next complete NULL-plus-offset class from the
   existing M3 inventory and enumerate all sites in one audit. The next
   selected class is `musyxTriggerVoiceAttack`'s voice-indexed record access.
   Session 3163 completed the selected `musyxTriggerVoiceAttack` class and
   confirmed `H-M3-Unclassified`; select the next unresolved producer edge
   from the existing M3 inventory. Session 3165 audited the
   `musyxStoreVoiceAdsrParams` `+0x67` index producer: no connected writer or
   recovered indirect/data producer was found, so it selects
   `H-M3-Unclassified`; do not add a guard. Session 3167 proved the complete
   `musyxMixActiveVoices` class (`0..31` over the 32-entry array), closing that
   selected lead. The generated-symbol sweep lead for
   `0x800A0000..0x800B0000` is closed by Session 3160; resume it only in a
   different address band after M3 is no longer actionable.

4. **Generated-symbol renaming sweep.** M5 remains blocked pending a route
   change, and Session 3167 closed the selected M3 voice-record class. Resume
   this regeneration-safe campaign. Session 3166 synchronized the explicit
   data gap at `0x800B75C4`; Session 3168 found the next band
   `0x800B75D0..0x800C0000` already synchronized except for the explicitly
   fake `0x800B89F4`, which remains unchanged. Session 3169 closed
   `0x800C0000..0x800D0000` as already synchronized or ambiguous. Session
   3170 closed `0x800D0000..0x800E0000`: two records remain
   ambiguous/fake, all other candidates are synchronized, and no placeholder
   definition remains in the interval. Continue at
   `0x800E0000..0x800F0000` is closed by Session 3171: its selected records
   are synchronized or ambiguous/fake, with zero stale placeholder
   definitions. Session 3172 closed `0x800F0000..0x80100000` as already
   synchronized or ambiguous/fake, with zero stale placeholder definitions.
   Session 3173 closed `0x80100000..0x80110000`: the only remaining
   placeholder in the generated snapshot was the independently classified
   invalid-data tail `static_4_801096D8`, now mechanically named
   `data_gap_801096D8`. Session 3174 closed
   `0x80110000..0x80120000` as synchronized or ambiguous/fake, with no
   placeholder definitions in the interval. Continue at
   Session 3175 closed `0x80120000..0x80130000` as already synchronized or
   ambiguous/fake, with zero stale placeholder definitions. Continue at
   Session 3176 closed `0x80130000..0x80140000` as already synchronized or
   ambiguous/fake, with zero stale placeholder definitions. Continue at
   Session 3177 closed `0x80140000..0x80150000`: the only selected record was
   already synchronized, with zero changed references and no stale generated
   placeholder definition. Session 3178 closed `0x80150000..0x80160000`: two
   records were ambiguous/fake, three were already synchronized, and no stale
   generated placeholder definition remained. Continue at
   `0x80160000..0x80170000`, closed by Session 3179: the helper selected zero
   generated references and the independent definition search found no stale
   placeholder body. Session 3180 synchronized the concrete data gaps at
   `0x80007064` and `0x800AE3E4`. Session 3181 closed
   `0x80170000..0x80180000`: the helper selected zero generated references
   and the independent definition search found no stale placeholder body.
   Session 3182 closed `0x80180000..0x80190000` the same way: zero generated
   references and no stale placeholder definition. Continue at the next
   unexamined address band. Session 3183 closed
   `0x80190000..0x801A0000` the same way: zero generated references and no
   stale placeholder definition. Session 3184 closed
   `0x801A0000..0x801B0000` with zero generated references, no placeholder
   occurrence or definition, and no companion symbol record. Continue at
   `0x801B0000..0x801C0000`, closed by Session 3186: the helper selected zero
   generated references, the independent definition search found no stale
   placeholder, and the companion symbol files had no record in the band.
   Session 3187 synchronized the stale declaration and overlay-table
   references for `0x800027B8` to the established `data_gap_800027B8` name.
   Session 3189 classified and synchronized `0x80029270` as
   `data_gap_80029270`; Session 3191 classified and synchronized
   `0x800A2114` as `data_gap_800A2114`; Session 3193 classified and
   synchronized `0x800A2218` as `data_gap_800A2218`; Session 3194 classified
   and synchronized `0x800A23BC` as `data_gap_800A23BC`; Session 3195
   classified and synchronized `0x800A2558` as `data_gap_800A2558`. Resume at
   `0x800A29BC`, the next unclassified generated record, and preserve
   ambiguous fragments.

5. **External retail-entry boundary — compare the new wait predecessors after
   a route change.** Session 3185's independent retail oracle found
   `bufferArbiterProducerScanWait` live in both target phases, with title
   predecessor `0x800C5CEC` and hangar predecessor `0x800B24E8`, while
   ProducerMark remained dominated by `0x8000C628`. This is single-source
   ground truth, not a port mismatch; do not add another port counter until a
   route change reaches title or hangar.

6. **M4 accumulator origin.** Parked because the latest route qualification
   had no target-phase positive-control rows. Do not interpret its nulls.

7. **M5 SP-yield lifecycle and CPU-side MORT publication.** Parked pending a
   route angle that reaches target phases. The corrected MORT descriptor edge
   is `+0x190` to `dmaVoiceSampleAndSignal`; `+0x194` is the speech source.

## Durable boundaries and operating rules

Factor 5 uses [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a positive control in the same run,
phase-scoped budgets, and two independent lines of evidence before a
conclusion is promoted. Phase-gate animated comparisons on VI transitions;
never use a stopwatch. Build every A/B arm together.

Regeneration order is `make_elf.py` → N64Recomp → `fixup_game_funcs.py` →
CMake. Never hand-edit generated functions for behavior changes. If `lib/`
changes, export submodule patches in the same iteration. Never run
`git submodule update`, `git checkout -- lib/...`, `git clean`, or
`git reset --hard`. Kill runs with SIGKILL and run from `build/`.

A mitigation-shaped change requires an `ORIGIN:` line naming the writer and
stating whether the value is legitimate. A null result without a positive
control is worthless. If three consecutive iterations on one hypothesis fail
to produce a discriminator, pivot or block with a specific question.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. The full
failed experiments remain in `PORTING-STATE.md` and the archived overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Evidence index

Recent evidence directories include:

- `scratch/agent/s3111_m5_retail_mode_selector_range/`
- `scratch/agent/s3107_m5_retail_mode_callsites/`
- `scratch/agent/s3106_m5_retail_mode_writer/`
- `scratch/agent/s3112_generated_symbol_rename/`

Use `grep -n` plus a bounded `sed` window for `PORTING-STATE.md`; never read
that multi-megabyte ledger wholesale. The soak queue is consumed by the
automation between iterations; fold only new tail lines into the next audit.
