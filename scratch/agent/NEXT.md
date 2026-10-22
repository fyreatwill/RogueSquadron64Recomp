# NEXT (s5889): does protecting class-2 (DAT type-0x14) descs let c1 climb past 8 toward 21?
Context (s5888): class-2 = DAT type-0x14 entries spawned by setupNpcUpdateFunctions via grid-cell activation (offline, single-source); co-located with class-1 by level data.
Hypotheses: (a) fail arm (c2==3) is the only blocker - with class-2 invulnerable, c1 keeps rising when fire hits class-1; (b) c1 saturates near 8 even with class-2 alive (class-1 reachability/aim, not class-2, is the limit); (c) class-1 teardown itself requires killing co-located class-2 first (shield semantics in script).
Discriminator: one run, ROGUESQ_NPC_INVULN=1 (class-2 only, tools/apply_s5806_npc_invuln.py) + g1_fireall.sh recipe (scratch/agent/s5887_pos.sh as template) + [m47]/[ctr1] c1 time series, 600 s hold, alive. Control: same recipe without INVULN ends via fail arm c2=3 (s5847/s5848). Also dump desc +0x00/+0x70 for 80319E5C/CCE/A9C at first msg=3 to confirm type 0x14/class 2.
Outcomes: c1>8 and rising => (a), next steer fire at class-1; c1 flat ~8 alive => (b), next log player-vs-survivor distance; c1 flat and class-1 descs never hit while class-2 invulnerable => (c).
HYPOTHESIS-ID: g1-mission-progression
