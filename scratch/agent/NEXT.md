# NEXT work unit — M3: characterize the `frameStartReset` SIGBUS (s84, new)

s84 landed the thr-resume `bad=1` gate (`lib/N64ModernRuntime/ultramodern/
src/threads.cpp:198-238`, `[thr-resume-skip]`, exported + committed, build
clean). The soak that validated the gate build instead surfaced a **new,
5th** crash class that fires **earlier** than every other crash in the
s81–s84 arc (hold+~1s — faster than s83's spline1 hold+3s, spline2
hold+12s, or s82's NaN hold+6s):

```
[CRASH] caught signal 10 (Bus error: 10)
frameStartReset + 532
  <- static_5_800AAD9C (runHangarSelectionFrame) + 1012
  <- static_5_800C6854 (runHangarMenuFromOverlay) + 628
  <- menuOverlayInit + 3512
  <- mainGameLoop + 2400
```

`frameStartReset` = 0x8000A6CC ("resets per-frame counters ..., calls
heapWalker, slot dispatch"). This is the **hangar-selection per-frame poll
loop itself** (runs while still inside SELECT YOUR CRAFT / during the leave
transition) — a completely different subsystem from the thread-resume/
semaphore path s70–s72/s83/s84 target. No overlap, no shared code path.

Because it now fires before any of the other 4 crash classes get a chance
to recur, it blocks validation of **both** the s84 thr-resume gate
(`bad_total` never leaves 0 — no positive control) **and** the s83 Metal
SIGSEGV reproducibility check (next-steps item 3). It is the new critical
path.

## Competing hypotheses

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| F1 | Unaligned load/store inside `frameStartReset` itself (same fault class as s80's parked `do_rom_read` Abort, different call site) | crash address is misaligned for its access width; static disasm of 0x8000A6CC shows a multi-byte load/store off a computed (not fixed) offset |
| F2 | A caller passes a bad/uninitialized pointer into `frameStartReset` (corruption upstream, not a local bug) | the faulting address itself is wildly out of any valid RDRAM/struct range (not just misaligned) |
| F3 | Timing-dependent: some other thread mutates state `frameStartReset` reads without synchronization (race), same general family as the s70–s72/s84 UAF work | crash offset/address varies run-to-run even with identical input timing; a rerun with unrelated code changes (e.g. thr-resume gate) shifts *when* it fires but not *whether* |
| F4 | Rare/nondeterministic — this run's early death was a fluke and it won't reliably reproduce | a second soak with identical env does NOT crash at `frameStartReset`, or does so at a very different hold offset |

## Discriminating measurement (start read-only, no code yet)

1. **Reproduce once more**, identical env to the s84 soak, to see if F4 is
   live:
   ```bash
   export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
   env PROBE_MODE=start_only HOLD_S=30 \
     zsh scratch/s73_post_a_scene/run_mission_keys.sh thrgate2 0 12
   ```
   Check `grep -a 'CRASH\|frameStartReset' run.log` and the hold-iteration
   count at death. Same site + similar early offset → F4 refuted, real
   dominant blocker. Different site, or no crash (holds full 30s) → F4
   supported, was a fluke; fall through to Next Steps item 2 (thr-resume
   gate retry) or item 3 (Metal SIGSEGV) instead.
2. **If it reproduces**, get the exact faulting instruction before writing
   any fix. `frameStartReset` = 0x8000A6CC; find it in the generated
   `RecompiledFuncs/*.c` (grep for the function's recompiled name — check
   `symbol_files/main_overlay.txt` for the exact translated symbol) and
   read the source around offset +532 (~133 instructions in, if roughly
   4 bytes/instr — recompiled C won't map 1:1, use the crash backtrace's
   native offset only as a rough locator, then correlate against the N64
   disassembly of 0x8000A6CC+0x214 for the real MIPS instruction). Identify:
   is the access at a fixed struct offset (favors F1 misalignment) or
   through a pointer chased from an argument/global (favors F2 bad pointer,
   or F3 race if the same global mutates under threads).
3. Only after step 2 identifies which of F1/F2/F3 fits, design the actual
   fix (likely an alignment guard or a null/range check at the load site,
   same pattern as the s78/s82/s84 gates) as a **separate** iteration —
   this work unit's job is diagnosis, not a same-iteration patch, since
   there is no existing detector to extend here (unlike thr-resume, which
   already had `bad`/`live` computed).

## Do not
- Don't conflate this with the thr-resume SIGBUS the s84 gate targets —
  confirmed unrelated call stack, per PORTING-STATE s84.
- Don't re-run the thr-resume gate soak (next-steps item 2) yet — it will
  almost certainly die at `frameStartReset` again before generating a
  `bad_total>0` positive control, wasting a build-run cycle.
- Don't write a fix before step 2 identifies the actual faulting
  instruction — a guessed alignment guard on the wrong offset is the kind
  of "gate that never fires" the s84 soak (0/117218 `bad=1`) just
  illustrated the cost of.
- Spend more than 3 consecutive iterations on diagnosis without a
  discriminating result (ITERATION.md rule 8) — if F1–F4 aren't
  distinguishable after 2 soaks + 1 disassembly pass, go BLOCKED with the
  specific ambiguity named.
