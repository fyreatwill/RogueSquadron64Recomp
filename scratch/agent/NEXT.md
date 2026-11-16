# NEXT (s7444)
HYPOTHESIS-ID: ungated-summary-prints

Class DA (CURRENT-TRUTH Next steps item 1): the idiom s7443 found in rs64_s5660_ustore — an always-on counter with a
periodic `if ((n & MASK) == 0|1) fprintf(...)` summary and no env latch. Enumerate:
  grep -rnE "& 0x[0-9A-Fa-f]+u?l*\) == [01]u?\)[^;]*fprintf" src     (10 sites, s7443 count; also widen to multi-line
  forms: grep -rnE "& 0x[0-9A-Fa-f]{3,}u?l*\) == [01]" src | grep -v getenv)
Classify each: GATED (env/static latch returns before the counter) / UNGATED-DIAG / UNGATED-NEEDED. Cross-check against
the default-arm stderr scratch/s7443/run.tlog (python3 tools/s7431_stderr_volume.py scratch/s7443/run.tlog) — a site that
prints there with no env is UNGATED by a second line of evidence.
Outcomes: H-clean (all gated or needed: close DA, take CURRENT-TRUTH item 20 / a new idiom class), H-hidden (latch each
UNGATED-DIAG site on its consumer env, ROGUESQ_G1E_TRIM=0 restores; cmake build; env S7431_ARM=DA zsh
tools/s7431_stderr_volume.sh 150 -> tag count 0; consumer control: same with the consumer env must print. NOTE: any
ROGUESQ_LOG_* env turns on [storediag] (100+ MB stderr) — prefer a non-LOG_ consumer env for the control arm).
