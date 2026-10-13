# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human): RSPRecomp is not in the headless allowlist (see
scratch/agent/UNBLOCK.md for the exact two rules). Do not work around it.
Until then, do NOT start the ovl2c splice regen.

Work unit (no RSPRecomp needed): static analysis of overlay 0x2C and a drafted fixup.
1. Disassemble the 0x240-byte image at ROM 0x27368 (dest 0x1DB0) with the repo's RSP
   disassembler / python; list every branch/jump target and confirm no target leaves
   the image except the two externals L_10D8 and L_112C (tests H-image-needs-more).
2. Summarize what it computes (vector ops, DMEM addresses read/written, whether 0x153
   is rewritten) so H-splice-fixes can be judged before any build.
3. Draft fixup 6r (model on 6k, tools/fixup_factor5_ucode.py ~line 1549) as
   scratch/agent/fixup6r_draft.py, NOT wired into the tool, so regen stays unbroken.
Positive control: run the same disassembly on overlay 0x1C (ROM 0x26EF8, 0x20C B) and
confirm it reproduces the known exit `j L_1268` / ori $5,0x20 at 0x1ECC.
When the allowlist lands: run RSPRecomp factor5_rsp_ovl2c.toml, wire 6r, regen
(make_elf -> N64Recomp -> fixup_game_funcs -> cmake), run scratch/agent/s4737_run.sh.
