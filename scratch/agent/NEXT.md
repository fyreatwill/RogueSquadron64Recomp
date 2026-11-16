# NEXT (s7479)
HYPOTHESIS-ID: canary-zero-slack-blocks

0. Fold scratch/agent/SOAK-RESULTS.md: s7478_canary_restale (L4/L7/L12 dd4, L15 dd8 21:9, HOLD=220). Pass = plant DETECTED,
   tail_hit_nonplant=0, slack_store=0 on all arms, stale_drop>0 expected. A non-zero slack_store row now means a LIVE block (hdr_ok=1):
   read its [s7478] store-bt/alloc-bt chain and name the writer (that is a real class, not EF).

Class EG (M3 idiom-class, heap overruns the s7475 canary cannot see): every s7475 summary shows noslack ~4780 vs rec ~3910, i.e. MORE
THAN HALF the rs_malloc blocks have req == rounded size and carry no canary band at all (and the walker only checks headers).
Hypotheses: H-clean (no live overrun in zero-slack blocks either) vs H-hidden (an overrun exists but lands in the next block's
header/body, which s7472 only sees when it breaks a header) vs H-pad-perturbs (padding changes layout enough to move/hide a bug).
Instrument (one build): ROGUESQ_S7475_PAD=<n> (default 0): under the canary, rs_malloc entry adds n (16) bytes to the request
(guest a0 at 0x80001ACC entry via the existing s6063 malloc hook path, or a tools/apply_* fixup at the rs_malloc prologue), records the
ORIGINAL req so [req, size) is the canary band for every block. Positive controls: existing in-flight PLANT + boot A1FIX=0 arm (ED overrun
must still score, hdr_ok=1). Run tools/s7475_canary_recipe.zsh LV="4:4 7:4 12:4 15:8" with PAD=16 (queue as soak if host busy).
Outcome: 0 live slack-stores with noslack~0 -> H-clean, class closed; live store -> name writer via the s7478 chains; boot hang or
behaviour change with PAD only -> H-pad-perturbs, record and fall back to a store-watch on next-block headers.
