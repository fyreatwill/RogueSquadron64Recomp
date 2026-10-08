# Next work unit: M5 Step 9n — guest writer of OSTask.data_ptr (RDRAM 0x1494A0)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4215: task struct layout verified (raw == host). H-task-struct-stale refuted.

Hypotheses:
- H-builder-skipped: the real audio builder is stubbed; data_ptr is set by some other (menu) code.
- H-builder-wrong-target: the guest audio builder writes data_ptr from a pointer it was handed by a stubbed/failed alloc.
- H-ucode-uses-other-ptr: list is reached via ucode data; data_ptr irrelevant.

First: read M5-S3482-TASK-WRITER-JOIN.md (may already name the writer). Then discriminator: store-watch on 0x1494A0 logging g_rs64_last_guest_pc / ra per write, with control watch on 0x149470 (type). Writer PC in audio-setup func => builder-skipped/wrong-target by its caller args.
Any lib/ edit needs submodule-patches/export.sh + commit.
