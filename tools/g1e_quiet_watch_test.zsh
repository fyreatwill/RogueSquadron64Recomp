#!/bin/zsh
# s6935: positive and negative control for watch_human in g1e_owner_quiet_arms.zsh, no game, no display lock. Rising idle must survive, a fall must kill and mark void.
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$(mktemp -d); R=$T; IDLE_FEED=$T/feed; export IDLE_FEED; rc=0
# s7250: watch_human became multi-line (s7233 lock/sleep void) and calls locked/front, so the old one-line grep defined nothing
# and this test had been failing "command not found". Take each needed function from its header through its closing "}" line.
eval "$(awk '/^(idle|locked|front|watch_human)\(\)/{f=1} f{print} f&&/\}[[:space:]]*$/{f=0}' tools/g1e_owner_quiet_arms.zsh)"
echo 500 > $IDLE_FEED; /bin/sleep 30 & v=$!; watch_human $v neg & w=$!
for i in 502 504 506; do /bin/sleep 2; echo $i >> $IDLE_FEED; done
if kill -0 $v 2>/dev/null && [ ! -e $R/void_neg ]; then echo "neg ok: rising idle left the arm alive"; else echo "neg FAIL"; rc=1; fi
kill -KILL $v; kill $w 2>/dev/null
echo 500 > $IDLE_FEED; /bin/sleep 30 & v=$!; watch_human $v pos & w=$!
/bin/sleep 3; echo 3 >> $IDLE_FEED; /bin/sleep 4
if ! kill -0 $v 2>/dev/null && [ -e $R/void_pos ]; then echo "pos ok: $(tail -1 $R/arms.log)"; else echo "pos FAIL"; rc=1; fi
kill -KILL $v 2>/dev/null; kill $w 2>/dev/null; exit $rc
