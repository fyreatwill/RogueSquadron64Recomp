# NEXT (s7500)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7499_ex_levels (tools/s7499_ex_recipe.zsh; `s7499_ex_levels ex arm=` rows in scratch/s7499_ex_levels/out.txt):
live=0 ctlst=ok on L1 dd8 21:9 / L7 / L10 / L12 dd4 -> EX CLOSED 6 levels. live>0 -> read `[s7499] x cls=live` rows first (that is the work unit).

Work unit: class EY, resurrection of a stale-covered image. s7499: 50-72 (A, B) pairs where A's writeback covers an image B last set >= 2
swaps earlier (e.g. 320-wide boot images under the 640 image). EX scored them as dead, but age is only "swaps since the last set".
Hypotheses: H-ey-dead (no covered B is ever set again) / H-ey-rewrite (B is set again, but RT64 or the game redraws or clears it before any
read, so no stale bytes are consumed) / H-ey-read (B is set again and read, as an fb-as-texture load or a guest load, while it still holds A's
bytes: name A, B, the reader).
Instrument, ONE build: in s7499_ex, record each stale/est cover event (B key, A key, wb#, swap). In rs64_s7493_img, when a covered B is set
again, log `[s7500] reset` with the gap in swaps and the first event on B after that: a fill/clear (rt64 fillRect keyed by colour address,
the s7497 zdraw hook), a draw, or an fb-as-texture read (find RT64's fb-texture load path in lib/rt64; edits under lib/ need export.sh).
Control: ROGUESQ_S7500_CTL re-sets the first covered B artificially, which must log `reset`.
Run: `env XC=ROGUESQ_S7500_EY=1+ROGUESQ_S7500_CTL=1 zsh tools/s7499_ex_recipe.zsh` (L4 dd1, L15 dd8 21:9).
