# Next work unit: why is the sample-stream node pool never replenished? (s4279)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4278: writer of head==0 is the legit unlink at 0x8008FD94 once pool (0x801499CC) hits 0 at ENTRY n~9514-9522, regardless of key timing (late arm crashes too). Nodes are bump-allocated 0x18 bytes each from 0x801F9D10..0x801FB2D0 (~231 nodes).
Hypotheses: H1 port calls fillSampleStreamRange far more often than retail (spin-yield / audio loop), consuming nodes faster than frees; H2 the free path (node return, probably stream-completion/DMA callback or audio-task completion) never runs in port; H3 retail also exhausts but handles pool==0 differently (port-only divergence).
Discriminator (one build/run set): (a) retail oracle (tools/oracle, physical watch on 0x1499CC pool word, whole-RDRAM positive control first) for pool trajectory + writer PCs and call rate; (b) port: log stores to the pool word vs ENTRY n to see whether any store ever moves it back. Outcomes: retail pool never nears 0 with far fewer calls -> H1; retail shows free-site PCs the port never executes -> H2; retail hits 0 too -> H3.
Scripts: scratch/agent/s4278_writer.sh (template), tools/apply_s4278_headwriter.py (live tree already patched).
