# G1d title garbage rect: H-up167 byte compare
HYPOTHESIS-ID: g1d-title-garbage-rect
s6272 plume loop closed clean (16/16, control PASS). Next unclosed rung: widescreen title backdrop garbage rect (CURRENT-TRUTH item 1, s6234). Log LoadTile RDRAM source/dxt/tmem offset for up_167 (h98bb35b7e7c80445) at upload and compare RDRAM bytes vs uploaded bytes. Outcomes: equal -> RT64 sampling/tile mapping (H-cache); differ -> upload path (LoadBlock dxt). Include a force-mark positive control. Owner-optional; if it needs more than one iteration, park.
