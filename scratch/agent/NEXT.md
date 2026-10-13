# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human, NOT to be retried by iterations): RSPRecomp is not in the headless
allowlist (denied s4741-s4745). Do NOT run it. The 0x2C splice (fixup 6r draft at
scratch/agent/fixup6r_draft.py, toml factor5_rsp_ovl2c.toml) resumes only when a human adds
the allow rules (see scratch/agent/UNBLOCK.md) and removes this paragraph.

s4749 result: 0xBD <=> 2C arrival <=> runaway (150/150 vs 0/550). H-bd-always-2c selected.
The runaway question is closed; what remains is the splice (blocked) .

s4750 DONE: offline decode of 0x2C in docs/F5-OVL2C-TEXRECTGEN.md (texrect emitter; post-splice test = count 0x24/0x25 words per mission frame vs retail).

Work unit if still blocked: (decode part done) now an M5/M3 audit or, if unblocked, the splice. Old text: M5/M3 idiom-class audit per CURRENT-TRUTH Next steps, or an
offline decode of what a 0xBD op's operands mean (docs/F5-UCODE-REFERENCE.md TexrectGen) to
predict the expected texrect output once spliced. Do not add more runaway counters.
