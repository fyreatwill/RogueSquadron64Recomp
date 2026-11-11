# NEXT: hop metric + owner sheet for NEARLIFT=1 NEARK=1.6 (constant, not toggled)
HYPOTHESIS-ID: fps60-wall-hop
Context (s7118): NEARK=1.6 removes the residual near-wall losses (steady 13/1 over 5 runs), but the lift fires on 8-19% of wall-hug ticks, p99 0.6-0.9 u,
max 1.3 u. The owner will judge it by eye; give them a number and a sheet first.
Hypotheses: H-smooth (the lift changes slowly tick to tick: its per-tick delta is under the natural camera y motion, so no visible hop),
H-hop (onset/offset steps: per-tick |delta lift| p99 exceeds the camera's natural per-tick y step at the same speed), H-shake (lift alternates on/off
on consecutive ticks near a wall edge -> jitter, a G3c(c)-style sign-alternating second difference).
Measurement (offline-first, one run): arm.zsh 6 4 m "<cmd_k env with ROGUESQ_S7115_NEARK=1.6 constant>"; from the push nl lines compute per-tick
lift delta, its second difference sign-alternation rate, and compare with per-tick eye y delta from rx/ch lines on non-lift ticks (same run).
Positive control: inject a known step offline (add 0.5 u to one tick) and confirm the metric flags it. Sheet: 6 frames around the 3 largest lift
onsets (tools/s7107_sheet.py on m.raw; keep the raw until the sheet exists) -> docs/owner_sheet_s7119_nearlift_hop.png.
Outcomes: H-smooth -> owner sheet, recommend; H-hop -> rate-limit the lift (ease over ~4 ticks) as ROGUESQ_S7115_NEAREASE, same-run tog;
H-shake -> add hysteresis (hold the lift N ticks).
