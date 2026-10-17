# Next: pick the next M3 idiom class (unsigned-base class is closed and gated, s5097)
HYPOTHESIS-ID: m3-idiom-class-audits

Enumerate another whole idiom class by grep (e.g. other 64-bit zero/sign-extension hazards in diagnostics:
`(uint32_t)` / `U32()` applied to a register that is then used as a MEM_x base; `r->r*` unsigned 32-bit adds
without S32 feeding MEM_x). Classify every site, guard or prove dead, add a positive control in the same run,
and, if code changes, add a post-condition in the fixup like s5097. Avoid reactive single-crash chases.
