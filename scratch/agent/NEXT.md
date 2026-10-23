# NEXT: G3 in-flight retail/port frame pair (lvl1 Tatooine)

HYPOTHESIS-ID: g3-inflight-oracle
s5977: retail oracle reaches mission 1 with alternating start/A presses (scratch/agent/s5977_retail_flight.sh) but the late start presses leave it PAUSED. Do: copy recipe to s5978, stop presses after ~75 s (check oracle.log origin 0x620400/0x690400 first appears ~78 s: stop at ~85 s; avoid start after that), dump 0x620000 and 0x690000 at 110 s, convert with scratch/agent/s4506_fb_png.py (origin start width 512 height 440). Then take the port lvl1 flight fbd dump (see docs/g1_flight_contact_sheet.png source files) and diff visually: terrain, craft, HUD, sky. Any visible port-only defect = datum to root-cause (name writer). No aim/steer work.
Outcomes: unpaused retail frame obtained -> pair; port differs -> G3 defect list; matches -> G3 in-flight closed for lvl1, repeat other levels needs retail route (hard).
