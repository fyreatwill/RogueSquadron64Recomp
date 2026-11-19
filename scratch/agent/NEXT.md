# NEXT (s7616)
HYPOTHESIS-ID: rt64-deferred-rdram-read

Class DQ closed s7615 (tools/s7615_dq_census.py --controls --witness scratch/s7615/witness.log: 16 queues + 12
vectors-as-queues, regex == clang, 29 producers in their allowed sets, 52 threads, controls 10/10, witness 14 static
deferred-message queues). Its declared scope gap is the next class.

Class RQ: deferred RDRAM reads inside lib/rt64. RT64 hands work from the gfx thread (processDisplayLists / the LLE RDP
range submit in src/main/rt64_render_context.cpp) to its own threads: workload queue, present queue, texture-cache /
upload threads, framebuffer-manager readbacks. Any of those that reads core.RDRAM (TMEM loads, texture hashing,
copyRAMToNative, VI XXH3 hash in updateScreen) LATER than the RDP command that names the address sees whatever the game
wrote in between. On hardware the RDP reads RDRAM at command time; the guest may reuse a buffer once DP FULL_SYNC fires.
Safe only when: (a) the read happens on the gfx thread before dp_complete is raised for that task (sync), (b) the bytes
are copied at command time (e.g. RDP_ASYNC Job.w), (c) the consumer is the VI scanout (s7542 18(c)), or (d) it is gated.
Method: tools/s7616_rq_scan.py: in lib/rt64/src, enumerate every RDRAM access (RDRAM[, rdram +, ->RDRAM, core.RDRAM,
getRDRAM, XXH3 over RDRAM) and the function/thread it runs on (call graph back to a thread entry: WorkloadQueue thread,
PresentQueue thread, TextureCache thread, gfx-thread entry points). Second source: clang AST (lib/rt64 TUs are in
build/compile_commands.json) MemberExpr/DeclRefExpr on RDRAM, same set. Rows: sync / copy / scanout / gated / BAD.
Controls: planted RDRAM read in a workload-thread function -> OPEN; drop a row; drop an access from one source ->
disagreement; misattributed thread -> OPEN.
Runtime witness for any default-on non-gfx-thread reader: count bytes it reads that differ from the bytes at command
time (snapshot at the RDP command on the gfx thread, compare at the late read; s7523 OVERWRITE is the model), title + L1.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE. Do NOT edit lib/ without export.sh + commit.
