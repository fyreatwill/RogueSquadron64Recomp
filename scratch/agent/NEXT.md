# NEXT (s7555)
HYPOTHESIS-ID: class-go-device-status-reads

GN CLOSED s7554 (async RDP NODRAIN=3: 0 clobbers, async witness sig=9427). GB (s7538) enumerated every completion SIGNAL the runtime
posts; GO is its polled twin: every device STATUS/progress value the runtime RETURNS to the guest, and whether each is consistent
with the hardware ordering (busy until the matching signal, then idle) in default config and under RDP_ASYNC=1 NODRAIN=3, SP_LATE=1, FPS60.
Sites to enumerate (static census, tools/s7555_go_census.py, like tools/s7538_gb_census.py): librecomp ai.cpp:233 osAiGetLength,
ai.cpp:239 osAiGetStatus, dp.cpp:36 osDpGetStatus, sp.cpp:162 osSpTaskYielded, pi.cpp:800 osPiGetStatus, vi.cpp:29/33
osViGetCurrent/NextFramebuffer, ultra_translation.cpp:102 osGetCount, plus any osViGetCurrentLine / __osSpGetStatus / SI busy /
MEM_ reads of mapped device registers (grep 0xA4xxxxxx / 0x04xxxxxx in src/ and the fixups), and every guest call site of each
(grep RecompiledFuncs for the _recomp names) with what the caller does with the value.
Hypotheses:
- H-consistent: every returned value is ordered with its signal in every mode (0 open rows).
- H-stale: some value reports idle/done while the worker still owns the job (e.g. osDpGetStatus under NODRAIN), or busy forever
  -> name the guest caller, measure with a counter in one run, fix (status reads from the same state the signal uses).
- H-unused: the guest never calls the function (dead row; prove with the call-site grep, not assumed).
Controls (--controls): synthetic rows for each verdict + a planted mis-ordered site must classify H-stale; census exits 0 only on 0 open.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
