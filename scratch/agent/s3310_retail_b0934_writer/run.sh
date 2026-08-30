#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT=$ROOT/scratch/agent/s3310_retail_b0934_writer
ORACLE=$ROOT/tools/oracle/build/rs64_oracle
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"

# Watch indices:
#  0 write 0x0:0x800000                 whole-RDRAM control (removed at 10000)
#  1 write 0x000B0934:0x000B0938        cinematic state pointer
#  2 exec 0x800AF408                    cinematicInitializer entry
#  3 exec 0x800AF430                    bne existing-ptr ($v0 = loaded word)
#  4 exec 0x800AF4B8                    sw $v0, 0x934($s2)
#  5 exec 0x800AF640                    sw $zero, 0x934($s0)
#  6 exec 0x800AF550                    cinematicStageAdvancer entry
#  7 exec 0x800AF55C                    beq $v1, $zero (ptr-check)
#  8 exec 0x800A5D80                    cinematicLoopBody entry
# Detail 1 and the rare exec PCs so --hit-cap / EXEC_LOG_CAP cannot hide them.
# AF550/AF55C stay histogram-only after the first 64 exec prints.

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
            --watch-write 0x000B0934:0x000B0938 \
            --watch-pc 0x800AF408,0x800AF430,0x800AF4B8,0x800AF640,0x800AF550,0x800AF55C,0x800A5D80 \
            --detail-watch 1 \
            --detail-watch 2 \
            --detail-watch 3 \
            --detail-watch 4 \
            --detail-watch 5 \
            --detail-watch 8 \
            --first-watch 1 \
            --pc-hist-watch 1 \
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
    0x800AF408, 0x800AF430, 0x800AF4B8, 0x800AF640,
    0x800AF550, 0x800AF55C, 0x800A5D80,
]
names = {
    0x800AF408: "init-entry",
    0x800AF430: "init-bne-existing",
    0x800AF4B8: "init-sw-v0",
    0x800AF640: "deact-sw-zero",
    0x800AF550: "adv-entry",
    0x800AF55C: "adv-beq-v1",
    0x800A5D80: "cine-entry",
}

rdram_hits = 0
m = re.search(r"watch write \[0x00000000,0x00800000\): (\d+) hit", text)
if m:
    rdram_hits = int(m.group(1))
pos_ctl = "positive-control threshold reached" in text
gpr_ctl = any(l.startswith("[gpr-ctl]") for l in lines)

ptr_hits = 0
m = re.search(r"watch write \[0x000b0934,0x000b0938\): (\d+) hit", text, re.I)
if m:
    ptr_hits = int(m.group(1))

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
    r".*width=(\d+) origin=(0x[0-9a-f]+)"
)
hit_write = re.compile(
    r"\[hit\] w addr=(0x[0-9a-f]+) pc=(0x[0-9a-f]+) prev_pc=(0x[0-9a-f]+) t=([0-9.]+)s n=(\d+)"
)

first = {}
last = {}
printed = collections.Counter()
exec_rows = collections.defaultdict(list)
for l in lines:
    m = hit_exec.search(l)
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
        "width": int(m.group(10)),
        "origin": int(m.group(11), 16),
        "raw": l,
    }
    printed[pc] += 1
    first.setdefault(pc, rec)
    last[pc] = rec
    exec_rows[pc].append(rec)

writes = []
for l in lines:
    m = hit_write.search(l)
    if not m:
        continue
    addr = int(m.group(1), 16)
    if not (0x000B0934 <= addr < 0x000B0938):
        continue
    writes.append({
        "addr": addr,
        "pc": int(m.group(2), 16),
        "prev": int(m.group(3), 16),
        "t": float(m.group(4)),
        "n": int(m.group(5)),
        "raw": l,
    })

writer_hist = []
for l in lines:
    m = re.search(r"\[oracle\] writer-pc watch=1 pc=(0x[0-9a-f]+) n=(\d+)", l)
    if m:
        writer_hist.append((int(m.group(1), 16), int(m.group(2))))
