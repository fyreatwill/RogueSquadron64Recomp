# Next work unit (s4285): why does WRAP_FLUSH=1 still leave ODD cimgs (81/2048 commits, all with laps)?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4284: every ODD commit has lap-dropped bumps (210/210 vs 26% baseline). Flush=1 only 5.0%->4.0%.
Hypotheses: F1) RT64 reads ranges lazily at commit even after flush's submit_rdp_range, so lap-2 overwrites still precede the read; F2) flush happens only on END<seen bump, but lap-2 bytes written before that bump are overwritten bytes of lap-1 not yet flushed (partial range lost); F3) other writers.
Discriminator: at each flush, hash first 64 bytes of each flushed range at flush time and again at ODD event; plus print whether RT64 processed the range synchronously (g_s4280 event emitted during flush vs at commit). F1: cimg events emitted at commit not flush. Control: same instrument with flush=0 must show no flush-time events.
Template: scratch/agent/s4284_laps.sh.
