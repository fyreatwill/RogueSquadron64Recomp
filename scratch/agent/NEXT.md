# Next work unit: is port steady-state AI output clipped vs retail? (s4238)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4237: hangar steady-state AI output is wide-band (distinct ~188) like title; the DC was a 19-buffer entry transient. Both reach +-32.7k.
Hypotheses: (a) port gain/mix is too hot so output saturates (fraction of |sample|>=32000 much higher than retail); (b) retail is equally loud - no defect; (c) clipping only when many voices stack (hangar/title).
Discriminator: one run per side, fraction of samples with |x|>=32000 and RMS over title-1024 buffers n>=256: port via an [ai-output-stats] extension in lib/N64ModernRuntime/librecomp/src/ai.cpp (then export.sh + commit), retail via tools/oracle (reaches title). Positive control: a synthetic full-scale buffer must register 100%. (a) = port fraction >> retail; (b) = similar.
Fallback if the oracle cannot give AI buffers: resume docs/M5-AUDIO-PLAN.md next step.
