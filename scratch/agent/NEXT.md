# Rerun s4788 DROP=1 at low host load, then read per-phase `res=0x2C` route counts at VI 512

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4788 produced no data: soak stalled in VI 640 (0 ovl-route rows, control failed) and a same-iteration rerun crashed at spTaskSchedulerThread+9632, both at host load 10-13 (Chrome/WindowServer, not ours).
Work unit: `uptime`; only run when 1-min load < 4 (else go BLOCKED asking the human to quiet the host). Run `zsh scratch/agent/s4788_drop1.sh` from repo root (no `timeout` binary on this mac). Extract `res=0x2C` rows after `[phase] vi_width=512` vs title phase.
Competing: (A) many phase-6 routes => stopgap drops real mission content; (B) ~0 routes while DL arrivals2c>0 => arrivals die before RSP routing; (C) still stalls at low load => not load, bisect vs previous binary.
Control: title-phase `res=0x2C` rows (152 in s4787) and the VI 512 line must both be present, else the run is void.
Then: in-run DROP toggle so DROP=1/0 compare within one phase.
