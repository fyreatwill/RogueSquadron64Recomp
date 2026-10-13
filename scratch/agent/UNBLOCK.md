# UNBLOCK s4755

Route 1 (refuted). The claimed permission dependency was unnecessary: the
already-installed `../N64Recomp/build/RSPRecomp` accepts the local TOML
directly. Running `../N64Recomp/build/RSPRecomp factor5_rsp_ovl2c.toml` from
the repo root exited 0 and emitted the 85,853-byte
`build/factor5_ucode/factor5_ucode_ovl2c_recompiled.c`, including the
`factor5_ucode_ovl2c` entry point and generated jump table.

The 0x2C splice itself remains the next experiment; this file records only
that RSPRecomp no longer blocks it.
