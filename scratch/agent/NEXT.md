# Next work unit: consume s5037 copy-guard soaks
HYPOTHESIS-ID: m3-idiom-class-audit
Read SOAK-RESULTS.md lines for s5037_copy_guard_force (control: cg=16, cg_skipped=0 required) and s5037_copy_guard_default (cg_skipped>0 => name ra callers + length source, rule 11; 0 => class closed on keyed route, record in CURRENT-TRUTH). Do not re-run. Then pick next unaudited class: message-queue/thread calls with unchecked pointers (osSendMesg/osRecvMesg/osJamMesg) or use-after-free reads after audited frees.
