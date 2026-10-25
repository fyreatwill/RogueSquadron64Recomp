#!/bin/zsh
# Paired 12 MB phase-4 census. s6198 adds ROGUESQ_LOG_G1D_FILLPC and stops
# once both arms have the join/copy/root controls plus a fill-PC summary.
set -u
setopt NULL_GLOB NO_NOMATCH
cd "$(git rev-parse --show-toplevel)" || exit 1
D="scratch/agent/soak_results/s6198e"
mkdir -p "$D/ctl-fb" "$D/wide-fb"
export FBD_EVERY_V=1
export HOLD_S=90 LEVEL=1

if /usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'; then
  echo "SCREEN LOCKED" | tee "$D/summary"
  exit 4
fi
for arm in ctl wide; do
  dir="scratch/agent/m6/g1_lvl1_${arm}"
  mkdir -p "$dir"
  rm -f "$dir/run.log" "$dir/keys.log" "$dir/summary" "$dir"/fail_att*.log
done

run_arm() {
  local arm=$1 aspect=$2 origin=$3 dump=$4 width=0
  [[ "$arm" == wide ]] && width=796
  env ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT="$aspect" ROGUESQ_FB_WIDTH="$width" \
      ROGUESQ_FB_DUMP_VI=1 ROGUESQ_FB_DUMP_DIR="$dump" TITLE_ORIGIN="$origin" \
      MISSION_RE=ZZZ ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FORCE_UNLOCK=1 \
      ROGUESQ_FORCE_SAVE_MISSION=1 LEVEL=1 ROGUESQ_G1B=1 TAG="s6198_${arm}" \
      TAG_SUFFIX="_${arm}" BUILD="$PWD/build" HOLD=90 ROGUESQ_NO_PKILL=1 \
      XENV_EXTRA="ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_FB_ALLOC=1 ROGUESQ_LOG_RDP_ROUTE=1 ROGUESQ_LOG_RDP_WORDS=1 ROGUESQ_LOG_G1D_COPY=1 ROGUESQ_LOG_G1D_CMD=1 ROGUESQ_LOG_G1D_TARGET=1 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_G1D_INPUT=1 ROGUESQ_LOG_G1D_READS=1 ROGUESQ_LOG_G1D_FILLPC=1 ROGUESQ_FB_DUMP_VI=1 ROGUESQ_FB_DUMP_DIR=$dump ROGUESQ_FB_WIDTH=$width" \
      python3 -c 'import os
try:
    os.setsid()
except OSError:
    pass
os.execvp("zsh", ["zsh", "scratch/agent/g1_level_coverage_common.zsh"])' \
      >"$D/$arm.out" 2>&1 &
  echo $!
}

# g1_level_coverage_common overwrites TAG to g1_lvl${LEVEL}${TAG_SUFFIX}.
arm_dir() { echo "scratch/agent/m6/g1_lvl1_$1"; }

arm_stats() {
  local arm=$1
  python3 - "$arm" "$D" <<'PY'
import sys
from pathlib import Path
arm, dest = sys.argv[1], Path(sys.argv[2])
d = Path(f"scratch/agent/m6/g1_lvl1_{arm}")
files = []
run = d / "run.log"
if run.exists():
    files.append(run)
files.extend(sorted(d.glob("fail_att*.log")))
best, bestn = None, -1
def count(path):
    joins = copies = roots = fills = sigs = 0
    node = b""
    keep = []
    with path.open("rb") as f:
        for raw in f:
            if b"[g1d-join] phase=4 " in raw: joins += 1
            elif b"[g1d-copy] phase=4 " in raw: copies += 1
            elif b"root_seq=1 " in raw and b"root_norm=0x003BD0" in raw: roots += 1
            elif b"[g1d-fill-hi]" in raw or b"[g1d-fill] gen=" in raw or b"[g1d-fill-exact]" in raw or b"[g1d-fill-ctl]" in raw or b"[g1d-fill-clobber]" in raw:
                fills += b"[g1d-fill] gen=" in raw
                sigs += b"value=05200002" in raw
                keep.append(raw)
            elif b"[g1d-node] phase=4 n=0 " in raw and not node:
                node = raw
                keep.append(raw)
    return joins, copies, roots, fills, sigs, node, keep
scored = []
for path in files:
    try:
        scored.append((path, count(path)))
    except OSError:
        continue
if not scored:
    print("0 0 0 0 0 missing")
    raise SystemExit
path, (joins, copies, roots, fills, sigs, node, keep) = max(scored, key=lambda item: item[1][0])
(dest / f"{arm}.fill").write_bytes(b"".join(keep))
if node:
    (dest / f"{arm}.node").write_bytes(node.split(b" bytes=")[0] + b"\n")
(dest / f"{arm}.logpath").write_text(str(path) + "\n")
print(f"{joins} {copies} {roots} {fills} {sigs} {path}")
PY
}

ready() {
  local arm=$1 need_sig=$2
  local line joins copies roots fills sigs log
  line=$(arm_stats "$arm") || return 1
  joins=${line%% *}
  line=${line#* }
  copies=${line%% *}
  line=${line#* }
  roots=${line%% *}
  line=${line#* }
  fills=${line%% *}
  line=${line#* }
  sigs=${line%% *}
  log=${line#* }
  echo "$arm joins=$joins copies=$copies roots=$roots fills=$fills sig052=$sigs log=$log" >> "$D/poll.txt"
  # Wide phase-4 copies plateaued at 392 while joins already sat at the 160
  # cap, so requiring 400 copies never returned. Joins + root are the controls.
  (( joins >= 160 && roots >= 1 && fills >= 1 )) || return 1
  (( need_sig == 0 || sigs >= 1 )) || return 1
  return 0
}

p1=$(run_arm ctl 4:3 0x00B90400 "$D/ctl-fb")
p2=$(run_arm wide 16:9 0x00B52200 "$D/wide-fb")
echo "pgids ctl=$p1 wide=$p2" | tee "$D/pgids"

deadline=$((SECONDS + 780))
while (( SECONDS < deadline )); do
  sleep 8
  # Stop on the route controls. sig052 is recorded either way; requiring it
  # kept a blind phase>=4 run alive through every nomission retry.
  if ready ctl 0 && ready wide 0; then
    echo "criteria met at ${SECONDS}s" | tee -a "$D/poll.txt"
    break
  fi
  kill -0 "$p1" 2>/dev/null || echo "ctl harness exited" >> "$D/poll.txt"
  kill -0 "$p2" 2>/dev/null || echo "wide harness exited" >> "$D/poll.txt"
  if ! kill -0 "$p1" 2>/dev/null && ! kill -0 "$p2" 2>/dev/null; then
    break
  fi
done
kill -KILL -"$p1" -"$p2" 2>/dev/null || true
kill -KILL "$p1" "$p2" 2>/dev/null || true
sleep 1
ready ctl 0 || true
ready wide 0 || true
echo "stopped at ${SECONDS}s" | tee -a "$D/poll.txt"
