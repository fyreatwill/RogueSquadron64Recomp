# NEXT work unit (s923)

HYPOTHESIS-ID: m3-voice-queue-receive-class

Audit the complete MusyX voice queue-receive idiom: every generated use of
the per-slot queue at `slot+0x11AC`, its gate/state fields, receive arguments,
returned-message consumers, and queue initialization/writers. Cover the
`serviceStreamingVoice` sites and the queue creation in `initMusyXVoiceSlot`,
then enumerate all generated callers and companion symbol/decomp evidence.
Do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-queue-receive-unclassified: a queue receive site has an unchecked queue
  base, incompatible record shape, unsafe returned-message use, or an
  unbounded retry/termination path.
- H-queue-receive-classified: every receive is state-gated/nonblocking with a
  coherent slot queue and bounded local control, and initialization/writers
  establish the same queue contract.
- H-queue-receive-shape-mismatch: one caller or sibling writer uses a distinct
  queue/slot contract; record the exact split and stop.

Discriminating measurement: a complete site table for every `slot+0x11AC`
queue access, including the exact `osRecvMesg`/queue-create arguments, gate and
state fields, message consumers, loop/termination bounds, all callers, and
companion basis. Any omitted access, unsafe message use, unbounded termination,
or incompatible queue shape rejects full classification.

Exact commands: use `rg -n '11AC|osRecvMesg|osCreateMesgQueue'` in
`../N64Recomp/RecompiledFuncs/funcs_26.c` and `funcs_27.c`, inspect bounded
windows around each site and callers, then inspect the matching
`rogue_squadron64/symbol_files/main_overlay.txt` entries. No game build or
soak is planned.
