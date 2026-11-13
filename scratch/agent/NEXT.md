# NEXT (s7276): G5c busy-host arm: does host CPU load produce the owner's in-flight freezes?
HYPOTHESIS-ID: g5c-busy-host
State: s7272-s7275 show 0 in-flight holds >= 250 ms at the owner recipe on L1/L4/L5/L12 (16:9 + 21:9, windowed + fullscreen, WIDEWIN and
PLAIN env, 300 s and 900 s), SIGSTOP control caught every time. Every one of those runs was on a QUIET host (HID idle hours, nothing else
running). The owner plays with Chrome/REAPER/WindowServer load (G1b H-host: only the P-cores sysctl hw.perflevel0 reports).
Hypotheses: H-host (holds >= 250 ms appear in flight under load: game/RSP threads pushed to E-cores or descheduled); H-robust (still 0 flight
holds under load: G5c needs an owner-side datum, e.g. a screen recording of a freeze); H-slow (no holds but changes/s drops a lot: a steady
slowdown, not a freeze; report the per-second change rate).
Discriminator: tools/s7272_g5c_hold_arm.zsh PLAIN=1 DUR=600 KEEP=1 FS=1 LEVEL=12 (no restarts in s7275), with a background load of one
`yes > /dev/null` per logical CPU (hw.ncpu) started at launch and killed after, in a SECOND arm with load = P-core count only. Same SIGSTOP
controls (3/3 required). Baseline = s7275 L12 quiet (39873 frames/900 s, 44.3 changes/s, 0 holds, longest 190 ms).
Commands (in-session; check HID idle >= 120 s + screen unlocked first):
  n=$(sysctl -n hw.ncpu); for i in $(seq $n); do yes > /dev/null & done; env PLAIN=1 DUR=600 KEEP=1 FS=1 LEVEL=12 TAG=s7276all ASP=16:9 CW=480 zsh tools/s7272_g5c_hold_arm.zsh; kill %{1..$n}
  then the same with n=$(sysctl -n hw.perflevel0.logicalcpu), TAG=s7276p. Kill every `yes` afterwards (pkill -x yes).
Expected: H-host -> holds in flight; sample the live process (`sample <pid> 3`) during the next recurrence and name the stalled thread;
fix candidate is thread QoS (QOS_ALL opt-in exists, s6962-s6989; owner decides default). H-robust -> G5c parked for an owner datum.
