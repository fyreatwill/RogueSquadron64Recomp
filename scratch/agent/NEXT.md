# NEXT: G1 — what makes class-1 NPCs take lethal damage (msg 5), given msg 2 is the by-design out-of-range despawn?
CLOSED (s5830): msg 2 = out-of-range despawn (s5814/5817/5818/5823, four lines). Do not re-instrument it.
Hypotheses: (a) projectiles never register hits on class-1 NPCs in the port (collision/damage path divergence); (b) hits register but damage is small/NPC_INVULN-free hp not reached in a short approach; (c) kills need the ship inside the 144 radius for the death-effect arm's rand()&3 gate (copy 2).
Step 1 (static, cheap): find the function that decrements health at *(slot+0x38) (grep funcs for stores through the health owner / callers of getNpcCurrentHealth's setter) and its callers from projectile code.
Step 2: ONE build, ONE run (g1_approach.sh, NPC_INVULN unset): per class-1 NPC log damage calls (count, amount, hp before/after, caller via backtrace) + positive control "log every damage call to any object". Outcome: zero class-1 damage calls with nonzero control -> (a); calls with hp never <=0 -> (b); hp<=0 reached but no msg 5 -> (c).
HYPOTHESIS-ID: g1-mission-progression
