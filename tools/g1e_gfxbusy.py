"""s6704 G1e: per-run Gfx-thread budget from [g1b] lines (t >= tmin). The Gfx thread runs send_dl (RSP LLE gfx task + RT64
submit) and update_screen (present) serially, so busy_ms/s = tasks*sd_wall + vi*us_wall. busy near 1000 => the Gfx thread
itself binds the frame rate (H-gfx); busy well under 1000 with tasks < 60 => the game thread or pacing binds (H-cpu/H-pace).
sd_cpu/sd_wall < ~0.9 flags descheduling (H-host). Usage: g1e_gfxbusy.py <run_dir>... [--tmin S]"""
import sys, os, re, statistics as st
args = sys.argv[1:]; tmin = 140
if "--tmin" in args: i = args.index("--tmin"); tmin = int(args[i + 1]); del args[i:i + 2]
R = re.compile(rb"^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/(\d+) sd_cpu=([\d.]+)/(\d+) us_wall=([\d.]+)/(\d+)")
for d in args:
    rows = []
    for ln in open(os.path.join(d, "run.log"), "rb"):
        m = R.match(ln)
        if m and int(m[1]) >= tmin:
            vi, tk, sw, sc, uw = int(m[2]), int(m[3]), float(m[4]), float(m[6]), float(m[8])
            rows.append((tk, tk * sw, vi * uw, sc / sw if sw else 1.0, sw))
    if not rows: print(f"{os.path.basename(d):30s} no g1b rows"); continue
    busy = [a + b for _, a, b, _, _ in rows]; q = sorted(busy)
    print(f"{os.path.basename(d):30s} n={len(rows):3d} tasks={st.mean(r[0] for r in rows):5.1f} sd_ms={st.mean(r[4] for r in rows):5.1f} "
          f"send_dl={st.mean(r[1] for r in rows):4.0f} present={st.mean(r[2] for r in rows):4.0f} busy={st.mean(busy):4.0f} "
          f"busy_p90={q[int(.9 * (len(q) - 1))]:4.0f} cpu/wall={st.mean(r[3] for r in rows):.2f} ms/s")


def serial_fit(d, tmin=140):
    """Within-run test of the serial model frame_ms = c + k*sd_ms over seconds with tasks < 58 (uncapped). k~1 => the game
    frame waits for the gfx task (no overlap); k~0 => gfx cost does not set the frame period."""
    xs, ys = [], []
    for ln in open(os.path.join(d, "run.log"), "rb"):
        m = R.match(ln)
        if m and int(m[1]) >= tmin and 5 <= int(m[3]) < 58:
            xs.append(float(m[4])); ys.append(1000.0 / int(m[3]))
    if len(xs) < 10: return None
    mx, my = st.mean(xs), st.mean(ys); sxx = sum((x - mx) ** 2 for x in xs)
    k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0
    r = st.correlation(xs, ys) if sxx else 0
    return len(xs), k, my - k * mx, r


if __name__ == "__main__":
    for d in args:
        f = serial_fit(d, tmin)
        print(f"  fit {os.path.basename(d):28s}", "n<10 (capped)" if not f else "n=%d frame_ms = %.1f + %.2f*sd_ms  r=%.2f" % (f[0], f[2], f[1], f[3]))


def hk_split(d, tmin=140, key="hk"):
    """s6704 same-run A/B: [g1b] seconds grouped by <key>=<0|1> (hk: ROGUESQ_RSP_HOOKS_TOGGLE; as: s6705 ROGUESQ_RDP_ASYNC_TOGGLE). Skips the first second
    after each flip so a task straddling the boundary does not smear across arms."""
    H = re.compile(rb"^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/.* " + key.encode() + rb"=(\d)")
    arms = {0: [], 1: []}; prev = None
    for ln in open(os.path.join(d, "run.log"), "rb"):
        m = H.match(ln)
        if not m: continue
        hk = int(m[5]); fresh = prev is not None and hk != prev; prev = hk
        if int(m[1]) >= tmin and not fresh and int(m[3]): arms[hk].append((int(m[3]), float(m[4])))
    for hk, r in arms.items():
        if r: print(f"  {key}={hk} n={len(r):3d} tasks={st.mean(x[0] for x in r):5.1f} sd_ms={st.mean(x[1] for x in r):5.2f} "
                    f"sd_ms_median={st.median(x[1] for x in r):5.2f}")


if __name__ == "__main__" and (os.environ.get("HK") or os.environ.get("AS")):
    for d in args: print(os.path.basename(d)); hk_split(d, tmin, "as" if os.environ.get("AS") else "hk")
