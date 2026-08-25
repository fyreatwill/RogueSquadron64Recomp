# NEXT work unit (s2345) — M5 C88 downstream ordinal join

HYPOTHESIS-ID: m5-c88-downstream-ordinal-join

## Work unit

Run one fresh ground-truth-first, same-build four-arm join of the existing
opt-in C88 treatment:

| audio arm | C88 | treatment |
|---|---:|---|
| stub | 0 | control |
| stub | 1 | C88 nonzero |
| image | 0 | control |
| image | 1 | C88 nonzero |

Keep `ROGUESQ_M5_B40_VALUE=0`. Extend the existing C88 launcher/parser with
one complete phase-keyed table; do not change the writer, consumer, task data,
slot code, voice code, or defaults. Retain the eleven-Start schedule, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, SIGKILL cleanup, and every
s2344 positive control. `ROGUESQ_LOG_AUDIOTICK_TRACE=1` is mandatory because
it gates the `0x80091468` branch rows.

## Competing hypotheses and discriminating measurement

- H-SameOrdinalVoicePath: C88=1 branch fall-through is followed in the same
  route ordinal by key-on normal-tail/slot-02/slot-00, descriptor/filter, and
  a new PCM source/consumer join in both audio arms.
- H-StaleOrdinalReuse: the C88=1 key-on, descriptor, or filter rows belong to
  a prior route ordinal or to `writer_seq=0` pre-writer rows; no same-ordinal
  downstream join exists.
- H-TaskOutputGap: C88=1 produces valid same-ordinal key-on/descriptor/filter
  work, but task metadata/DMA/output overlap and PCM publication remain absent
  or unchanged; the remaining boundary is the image task/output contract.
- H-ConsumerGap: C88=1 produces a same-ordinal nonzero PCM source, but the
  consumer is absent, mismatched, or ordered before the source.

The discriminator is one table keyed by
`(audio_arm,c88,phase,width,origin,writer_seq,branch_event,branch_lhs,
branch_taken,route_ordinal,keyon_table,normal_tail,slot02,slot00,
descriptor_event,filter_event,pcm_source_event,pcm_consumer_event)`.
Interpret no null until the fresh retail whole-RDRAM/target/title/hangar and
named-PC controls pass, and all four port arms have title/hangar, task, DMA,
guest-receive, PCM, filter, render, key-on, and callback-helper controls.
Select H-SameOrdinalVoicePath only if the same ordinal closes through PCM in
both C88=1 arms; select H-StaleOrdinalReuse if all downstream rows lose the
join; select H-TaskOutputGap if same-ordinal CPU voice work is real but PCM
does not follow; select H-ConsumerGap only with a new same-ordinal source and
consumer mismatch. A route change, crash avoidance, or aggregate counter
increase without the join selects none of these.

## Exact commands

Run the independent retail witness before the port build/run:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x165000:0x16B000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 --watch-write 0x1498A:0x1498C --watch-write 0x154620:0x154624 --watch-write 0x11A8A4:0x11A8B4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48 --post-value-pc-detail --watch-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --pc-phase-log-width 0x006AB400:512 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2345_m5_c88_ordinal_oracle.log 2>&1
    zsh -n scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2345_m5_c88_downstream_ordinal_join

The new driver must launch all four arms itself from `build/`, and its table
must be written under `scratch/agent/s2345_m5_c88_downstream_ordinal_join/`.
If the oracle or any arm misses a required positive control, stop as
H-CoverageInvalid rather than interpreting a null.
