#!/bin/zsh
# s7364 class AO two-arm control: every pre arm must trip ASan (global/heap/stack overflow), every post arm must run clean.
cd "${0:A:h}/.." || exit 1
mkdir -p scratch/s7364
clang++ -std=c++17 -g -O0 -fsanitize=address tools/s7364_ao_ctl.cpp -o scratch/s7364/ao_ctl || exit 1
ok=0
for c in wlreset eep shadow sh2 modbin who; do
  if scratch/s7364/ao_ctl $c pre > scratch/s7364/ctl_${c}_pre.log 2>&1; then echo "$c pre ran clean: control INVALID"; else
    k=$(grep -oE '(global|heap|stack|container)-buffer-overflow|stack-buffer-underflow|unknown-crash|SEGV|BUS' scratch/s7364/ctl_${c}_pre.log | head -1)
    [[ -n $k ]] && { echo "$c pre -> $k"; ok=$((ok+1)); } || echo "$c pre failed without an ASan report: INVALID"; fi
  if scratch/s7364/ao_ctl $c post > scratch/s7364/ctl_${c}_post.log 2>&1; then echo "$c post clean: $(head -1 scratch/s7364/ctl_${c}_post.log)"; ok=$((ok+1)); else echo "$c post FAIL"; fi
done
[[ $ok == 12 ]] && echo "s7364 ctl 12/12 PASS" || { echo "s7364 ctl FAIL ($ok/12)"; exit 1; }
