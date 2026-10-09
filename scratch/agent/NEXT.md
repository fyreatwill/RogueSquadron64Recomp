# Next work unit (s4447): who calls fillSampleStreamRange (0x8008FAAC) in the port when retail never touches the allocator list?

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4446): retail writes head/tail/pool (0x801499E4/B4/CC) once at init over 60 s; port inserts ~1 per call.
Hypotheses: (a) port-induced callers (a stream-playback path retail does not start in title, e.g. a sound the port triggers/loops); (b) retail uses the function but through a different allocator (exec-watch was unusable, so not excluded); (c) mis-executed guest path.
Discriminator: histogram of ra= in [s4234-ENTRY] rows (scratch/agent/s4441/port_A1.log; rows are only printed for n<=30 / head==0 / ra==0, so first 30 only) -- if insufficient, add a compact ra histogram to tools/apply_s4234_entryprobe.py (fixup script, not RecompiledFuncs). Then map callers' guest function names and check in oracle with write-watch on their state (fix exec-watch control first: use --watch-pc with a function that must fire many times, or check hit-cap semantics).
