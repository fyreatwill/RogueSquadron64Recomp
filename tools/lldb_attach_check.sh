#!/bin/zsh
# s7661: preflight for lldb-backed soaks. Proves THIS session can attach (by pid and by -w name) to a
# non-platform binary carrying the game's process name, and that a SIGSEGV stop reaches a backgrounded
# lldb's output file (the exact s7660 boot() shape). Exit 0 = attach usable; 1 = not (lldb nulls void).
# Note: /bin/sleep etc. are platform binaries and are ALWAYS denied; never use them as the control.
set -u
NAME=${1:-RogueSquadron64Recomp}; D=$(mktemp -d /tmp/lldbchk.XXXXXX); B="$D/$NAME"
printf '#include <unistd.h>\nint main(){for(int i=0;i<40;i++)sleep(1);return 0;}\n' > $D/t.c
clang -o "$B" $D/t.c || { echo "lldb_attach_check: compile FAIL"; exit 1; }
T(){ perl -e 'alarm shift; exec @ARGV' "$@"; }
"$B" & P=$!; sleep 0.5
T 30 /usr/bin/lldb -b -o "process attach -p $P" -o detach > $D/p.lldb 2>&1
kill -9 $P 2>/dev/null; wait $P 2>/dev/null
grep -q 'stopped' $D/p.lldb && pid=PASS || pid=FAIL
/usr/bin/lldb -b -o "process attach -n $NAME -w" -o 'process handle SIGSEGV -s true -n true -p true' -o continue -o 'bt 3' > $D/w.lldb 2>&1 &
L=$!; sleep 2; "$B" & P=$!; sleep 4; kill -SEGV $P 2>/dev/null; sleep 3
kill -9 $P $L 2>/dev/null; wait 2>/dev/null
grep -q 'stop reason = signal SIGSEGV' $D/w.lldb && wait_=PASS || wait_=FAIL
echo "lldb_attach_check name=$NAME pid=$pid wait_segv=$wait_ devmode=$(DevToolsSecurity -status 2>&1 | grep -q enabled && echo on || echo off)"
[ $pid = PASS ] && [ $wait_ = PASS ] && { rm -rf $D; exit 0; }
echo "lldb_attach_check: logs kept in $D"; tail -3 $D/p.lldb $D/w.lldb; exit 1
