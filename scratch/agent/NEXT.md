# Next work unit (s4286): restore-from-shadow arm at wrap flush

HYPOTHESIS-ID: m5-audio-destub-sequence

s4285: ~21% of wrap flushes find lap-1 bytes already overwritten (shadow!=live). ODD cimgs still 60/60 inDropped.
Hypotheses: R1) feeding bump-time bytes (restore shadow words into RDRAM around submit_rdp_range, then put live back) removes ODD cimgs; R2) ODD persist (shadow cap >0x400 skips ranges, or RT64 reads deferred at commit not submit); R3) restore breaks lap-2 content.
Discriminator: arm A flush=1 as now, arm B flush=1 + ROGUESQ_WRAP_RESTORE=1 (patch in the flush block of dpc_bridge.cpp, guarded env; also raise shadow cap to 0x2000 via env). Compare ODD count and `[s4285-flush]` diff after restore (must be 0 during submit = positive control). R1 if B odd << A odd.
Template: scratch/agent/s4285_flush.sh (arm loop; set env per arm). Use tools/patch_s4286.py for the code change; sed -i needs '' on macOS.
