# NEXT (s7658)
HYPOTHESIS-ID: gate-sweep-standing

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7657: sweep 135 = 127 GREEN, 3 NEEDS-INPUT (s7215 run.log, s7316 rdram dumps, s7573 game logs), 5 REPORT, 0 RED.
Work unit: turn the 3 NEEDS-INPUT gates into counted gates by RETAINING a small input for each, captured once:
- s7215: queue scratch/agent/soak_queue/s7658_shape_log.sh (scratch/s7215/r.zsh recipe, ROGUESQ_VI_SHAPE_LOG=1, 21:9, L17
  long route, `# SOAK_NEEDS_IDLE=600`) that copies only the [g1d-vishape-vp]/[s7213-shape]/osViSetMode/vi-mode-table lines
  to scratch/s7215/shape_lines.txt (zstd if > 1 MB); then add ARGS for s7215 with that file (decompress to build/ if zstd).
- s7573: same pattern with --retained DIR from an owner-recipe soak log tail; s7316: one ROGUESQ_RDRAM_DUMP_DIR dump.
Positive control per gate: a planted bad input (s7215: a shape line with no mode switch within 1000 lines) must read RED.
Hypotheses: H-small (filtered lines are < 1 MB, commit them) vs H-large (need zstd + a decompress step in the sweep).
Also measure: sweep wall when lib/rt64 is newer than scratch/s7631/ast.json (touch a COPY? no: `touch` one rt64 header),
to check the s7631 ~165 s regen stays under the 300 s cap with 6 parallel jobs; if not, raise its cap or run it serially.
Rules: never touch build/saves; one game at a time; SIGKILL only.
