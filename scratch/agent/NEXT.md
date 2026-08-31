# NEXT work unit — obtain a like-for-like send/receive join

HYPOTHESIS-ID: m5-frequency-writer-contract

Session 3439 found the send hook live but not comparable: the port producer
census reached 512 rows, with 486 rows on queue `0x8010FEE0` and 490 message
values equal to zero, while the retail arm only watched receive-side PCs.
The earlier input gap remains open.

Before building, ask ground truth for the missing like-for-like edge: run the
retail oracle with whole-RDRAM control, both title origins, hangar, and
`--watch-pc 0x80033410` (the retail `osSendMesg` entry), phase-gated to the
same width/origin buckets. Then add one port join at `osRecvMesg_recomp` after
the receive call: record the delivered message value and a bounded producer
sequence/queue key alongside the existing caller and wrapper rows. Keep the
existing send census.
Build once with `cmake --build build --config Debug --target
RogueSquadron64Recomp`, and run from `build/` with the validated
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1` route, title/hangar phase gates, and
SIGKILL cleanup.

Competing hypotheses and the single discriminating measurement:

- `H-RetailSendParity`: retail and port share normalized `(queue,msg,flag)`
  send publications that reach the selected receive rows; the gap is later.
- `H-EarlierPortSendGap`: retail has phase-qualified send tuples absent from
  the port send table and no delivered-message join exists.
- `H-SendJoinUnevaluable`: retail send execution or port delivered-message rows
  are absent despite live controls.

The measurement is the exact normalized `(queue,msg,flag)` intersection
between retail `0x80033410` rows and port send rows, plus the same-run join of
port sent `(queue,msg)` to post-receive delivered `(queue,msg)`. A retail/port
send intersection with delivered joins selects a later boundary; retail-only
tuples select `H-EarlierPortSendGap`; missing retail or delivered rows with
live positive controls select `H-SendJoinUnevaluable`. Do not change waits,
slots, dispatch, clear behavior, or PCM writeback.

Build once with `cmake --build build --config Debug --target
RogueSquadron64Recomp`; run the oracle first, then the port from `build/` on
the validated `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1` route with
phase/caller/wrapper/producer controls and SIGKILL cleanup.
