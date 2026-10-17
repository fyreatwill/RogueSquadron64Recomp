# UNBLOCK (s5352) — route 1 (refute) + route 3 (re-scope)

Block claimed: (a) mips64-elf toolchain must be supplied; (b) a human must "authorize oracle-driving work" past attract.
- (b) is FALSE as framed. Authorization is not needed and the capability exists: CURRENT-TRUTH (s5330) records the in-process
  autopilot route `3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a`; s5335 ran both arms to the hangar with same-run
  positive controls (10,000 oracle whole-RDRAM hits; port reached 0x006AB400/512). The real obstruction is key-domain
  mismatch (retail RSP PCs 0x0088..0x0FE8 vs port generated PCs 0x112C/0x17F0; origins 0x006AB800 vs 0x006AB400), which is
  offline analysis, not a human decision.
- (a) is a real, already-documented NON-blocking dependency (clang has no MIPS target; no mips64-elf-gcc/ld). Installing it
  is out of bounds for this iteration; recorded as an open dependency only.
Re-scope: NEXT.md is now an offline work unit deriving an independently justified generated-PC -> IMEM-PC mapping.
