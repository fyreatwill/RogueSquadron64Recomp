#!/bin/zsh
# s7665: build the s7523 model fuzz harness with ASan+UBSan and run seeds + the planted-invariant control.
set -u; cd "${0:A:h}/.."; O=${O:-scratch/s7665}; mkdir -p $O
clang++ -std=c++17 -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all -o $O/t7523 tools/test_s7523_model.cpp || exit 3
fail=0
for s in 1 2 3 4 5 6; do $O/t7523 ${STEPS:-400000} $s 0 2>&1 | tail -3 | grep -q '^OK' || { echo "seed $s FAIL"; $O/t7523 ${STEPS:-400000} $s 0 2>&1 | grep -v '^\[s752' | head -20; fail=1; }; done
$O/t7523 200000 1 1 >/dev/null 2>&1; rc=$?; if [[ $rc == 2 ]]; then echo "ctl PASS (planted bad offset caught)"; else echo "ctl FAIL rc=$rc"; fail=1; fi
$O/t7523 400000 1 2 > $O/ctl2.log 2>&1; rc=$?; if grep -q "AddressSanitizer.*consume\|#[0-9] .* in .*consume" $O/ctl2.log; then echo "ctl2 PASS (ASan caught OOB in consume, rc=$rc)"; else echo "ctl2 FAIL rc=$rc"; fail=1; fi
[[ $fail == 0 ]] && echo "test_s7523_model: PASS" || echo "test_s7523_model: FAIL"; exit $fail
