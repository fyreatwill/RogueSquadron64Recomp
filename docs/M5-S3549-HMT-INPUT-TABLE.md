# M5 session 3549 — HMT input table

The regeneration-safe table covered `loadDebugAssets` (`0x800246E8`),
`registerHmtTextureInTable` (`0x80022B90`), and `parseHmtMaterials`
(`0x80022A00`). The corrected Debug build passed its HMT positive control and
emitted 256 rows before the process crashed in the pre-title route with
`last-guest-pc=0x8000834C`; it reached only 640-wide VI origin `0x0066A500`,
not title or hangar.

The table proves the HMT entry path executes. It does not prove malformed
input: the provisional `bad` bit treated every non-pointer-like scalar as
suspicious, so ordinary indices and counts set it. The first rows include
mapped guest pointers such as `0x80165F48`, `0x80165F70`, and `0x80787840`,
alongside scalar values. `H-HmtEntryAbsent` is refuted; valid-versus-malformed
input remains unresolved.

Evidence: `scratch/agent/s3549_m5_hmt_input_table_fixed3/run.log`.
