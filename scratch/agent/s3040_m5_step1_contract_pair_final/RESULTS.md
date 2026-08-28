# Session 3040 M5 Step-1 qualification

The independent retail oracle passed the whole-RDRAM positive control and
reached title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`.

The same-build port arms were launched concurrently with the full M5 marker
set. Both reached only VI 640 at `0x0066A500`; neither reached title or hangar.
The silent arm dispatched 44 tasks with `real_ucode=0`; the image arm
dispatched 44 with `real_ucode=1`. Both had zero task-ABI, DMA, image-stage,
audio-return, service, PCM-boundary, crash, and abort rows in target phases.
The route gate failed, so all downstream audio hypotheses remain unevaluable.

The first attempt exposed a harness defect: it serialized the arms and exited
before launching the image when silent missed hangar. The corrected driver
launches both arms concurrently, uses the scheduled AUTOPILOT route, and
cleans up known child processes. The corrected run reproduced the same route
boundary. No audio behavior or mitigation changed.
