# NEXT: gate the ungated diagnostic helpers on the Gfx Thread and audio game thread
HYPOTHESIS-ID: host-selftime-audit
Context (s7067): tools/s7067_selftime.py over scratch/s7067/{on,off} (and s7066) shows diag = 6.4% of Gfx Thread on-CPU self
(rs64_dpc_record_submit_impl 329, rs64LogE9BoundaryCommand 157 [lib/rt64/src/hle/rt64_interpreter.cpp:289], rs64_e9prov_task_begin /
rs64_e9prov_authoritative_span 198 [src/rsp/dpc_bridge.cpp:2193/3282]) and ~10% of [Game] 0 (rs64_m5_lowfield_store 172,
rs64_s4307_synth_read 127). rs64_spike_scan is the default-on CULL_SPIKE: functional, leave it.
Hypotheses:
 H-ungated: each helper does real work (ring writes, string building) with no env flag set -> gate it behind a cached static,
   default off, keep the env to turn it on.
 H-needed: some feed a default-on feature (like spike_scan feeds CULL_SPIKE) -> leave, document.
Discriminator: read each helper's entry; then one same-build run with the sampler (scratch/s7067/both.zsh pattern, knob =0 arm
restoring old behaviour), diag self samples per helper on vs off, plus the s7066 getenv control still at 0.
Low value (~0.5% of a core). If an owner report arrives, it takes priority. lib/rt64 edits need submodule-patches/export.sh + commit.
