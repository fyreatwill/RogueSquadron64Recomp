#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3312_retail_cine_init_path
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

# Watch indices:
#  0 write 0x0:0x800000                 whole-RDRAM control (removed at 10000)
#  1 exec 0x800A5D80                    cinematicLoopBody entry
#  2 exec 0x800A626C                    beq $v1,$zero -> 627C (time-pred; taken bypasses flag)
#  3 exec 0x800A6274                    beq $v0,$zero -> 62EC (flag-byte; taken skips jal)
#  4 exec 0x800A6288                    bne $v0,$zero -> 62EC (already-active; taken skips jal)
#  5 exec 0x800A62B4                    jal cinematicInitializer
#  6 exec 0x800AF4B8                    sw $v0, 0x934($s2) (same-run jal-completed control)
# Detail 2-6 so --hit-cap / EXEC_LOG_CAP cannot hide the path into 62B4.

run_oracle() {
    local secs=$1
    local log=$2
    local driver=$3
    local hitcap=$4
    : > "$log"
    print "oracle_start secs=$secs hitcap=$hitcap" >> "$driver"

    (
        cd "$ROOT" || exit 2
        exec env "$ORACLE" \
            --core "$CORE" \
            --rom "$ROM" \
            --video "$VIDEO" \
            --watch-write 0x0:0x800000 \
            --watch-pc 0x800A5D80,0x800A626C,0x800A6274,0x800A6288,0x800A62B4,0x800AF4B8 \
            --detail-watch 2 \
            --detail-watch 3 \
            --detail-watch 4 \
            --detail-watch 5 \
            --detail-watch 6 \
            --pc-hist-phase 0x0066A500:640 \
            --pc-hist-phase 0x00696100:640 \
            --pc-hist-phase 0x00696600:640 \
            --pc-hist-phase 0x00790400:1024 \
            --secs "$secs" --hit-cap "$hitcap" \
            --vi-trace --vi-poll
    ) > "$log" 2>&1 &
    local pid=$!
    print "pid=$pid" >> "$driver"

    local deadline=$((SECONDS + secs + 45))
    local terminal=watchdog
    while (( SECONDS < deadline )); do
        if ! kill -0 "$pid" 2>/dev/null; then
            terminal=process-exit
            break
        fi
        sleep 0.5
    done
    if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
        sleep 0.2
        kill -9 "$pid" 2>/dev/null || true
        terminal=watchdog
    fi
    wait "$pid" 2>/dev/null
    local rc=$?
    print "terminal=$terminal rc=$rc" >> "$driver"
    return 0
}