phase_hists = collections.defaultdict(list)
for l in lines:
    m = re.search(
        r"\[oracle\] writer-pc-phase origin=(0x[0-9a-f]+) width=(\d+) watch=1 pc=(0x[0-9a-f]+) n=(\d+)",
        l,
    )
    if m:
        key = (int(m.group(1), 16), int(m.group(2)))
        phase_hists[key].append((int(m.group(3), 16), int(m.group(4))))

done = None
for l in lines:
    if l.startswith("[oracle] done:"):
        done = l

def n_for(pc):
    if pc in watch_hits:
        return watch_hits[pc]
    return sum(n for _, n in exec_prev.get(pc, []))

entry_n = n_for(0x800A5D80)
init_n = n_for(0x800AF408)
store_n = n_for(0x800AF4B8)
deact_n = n_for(0x800AF640)
bne_n = n_for(0x800AF430)
adv_n = n_for(0x800AF550)
beq_n = n_for(0x800AF55C)

controls_ok = (rdram_hits >= 10000 and pos_ctl and gpr_ctl and vi_640 and entry_n >= 1)

t_entry = first[0x800A5D80]["t"] if 0x800A5D80 in first else None
t_title = t_1024

def in_first_attract(t):
    if t_entry is None:
        return False
    if t < t_entry:
        return "before-entry"
    if t_title is not None and t >= t_title:
        return "after-title"
    return "during-cinematic"

af4b8_writes = [w for w in writes if w["pc"] in (0x800AF4B8, 0x800AF4B4)]
af640_writes = [w for w in writes if w["pc"] in (0x800AF640, 0x800AF63C)]
other_writes = [w for w in writes if w not in af4b8_writes and w not in af640_writes]

def is_kseg0(v):
    return 0x80000000 <= v <= 0x807FFFFF or 0xA0000000 <= v <= 0xA07FFFFF

store_v0s = [r["v0"] for r in exec_rows.get(0x800AF4B8, [])]
bne_v0s = [r["v0"] for r in exec_rows.get(0x800AF430, [])]
live_store = any(is_kseg0(v) for v in store_v0s)
zero_bne = any(v == 0 for v in bne_v0s)
live_bne = any(is_kseg0(v) for v in bne_v0s)

af4b8_before_or_at_entry = any(
    t_entry is not None and w["t"] <= t_entry + 0.2 for w in af4b8_writes
)
af4b8_during = any(in_first_attract(w["t"]) == "during-cinematic" for w in af4b8_writes)
zero_during = any(in_first_attract(w["t"]) == "during-cinematic" for w in af640_writes)
zero_before_title = any(
    t_title is None or w["t"] < t_title for w in af640_writes
)
zero_after_title = any(
    t_title is not None and w["t"] >= t_title for w in af640_writes
)

if not controls_ok:
    hyp = "H-CoverageInvalid"
    reason = "missing whole-RDRAM / gpr-ctl / VI-640 / cinematic-entry control"
elif (af4b8_writes or live_store or live_bne) and zero_during and not (t_title and all(
        in_first_attract(w["t"]) == "after-title" or (
            t_title is not None and w["t"] >= t_title - 1.0
        ) for w in af640_writes)):
    # zero store while still in first cinematic (before title, and not the
    # ~1s exit-cleanup window just before title) selects init-then-clear.
    early_zeros = [
        w for w in af640_writes
        if in_first_attract(w["t"]) == "during-cinematic"
        and (t_title is None or w["t"] < t_title - 1.0)
    ]
    if early_zeros:
        hyp = "H-RetailInitThenClear"
        reason = "live write then AF640 zero during first cinematic before exit"
    elif af4b8_writes or live_store:
        hyp = "H-RetailPtrLive"
        reason = "AF4B8/KSEG0 write; AF640 only at/after cinematic exit"
    else:
        hyp = "H-RetailPtrLive"
        reason = "existing KSEG0 snapshot at AF430; AF640 only at/after exit"
elif af4b8_writes or live_store:
    hyp = "H-RetailPtrLive"
    reason = "AF4B8 store of KSEG0 (or named-PC write) before/during first attract"
