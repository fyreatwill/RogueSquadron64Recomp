# Next work unit

HYPOTHESIS-ID: m5-b40-gate-default

s4702: 6 default-B40 arms -> 0 crashes, but 5/6 stalled at VI 640 (origin 0x5D4000, rdpFs frozen 157, dereg-enter=1) vs s4701 3/3 healthy at 4-way concurrency.
Hypotheses: H1 B40 pass-through causes a boot stall; H2 6-way load starves boot; H3 preexisting flaky 640 stall.
Unit: copy scratch/agent/run_s4701_b40_long.sh to run_s4703_stall_split.sh with FOUR arms (2x default, 2x ROGUESQ_M5_B40_VALUE=0), 4 concurrent, 120 s window. Count arms reaching vi_width=1024 origin=0x00790400.
Outcomes: default stalls and B40=0 never => H1. Both stall sometimes => H3. All healthy => H2 (load); then confirm with sequential single arms.
