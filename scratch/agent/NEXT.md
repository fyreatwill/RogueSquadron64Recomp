# NEXT: owner reports first; otherwise RSP-ucode fixup census (build/factor5_ucode vs a pristine RSPRecomp pass)
HYPOTHESIS-ID: rsp-ucode-fixup-census
Context: s7090 closed the CPU fixup layer (tools/s7090_fixup_statement_census.py: 0 untagged dup/drop in 2,476 functions;
positive control = pre-s7089 funcs_24). The recompiled RSP microcode in build/factor5_ucode/*.c (12 files, 0 PATCH tags)
is written by RSPRecomp and then edited by tools/fixup_factor5_ucode.py, apply_fixup24_ovl2cdrop.py, apply_s4210_cmd_ring.py,
apply_s4220_snap.py, apply_s4805_ovl2c_mode.py. That layer was never compared to a pristine pass.
Step 0 (boring first): is build/factor5_ucode compiled into the game at all, and which files? (grep CMakeLists.txt for
factor5_ucode; check how the gfx ucode runs: LLE interpreter vs these recompiled files). If unused, record it and close.
Unit (offline):
1. Regenerate a pristine RSPRecomp output for each ucode into scratch/s7091/pristine (find the RSPRecomp invocation and
   .toml configs the fixup scripts expect; do not write into build/).
2. Adapt the s7090 tool (per function / per RSP address statement multiset; RSPRecomp comments look different, check).
3. Classify every difference: tagged / named by a fixup script (grep the script for the needle) / untagged dup / drop.
Controls: positive = apply one fixup's edit twice to a copy (or revert one) and show it is flagged; negative = an untouched file.
Expected outcomes: all differences owned by a named fixup (closes the RSP layer), or N untagged sites, each a writer + fix
+ rebuild + L6 boot (`zsh scratch/s7089/run.zsh`).
