# Next work unit: structural DL comparison, retail vs port (hangar VI 512)

HYPOTHESIS-ID: hangar-artifact-triage

s4508: raw byte diff of first VI-512 DL is uninformative (within-side variance 12k/16k bytes > cross-side 6k). Dumps in scratch/agent/s4508/ (oracle_w512_{0,1,2}.bin, port_w{320,512,640,1024}_{0,1,2}.bin), env RS64_GFX_DL_DUMP_DIR on both sides.
Hypotheses: H1/H3 port renderer/ucode vs H2 guest data bug.
Discriminator: parse DLs offline (python): command-class histogram, DL-call (06) targets, vertex-load (04) counts, texture (fd) address ranges, per frame; compare retail frames vs port frames. Differences in command classes/counts that persist across frames => H2; matching structure => H1/H3 (renderer). Control: port 1024 title DL vs itself across frames shows the natural variance band.
Also consider dumping at task completion to exclude mid-write capture, and a retail 1024 control (oracle only gates 512 phase).
