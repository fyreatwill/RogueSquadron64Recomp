Single next work unit (s5619): fold the s5618 soaks (s5618_nopoke_{a,b,c}, s5618_poked_ctl) from SOAK-RESULTS.md.
Method: grep '\[hudbit' scratch/agent/m6/s5618_*/run.log. Resolve each ra to a function name via syms/rogue_squadron.syms.toml (or tools/disasm_mips_elf.py). Positive control: poked_ctl must log >=1 [hudbit4]/[hudbit8] call, else the instrument is unproven and nopoke zeros mean nothing.
Hypotheses (H4b refuted statically s5618): H4a-i lv0_checkComplexObjectives sites; H4a-ii script call via hookSetHudEnableBit4; H4c gate written without setter call.
Outcomes: ra in datItem*/actor-destruction code => H4a; timer/ally function => H4b; no call but gate 4 => H4c, then find writers of 0x8010CA20 (m6 doc).
If soaks have not run yet, do offline work: static callers of 800C7738 (funcs_44/48 lines) classified by function.
HYPOTHESIS-ID: m6-mission-endurance
