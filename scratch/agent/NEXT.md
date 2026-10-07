# Next work unit: M5 Step 9i — who writes ASCII into the audio command buffer (data_ptr) in phases 4/5

HYPOTHESIS-ID: m5-audio-destub-sequence

s4210: audio ucode handles 1 x 0x50-byte record per task. Phase 3: valid record (w30=0x104, w38=0x19004B0F), nonzero writes. Phase 4/5: record at data_ptr+0x10 (0x80171CF0 / 0x80171E80) holds ASCII ("expl","mat_11","tie_") and output writes are zero. Tools: tools/apply_s4210_cmd_ring.py, scratch/agent/s4210_cmdring.sh (live-tree patches; never regen).

Hypotheses:
- H-heap-alias: a loader/allocator writes filename text into the freed/never-owned audio command buffer (writer is a non-audio PC).
- H-builder-skip: the MusyX command builder (guest) writes only some fields; stale text remains because the buffer was allocated from dirty heap and the builder skips a field init our port never reaches (audio-disabled degenerate path).
- H-wrong-ptr: data_ptr is wrong (our scheduler/OSTask copy points at the wrong buffer; true buffer elsewhere is valid).

Discriminator (one build, one run): guest store watch (in the recompiled MEM_W/SW store helpers or a ring in the funcs store macro) on [data_ptr-0x10, data_ptr+0x100) of the CURRENT audio task, logging writer PC (ctx/ra) and value for the first 64 stores per phase, plus a whole-RDRAM-range positive control (must fire) and the stores made by the guest builder (PC in musyx range). Also dump the guest-side OSTask struct fields at osSpTaskLoad vs the host s_pending_task copy (data_ptr equality).
Outcomes: writer PC is loader/string code => H-heap-alias (find the allocator that owns 0x80171CE0); writers are only musyx and never touch +0x30 => H-builder-skip; data_ptr differs guest vs host => H-wrong-ptr.
Also try oracle (tools/oracle/README.md) in title phase to see if retail data_ptr buffers hold text.
