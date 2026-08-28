# NEXT work unit — bounded audio-task publication-to-consumer audit

HYPOTHESIS-ID: m5-route-task-handoff

Perform one bounded static audit of the distinct handoff between audio-task
publication and the first route consumer. Do not add a probe or build unless
the audit identifies a concrete non-mitigation change.

Competing hypotheses and the discriminator:

- H-TaskPublicationMissing: the pending audio task is not published for the
  target transition, so route preparation has no correct task to consume.
- H-TaskPublicationStale: publication and consumption cross a thread/queue
  boundary without a happens-before edge and the consumer sees stale task
  metadata.
- H-TaskConsumerWrong: the first audio route consumer reads the wrong task,
  arm, or task fields, independently of VI acceptance.
- H-StaticInsufficient: all task publication and consumption edges are
  present and ordered, so no behavior change is justified.

The single discriminator is a complete task table: every writer of
`s_pending_audio_task` and its guest pointer, every queue/event handoff and
memory-order operation, every first consumer (`rs64_m5_task_handoff` and RSP
dispatch), and the retail-grounded target transition. A missing writer selects
the concrete publication edge; a stale handoff selects the exact ordering
edge; a wrong consumer selects its field/arm boundary; otherwise preserve the
route-failure boundary. Do not infer audio behavior from VI-640 `accepted=0`.

Exact commands from the repo root:

    rg -n -C 35 's_pending_audio_task|pending_audio_task|rs64_m5_task_handoff|M_AUDTASK|audio task|task_ptr|data_ptr' src/main/main.cpp src/main/upstream_compat.cpp lib/N64ModernRuntime
    rg -n -C 20 'osSendMesg|osRecvMesg|submit_rsp_task|M_AUDTASK|audioTask' /Users/williambuckley/Documents/Tools/rogue_squadron64
    git diff -- src lib syms tools

Record the complete table and decision in
`scratch/agent/s3044_m5_task_handoff_audit/`.
