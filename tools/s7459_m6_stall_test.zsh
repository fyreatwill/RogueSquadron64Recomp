#!/bin/zsh
# s7459 class DO: m6_god_common.sh scored stalls by [vi] row COUNT, but rows print every 64 VIs whatever the game does, so a held
# frame (fs stuck, VI ticking: s6993 shape) read vi_stalls30s=0. Checks: (1) the m6 progress probe vprog follows fs=, not the row
# count; (2) tools/agent/vilog_stalls.py flags a fake held-fs log and a REAL one (s61_death_repro run4, fs=2199 for 3776 VIs) and
# passes a fake advancing log; (3) soak_verdict_fields counts fs_holds>0 as a stall arm; (4) mutation: M6_STALL_LINES=1 (old row
# count) cannot tell held from advancing; a vilog scorer with the hold test removed misses the held log.
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$(mktemp -d /tmp/s7459.XXXX); fail=0
chk(){ if [[ $2 == $3 ]]; then echo "ok   $1 ($2)"; else echo "FAIL $1 got '$2' want '$3'"; fail=$((fail+1)); fi; }
mk(){ local i; for i in $(seq 0 $2); do echo "[vi] update_screen #$((i*64)) origin=0x0098B038 width=796 status=0x3246 v_current=0 nonzero=1 fs=$(($1 ? i*50 : 273)) pq.wc=0"; done > $3; }
mk 1 60 $T/adv.log; mk 0 60 $T/held.log
eval "$(grep -E '^  vprog\(\)' scratch/agent/m6_god_common.sh)" || echo "FAIL vprog not found"
L=$T/held.log; a=$(vprog); echo "[vi] update_screen #9999 origin=0x0098B038 fs=273" >> $L; b=$(vprog)
chk "vprog held log: no progress after a new row" "$([[ $a == $b ]] && echo same || echo moved)" same
L=$T/adv.log;  a=$(vprog); echo "[vi] update_screen #9999 origin=0x0098B038 fs=99999" >> $L; b=$(vprog)
chk "vprog advancing log: progress (neg ctl)" "$([[ $a == $b ]] && echo same || echo moved)" moved
L=$T/held.log; a=$(env M6_STALL_LINES=1 zsh -c "L=$L; $(grep -E '^  vprog\(\)' scratch/agent/m6_god_common.sh); vprog"); echo "[vi] update_screen #10063 origin=0x0098B038 fs=273" >> $L
b=$(env M6_STALL_LINES=1 zsh -c "L=$L; $(grep -E '^  vprog\(\)' scratch/agent/m6_god_common.sh); vprog")
chk "mutation: row count reads the held log as progress" "$([[ $a == $b ]] && echo same || echo moved)" moved
VS(){ python3 tools/agent/vilog_stalls.py $1 2>/dev/null | cut -d' ' -f1; }
chk "vilog fake advancing -> 0" "$(VS $T/adv.log)" "fs_holds=0"
chk "vilog fake held -> 1"      "$(VS $T/held.log)" "fs_holds=1"
R=scratch/s61_death_repro/run4/vilines.txt
[ -f $R ] && chk "vilog REAL s61 run4 held fs=2199 -> 1" "$(VS $R)" "fs_holds=1" || echo "skip real control (missing $R)"
chk "vilog no rows -> na" "$(echo hello > $T/none.log; VS $T/none.log)" "fs_holds=na"
sed 's/            if h >= gap: eps.append((s_vi, last_vi, s_fs))/            pass/' tools/agent/vilog_stalls.py > $T/vm.py; grep -q '^            pass$' $T/vm.py || echo 'FAIL mutation sed did not apply'
chk "mutation: scorer without hold test misses held" "$(python3 $T/vm.py $T/held.log | cut -d' ' -f1)" "fs_holds=0"
V(){ printf '%s\n' "$1" > $T/v.log; zsh tools/agent/soak_verdict_fields.sh $T/v.log | grep -oE 'stall_arms=[0-9]+|stall_na=[0-9]+' | tr '\n' ' '; }
chk "verdict fs_holds=1 with vi_stalls30s=0 -> stall" "$(V 'tag=a alive_at_end=1 crashlines=0 vi_stalls30s=0 fs_holds=1 max_fs_hold_vi=3776')" "stall_arms=1 stall_na=0 "
chk "verdict fs_holds=0 -> clean" "$(V 'tag=a alive_at_end=1 crashlines=0 vi_stalls30s=0 fs_holds=0')" "stall_arms=0 stall_na=0 "
chk "verdict dead arm na -> stall_na" "$(V 'tag=a alive_at_end=0 crashlines=1 vi_stalls30s=na')" "stall_arms=0 stall_na=1 "
zsh tools/s7453_harness_death_test.zsh > $T/dt.out 2>&1; chk "s7453 harness test still passes" $? 0; grep FAIL $T/dt.out
rm -rf $T; echo "failures: $fail"; exit $((fail > 0))
