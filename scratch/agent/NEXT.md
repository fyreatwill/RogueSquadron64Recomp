# NEXT: with all s4581/s4586/s4587 instruments OFF, does the run die at pi.cpp:113 (odd PI DMA source) around VI 5850, and which guest caller issues the odd cart address?
HYPOTHESIS-ID: m5-audio-destub
Context (s4587): the permanent rs_malloc window was caused by ROGUESQ_LOG_S4581's backtrace_symbols_fd. Without it (S4581_NOBT=1) tid 3 runs and the run dies at VI ~5850 on pi.cpp:113 (do_rom_read, physical_addr odd). Anything measured in s4580-s4586 under LOG_S4581 backtrace is suspect.
Hypotheses: H-odd-src-from-mixer (audio DMA with ASCII/garbage node, per s4580), H-odd-src-from-other (stream/fillSampleStreamRange), H-instrument-free-differs (clean run does not die at 5850 / dies elsewhere).
Discriminator (ONE build, 2 concurrent arms): arm A all logging OFF (just AUTOPILOT env from s4587_rq.sh), arm B same + a log in do_rom_read (lib/N64ModernRuntime/librecomp/src/pi.cpp) of cart addr, dram addr, len, guest PC (g_rs64_last_guest_pc) and ultramodern::this_thread() id/priority on the odd case before the assert. Control: first 20 even DMAs also logged. Crash site and VI must match in A and B.
Commit pi.cpp change with ./submodule-patches/export.sh.
