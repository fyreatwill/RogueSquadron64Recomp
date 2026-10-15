# Next work unit

HYPOTHESIS-ID: m5-retrace-pacing-vs-retail

s4900: retail retrace entry (0x8009123C) is steady 1 per VI origin change
(1223/1301 intervals =1, 38 zero, 38 two). Port (s4899) averages 1 per
update_screen but is bimodal 0/2 (4341 R=0, 4294 R=2).

Hypotheses:
* H-alias: port update_screen runs ~30/s while true VI/retraces run 60/s, so 0/2
  per update_screen is just 2 retraces per frame; per TRUE VI port is steady 1.
* H-burst: port VI origin changes 60/s but retrace queue delivery coalesces
  (0 then 2) -> port retrace/VI-thread pacing differs from retail.
Discriminator: add to the s4899 per-VI flush a count of true VI origin changes
(osViSwapBuffer-observed or host VI interrupt) and a per-origin-change histogram
of retrace returns (R) and synth entries (S). Reuse
scratch/agent/run_s4899_cadence_join.sh; controls: phase lines + R total == S total.
H-alias -> per-origin-change R histogram is ~all 1; H-burst -> still 0/2.
