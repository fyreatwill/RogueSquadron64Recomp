# Next work unit: consume s5038 message-queue census soaks
HYPOTHESIS-ID: m3-idiom-class-audit
Read SOAK-RESULTS.md for s5038_mq_census_force (control: mq=16 and mq_force=16 required) and s5038_mq_census_default (mq>0 => name ra callers + which queue field is bad, find the writer, rule 11; 0 => class closed on keyed route, record in CURRENT-TRUTH). Do not re-run. Then pick the next unaudited class: use-after-free reads after audited frees, or osJamMesg/osSetEventMesg arguments.
