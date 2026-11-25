#!/bin/sh
# s7951: planted controls for tools/agent/run_dir_guard.sh (case-only run-dir collisions on a case-insensitive fs).
G=$(dirname "$0")/run_dir_guard.sh; T=$(mktemp -d); f=0
mkdir "$T/g1_lvl4s7031L4A"
sh $G "$T" g1_lvl4s7031L4A >/dev/null; [ $? -eq 0 ] || { echo "FAIL exact re-run refused"; f=1; }
o=$(sh $G "$T" g1_lvl4s7031L4a); r=$?
[ $r -eq 3 ] && [ "$o" = "run_dir_collision=g1_lvl4s7031L4A" ] || { echo "FAIL planted case collision not caught rc=$r o=$o"; f=1; }
sh $G "$T" g1_lvl4s7031L4b >/dev/null; [ $? -eq 0 ] || { echo "FAIL distinct name refused"; f=1; }
sh $G "$T/absent" x >/dev/null; [ $? -eq 0 ] || { echo "FAIL absent parent refused"; f=1; }
# s7952 one-arg path form (OUTDIR launchers), with and without trailing slash
o=$(sh $G "$T/g1_lvl4s7031L4a"); [ $? -eq 3 ] || { echo "FAIL one-arg collision missed o=$o"; f=1; }
o=$(sh $G "$T/g1_lvl4s7031l4A/"); [ $? -eq 3 ] || { echo "FAIL one-arg trailing-slash collision missed o=$o"; f=1; }
sh $G "$T/g1_lvl4s7031L4A" >/dev/null || { echo "FAIL one-arg exact refused"; f=1; }
# mutation control: a guard comparing case-sensitively only must miss the planted collision
m=$(ls -1 "$T" | awk -v n=g1_lvl4s7031L4a '$0 == n' | head -1); [ -z "$m" ] || { echo "FAIL mutation control"; f=1; }
rm -rf "$T"
[ $f -eq 0 ] && echo "PASS test_run_dir_guard (exact ok, planted L4A/L4a caught, distinct ok, absent ok, one-arg path form, mutation misses)" || exit 1
