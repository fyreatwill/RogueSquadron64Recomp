# NEXT (s7330): item 22 — audio RSP reads of song-channel arrays freed 0-14 ms earlier at the scene transition
HYPOTHESIS-ID: audio-freed-song-read
Context: s7329 closed spill-rcp-dma-width (dd6 21:9 tile pool gfx-read, s7327 fix exact). Item 22 (s7325, single-source): 46 audio
DMA reads + 6 writes per 200 s land in a guest FREE block; the song-channel arrays were freed 0-14 ms earlier by
waitForMusyXAudioTaskDone (reached via musyxNoopStub) or the scene sync.
Hypotheses:
- H-wait-noop: our wait returns before the in-flight host audio RSP task finishes (stubbed/degenerate path), so the guest frees
  arrays the task is still reading. Port artefact; reads could see reused bytes (audio glitch / corruption at transitions).
- H-retail-race: retail frees the same way while its audio task runs; harmless because nothing reuses the block within one task.
- H-next-task: the reads come from a task SUBMITTED after the free (the song list still points at freed arrays) = game-side
  dangling pointer, retail or ours.
Discriminating measurement (ONE build, ONE run): host-stamp (a) each audio RSP task submit + end (task id, wall ns), (b) the guest
wait's entry/return, (c) the free of each song array (addr, ns), (d) each freed-block DMA (addr, task id, ns). Read: hit task started
before the free and the wait returned before the task end -> H-wait-noop; hit task started after the free -> H-next-task; wait
genuinely blocked until task end and the hit precedes it -> impossible, recheck instrument. Positive control: the same stamps on a
non-freed audio DMA must show task-id attribution 100%. Route: scratch/s7326/run.zsh (hangar route, scene transitions) with
ROGUESQ_S7317_ALLOCMAP=1 (s7325 heapsync map), reports tools/s7325_gap_report.py as the starting point.
Check first (boring): what musyxNoopStub does today and whether a ROGUESQ flag re-enables a real wait (grep CURRENT-TRUTH/M5 plan).
