# NEXT: G1d step 26 - OSMEM=12: why is the scanned-out frame garbage (loop is alive)
HYPOTHESIS-ID: g1d-widescreen
Known (s6133): frame loop runs at 12 MB (swap-ack cycles ~30/s); fbd frames 3000-4500 identical stripe garbage; harness hardcodes origin 0x00790400 (m6_god_common.sh:30) so 12 MB runs read "notitle".
Hypotheses: H-ci (RDP color-image address >8 MB masked/clamped so RT64 draws elsewhere), H-vi (RT64 reads VI origin 0xA90400 from a 8 MB-bounded rdram view), H-nodraw (game never issues draws; fb is uninitialised memory).
Discriminator: one run OSMEM=12 logging per frame the SetColorImage address, VI origin and a hash of rdram at that origin after the RDP task; positive control = same logging at 8 MB. Also make the harness origin check accept a regex/ROGUESQ-derived origin.
