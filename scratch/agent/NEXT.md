# NEXT (s7465)
HYPOTHESIS-ID: host-uninit-padhash

s7464 closed class DU (quiet-arms spec split: s7463_padhash_flight's CONTROL FAIL was 4 phantom arms, cnt data lost; harness now
rejects bad specs, exit 3). Re-queued scratch/agent/soak_queue/s7464_padhash_flight.sh (L4 cnt PADCOUNT=1, L1 ctl PADCOUNT=ctl,
both dd4, HOLD=150, R=scratch/s7464q).

Hypotheses for flight: H-const (cnt distinct_raw==distinct_fixed at every site: fix is latent-only) vs H-split (raw>fixed at some
site: old code fragmented that cache in flight; quantify from dck_newkey extra=) vs H-unreached (reinterpret site 0 calls in flight).

Step 1: fold s7464_padhash_flight from SOAK-RESULTS.md + scratch/s7464q/s7463.txt.
  - CONTROL PASS -> one line under item 1 DS with per-site verdicts; close DS.
  - CONTROL FAIL with arm alive -> grep '[s7463] mode' scratch/s7464q/log_ctl.txt (env reached the game?).
  - not yet run / void -> do Step 2 meanwhile.
Step 2 (new slug host-null-deref-audit): class DT, analyzer null-deref / CallAndMessage findings in host code
  (tools/s7463_uninit_census.py line B, widen B_RE to "null pointer|Called C\\+\\+ object pointer is null"; main.cpp:12987,
  plume_metal.cpp:1958/1976/2571/3906 seen); classify each FP (prove non-null invariant) or guard with an ORIGIN: line.
