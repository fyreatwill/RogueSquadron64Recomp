# Next work unit (s4431): who selects the selector entry (0x80091CB8 vs 0x8008EE84)?

HYPOTHESIS-ID: m5-selector-entry-path

s4430 closed the table-contents branch: port == retail for the title heap words.
Remaining divergence: retail title enters 0x80029E80 from 0x8008EE84; the port
enters exact 0x80029E78 (via 0x80091CB8 -> 0x80029D20 predecessor) in title.

Hypotheses:
- H-state-flag: a state word read before the branch (in the function containing
  0x8008EE84 / 0x80091CB8) differs between arms (port-side init gap).
- H-caller-mix: both arms call both entries but at different frequencies/phases.
- H-instrument: port has no witness at 0x8008EE84 (generated-code coverage).
Discriminator: one paired run: retail execution watch on 0x8008EE84, 0x80091CB8,
0x80029E78, 0x80029E80 with the branch-condition registers at the splitting
branch; port: static census of funcs for 0x8008EE84 (is the site in generated
code?) + callers witness. First step: disassemble 0x8008EE60-0x8008EEA0 and
0x80091C90-0x80091CC0 to name the splitting condition. Controls: whole-RDRAM
watch (>=10k hits), title+hangar VI. Port recipe: scratch/agent/s4429_port/run.sh
(needs ROGUESQ_LOG_ALL=1).
