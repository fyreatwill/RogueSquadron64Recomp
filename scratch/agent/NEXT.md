# Next work unit: M5 Step 9j — name the second owner of the audio data_ptr heap band

HYPOTHESIS-ID: m5-audio-destub-sequence

s4211: data_ptr buffers (phase4 0x171CE0/0x173B20, phase5 0x171E70/0x173CB0) get no PI DMA but hold name text (mat_11, ltex_cache_329) and change every task. Tools: tools/apply_s4211_dp_writer.py, scratch/agent/s4211_dp_writer.sh (live-tree patches; never regen).

Hypotheses:
- H-heap-ownership: the guest allocator hands the audio cmd buffer region to another owner too (double allocation / free-while-live); second owner writes text.
- H-builder-overruns: the audio builder itself is fine but a name-table builder with a stale pointer writes into it.
- H-wrong-ptr: the audio thread's real cmd buffer is elsewhere; task data_ptr read from a stale OSTask field.

Discriminator (one build, one run): fixup-script hook (tools/fixup_game_funcs.py, per BREADCRUMB19 pattern) on rs_malloc/rs_free/rs_memcpy/rs_memset logging ret ptr+size/dest+len and ra when overlapping [0x80171C00,0x80174000) in phase>=3, plus guest-side dump of the OSTask data_ptr field at the audio thread's osSpTaskLoad call vs rsp.cpp's. Positive control: an all-range mode must fire thousands of times.
Outcomes: malloc returns overlapping live audio buffer from two callers => H-heap-ownership (name both ra's); only memcpy/memset ra's from name-table code with no malloc => H-builder-overruns; guest field != host dp => H-wrong-ptr.
