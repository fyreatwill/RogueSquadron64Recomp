# NEXT: M6 boot freeze, active hunt (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: m6-boot-freeze-loop
Why: s6993 caught 1 boot freeze in ~65 boots: [stall-dump] retrace thread 8011CD28 blocked on a FULL send to message queue 0x80128CF0.
Passive waiting has not recurred; ITERATION 3b says loop boots actively and read the real stacks.
Hypotheses: H-consumer (the queue's receiver thread is itself blocked elsewhere, e.g. on audio/MusyX or a DMA completion, so the queue fills),
H-race (our VI/retrace delivery posts twice per VI under a scheduling burst and the 8-deep queue overflows; retail drops with OS_MESG_NOBLOCK),
H-host (a host-side lock in the present/RT64 init path stalls the receiver).
Discriminator: on recurrence, ROGUESQ_STALL_SAMPLE_DIR host stacks of every guest thread + the queue's validCount/msgCount and the receiver's
guest PC. Receiver blocked elsewhere -> H-consumer (name where); receiver runnable but queue full of duplicate VI msgs -> H-race; host lock in
stacks -> H-host.
Work: write scratch/agent/soak_queue/s7190_bootloop_{a,b,c,d}.sh: each boots the game from build/ ~15 times (35 s each, SIGKILL), with
ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_STALL_SAMPLE_DIR=<dir> ROGUESQ_G1B=1, owner recipe (FPS60=1 DRAW_DISTANCE=4 ASPECT=16:9), stall = VI origin
unchanged > 10 s or no [g1b] line for 10 s; on stall run `sample <pid> 3` before SIGKILL, exit 1. Template: scratch/s6993/drive169.sh.
Positive control for the stall detector in the same recipe: one boot with ROGUESQ_XTRACE_POKE or a SIGSTOP of the game for 12 s must be flagged.
Then do offline work while the loop runs them.
