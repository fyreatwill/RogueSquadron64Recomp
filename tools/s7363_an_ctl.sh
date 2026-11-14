#!/bin/zsh
# s7363 class AN two-arm control: every pre arm must trip ASan (global/heap/stack overflow), every post arm must run clean.
cd "${0:A:h}/.." || exit 1
mkdir -p scratch/s7363
clang++ -std=c++17 -g -O0 -fsanitize=address tools/s7363_an_ctl.cpp -o scratch/s7363/an_ctl || exit 1
ok=0
for c in aim snap grow; do
  if scratch/s7363/an_ctl $c pre > scratch/s7363/ctl_${c}_pre.log 2>&1; then echo "$c pre ran clean: control INVALID"; else
    k=$(grep -oE '(global|heap|stack|container)-buffer-overflow|stack-buffer-underflow|unknown-crash|SEGV|BUS' scratch/s7363/ctl_${c}_pre.log | head -1)
    [[ -n $k ]] && { echo "$c pre -> $k"; ok=$((ok+1)); } || echo "$c pre failed without an ASan report: INVALID"; fi
  if scratch/s7363/an_ctl $c post > scratch/s7363/ctl_${c}_post.log 2>&1; then echo "$c post clean: $(head -1 scratch/s7363/ctl_${c}_post.log)"; ok=$((ok+1)); else echo "$c post FAIL"; fi
done
[[ $ok == 6 ]] && echo "s7363 ctl 6/6 PASS" || { echo "s7363 ctl FAIL ($ok/6)"; exit 1; }
