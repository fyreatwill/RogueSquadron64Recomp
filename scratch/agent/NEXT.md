# NEXT work unit — M3: find the source of the deterministic `do_rom_read` corruption

s91 turned the "shared corruption race" hypothesis into something much
stronger: the `do_rom_read` SIGSEGV that first showed up in s85 is not
random. It is the **exact same DMA call**, byte-for-byte, recurring
3 times now across 3 sessions and 2 rebuilds:

```
mb=0x80111270 pri=1 dir=0 dram=0xFFFFFFFF80195190 size=0x600
raw_r7=0x6C676672 (devAddr=0x7C676672, phys=0x1C676672)
ra=0x00000000
```

Always on thread id=1 (the PI DMA worker), always immediately after a
`[thr-resume] tag=swap` onto that thread. `raw_r7` and `ra` are BOTH
wrong together, identically, every time — not a plausible near-valid
value (every real call this run had `raw_r7` in the `0xB0FFxxxx` kseg1
shape; the bad one is `0x6C67...`, a totally different pattern). This
smells like reading an uninitialized or reused-before-write context,
not a race clobbering a live register.

## Two competing hypotheses

- **H1 (guest-side):** the `OSIoMesg` at `mb=0x80111270` was enqueued
  with genuinely garbage `devAddr` — a real bug in whatever game code
  builds this DMA request (uninitialized struct field, wrong overlay
  load table entry, etc.). If true, `devAddr` should already be
  `0x6C676672`-shaped in guest RDRAM *before* `piDmaWorker` ever reads
  it.
- **H2 (host-side):** `piDmaWorker`'s `recomp_context` itself is being
  read before it was ever properly populated for this specific
  resume — e.g. a freshly-created or freshly-reused thread context
  whose register file is still zero/stale memory, with `ctx->r31==0`
  being the tell (a real `jal` call always sets `$ra`; zero looks like
  "never written," not "overwritten with junk").

## Discriminating measurement

1. Reproduce: same command as s91 (built already, no rebuild needed
   unless you add the log in step 2):
   ```
   env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
       ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
       ROGUESQ_LOG_DMA=1 \
       PROBE_MODE=start_only HOLD_S=30 zsh \
       scratch/s73_post_a_scene/run_mission_keys.sh animcb7 0 12
   ```
   This has reproduced the target crash in 2/2 attempts so far (s91) —
   high confidence a 3rd soak reproduces it again at ~hold+11-13s.
2. Add ONE more log: in `osPiStartDma_recomp`
   (`lib/N64ModernRuntime/librecomp/src/pi.cpp:347`), before computing
   anything, read the `OSIoMesg`/message contents already resident in
   guest RDRAM at the address the message queue handed back (the `mb`
   local IS `ctx->r4`, the message pointer — dump the struct fields at
   that address directly via `MEM_W`, not through the register path,
   for at least `devAddr`/`dramAddr`/`size` offsets). If RDRAM at
   `mb=0x80111270` already contains `0x6C676672`-style garbage at the
   moment of the call, that's H1 (upstream, whoever built the message).
   If RDRAM there looks sane/zeroed/mismatched vs. what the registers
   show, that points at H2 (something in the register-restore path for
   this specific thread resume).
3. Either way, cross-reference against the immediately-preceding
   `[thr-resume] tag=swap id=1` line's `n=` counter — is this always
   the Nth resume of thread id=1 specifically, or does the resume
   counter vary? A fixed resume-count-since-thread-creation would be
   strong evidence this is a specific, replayable sequence (e.g. "the
   3rd DMA this thread ever issues"), not merely "eventually happens."
4. If H1: the `OSIoMesg` at `mb=0x80111270` was built by some caller —
   find it by searching the DMA message-queue send path (`osSendMesg`/
   `osJamMesg` calls feeding the PI manager queue) for what populates
   messages destined for this queue, or by adding a log at the point
   the message is dequeued vs. enqueued to see if it changes in
   between (would indicate H2 despite looking like H1 at the dequeue
   point — i.e. corruption between enqueue and dequeue, not at
   creation).

## Do not

- Do not re-run the "arm one flag, hope for TMEM-zero" soak — 0/5,
  parked to opportunistic (CURRENT-TRUTH next-steps item 2).
- Do not chase `advancePlayerAnimationPhase` — parked since s89, 3
  non-recurrences.
- If this soak's crash is a genuinely NEW (11th) class instead of the
  `do_rom_read` recurrence, treat that as its own finding — read the
  backtrace symbols against `symbol_files/*.txt` before assuming it's
  one of the 10 known classes.
- Budget: this is the 1st dedicated soak on the *refined* H1/H2
  question (the prior 3 occurrences established reproducibility, not
  root cause) — the rule-8 counter resets here, this is a new
  experiment shape.
