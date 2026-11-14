#!/bin/zsh
# s7313: the ONE live game PID, or nothing. Source this file, then call rs64_game_pid.
# Why: `pgrep -x RogueSquadron64Recomp | head -1` returns the LOWEST pid, i.e. the OLDEST game. s7312's batch-1 L5 arm was
# still alive when batch 2 ran, so the L1 arm's window capture grabbed the L5 window ("stale frame" that was never stale).
# rs64_game_pid        -> prints the pid and returns 0 only when exactly one game process exists; 1 when none, 2 when >1
#                         (and logs "[rs64_game_pid] N games alive: pids" to stderr).
# rs64_no_foreign_game [wait_s] -> returns 0 once no game is running (waits up to wait_s, default 30), else 3 with a message.
#                         Call before launching an arm so a leftover game can never be mistaken for ours.
rs64_game_pid() {
  local -a p; p=(${(f)"$(pgrep -x RogueSquadron64Recomp)"})
  (( $#p == 0 )) && return 1
  (( $#p > 1 )) && { echo "[rs64_game_pid] $#p games alive: ${p[*]}" >&2; return 2; }
  echo $p[1]
}
rs64_no_foreign_game() {
  local w=${1:-30} i
  for i in $(seq 0 $w); do pgrep -x RogueSquadron64Recomp >/dev/null || return 0; (( i < w )) && sleep 1; done
  echo "[rs64_no_foreign_game] game still alive after ${w}s: $(pgrep -x RogueSquadron64Recomp | tr '\n' ' ')" >&2; return 3
}
