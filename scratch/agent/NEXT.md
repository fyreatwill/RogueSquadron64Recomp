# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human, NOT to be retried by iterations): RSPRecomp is not in the headless
allowlist (denied s4741, s4742, s4744, s4745). Do NOT run it, do NOT write "try it then go
BLOCKED" again — that loop wasted s4744. The 0x2C splice (fixup 6r draft at
scratch/agent/fixup6r_draft.py, toml factor5_rsp_ovl2c.toml) resumes only when a human adds
the allow rules (see scratch/agent/UNBLOCK.md) and removes this paragraph.

Work unit that does not need it: quantify what the runaway DL tasks (site-3 restarts via
L_1DB0, 10-14x per task, tasks 240+) cost the mission frame, using the already-working port
and s4737_run.sh / existing logs:
1. Offline first: from the s4737 logs, list per-task (a) restart count, (b) gfx commands
   consumed before/after the first restart, (c) whether ship/HUD display-list branches
   (the DL that should follow the terrain ribbons) appear in the walked command stream.
2. Discriminator: if ship/HUD commands are only reachable after the first restart point
   (the DL walk is truncated by the 0x2C fall-through) then the splice is the missing-ship/HUD
   fix; if they never appear even in non-runaway tasks, the missing ship/HUD is an unrelated
   cause (mission-object spawn) and the 0x2C splice cannot fix it. Positive control: a
   normal 1x task whose terrain commands are known to render.
