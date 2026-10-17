# Who writes 0x03 at record+0x22 after the port's own clear
HYPOTHESIS-ID: port-byte-not-retail-clear

Session 5228: the port runs `sb $zero,0x22` (0x80090F3C) on 53/53 entry
records, yet the entry byte (0x8008FAAC read) is 0x03. A later writer
restores 0x03. The port also has 53 distinct entry bases vs retail's 41.

Competing hypotheses:
- H-generated-store: a recompiled store with offset covering +0x22 in
  musyxRenderVoiceSamples / the 0x20/0x21 update (0x80090720/780) lands on it.
- H-host-write: a host memcpy/memset (audio stub, DMA, LLE writeback)
  overwrites the record.
- H-read-is-stale-width: the entry read of 0x22 is a wider view whose
  neighbouring byte is 0x03 (check disassembly after 0x8008FAAC).

Discriminator (one build, one run, driver scratch/agent/s5228_port_stores.sh):
keep a shadow set of the 53 addresses; on every generated-store and host
write hook (rs64_m5_lowfield_store / rs64_m5_writer_parity exist) log
(pc, addr, value) when addr is in the set and value != 0 in phases
0x00620400/0x00690400; histogram by pc. Positive control: the 0x80090F8C
constant-1 store must show up as a writer row. Do the cheap static grep
first: MEM_B/H/W stores at offsets 0X20..0X22 off the 0x88-stride pointer
in funcs_23.c/funcs_24.c.
