# NEXT (s7641)
HYPOTHESIS-ID: owner-items-wait

G6a (rumble, incl. s7638 fallback chain), G6b (F6 controls), G6c (stand-ins) and the G5 looks wait only on the owner
(docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Do NOT schedule a ladder-item-4 REVISIT or the rename sweep (CURRENT-TRUTH Next steps, first bullet).
Work unit if no owner report: another NEW host-side idiom-class audit (CURRENT-TRUTH items 19-27; grep class letters first;
ST and AT are taken). Candidate: class MT-SAN = Thread Sanitizer-free race witness is too costly; cheaper new class:
**CF = CoreFoundation/IOKit/HID callbacks** (SDL's IOKit HID + GCController callbacks, IOKit registry reads in plume
getRenderDeviceVendor, mach timebase use) - which run loop/thread delivers each callback and whether our code touched from it
(set_rumble/get_n64_input paths, s7638 haptic fallback) races with the main thread. Ground truth: Apple's Main Thread Checker
already runs clean (s7640, scratch/s7640/run.zsh), so reuse it as a regression check in the same run.
H-clean vs H-defect; planted-call control. Never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
