# Port-side ordering: does the port tick musyxSynthFrame between the teardown free burst and re-init completion?

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4783 (retail, 8/8): wait -> 6-9 synth ticks -> rs_free burst -> gate clear -> 32-44 rs_malloc re-init -> next synth tick. Zero synth ticks in the free->re-init gap.
Hypotheses for the port: A) a host thread / VI callback dispatch ticks synth inside the gap (port-only concurrency); B) port tick lands in the gap because the port re-init is deferred (alloc happens much later, s4780: ~215k lines); C) port re-init order differs (73728 alloc before the audio blocks are re-created).
Discriminator: one port run (VI 640 phase 3 route, scratch/agent/s4782_run.sh recipe) with entry logs on musyxNoopStub, rs_free (burst), rs_malloc, musyxSynthFrame entry, tagged with thread id and a monotonic sequence number; compute synth ticks between first burst free and the next audio re-init alloc, and the dispatching thread. Control: synth-entry rows > 0 overall. A: ticks>0 in gap with other thread id; B/C: ticks>0 in gap same thread.
Then (ORIGIN: retail ordering, s4783) quiesce synth dispatch from musyxNoopStub entry to re-init end behind an env rollback flag, and soak the crash route.
