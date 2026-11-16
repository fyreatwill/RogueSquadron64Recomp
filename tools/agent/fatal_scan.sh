#!/bin/zsh
# s7450 class DG: ONE fatal-exit pattern list for every harness scorer (tools/agent/fatal_patterns.txt, ERE, one per line).
# The old scorers grepped CRASH|SIGSEGV|abort and missed non-signal exits: librecomp switch_error / do_break (printf +
# exit(1)), ultramodern quick_exit ("Exiting with exit status", _Exit), message_box, RSP "exited unexpectedly".
# usage: fatal_scan.sh <log>       -> prints "fatal=<n> first=<first matching line, 80 chars>"
#        fatal_scan.sh --selftest  -> positive control (every pattern must hit a planted line) + negative (clean log = 0)
P=${0:A:h}/fatal_patterns.txt
scan() { local n f; n=$(grep -acEf $P "$1"); f=$(grep -aEm1 -f $P "$1" | cut -c1-80 | tr ' ' '_'); print "fatal=${n:-0} first=${f:-none}"; }
if [ "${1:-}" = --selftest ]; then
  T=$(mktemp -d); rc=0
  printf '%s\n' '[CRASH] caught signal 11 (SIGSEGV), dumping stack:' 'x SIGBUS y' 'x SIGABRT' 'abort() called' \
    'Switch-case out of bounds in f at 0x80001234 for jump table at 0x800A0000' 'Encountered break at original vram 0x80001234' \
    "Exiting with exit status '1'. Function f, at file x:1" 'Unhandled status register bits changed: 0x1' \
    'Failed to allocate memory!' '[Error] Error opening stored ROM!' 'RSP ucode 1 exited unexpectedly. exit_reason: 3' \
    'Failed to find function at 0x80001234' 'Assertion failed: (x), function f' 'SDL_Init failed: x' 'SDL_CreateWindow failed: x' \
    'libc++abi: terminating due to uncaught exception' 'Cannot partially unload section' \
    '[s7356] FATAL init_overlays: calloc(9, 4) for section_addresses failed' > $T/pos  # s7451 class DH: NDEBUG-silent sites
  printf '%s\n' '[vi] update_screen #1 origin=0x00A12B00' '[initMission] call#1 B40=0x04' '[godmode] refill' '[autopilot] fire t=3' \
    '[fbhash #1] fb=0x80A12600 h=331902425f49f3e3' '[g1b] frame 1 ms=16.6' > $T/neg
  np=$(grep -cv '^$' $P); hit=0
  while IFS= read -r pat; do [ -z "$pat" ] && continue; grep -aqE -- "$pat" $T/pos && hit=$((hit+1)) || { print "selftest: pattern '$pat' matched nothing"; rc=1; }; done < $P
  [ "$(grep -acEf $P $T/pos)" = 18 ] || { print "selftest: pos lines $(grep -acEf $P $T/pos)/18"; rc=1; }
  [ "$(grep -acEf $P $T/neg)" = 0 ] || { print "selftest: negative log matched"; rc=1; }
  rm -rf $T; print "fatal_scan selftest patterns=$hit/$np rc=$rc"; exit $rc
fi
scan "$1"
