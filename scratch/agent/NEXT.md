# Next work unit (s4502): audit audio shutdown function rs_free sequence at 0x80091DA0

HYPOTHESIS-ID: m3-idiom-class-audit

Audit the 16 unaudited `jal rs_free` sites 0x80091DEC..0x80091F9C (list in
docs/M3-S4501-RS-FREE-CLASS-CLOSURE-TALLY.md) as ONE function: what each frees
(source field), whether the function is reachable in the port (S3605 says it is
skipped/null-destructor related), writer of each pointer, double-free risk,
guard or prove dead. Use scratch/agent/s4500_dis.py. If the whole class is then
closed, pivot to M5 de-stub plan (docs/M5-AUDIO-PLAN.md) next.
Hypotheses: H-Dead (function never runs in port), H-Guarded (frees are
null/once-only), H-Unguarded (needs a guard). Discriminator: reachability +
per-site pointer writer. No runtime run needed first.
