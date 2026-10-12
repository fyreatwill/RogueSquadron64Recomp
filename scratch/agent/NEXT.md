# Next work unit

HYPOTHESIS-ID: m3-load-idiom-census

s4704 closed the `LD` census (11 GPR sites, none pointer-forming). M5 plan has no unchecked steps.
Next: census `do_lwl`/`do_lwr` (212/206 sites) with a tools/census_lwl.py modelled on tools/census_ld.py: pair each lwl with its lwr, classify unaligned-word copy vs pointer reconstruction, assert counts equal an independent grep. Discriminator: any site whose dst feeds a MEM_*/address use without a named valid writer. If none, M3 load-idiom classes are fully closed; then ask the owner for a new mission-entry discriminator (BLOCKED) rather than starting another sweep.
