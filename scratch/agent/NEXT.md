# NEXT: [mtm] fold s5750 backtrace soaks
Read SOAK-RESULTS s5750_mtma/b logs: grep -A30 'a0==2 BACKTRACE'. Control: '[mtm] n=' lines present.
Backtrace frames name the a0=2 caller (checkComplexObjectives/setHudEnableBit4 => bool arms; other => H2). If no a0==2 line occurs, a0=2 is lldb-only (s5470 r4 read) - check s5470 arg capture.
HYPOTHESIS-ID: g1-nonhealth-fail
