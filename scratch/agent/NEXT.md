# NEXT: fold hangar_route f,g,h,i (SOAK-RESULTS.md), then G3 hangar native artifacts
HYPOTHESIS-ID: g4-crash-stall-hunt
Grep att=/crashlines/vi_stalls30s for s6008_hangar_route_f and s6009_hangar_route_g/h/i. att>1 or abort => lldb/ASan backtrace, name writer. 9/9 clean => edit CURRENT-TRUTH flake note to "not reproduced", close G4 hangar route, take G3: pick one parked hangar artifact (rim band) and name its writer via oracle/RDP-bin comparison. G2 is closed by owner ear; do not do PCM compare.
