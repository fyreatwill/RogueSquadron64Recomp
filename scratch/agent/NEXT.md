# NEXT (s7644)
HYPOTHESIS-ID: owner-items-wait

G6a (rumble), G6b (F6 controls), G6c (stand-ins) and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner
reports on any of them, take that first. Do NOT schedule a ladder-item-4 REVISIT or the rename sweep.

Work unit if no owner report: class TS-3 = RSP task vs guest PI DMA on the same RDRAM bytes. s7643 (CURRENT-TRUTH item 30) saw
recomp::do_rom_read (guest thread, PI DMA) write RDRAM bytes recomp::rsp::run_task (RSP thread, audio task; the s4211 hash of
[dp-0x10, dp+0x120)) had just read. Hypotheses: H-margin (the bytes lie only in the s4211 diagnostic's over-read margin outside the
task's real command list: harmless, diag only) vs H-live (a PI DMA lands inside the live audio command list / sample buffer the RSP
task is consuming = port timing hardware would not allow, e.g. the port runs the audio task late relative to the next DMA) vs
H-retail (the game does this on hardware too: check with the oracle tools/oracle/README.md, watch the same physical range during an
audio task). One instrument, one build, default off: ROGUESQ_S7644_RSPDMA=1 records per audio task [data_ptr, data_size] and the
task's start/end host-ns, and per PI DMA [dram, size, ns]; at exit dump every DMA whose range overlaps a task's range while that
task ran, split by inside-command-list vs margin-only. Positive control: ROGUESQ_S7644_RSPDMA_CTL=1 issues one synthetic overlap
record that must appear. Arms in one run each: boot 45 s + L1 dd2 120 s flight (g1e_owner_quiet_arms, real binary, ALLOW_SLOW).
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
TSan reuse: tools/s7643_tsan_host_build.sh + tools/s7643_tsan_pairs.py (semaphore now annotated; expect ~26 Metal-class boot reports).
