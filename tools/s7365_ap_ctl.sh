#!/bin/zsh
# s7365 class AP two-arm control: every pre arm must trip ASan (use-after-free / overflow), every post arm must run clean.
cd "${0:A:h}/.." || exit 1
mkdir -p scratch/s7365
clang++ -std=c++17 -g -O0 -fsanitize=address tools/s7365_ap_ctl.cpp -o scratch/s7365/ap_ctl || exit 1
ok=0; n=0
for c in fwd; do
  n=$((n+2))
  if scratch/s7365/ap_ctl $c pre > scratch/s7365/ctl_${c}_pre.log 2>&1; then echo "$c pre ran clean: control INVALID"; else
    k=$(grep -oE 'heap-use-after-free|(global|heap|stack|container)-buffer-overflow|SEGV|BUS' scratch/s7365/ctl_${c}_pre.log | head -1)
    [[ -n $k ]] && { echo "$c pre -> $k"; ok=$((ok+1)); } || echo "$c pre failed without an ASan report: INVALID"; fi
  if scratch/s7365/ap_ctl $c post > scratch/s7365/ctl_${c}_post.log 2>&1; then echo "$c post clean: $(head -1 scratch/s7365/ctl_${c}_post.log)"; ok=$((ok+1)); else echo "$c post FAIL"; fi
done
[[ $ok == $n ]] && echo "s7365 ctl $ok/$n PASS" || { echo "s7365 ctl FAIL ($ok/$n)"; exit 1; }
