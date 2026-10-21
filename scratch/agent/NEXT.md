# NEXT: fold s5710_lvl7{a,b} from SOAK-RESULTS.md. Positive control: log has `copyToRAM: range ... exceeds` (guard fired) and `gCurLevel=7`.
If crashlines==0 and alive: guard works; then find who issues the SetColorImage w=442 (ORIGIN: writer, via oracle/DL dump on forced lvl7) instead of leaving the guard as the answer.
If still crashing: take the new backtrace; the cause is elsewhere. Also step lvl4 fbd frames to see if flight was entered.
HYPOTHESIS-ID: g1-level-select
