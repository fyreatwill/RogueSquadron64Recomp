# NEXT (s7664)
HYPOTHESIS-ID: owner-wait-standing

s7663 landed owner launch presets/settings.txt (src/main/rs64_settings.cpp; OWNER-OPT-INS top row). Everything else
(G5, G6a/b/c, owner default decisions) waits on the owner. If the owner has reported anything, take that first.
Otherwise take the first open 3c rung per CURRENT-TRUTH Next steps; do NOT do another census-gate housekeeping pass.
Upstream origin/main was re-read s7663: its new commits (rewind/record, MCP, co-op, combo bindings) are debug/HLE-side; nothing
owner-requested is unported. Rules: never touch build/saves; one game at a time; SIGKILL only; at most 2 CPU-heavy jobs.
