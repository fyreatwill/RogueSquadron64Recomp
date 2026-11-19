# NEXT (s7640)
HYPOTHESIS-ID: owner-items-wait

G6a (rumble, incl. s7638 fallback chain), G6b (F6 controls; s7639 moved its window-size read to the main thread), G6c
(stand-ins) and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Do NOT schedule a ladder-item-4 REVISIT or the rename sweep (CURRENT-TRUTH Next steps, first bullet).
Work unit if no owner report: another NEW host-side idiom-class audit in the s7579-s7639 style (CURRENT-TRUTH items 19-26; grep
the class letters first; ST is taken). Candidate not yet done: class AT = Objective-C/AppKit calls in src/main/*.mm and
lib/rt64 plume_apple.mm reached off the main thread (the ST census covers SDL only; reuse its scope/root machinery from
tools/s7639_st_census.py, with `[NSThread isMainThread]`/dispatch_* as guards). H-clean vs H-defect; planted-call control.
Never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
