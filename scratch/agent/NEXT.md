# NEXT: fold s6012_ftz1 vs ftz0 soaks
HYPOTHESIS-ID: fp-ftz-parity
Fold SOAK-RESULTS lines. ftz1 clean (0 crash/0 stall) => consider default-on later with more levels; any NAN_CHECK abort in ftz1 only => FTZ hurts, keep off. Then G3/rim-band is stale (s4644: no longer visible).
