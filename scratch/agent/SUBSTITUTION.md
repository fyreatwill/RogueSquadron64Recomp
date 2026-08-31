The configured-host PatchesLib unit stopped because this iteration is running
in the Darwin Unix checkout and measured `E:/mips-toolchain` absent. The
configured Windows/MIPS host is not available here; the local missing-target
build was already checked in Session 3316 and was not repeated.

This iteration's evidence is `uname -srm` = `Darwin 25.4.0 arm64`, the current
workspace path under `/Users`, and the absent configured-host path. The
substitute source reconciliation is recorded in
`scratch/agent/s3317_m5_plan_reconciliation.md`.

The falsifying experiment is one run of
`cmake --build build --config Debug --target PatchesLib` on the configured
Windows/MIPS host, observing whether the target and inputs exist.
