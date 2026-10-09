# Next work unit (s4437): build patched oracle, run s4436_oracle_vi.sh

HYPOTHESIS-ID: m5-ai-buffer-rate

Build: cc -O2 -std=c11 -I$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/api -o tools/oracle/build/rs64_oracle tools/oracle/rs64_oracle.c -lm
Run: zsh scratch/agent/s4436_oracle_vi.sh ; read `ai-output-summary ... vi_swaps=` lines in scratch/agent/soak_results/s4436_vi/oracle.log.
Hypotheses (from s4435: port feeds ~59 x 768 B buffers/s, 115/s needed):
- H-port-slow: retail title calls/vi_swaps ~2, port ~1.
- H-retail-same: retail ~1 too; SDL freq/buffering is the issue.
- H-port-throttled-by-host: port VI/s < 60.
Positive control: the pre-title bucket must show thousands of calls and swaps (s4238 had 5914 calls); if the comma --watch-pc form fails, vi_swaps will read 0 everywhere.
