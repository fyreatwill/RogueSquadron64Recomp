#!/bin/sh
# s7455 class DK: exact field test on a harness summary line (space-separated key=value tokens).
# usage: summary_field.sh <summary-file> <key> <op> <value>   op: eq | ne | le | ge | lt | gt | is (string equal)
# Exit 0 = test holds, 1 = test fails OR key missing OR non-numeric value for a numeric op, 2 = usage.
# Why: `grep -q 'inits=1' summary` also passes inits=10..19 and `[[ $S == *exitrc=1* ]]` passes exitrc=134 (SIGABRT);
# `grep -q 'restarts=0'` passes on mission_restarts=0. This parses the token whose key is exactly <key>.
# Scans every line, the last occurrence of <key> wins (s5745_crawlshot appended a shots= line after the summary line;
# the allattempts-failed line has no per-run keys -> missing -> 1).
# Self-test: tools/agent/test_summary_field.sh.
[ $# -eq 4 ] || { echo "usage: $0 <summary> <key> <eq|ne|le|ge|lt|gt|is> <value>" >&2; exit 2; }
[ -r "$1" ] || { echo "summary_field: no file $1" >&2; exit 1; }
case $3 in eq|ne|le|ge|lt|gt|is) ;; *) echo "summary_field: bad op $3" >&2; exit 2;; esac
awk -v k="$2" -v op="$3" -v want="$4" '
{ for (i = 1; i <= NF; i++) { p = index($i, "="); if (p > 1 && substr($i, 1, p-1) == k) { v = substr($i, p+1); found = 1 } } }
END {
  if (!found) { print "summary_field: " k " missing" > "/dev/stderr"; exit 1 }
  if (op == "is") exit (v == want) ? 0 : 1
  if (v !~ /^-?[0-9]+$/ || want !~ /^-?[0-9]+$/) { print "summary_field: " k "=" v " not numeric" > "/dev/stderr"; exit 1 }
  v += 0; want += 0
  if (op == "eq") exit (v == want) ? 0 : 1
  if (op == "ne") exit (v != want) ? 0 : 1
  if (op == "le") exit (v <= want) ? 0 : 1
  if (op == "ge") exit (v >= want) ? 0 : 1
  if (op == "lt") exit (v <  want) ? 0 : 1
  if (op == "gt") exit (v >  want) ? 0 : 1
}' "$1"
