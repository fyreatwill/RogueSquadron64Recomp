# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show c4755af1e:scratch/agent/NEXT.md).

# NEXT: name the game-thread phase that makes the 20-23 ms frames behind 21:9 level onsets
HYPOTHESIS-ID: g1e-level-onset-late-frame
s6966: 27/33 level onsets follow a present shown one vsync late; that frame's workload arrived 21-22 ms after the previous one (W gap), with
the present path clean. HITCH drain refuted as a fix; a shallow level (acq 3-4 ms) also evades ACQ=8. So fix the over-budget frames.
1. Boring first: grep src/ and lib/N64ModernRuntime for an existing per-frame game-thread stamp (G1B is per second; the [g1b-gt] row is a
   per-second histogram). If none, ONE instrument, ONE build: per gfx task a ring row (same present ring, "G" row) with wall t, game-thread
   time since previous task split into: sim/runInMissionFrame, DL build/send_dl, RSP task host ms, RDP/RT64 workload submit, and thread
   CPU vs wall (preemption = wall-cpu). Positive control: rows with total >= 20 ms must exist (a2 had ~0.15 misses/s).
2. Run lvl1 21:9 dd4 FPS60 (tools/g1e_owner_quiet_arms.zsh, HOLD 230, ACQ=8 only, 1 arm + 1 replicate), join G rows to the late presents
   (tools/g1e_late_present.py logic) vs normal frames.
   H-sim: sim/game logic phase grows on the late frame (fix: game-side cost, e.g. another CELLIDX-style host index).
   H-rsp: RSP task host ms grows (dense scene ucode cost).
   H-preempt: wall-cpu gap grows (host scheduling / E-core; fix QoS).
   H-submit: game waits on the RT64 workload queue (back-pressure from the present side).
3. Fix the winner; acceptance = misses/s and onsets/min down same run (toggle), lat p50 at 21:9 <=27 ms with no drain knob.
Defaults: DRAIN, DRAIN_ACQ, DRAIN_HITCH, SKYZ, SCREEN_JOB, INFLIGHT, PROVCACHE stay opt-in, owner decides. Owner reports override all of this.
