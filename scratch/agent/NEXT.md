# NEXT (s7478)
HYPOTHESIS-ID: canary-one-byte-past-request

Class EF (M3 idiom-class): the s7475 slack canary still reports two 1-byte stores exactly at offset == request size, in the
8-byte rounding slack (s7476_canary_flight logs scratch/s7476_canary/log_l*.txt, `[s7475] slack-store`):
  (1) rs_memset pc=0x800078EC a=0x800CDB38 blk=0x800CAE80 req=0x2CB8 alloc=spawnCutsceneObjectsFromList+0x214c t=10.9 (all arms)
  (2) parseImageFile pc=0x8001EE04 a=0x809B601C blk=0x809B6010 req=0xC alloc=loadDatFile+0x8de0 t=11.1 (L15 21:9 dd8 only)
Hypotheses: H-retail (retail code writes req+1 bytes: an off-by-one the 8-byte rounding hides; same store on hardware) vs
H-port-size (a port patch shrinks the request, e.g. a dd/wide size computation or a size fixup) vs H-attr (the canary's
alloc attribution / req is wrong: spawnCutsceneObjectsFromList+0x214c is past any real function end, and 0x800CAE80 is in the
static .bss range, not an rs_malloc arena -> check how the canary registered that block).
Discriminator, offline first (no build):
 1. Disassemble both writer sites in the ROM ELF (tools/make_elf.py output, mips64-elf-objdump) and the caller of rs_memset that
    passes length; read whether the length is req+1 or the memset starts at +req (string NUL / terminator idiom).
 2. Check the canary registration path for blk=0x800CAE80 (grep s7475 canary in src/main/upstream_compat.cpp): is it a heap block?
 3. If still open: oracle (tools/oracle/README.md) write-watch physical 0x0CDB38 and 0x9B601C w/ positive control; same PC ->
    H-retail (whitelist the two sites in the canary, document); none/different -> H-port-size, name the writer.
Close with: each site classified, canary allowlist or fix landed, s7476_canary_flight re-scored clean.