elif live_bne and not af4b8_writes:
    hyp = "H-RetailPtrLive"
    reason = "AF430 $v0 already KSEG0; initializer skipped the store"
elif ptr_hits == 0 and init_n >= 1 and (zero_bne or (bne_n >= 1 and not live_bne and not live_store)):
    hyp = "H-RetailPtrAlsoZero"
    reason = "initializer executed; pointer snapshot 0; no 0x000B0934 writes"
elif ptr_hits == 0 and init_n >= 1:
    hyp = "H-RetailPtrAlsoZero"
    reason = "initializer executed with no 0x000B0934 writes"
elif ptr_hits == 0 and init_n == 0 and adv_n >= 1:
    hyp = "H-RetailPtrAlsoZero"
    reason = "advancer live, initializer silent, no pointer writes"
elif other_writes:
    hyp = "H-RetailPtrLive"
    reason = "unnamed writer hit 0x000B0934"
else:
    hyp = "H-CoverageInvalid"
    reason = "unclassified (no pointer writes, initializer/advancer pattern unmatched)"

retry = 0
if rdram_hits >= 10000 and pos_ctl and gpr_ctl and vi_640 and entry_n == 0:
    retry = 1  # hit-cap may have truncated before cinematic entry

def fmt_rec(fr):
    if not fr:
        return ""
    return (f" first_t={fr['t']:.1f} first_prev=0x{fr['prev']:08x}"
            f" first_v0=0x{fr['v0']:08x} first_s1=0x{fr['s1']:08x}"
            f" first_a0=0x{fr['a0']:08x} first_a2=0x{fr['a2']:08x}"
            f" first_w={fr['width']} first_org=0x{fr['origin']:08x}")

with open(outp, "w") as f:
    def p(s=""):
        f.write(s + "\n")
        print(s)
    p(f"rdram_hits={rdram_hits} pos_ctl={int(pos_ctl)} gpr_ctl={int(gpr_ctl)}")
    p(f"vi_640={int(vi_640)} t_640={t_640} origin_640={origin_640 and hex(origin_640)}")
    p(f"vi_1024={int(vi_1024)} t_1024={t_1024}")
    p(f"done={done or 'missing'}")
    p(f"controls_ok={int(controls_ok)} retry={retry}")
    p(f"selected={hyp}")
    p(f"reason={reason}")
    p(f"ptr_watch_hits={ptr_hits} printed_writes={len(writes)}")
    p(f"t_entry={t_entry}")
    p("pc_table")
    for pc in pcs:
        prev_s = ",".join(f"0x{pr:08x}:{n}" for pr, n in exec_prev.get(pc, [])) or "none"
        p(f"  {names[pc]:18s} pc=0x{pc:08x} n={n_for(pc)} printed={printed[pc]} prevs={prev_s}{fmt_rec(first.get(pc))}")
    p("init_bne_v0=" + ",".join(f"0x{v:08x}" for v in bne_v0s[:20]) or "none")
    p("init_sw_v0=" + ",".join(f"0x{v:08x}" for v in store_v0s[:20]) or "none")
    p("writes")
    if not writes:
        p("  none")
    for w in writes:
        p(f"  t={w['t']:.1f} pc=0x{w['pc']:08x} prev=0x{w['prev']:08x} phase={in_first_attract(w['t'])} n={w['n']}")
    p("writer_hist=" + ",".join(f"0x{pc:08x}:{n}" for pc, n in writer_hist) or "none")
    for key, rows in phase_hists.items():
        origin, width = key
        p(f"writer_hist_phase origin=0x{origin:08x} width={width} "
          + (",".join(f"0x{pc:08x}:{n}" for pc, n in rows) or "none"))
    p(f"af4b8_writes={len(af4b8_writes)} af640_writes={len(af640_writes)} other_writes={len(other_writes)}")
    p(f"live_store={int(live_store)} live_bne={int(live_bne)} zero_bne={int(zero_bne)}")
    p(f"zero_during={int(zero_during)} zero_before_title={int(zero_before_title)} zero_after_title={int(zero_after_title)}")
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
