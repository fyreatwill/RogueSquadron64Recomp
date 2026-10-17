# Choose the next work unit after closing the entry-byte thread
HYPOTHESIS-ID: m5-audio-destub-next-step

s5229 closed port-byte-not-retail-clear (census read lacked the MEM_B ^3
swizzle; port entry byte is 00/01 like retail). Nothing to guard.

Next unit: read docs/M5-AUDIO-PLAN.md rows 12+ and the Next-steps list; pick
the first open M5 step and write its design + validation row there BEFORE
touching runtime. If M5 has no open step, do an M3 idiom-class audit
(grep-enumerate one class, classify every site, guard or prove dead).
Do not re-open the retail-entry thread without an angle independent of the
s5223-s5228 byte census. Audit for other raw rdram[] byte reads lacking ^3
in fixup/census code is a cheap first sub-step (grep `rdram\[[a-z_]*\]` in
tools/fixup_game_funcs_vendored.py and src/main).
