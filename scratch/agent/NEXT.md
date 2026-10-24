# NEXT: G1d step 27 - OSMEM=12: control run + where RT64 draws
HYPOTHESIS-ID: g1d-widescreen
Known (s6134): RT64 caps at workload_queue:500 and f3dfactor5:193 widened; 12 MB still ends "nomission" with garbage fbd frames, VI origins vary (0xA96100/0xAAB400/0xB90400).
Hypotheses: H-ci (some other bound drops/relocates >8MB colour images, e.g. fbManager readback/present), H-game (game at 12 MB never reaches flight; garbage is legit uninitialised fb), H-dump (fbd dumper reads wrong address/size at 12 MB).
Discriminator: run the SAME recipe at ROGUESQ_OSMEM_MB=8 (positive control; TITLE_ORIGIN default) and 12, logging per VI the SetColorImage address, VI origin, and rdram hash at origin after the RDP task; compare whether RT64 write-back lands at origin.
