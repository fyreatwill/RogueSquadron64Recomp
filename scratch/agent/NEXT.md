# Next work unit (s4299): name the writer of the ASCII text in stream-node ROM pairs (first 8 bytes of 24-byte nodes {romA,romB,size,dram,prev,next}), found at s4298

HYPOTHESIS-ID: m5-audio-destub-sequence

State: crash source is musyxSynthFrame -> submitDmaRequestBatch with devAddr = ASCII base. Node array seen at rdram 0x17DBE0 (stride 0x18); neighbours valid. Recipe: scratch/agent/s4298_romread.sh (copy; bump the OUT name). Competing hypotheses:
- H-name-copy: the mission/model loader strcpy's names (name table 0x15CC34..0x172390: tie_wing_lod ...) over live nodes (writer is a guest store with PC; legit data, wrong destination = stale pointer / freed heap reused).
- H-stale-node: musyx still references freed nodes; heap block was freed at mission start and reused for strings (retail's audio stop-all on mission change not reached in port).
- H-host-write: an RT64 copyToRAM / host DMA writes the text (check [s4298-rtw] ranges: log is already emitted, join against node address).
Discriminator: at the bad batch the node address is known (hit address minus field); join (a) [s4298-rtw] ranges covering it (host), (b) guest store watch (apply_s4222_storewatch.py, retarget to the node block 0x17D000..0x17E200, log PC + value when value top byte is ASCII 0x20..0x7E) — positive control: any store in range. Writer PC -> function name decides name-copy vs other. Also check retail with tools/oracle whether the same nodes get text (H-real).
