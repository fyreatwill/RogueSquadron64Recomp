# NEXT: fold s6529 bypass soak verdicts, then name the span-saturation writer
HYPOTHESIS-ID: g1c-span-reject-predicate

Read SOAK-RESULTS.md s6529_* lines (dd4 bypass lvl1/5/10; opt-out lvl1 is the toggle positive control). Score from logs: G1B frame time/VI per s, terrain fraction (fixed-camera scorer), tri count, crashes, spike log vs s6459/s6463/s6464 pre-bypass.
Hypotheses: H-bypass-safe (VI 60/s, 0 crash, fraction up) / H-bypass-costly (VI drops or ucode cap hit -> gate bypass to dd<=3 or cap cells) / H-toggle-broken (opt-out arm differs from pre-bypass -> patch not what we think).
Then: log pre-clamp inputs into scanConvertTriangleToSpanTable at dd4 to name the writer of -128 (ORIGIN).
