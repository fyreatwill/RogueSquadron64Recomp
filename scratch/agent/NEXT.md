# Next work unit

HYPOTHESIS-ID: oracle-poke-mission-entry

s4725: retail mission VI = 512 wide at 0x69xxxx; retail game code writes 0x1F0D70..80 (292 writes, PCs in PORTING-STATE s4725).
Unit: rerun scratch/agent/s4725_run.sh adding `--post-value-watch 1` (and a post-value PC from the writer list e.g. --post-value-pc 0x800078EC) to capture the stored word values at 0x1F0D74; compare to the port's width-1161 colour-image word. Add a phase gate so hits are not exhausted by hit-cap.
Outcomes: retail stores a 1161 width => legitimate, port-side guards are masking real behaviour; retail stores other values => port writer is wrong, trace the port's equivalent PC.
Positive control: whole-RDRAM watch fires.
