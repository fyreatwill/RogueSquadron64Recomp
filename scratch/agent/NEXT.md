# Hold synth quiesce past the gate clear until guest audio re-init ends

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4784: port teardown ordering inside the noop window matches retail; the divergence is AFTER the gate clear: the synth host thread ticks 0 mallocs after the clear (retail: 32-44 rs_malloc first).
Hypotheses: A) retail's post-clear protection is simply "re-init runs before the next tick" (single-threaded/cooperative); holding the s4562 pause until re-init end removes the crash. B) the crash survives a held pause (then the freed-arena hit is a stale pointer in the re-init itself, not a tick race). C) re-init never completes before the next noop window in the port.
Discriminator: find the guest return/point after the 32-44 mallocs (analyze scratch/agent/s4783 oracle data with tools/s4783_noop_gap.py for the PC of the last malloc caller before the first post-clear synth tick; map to a funcs_*.c anchor), release g_s4562_pause there instead of at 0x8008ED48 (PAUSE=4, env-gated), run the VI640 phase-3 route (scratch/agent/s4784_run.sh with ROGUESQ_S4562_PAUSE=4), count crash + SYNTH-POST positions. Control: PAUSE=3 arm in the same iteration (expect crash). A: PAUSE=4 survives past old crash point; B: still crashes.
ORIGIN: retail ordering (s4783 oracle, s4784 port).
