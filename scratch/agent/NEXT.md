# NEXT (s7450)
HYPOTHESIS-ID: harness-fatal-exit-coverage

First: fold SOAK-RESULTS line for s7449_argck_levels (L4/L10 under QUIET with the s7449 argcheck filter). Pass = inits=1,
alive_at_end=1, vi_stalls30s=0, crashlines=0 both, run.log size in the s7448 range (450-610 KB) -> class DF flight line.

Class DG: scratch/agent/m6_god_common.sh:89 crashlines = grep 'CRASH\|SIGSEGV\|abort'. Non-signal fatal exits print other
words: librecomp recomp.cpp:465 switch_error "Switch-case out of bounds" (printf stdout + exit), :471 do_break "Encountered
break", ultramodern quick_exit "Exiting with exit status", message_box "Failed to allocate memory!"/"[Error] ...", RSP
"exited unexpectedly", plus SIGBUS without "SIGSEGV" text. alive_at_end=0 would flag the death but not name it.
Step 1 (offline): list every harness/scorer that classifies a run (grep crashlines|CRASH in scratch/agent/*.sh *.zsh,
tools/*.py, tools/agent/loop.sh soak verdicts); for each, which fatal-exit classes it would miss.
Step 2 (one run per class is NOT needed): reuse ROGUESQ_PLANT_FAIL (s7449, prints all classes then SIGSEGV) plus add a
ROGUESQ_PLANT_EXIT=<s> mode that prints the switch_error line and exit(1) without a signal; run each harness scorer on the
two logs. Members: scorers that report crash=0 on the PLANT_EXIT log.
Hypotheses: H-none (every scorer also gates on alive/exit code), H-few (some scorers miss non-signal exits -> one shared
fatal-pattern list, e.g. tools/agent/fatal_patterns.txt, used by all), H-stdout (stdout not captured in some recipes).
Discriminator: per-scorer verdict on the PLANT_EXIT log. Positive control: PLANT_FAIL log must score crash>0 everywhere.
