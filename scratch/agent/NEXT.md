# NEXT (s5665): who owns/writes the voice sample buffer at 0x801B2C60 (= *(0x80154674))?
Fact (s5664): buffer is rs_malloc(streamSampleCountToByteSize(0x10E0)) from initMusyXVoiceTable; pointer is legit. H4 dead.
Hypotheses: H5 nothing decodes ring (0x801535C0) into it; H6 filled late (after several ring cycles); H7 allocator overlap: other allocs/DMAs land inside the block (6,722 PI DMAs overlap the wide range).
One build (fixup script, ROGUESQ_LOG_HUDBIT-gated): log rs_malloc return+size for the 0x10E0 call, any later rs_malloc/rs_free overlapping the block, and a write-watch on [buf, buf+size) with PC (control: writes by initMusyXVoiceTable's own users / known DMA). Outcomes: overlapping alloc -> H7; only voice-code writes -> H6; no writes at all while ring cycles -> H5.
Queue as soak; fold results next iteration.
HYPOTHESIS-ID: g2-voice-never-requested
