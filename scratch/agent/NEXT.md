# NEXT (s7445)
HYPOTHESIS-ID: default-diag-bursts

Class DB (CURRENT-TRUTH Next steps item 1): budgeted one-shot / burst diagnostic prints that fire at the owner recipe with
no env. Class DA (s7444) closed the periodic-summary idiom; the default-arm stderr (scratch/s7444/run.tlog, 150 s owner
recipe) still carries non-PERSISTENT burst tags:
  [s4234-ENTRY]  ~257 KB / 2101 lines, 149 KB in ONE second at t=6.5 s   (tools/apply_s4234_entryprobe.py, budget n<=2000)
  [newbtn]       ~84 KB / 793 lines from t=2.2 s
  [drain-path]   ~55 KB / 190 lines in one second at t=44.8 s              (tools/fixup_game_funcs_vendored.py, 5+ copies)
Enumerate: python3 tools/s7431_stderr_volume.py scratch/s7444/run.tlog | grep -v PERSISTENT  (every non-PERSISTENT tag)
and grep the emitting site of each (src/ and tools/apply_*.py / fixup_*.py, since some live in generated code).
Classify each: GATED (wrongly reached: env check missing) / UNGATED-DIAG (investigation closed, latch it) / NEEDED.
Hypotheses: H-clean (all needed or harmless: close DB, no change), H-hidden (latch each UNGATED-DIAG site on its consumer
env, G1E_TRIM=0 restores; generated-code sites go in the apply/fixup scripts and need the full regen order
make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake), H-stall (the 149 KB one-second [s4234-ENTRY] burst costs a
measurable frame-time hitch at t=6.5 s: check the run's [vi] / fbhash timestamps around it).
Measure: env S7431_ARM=DB zsh tools/s7431_stderr_volume.sh 150 -> latched tags 0; consumer control: the same run with the
consumer env must print them (prefer a non-LOG_ env; any ROGUESQ_LOG_* turns on [storediag], 100+ MB).
