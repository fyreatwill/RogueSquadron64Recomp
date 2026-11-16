# NEXT (s7464)
HYPOTHESIS-ID: host-uninit-padhash

s7463 opened class DS (host uninitialized reads / padded-struct hashes): census rc 0, 3 padded hash keys routed through
rs64_s7463_hash (ROGUESQ_S7463_PADFIX=0 old); title+attract H-const (stable garbage). Queued
scratch/agent/soak_queue/s7463_padhash_flight.sh (L4 cnt PADCOUNT=1, L1 ctl PADCOUNT=ctl; HOLD=150).

Hypotheses for flight: H-const (raw==fixed distinct counts at every site: fix is latent-only) vs H-split (raw>fixed at some site:
the old code fragmented that cache in flight; the fix is a live perf/memory fix - quantify cachedKeyMap / tileCopy growth from
dck_newkey extra=) vs H-unreached (reinterpret site 0 calls in flight too: leave it as static-only, say so).

Step 1: fold s7463_padhash_flight from SOAK-RESULTS.md + scratch/s7463q/s7463.txt.
  - CONTROL PASS -> write one line under item 1 DS with the per-site verdicts; close DS.
  - CONTROL FAIL with arm alive -> read log_ctl.txt for [s7463] lines (mode line printed? PADCOUNT passed through ARMS env?).
  - void (rc 2) -> the loop re-queues; do Step 2 meanwhile.
Step 2 (new slug): class DT, analyzer null-deref / CallAndMessage findings in host code (tools/s7463_uninit_census.py line B,
  widen B_RE to "null pointer|Called C\\+\\+ object pointer is null"; main.cpp:12987, plume_metal.cpp:1958/1976/2571/3906 seen);
  classify each as FP (prove the non-null invariant) or guard with an ORIGIN: line naming the writer.
