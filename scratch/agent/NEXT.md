# NEXT (s7591)
HYPOTHESIS-ID: mach-right-release-census

HR-2 closed s7590 (H-dead: guest-thread mach_thread_self refs, fixed, ROGUESQ_S7590_THRPORT=0 = old). Class MR = the rest of the
idiom: every call in OUR code (src/, lib/N64ModernRuntime, lib/rt64 incl. plume, not vendored SDL/system) that returns a Mach right
the caller owns, classified per site:
  released (matching mach_port_deallocate / IOObjectRelease / semaphore_destroy / vm_deallocate of the array) |
  borrowed (pthread_mach_thread_np, mach_task_self: no ref taken) | leaked-gated (only under a diagnostic env) | leaked-default.
Known starting rows (s7590 grep): main.cpp:9611/9620 fl-zero task_threads + mach_thread_self; main.cpp:14007 s7382 task_threads
(deallocs on the error path - check the success path and the array); events.cpp:1268 G1E_THREADS 1 kHz task_threads (each th[i]
and the array must be freed every tick, or a gated run leaks ~65 rights per ms); events.cpp:835/1652 pthread_mach_thread_np
(borrowed); threads.cpp:322 (borrowed) / 323 (fixed s7590).
Hypotheses: H-clean (0 leaked-default rows left), H-gated (only leaked-gated rows: fix the ones that can flood, e.g. a 1 kHz loop),
H-default (another default-path leak: fix env-gated, =0 old).
Tool: tools/s7591_mr_census.py --controls: regex-enumerate the right-returning calls, print file:line + the release found within
the same function (or none), plant control = a scratch file with one leaked and one released site that must classify correctly.
Runtime witness for any fixed gated row: tools/s7590_portcensus.dylib (RS64_PC_OUT, RS64_PC_PLANT_DELAY) on L4 dd4 150 s with
that env on, D and S/1 flat, plant +1/leak. Game runs with DYLD_INSERT need the Bash sandbox OFF.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
