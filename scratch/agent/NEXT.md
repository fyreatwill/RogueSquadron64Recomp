# Next work unit (s4476): M3 systematic idiom-class audit (priority 3; M5 closed at s4475)

HYPOTHESIS-ID: m3-idiom-class-audit
Pick ONE not-yet-audited idiom class (see M3-S3597..S3605 docs and the s282-s288 -0x25A4 model for the method): grep-enumerate every site in generated code, classify each, guard or prove dead, commit the guard/fixup. No reactive single-crash chases.
H1: class has unguarded live sites; H2: all sites dead/guarded -> close class.
Discriminator: per-site classification table with a positive control (a known guarded site must be found by the same grep).
Optional: s4474 guard-fire positive control (force a guard once) if cheap.
