# Next work unit (s4436): AI buffers per VI, port vs retail

HYPOTHESIS-ID: m5-ai-buffer-rate

s4435: port title feeds ~59 x 768 B buffers/s; SDL queue never exceeds one buffer; 22047 Hz needs 115/s.
Hypotheses:
- H-port-slow: port audio thread issues ~1 buffer/VI while retail issues ~2/VI (pacing defect in port).
- H-retail-same: retail also ~1/VI; the DAC rate/real-time model differs, so port timing is correct and SDL freq/buffering is the issue.
- H-port-throttled-by-host: port game loop runs below 60 VI/s (compute-bound), so buffer rate is a symptom of slow emulation.
Discriminator: count AI set-next calls and VI swaps per second in each arm over the same title window. Oracle: extend dump_ai_output in tools/oracle/rs64_oracle.c to print a VI-swap count + wall clock with each summary; port: ratio of setnext to VI transitions from existing [s4245] ticks. Positive control: whole-RDRAM watch. If port VI/s < 60 -> H-port-throttled-by-host.
