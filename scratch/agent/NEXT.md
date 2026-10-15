# Next work unit

HYPOTHESIS-ID: m5-audio-destub

30 Hz pacing is PARKED (s4906): fullSync ~12.9 ms = tiles 3.1 + renderSync 3.2 + postEvict 2.3 + updateScreen 3.9, control passed. Host-bound; do not resume unless a new idea (optional: updateScreen 3.9 ms may be a swapchain/vsync wait).

Do: resume M5 audio de-stub. Read docs/M5-AUDIO-PLAN.md step table, then pick the first row not marked qualified/closed. Last soak evidence: s4854 single-source H-port-load-unreached (port_control=0, port_rows=0, sp_enter=1255, pcm>0) -- the port-load control was absent, so qualify it (positive control first) or select the next open row. Write 2-4 hypotheses + the discriminating measurement here BEFORE building; one build, all arms concurrent.
