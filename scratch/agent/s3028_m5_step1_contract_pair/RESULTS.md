# Session 3028 — M5 Step 1 baseline

The Debug target built successfully. The retail oracle passed the whole-RDRAM
positive control at 10,000 callbacks and reported title 1024 at origin
0x00790400 plus hangar 512 at origin 0x006AB400.

The first driver attempt was invalid because it omitted the in-process
autopilot; both arms stayed at VI 640. The corrected driver added the
documented autopilot and launched silent (ROGUESQ_AUDIO_UCODE=0) and image
(=1) concurrently from the same build. It still left both port arms at VI
640 (0x0066A500) and never reached title or hangar. Each arm produced 340
audtask-dispatch rows, with zero audio-return, audtask-abi, or DMA rows in
the captured summaries and zero crash/abort markers. The run was SIGKILLed
after repeated full-log scans made the nominal phase wait impractically slow.

The only valid conclusion is that the task-dispatch positive control fired and
the M5 downstream comparison is unevaluable before the target phase. This
does not select or reject an audio-contract hypothesis. The route-repair or
independent-handoff dependency remains open.
