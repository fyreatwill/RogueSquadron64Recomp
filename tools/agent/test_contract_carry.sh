#!/bin/bash
# s7708 test: an exit contract still unmet after the loop's retries is carried into the NEXT
# iteration's prompt (scratch/agent/CONTRACT-CARRY.md) and removed once stop_gate --verify passes.
# Runs loop.sh's own contract_carry_write / contract_carry_clear / build_prompt_file against a
# fake stop_gate, then checks loop.sh wires them (build before runner.sh, write/clear after the
# final verify). Usage: test_contract_carry.sh [loop.sh]   (pass a mutated copy for the control)
set -u
here=$(cd "$(dirname "$0")" && pwd); LOOP=${1:-$here/loop.sh}
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
awk '/^contract_carry_write\(\)/{f=1} f{print} f&&/^}$/&&seen{exit} /^build_prompt_file\(\)/{seen=1}' "$LOOP" > "$T/fn.sh"
log(){ echo "LOG $*" >> "$T/log"; }
AG=$T/ag; mkdir -p "$AG" "$T/tools/agent"; echo "ITERATION BODY" > "$T/tools/agent/ITERATION.md"
printf '#!/bin/bash\nn=$(cat %s/calls 2>/dev/null || echo 0); n=$((n+1)); echo $n > %s/calls\n[ "$n" -gt 2 ] && exit 0\necho "Exit contract unmet: census gates RED (fake $n)"; exit 1\n' "$T" "$T" > "$T/tools/agent/stop_gate.sh"
chmod +x "$T/tools/agent/stop_gate.sh"
source "$T/fn.sh"; cd "$T"; fail=0
chk(){ if eval "$2"; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }
# the loop's post-hoc tail, in loop.sh's order
post(){ contract_ok=0; tools/agent/stop_gate.sh --verify >/dev/null 2>&1 && contract_ok=1
        if [ "$contract_ok" = "1" ]; then contract_carry_clear; else contract_carry_write "$(tools/agent/stop_gate.sh --verify 2>&1)"; fi; }
build_prompt_file
chk "iter1: no carry, plain prompt" '[ "$prompt_file" = tools/agent/ITERATION.md ]'
post
chk "iter1 unmet: carry file written with verdict" 'grep -q "fix FIRST" $AG/CONTRACT-CARRY.md && grep -q "census gates RED" $AG/CONTRACT-CARRY.md'
build_prompt_file
chk "iter2: carry heads the prompt" 'head -1 "$prompt_file" | grep -q "Unmet contract from the previous iteration" && grep -q "ITERATION BODY" "$prompt_file"'
echo "PIVOT X" > $AG/PIVOT.md; build_prompt_file
chk "iter2 with pivot: both preambles, carry first" 'grep -q "PIVOT X" "$prompt_file" && head -1 "$prompt_file" | grep -q Unmet'
rm -f $AG/PIVOT.md; post
chk "iter2 gate passes: carry removed" '[ ! -e $AG/CONTRACT-CARRY.md ]'
build_prompt_file
chk "iter3: plain prompt again" '[ "$prompt_file" = tools/agent/ITERATION.md ]'
# wiring in loop.sh itself
B=$(grep -n '^  build_prompt_file$' "$LOOP" | head -1 | cut -d: -f1); R=$(grep -n 'tools/agent/runner.sh "\$prompt_file"' "$LOOP" | head -1 | cut -d: -f1)
chk "loop.sh builds the prompt before the runner call" '[ -n "$B" ] && [ -n "$R" ] && [ "$B" -lt "$R" ]'
chk "loop.sh writes/clears the carry after the final verify" 'grep -q "then contract_carry_clear" "$LOOP" && grep -q "else contract_carry_write" "$LOOP"'
[ $fail = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
