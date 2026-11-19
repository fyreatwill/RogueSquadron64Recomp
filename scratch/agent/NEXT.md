# NEXT (s7660)
HYPOTHESIS-ID: owner-wait-standing

s7659 closed the gate-sweep timing question (H-fits, cap now 600 s). Gate tooling is finished: do NOT start more gate work.
G6a/G6b/G6c and every G5 item wait on the owner (docs/OWNER-OPT-INS.md). If the owner has reported anything, take that first.
Otherwise: pick a rung of ITERATION.md 3c with an engineering step left that is not an owner look. Candidate, not yet tried:
the 3b secondary (~1/7 title-boot plume SIGSEGV si_addr=0x58, CURRENT-TRUTH "Title plume parked"): loop title boots
under lldb (one game at a time, SIGKILL) and read a real backtrace. Hypotheses: H-gone (0 in N>=14 boots, with a crash
control) vs H-live (backtrace names the writer). Same-run control: an lldb-attached boot that does stop on an injected fault.
Rules: never touch build/saves; one game at a time; SIGKILL only; re-run tools/s7651_gate_sweep.py after src/ or lib/ edits.