parse_log() {
    local log=$1
    local out=$2
    python3 - "$log" "$out" <<'PY'
import re, sys, collections
log, outp = sys.argv[1], sys.argv[2]
text = open(log, "rb").read().decode("utf-8", "replace")
lines = text.splitlines()

pcs = [
    0x800A5D80, 0x800A626C, 0x800A6274, 0x800A6288,
    0x800A62B4, 0x800AF4B8,
]
names = {
    0x800A5D80: "cine-entry",
    0x800A626C: "time-pred",
    0x800A6274: "flag-byte",
    0x800A6288: "already-active",
    0x800A62B4: "init-jal",
    0x800AF4B8: "init-sw-v0",
}

rdram_hits = 0
m = re.search(r"watch write \[0x00000000,0x00800000\): (\d+) hit", text)
if m:
    rdram_hits = int(m.group(1))
pos_ctl = "positive-control threshold reached" in text
gpr_ctl = any(l.startswith("[gpr-ctl]") for l in lines)

vi_640 = False
vi_1024 = False
t_640 = None
t_1024 = None
origin_640 = None
vi_rows = []
for l in lines:
    if l.startswith("[vi] "):
        vi_rows.append(l)
        if "WIDTH" in l and "640" in l:
            vi_640 = True
            if t_640 is None:
                tm = re.search(r"t=\s*([0-9.]+)s", l)
                om = re.search(r"origin=(0x[0-9a-f]+)", l, re.I)
                if tm:
                    t_640 = float(tm.group(1))
                if om:
                    origin_640 = int(om.group(1), 16)
        if "1024" in l:
            vi_1024 = True
            if t_1024 is None:
                tm = re.search(r"t=\s*([0-9.]+)s", l)
                if tm:
                    t_1024 = float(tm.group(1))

exec_prev = collections.defaultdict(list)
for l in lines:
    m = re.search(r"\[oracle\] exec-prev pc=(0x[0-9a-f]+) prev=(0x[0-9a-f]+) n=(\d+)", l)
    if m:
        exec_prev[int(m.group(1), 16)].append((int(m.group(2), 16), int(m.group(3))))

watch_hits = {}
for l in lines:
    m = re.search(r"\[oracle\] watch pc \[(0x[0-9a-f]+),0x[0-9a-f]+\): (\d+) hit", l)
    if m:
        watch_hits[int(m.group(1), 16)] = int(m.group(2))

hit_exec = re.compile(
    r"\[hit\] x addr=0x[0-9a-f]+ pc=(0x[0-9a-f]+) prev_pc=(0x[0-9a-f]+) t=([0-9.]+)s n=(\d+)"
    r" v0=(0x[0-9a-f]+) s1=(0x[0-9a-f]+) a0=(0x[0-9a-f]+) a1=(0x[0-9a-f]+) a2=(0x[0-9a-f]+)"
    r".*?v1=(0x[0-9a-f]+)"
    r".*width=(\d+) origin=(0x[0-9a-f]+)"
)
# fallback if v1 is missing from an older binary
hit_exec_nov1 = re.compile(
    r"\[hit\] x addr=0x[0-9a-f]+ pc=(0x[0-9a-f]+) prev_pc=(0x[0-9a-f]+) t=([0-9.]+)s n=(\d+)"
    r" v0=(0x[0-9a-f]+) s1=(0x[0-9a-f]+) a0=(0x[0-9a-f]+) a1=(0x[0-9a-f]+) a2=(0x[0-9a-f]+)"
    r".*width=(\d+) origin=(0x[0-9a-f]+)"
)

first = {}
last = {}
printed = collections.Counter()
exec_rows = collections.defaultdict(list)
v1_present = 0
for l in lines:
    m = hit_exec.search(l)
    if m:
        v1_present += 1
        pc = int(m.group(1), 16)
        rec = {
            "pc": pc,
            "prev": int(m.group(2), 16),
            "t": float(m.group(3)),
            "n": int(m.group(4)),
            "v0": int(m.group(5), 16),
            "s1": int(m.group(6), 16),
            "a0": int(m.group(7), 16),
            "a1": int(m.group(8), 16),
            "a2": int(m.group(9), 16),
            "v1": int(m.group(10), 16),
            "width": int(m.group(11)),
            "origin": int(m.group(12), 16),
            "raw": l,
        }
    else:
        m = hit_exec_nov1.search(l)
        if not m:
            continue
        pc = int(m.group(1), 16)
        rec = {
            "pc": pc,
            "prev": int(m.group(2), 16),
            "t": float(m.group(3)),
            "n": int(m.group(4)),
            "v0": int(m.group(5), 16),
            "s1": int(m.group(6), 16),
            "a0": int(m.group(7), 16),
            "a1": int(m.group(8), 16),
            "a2": int(m.group(9), 16),
            "v1": None,
            "width": int(m.group(10)),
            "origin": int(m.group(11), 16),
            "raw": l,
        }
    printed[pc] += 1
    first.setdefault(pc, rec)
    last[pc] = rec
    exec_rows[pc].append(rec)

done = None
for l in lines:
    if l.startswith("[oracle] done:"):
        done = l

def n_for(pc):
    if pc in watch_hits:
        return watch_hits[pc]
    return sum(n for _, n in exec_prev.get(pc, []))

entry_n = n_for(0x800A5D80)
pred_n = n_for(0x800A626C)
flag_n = n_for(0x800A6274)
act_n = n_for(0x800A6288)
jal_n = n_for(0x800A62B4)
store_n = n_for(0x800AF4B8)

controls_ok = (rdram_hits >= 10000 and pos_ctl and gpr_ctl and vi_640 and entry_n >= 1)
t_entry = first[0x800A5D80]["t"] if 0x800A5D80 in first else None
t_title = t_1024

def taken_time(rec):
    # beq $v1,$zero -> 627C: taken when v1==0 (count >= limit-10)
    if rec["v1"] is None:
        return None
    return 1 if rec["v1"] == 0 else 0

def taken_flag(rec):
    # beq $v0,$zero -> 62EC: taken when v0==0 (also a0 byte)
    return 1 if rec["v0"] == 0 else 0

def taken_active(rec):
    # bne $v0,$zero -> 62EC: taken when v0!=0 (pointer already live)
    return 1 if rec["v0"] != 0 else 0

def classify_rows(pc, taken_fn):
    rows = exec_rows.get(pc, [])
    n_taken = 0
    n_not = 0
    n_unk = 0
    v0s = collections.Counter()
    v1s = collections.Counter()
    a0s = collections.Counter()
    for r in rows:
        t = taken_fn(r) if taken_fn else None
        if t is None:
            n_unk += 1
        elif t:
            n_taken += 1
        else:
            n_not += 1
        v0s[r["v0"]] += 1
        if r["v1"] is not None:
            v1s[r["v1"]] += 1
        a0s[r["a0"]] += 1
    return n_taken, n_not, n_unk, v0s, v1s, a0s

pred_taken, pred_not, pred_unk, pred_v0, pred_v1, pred_a0 = classify_rows(0x800A626C, taken_time)
flag_taken, flag_not, flag_unk, flag_v0, flag_v1, flag_a0 = classify_rows(0x800A6274, taken_flag)
act_taken, act_not, act_unk, act_v0, act_v1, act_a0 = classify_rows(0x800A6288, taken_active)

jal_rows = exec_rows.get(0x800A62B4, [])
first_jal = jal_rows[0] if jal_rows else None
t_jal = first_jal["t"] if first_jal else None

def last_before(pc, t, window=1.0):
    rows = exec_rows.get(pc, [])
    if t is None:
        return None
    before = [r for r in rows if r["t"] <= t + 0.05]
    if not before:
        return None
    last_r = before[-1]
    if last_r["t"] < t - window:
        return last_r  # still return; caller notes the gap
    return last_r

last_pred = last_before(0x800A626C, t_jal, window=2.0)
last_flag = last_before(0x800A6274, t_jal, window=2.0)
last_act = last_before(0x800A6288, t_jal, window=2.0)

# First-attract window: entry until title (or first jal if title missing)
def in_first_attract(t):
    if t_entry is None:
        return False
    if t < t_entry:
        return False
    if t_title is not None and t >= t_title:
        return False
    return True

pred_attr = [r for r in exec_rows.get(0x800A626C, []) if in_first_attract(r["t"])]
flag_attr = [r for r in exec_rows.get(0x800A6274, []) if in_first_attract(r["t"])]
act_attr = [r for r in exec_rows.get(0x800A6288, []) if in_first_attract(r["t"])]
jal_attr = [r for r in jal_rows if in_first_attract(r["t"]) or (t_jal is not None and abs(r["t"] - t_jal) < 0.2)]

# Flag fall-through that can continue to jal: taken=0 ($v0!=0 / $a0!=0)
flag_fallthrough_to_jal = False
if last_flag is not None and t_jal is not None:
    if taken_flag(last_flag) == 0 and last_flag["t"] >= t_jal - 0.5:
        flag_fallthrough_to_jal = True

pred_taken_at_jal = None
if last_pred is not None:
    pred_taken_at_jal = taken_time(last_pred)

# 6274 silent on the last pre-jal 626C window: last flag is earlier than last pred,
# or flag never fired after last taken-pred.
flag_silent_at_jal = False
if last_pred is not None and t_jal is not None:
    if last_flag is None:
        flag_silent_at_jal = True
    elif last_flag["t"] + 0.05 < last_pred["t"] and pred_taken_at_jal == 1:
        flag_silent_at_jal = True
    elif last_flag["t"] + 0.05 < t_jal and pred_taken_at_jal == 1 and taken_flag(last_flag) == 1:
        flag_silent_at_jal = True

act_not_taken_at_jal = None
if last_act is not None:
    act_not_taken_at_jal = taken_active(last_act) == 0

retry = 0
if rdram_hits >= 10000 and pos_ctl and gpr_ctl and vi_640 and entry_n == 0:
    retry = 1

if not controls_ok:
    hyp = "H-CoverageInvalid"
    reason = "missing whole-RDRAM / gpr-ctl / VI-640 / cinematic-entry control"
elif jal_n < 1:
    hyp = "H-CoverageInvalid"
    reason = "cinematic entry and VI-640 live but 62B4 silent (retail jal expected ~48s)"
elif flag_fallthrough_to_jal:
    hyp = "H-RetailFlagSet"
    reason = "6274 taken=0 ($a0/$v0 != 0) on a row that continues to 62B4"
elif pred_taken_at_jal == 1 and (flag_silent_at_jal or (last_flag is not None and taken_flag(last_flag) == 1)):
    hyp = "H-RetailTimeBypass"
    reason = "626C taken=1 ($v1==0) on last pre-jal window; 6274 silent or taken=1 (no fall-through)"
elif pred_taken_at_jal == 0 and last_flag is not None and taken_flag(last_flag) == 0:
    hyp = "H-RetailFlagSet"
    reason = "626C not-taken and 6274 fall-through ($v0!=0) into 62B4"
elif jal_n >= 1:
    hyp = "H-RetailJalOther"
    reason = "62B4 fired without 626C taken-bypass or 6274 fall-through describing the path"
else:
    hyp = "H-CoverageInvalid"
    reason = "unclassified"

def fmt_rec(fr):
    if not fr:
        return ""
    v1s = "" if fr["v1"] is None else f" first_v1=0x{fr['v1']:08x}"
    return (f" first_t={fr['t']:.1f} first_prev=0x{fr['prev']:08x}"
            f" first_v0=0x{fr['v0']:08x}{v1s} first_s1=0x{fr['s1']:08x}"
            f" first_a0=0x{fr['a0']:08x} first_a2=0x{fr['a2']:08x}"
            f" first_w={fr['width']} first_org=0x{fr['origin']:08x}")

def fmt_last(fr, taken):
    if not fr:
        return "none"
    v1s = "v1=missing" if fr["v1"] is None else f"v1=0x{fr['v1']:08x}"
    ts = "unk" if taken is None else str(taken)
    return (f"t={fr['t']:.1f} prev=0x{fr['prev']:08x} v0=0x{fr['v0']:08x} {v1s} "
            f"a0=0x{fr['a0']:08x} taken={ts} w={fr['width']} org=0x{fr['origin']:08x}")

def top_counter(c, k=6):
    if not c:
        return "none"
    return ",".join(f"0x{v:08x}:{n}" for v, n in c.most_common(k))

with open(outp, "w") as f:
    def p(s=""):
        f.write(s + "\n")
        print(s)
    p(f"rdram_hits={rdram_hits} pos_ctl={int(pos_ctl)} gpr_ctl={int(gpr_ctl)}")
    p(f"vi_640={int(vi_640)} t_640={t_640} origin_640={origin_640 and hex(origin_640)}")
    p(f"vi_1024={int(vi_1024)} t_1024={t_1024}")
    p(f"done={done or 'missing'}")
    p(f"controls_ok={int(controls_ok)} retry={retry} v1_printed={v1_present}")
    p(f"selected={hyp}")
    p(f"reason={reason}")
    p(f"t_entry={t_entry} t_jal={t_jal} t_title={t_title}")
    p("pc_table")
    for pc in pcs:
        prev_s = ",".join(f"0x{pr:08x}:{n}" for pr, n in exec_prev.get(pc, [])) or "none"
        p(f"  {names[pc]:16s} pc=0x{pc:08x} n={n_for(pc)} printed={printed[pc]} prevs={prev_s}{fmt_rec(first.get(pc))}")
    p(f"time_pred taken={pred_taken} not={pred_not} unk={pred_unk} v0={top_counter(pred_v0)} v1={top_counter(pred_v1)} a0={top_counter(pred_a0)}")
    p(f"flag_byte taken={flag_taken} not={flag_not} unk={flag_unk} v0={top_counter(flag_v0)} v1={top_counter(flag_v1)} a0={top_counter(flag_a0)}")
    p(f"already_active taken={act_taken} not={act_not} unk={act_unk} v0={top_counter(act_v0)} a0={top_counter(act_a0)}")
    p(f"last_pred_at_jal={fmt_last(last_pred, pred_taken_at_jal)}")
    p(f"last_flag_at_jal={fmt_last(last_flag, None if last_flag is None else taken_flag(last_flag))}")
    p(f"last_act_at_jal={fmt_last(last_act, None if last_act is None else taken_active(last_act))}")
    p(f"flag_fallthrough_to_jal={int(flag_fallthrough_to_jal)} flag_silent_at_jal={int(flag_silent_at_jal)}")
    p(f"pred_taken_at_jal={pred_taken_at_jal} act_not_taken_at_jal={act_not_taken_at_jal}")
    p(f"first_attract pred={len(pred_attr)} flag={len(flag_attr)} act={len(act_attr)} jal={len(jal_attr)}")
    p("jal_rows")
    if not jal_rows:
        p("  none")
    for r in jal_rows[:8]:
        v1s = "missing" if r["v1"] is None else f"0x{r['v1']:08x}"
        p(f"  t={r['t']:.1f} prev=0x{r['prev']:08x} v0=0x{r['v0']:08x} v1={v1s} a0=0x{r['a0']:08x} w={r['width']} org=0x{r['origin']:08x}")
    p("vi_rows")
    for l in vi_rows:
        if "WIDTH" in l and ("->" in l or "1024" in l or "640" in l):
            p("  " + l)
PY
}

DRIVER=$OUT/driver.log
: > "$DRIVER"
print "HYPOTHESIS-ID: m5-osvimode-postviewer-continuation" >> "$DRIVER"

run_oracle 90 "$OUT/run.log" "$DRIVER" 20000
parse_log "$OUT/run.log" "$OUT/summary.txt"
cat "$OUT/summary.txt" >> "$DRIVER"

retry=$(awk -F= '/^retry=/{print $2}' "$OUT/summary.txt")
if [ "$retry" = "1" ]; then
    print "retrying secs=90 hitcap=100000 because cinematic entry was silent with live VI-640" >> "$DRIVER"
    run_oracle 90 "$OUT/run_retry.log" "$DRIVER" 100000
    parse_log "$OUT/run_retry.log" "$OUT/summary_retry.txt"
    cat "$OUT/summary_retry.txt" >> "$DRIVER"
    cp "$OUT/summary_retry.txt" "$OUT/summary.txt"
fi

print "final_selected=$(awk -F= '/^selected=/{print $2}' "$OUT/summary.txt")" >> "$DRIVER"
exit 0
