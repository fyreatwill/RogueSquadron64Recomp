# Next work unit: M5 Step 9s — who writes the voice-record gain words (+0x00..+0x0C), and why zero in the port

HYPOTHESIS-ID: m5-audio-destub-sequence

s4220: port voice records have zero gain words in phases 4/5 (0/181) vs retail 14/16 nonzero; ucode exonerated.

Hypotheses:
- H-writer-never-runs: the guest MusyX routine that computes per-bus gain (volume*pan*master) is not reached for active voices in the port (stubbed/gated audio path, e.g. synth tick or volume-update function).
- H-writer-runs-zero-input: it runs but its input (voice volume / master volume / fade state) is 0 in the port (an upstream init that retail does, e.g. sfx volume set at boot, is skipped).
- H-overwritten: gains are written nonzero then cleared before the task (reaping/zeroing of the record).
Discriminator (one build, one run): port guest store-watch with PC on voice records' +0x00..+0x0C for voice 0..3 of the block at data_ptr (phase 5), logging store PC + value + a running count of nonzero vs zero stores; positive control: the same watch in phase 3 (4/5 rows nonzero) must fire with nonzero values. Writer PC never fires (only the clear/init) => H-writer-never-runs; fires with value 0 => runs-zero-input (then trace the operand); nonzero store followed by zero store => overwritten. Also arm oracle write-watch on the same retail field (tools/oracle/README.md, physical addresses, whole-RDRAM control first) for the retail writer PC. Reuse apply_s4218_active_voices.py to locate the block.
