# RS64 recomp — UNBLOCK iteration

The loop stopped because a previous iteration wrote `scratch/agent/BLOCKED.md`.
You are NOT running a normal work unit. Your only job is to make that block
false, or to prove it is real. Read `scratch/agent/BLOCKED.md` first, then
`scratch/agent/NEXT.md`.

Everything in `tools/agent/ITERATION.md` about evidence still binds: positive
controls, phase-gating, two independent sources, no cross-run A/B on animating
scenes. What changes is the objective.

## The block is a CLAIM, not a fact

An iteration that hits a wall writes down the wall as it understood it at the
time, in a context that had already been narrowed by the work unit. Treat it as
an unverified hypothesis authored by someone with less information than you
have now. Work the four routes below IN ORDER and stop at the first that works.

### 1. Refute it

Try to make the dependency unnecessary. Most blocks in this project's history
were not missing resources; they were missing readings of resources already
present.

- Read the `--help`, README, and source of the tool that is "blocked". A
  measured example: an iteration blocked four times needing an alternate
  Mupen64Plus RSP plugin, while the oracle's own `--help` said
  `--video PATH  (default none -> core dummy, no RDP at all)` and two video
  plugins were already installed. Attaching one produced the exact phase
  progression the alternate RSP was supposed to reveal. The block was real as
  written and false as reasoned.
- Ask explicitly: **what observation would prove this dependency unnecessary?**
  Then go make that observation. If you cannot name one, you have not
  understood the block well enough to escalate it.
- Check whether the blocked measurement has a second route to the same
  discriminating answer using materials already on disk.

### 2. Satisfy it locally

If the dependency is real but obtainable without a human decision — an
already-installed alternative, a rebuild of something in the repo or in a
source tree this project already maintains, a flag that was never passed — do
that and verify it works before declaring it resolved.

### 3. Re-scope

If the dependency is real and not locally obtainable, the project does not
stop. Rewrite `scratch/agent/NEXT.md` as the highest-information work unit that
does NOT need the blocker, record the blocker as an open dependency in
`docs/CURRENT-TRUTH.md`, and let the loop continue on that instead.

### 4. Escalate

Only if all three fail. Leave `scratch/agent/BLOCKED.md` in place, rewritten to
state what you tried this iteration and the one experiment that would refute
your conclusion. The loop will stop and notify the human.

## Hard boundary — what stays a human decision

Do NOT, under any circumstance, resolve a block by:

- installing software from the internet, or downloading and running binaries;
- spending money, raising a quota, or changing a billing setting;
- changing system, security, or privacy settings (TCC, permissions, keychain);
- disabling a safety check, gate, or guard to make the symptom disappear;
- weakening a measurement so a failing result passes.

If the block genuinely needs one of these, that is route 4. Say so plainly.

## Deleting BLOCKED.md is a claim you must earn

The loop verifies you: after this iteration it re-runs `stop_gate.sh --verify`,
and if `BLOCKED.md` is gone while the exit contract is unmet, it restores a
block and stops anyway. Removing the file without resolving anything wastes an
iteration and the loop will catch it.

Also write `scratch/agent/UNBLOCK.md` recording: which of the four routes you
took, the evidence, and — if you resolved it — the specific observation that
proved the block false or satisfied it.

## Exit contract

Same as a normal iteration, and the same gate enforces it:

1. Append a dated session entry to `PORTING-STATE.md` describing the block and
   what you did about it. A refuted block is a real result — write it up as one.
2. Update `docs/CURRENT-TRUTH.md` if a conclusion changed.
3. Rewrite `scratch/agent/NEXT.md` with the next work unit and a
   `HYPOTHESIS-ID:` line.
4. `git add -A && git commit` (message: `unblock: <one-line outcome>`).
5. Write `scratch/agent/STATUS`: `DONE` if the loop may continue, `BLOCKED` if
   you took route 4.
6. Write `scratch/agent/OUTCOME`: `ADVANCED` if you resolved or refuted the
   block, otherwise `BLOCKED`.
