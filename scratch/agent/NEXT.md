# NEXT (s7662)
HYPOTHESIS-ID: owner-wait-standing

s7661 closed the lldb-attach question (works; tools/lldb_attach_check.sh is the preflight for any lldb-backed run).
G6a/G6b/G6c and every G5 item wait on the owner (docs/OWNER-OPT-INS.md). If the owner has reported anything, take that first.
Otherwise take the first open rung of the 3c ladder per CURRENT-TRUTH Next steps; any lldb-backed recipe must run
`zsh tools/lldb_attach_check.sh` first (exit 1 -> its nulls are void).
Rules: never touch build/saves; one game at a time; SIGKILL only; at most 2 CPU-heavy jobs.
