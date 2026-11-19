# NEXT (s7663)
HYPOTHESIS-ID: owner-wait-standing

s7662 compacted CURRENT-TRUTH to ~40.7 KB (s7647-s7659 + items 21-35 archived in PROJECT-OVERVIEW "(s7662 maintenance)").
G6a/G6b/G6c and every G5 item wait on the owner (docs/OWNER-OPT-INS.md). If the owner has reported anything, take that first.
Otherwise take the first open 3c rung per CURRENT-TRUTH Next steps. Do NOT do another census-gate housekeeping pass: the sweep is
0 RED and a standing stop-gate check. Any lldb-backed recipe runs `zsh tools/lldb_attach_check.sh` first (exit 1 -> nulls void).
Rules: never touch build/saves; one game at a time; SIGKILL only; at most 2 CPU-heavy jobs.
