# NEXT (s7615)
HYPOTHESIS-ID: host-queue-deferred-guest-read

Class HM closed s7614 (tools/s7614_hm_census.py --controls --witness: 24 statics / 34 rows 0 open, two-source agreement,
contracts B/V1/Q1/HF/U1, controls 8/8; the one default-on deferred guest view, the audio OSTask* in
events_context.sp_task_queue, witnessed unchanged enqueue->consume 236/236 with a working off-by-one control).
Its declared scope gap is the next class.

Class DQ: deferred guest reads through host queues. A host queue / channel / deferred callback (moodycamel queues,
std::deque/queue/vector used as a queue, action_queue variants, timer queues, RT64 workload queues, std::thread lambdas
capturing guest addresses) whose ELEMENT carries a guest address (PTR(T), uint32 vaddr) or a host view, and whose consumer
reads guest memory through it LATER than the producer's call. On hardware the read happens at the producer's call (or the
guest protocol forbids touching the object until a completion message), so a deferred read is safe only when (a) the element
carries a value copy, or (b) the guest waits for a completion event before rewriting the object, or (c) the read is log-only.
Method: tools/s7615_dq_scan.py: enumerate every enqueue/push/emplace/push_back/send call on a container that is a member or
static (reuse s7614 AST records + vars for the container list; regex for `.enqueue(` / `.push(` / `.emplace(`), classify the
element type (value copy / PTR / host view), and find each consumer (dequeue / pop / front) and what it dereferences.
Second source: the s7614 clang AST (queue-typed fields/vars with element type) vs the regex call census must list the same
queues. Rows: copy / protocol (+ which completion event) / logonly / gated / BAD.
Controls: (1) plant a static deque<uint32_t> of guest addresses whose consumer does MEM_W through it -> OPEN; (2) drop a row;
(3) plant a value-copy element -> classified copy automatically; (4) drop a queue from one census -> disagreement OPEN.
Witness for any default-on protocol row: an existing log or a lifetime-style log pairing producer and consumer contents
(the s7614 W pairing is the model; tools/s7614_hm_witness.sh shows the run recipe).
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
