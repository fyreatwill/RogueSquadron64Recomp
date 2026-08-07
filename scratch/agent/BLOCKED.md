# BLOCKED (s421)

## What's needed
A human decision on where the project's focus goes next. Not a technical blocker — the environment,
tools, and build pipeline are all working fine (this session closed a major M4 item end-to-end,
including a full build+live-verify cycle, with no infrastructure problems).

## From whom
The user (per `docs/CURRENT-TRUTH.md`'s "USER DIRECTIVE (2026-08-04, human-set)" section, which
explicitly reserves priority-setting to the human once its listed legs are exhausted).

## Why now
The USER DIRECTIVE set a strict priority order: (1) maintenance, (2) M5 audio de-stubbing, (3) M3
idiom-class audits only, with M4 item -249 (`main_overlay.txt` phantom-function relocation) as the
sanctioned fallback once M3's idiom-audit method was exhausted (s397). This session closed M4 item -249
entirely (784 functions relocated, 0 actionable candidates remain — see `PORTING-STATE` session 421 and
`docs/PROJECT-OVERVIEW.md` §15). That means **all three legs of the directive are now simultaneously
closed or exhausted**: M5 fully closed, M3 idiom-audit-only exhausted since s397, and now M4's fallback
closed too. There is no sanctioned autonomous work unit left under the current directive.

## What was already tried
Nothing needs re-trying — this isn't a stuck-experiment situation. `scratch/agent/NEXT.md` lists three
concrete candidate next directions the closure surfaced (most promising: a dedicated root-cause session
on the `last-guest-pc=0x800290d4` crash site, which now has SIX independent trigger functions found via
this session's and prior sessions' bisection work — the strongest lead currently on the table). None of
these are sanctioned by the current directive, so none were started.

## What the human needs to do
Pick one (or set a new priority order entirely) and update the USER DIRECTIVE section of
`docs/CURRENT-TRUTH.md`, or explicitly tell the next iteration to proceed with a specific candidate from
`scratch/agent/NEXT.md`. Two minutes: read the "Candidate next work" section of NEXT.md, pick one line.
