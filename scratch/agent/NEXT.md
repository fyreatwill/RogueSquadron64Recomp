Single next work unit (s5648): D2 vs D3. In one instrument/build: log, per audio task, whether any ucode cmd-list address (A_SETBUFF/A_LOADBUF/A_ADPCM/A_RESAMPLE dmem<-dram addrs) falls inside [slot+0x198 target, +0x1000) or the +0x11C0 ring; positive control: mark-everything must match all cmds. Also hash the +0x198 buffer vs ROM speech region.
Outcomes: D2 (no cmd references the buffer) => the mixer never gets the voice, find the cmd builder (M5 de-stub). D3 (referenced) => loss is later; compare AI PCM with retail oracle in the same phase.
HYPOTHESIS-ID: g2-voice-never-requested
