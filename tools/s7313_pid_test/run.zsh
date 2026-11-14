#!/bin/zsh
# s7313 positive control for tools/rs64_game_pid.zsh without the game: two fake processes named RogueSquadron64Recomp
# (a 3-line C sleeper; a copied /bin/sleep is SIGKILLed by macOS). Shows the old `pgrep | head -1` picks the OLDER one (the s7312 mechanism) and the helper refuses.
# Exit 0 = all checks pass. Refuses to run while a real game is alive.
cd "$(git rev-parse --show-toplevel)" || exit 2
pgrep -x RogueSquadron64Recomp >/dev/null && { echo "real game alive, not testing"; exit 2; }
. tools/rs64_game_pid.zsh
T=$(mktemp -d)/RogueSquadron64Recomp; printf '#include <unistd.h>\n#include <stdlib.h>\nint main(int c,char**v){sleep(atoi(v[1]));return 0;}\n' | clang -x c -o $T - || exit 2; f=0
ok() { if eval "$2"; then echo "PASS $1"; else echo "FAIL $1"; f=1; fi; }
ok none '! rs64_game_pid >/dev/null'
$T 30 & a=$!; sleep 0.3
ok one-pid '[ "$(rs64_game_pid)" = "$a" ]'
ok foreign-blocks '! rs64_no_foreign_game 1 2>/dev/null'
$T 30 & b=$!; sleep 0.3
old=$(pgrep -x RogueSquadron64Recomp | head -1)
ok old-head1-picks-older '[ "$old" = "$a" ] && [ "$a" != "$b" ]'
ok two-refused '! rs64_game_pid >/dev/null 2>&1'
rs64_game_pid >/dev/null 2>&1; ok two-rc2 "[ $? = 2 ]"
kill -9 $a; wait $a 2>/dev/null; sleep 0.2
ok back-to-one '[ "$(rs64_game_pid)" = "$b" ]'
kill -9 $b; wait $b 2>/dev/null; sleep 0.2
ok foreign-clear 'rs64_no_foreign_game 2'
rm -f $T; exit $f
