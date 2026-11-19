# NEXT (s7661)
HYPOTHESIS-ID: owner-wait-standing

s7660 closed the title-boot plume SIGSEGV (0/20 on the current build, 76 cumulative, crash-handler control PASS).
G6a/G6b/G6c and every G5 item wait on the owner (docs/OWNER-OPT-INS.md). If the owner has reported anything, take that first.
Otherwise, a candidate with engineering left: lldb `process attach -n RogueSquadron64Recomp -w` no longer attaches in loop
sessions (s7660 control.lldb showed only the attach line). Hypotheses: H-tcc (developer-tools permission missing for this
session: `DevToolsSecurity -status`; `lldb -b -o 'process attach -p <pid>'` on a plain `sleep 60`) vs H-wait (-w name
match broken on this lldb: attach by -p works). Discriminator: attach to a plain sleep by pid and by -w name. If H-tcc,
NEEDS-HUMAN system-settings; if H-wait, switch attach recipes to launch-then-attach-by-pid and rerun the s7660 control.
Rules: never touch build/saves; one game at a time; SIGKILL only.
