#!/usr/bin/env python3
"""s6806 G3: batch song-window audit over every saved dt-pinned retail/port pair (g3_song_windows.py per pair).
Finds every RETAIL_DIR/oracle.log[.zst] under scratch/ that carries the song-handle dump (m=8010c0e0), pairs it with
the sibling port rand log (retail -> port.rand.txt, retailb -> portb.rand.txt, retail_gap2 -> port.rand.txt), and
prints one row per song window matched by order: retail ticks/VI/buffers vs port ticks/VI/buffers and the ratios.
H-parity: every VI/buffer ratio within ~1%. A song whose ratio is off = audio-rate defect (H-rate) or a game-event end.
usage: g3_song_audit.py [GLOB ...]   (default scratch/s67*/ scratch/s68*/)"""
import glob, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# scratch dir -> level (session N's runs often live in scratch/s(N+1)); s6756 port/portb predate the s6755 VI-edge fix
LEVEL = {"s6756": 4, "s6757": 5, "s6758": 6, "s6759": 7, "s6760": 8, "s6761": 9, "s6762": 9, "s6763/lvl9": 9,
         "s6763": 10, "s6764": 11, "s6765": 12, "s6766": 13, "s6767": 14, "s6768": 15, "s6769": 16, "s6770": 16,
         "s6771/m17": 17, "s6771/r17": 17, "s6778/r17p": 17, "s6772/r18": 18, "s6773/r19": 19, "s6777": 3,
         "s6804/pair": 9, "s6805": 9}
EXTRA = [("s6756", "retailb", "portd")]  # s6755: portd is the fixed-VI arm of the lvl4 pair
RACE = {"s6771/r17", "s6771/m17", "s6770/m17", "s6778/r17p"}  # s6771: the race never ticks 0x800FA730

def load_ai_clock(tick):
    os.environ["G3_TICK"] = tick
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "g3_ai_clock.py")).read()
    ns = {"__name__": "g3_ai_clock_lib"}
    exec(src.replace("\nmain()", ""), ns)
    return ns

def windows(ac, path, retail):
    tick, ticks, bufs, song = -1, [], [], []
    for vi, pc, l in ac["rows"](path, retail):
        if pc == ac["TICK"]:
            tick += 1
            ticks.append(vi)
            i = l.find(" m=8010c0e0:")
            if i >= 0:
                song.append((tick, l[i + 12:].split()[0].split("[")[0]))
        elif pc in ac["AI"]:
            bufs.append((tick, vi))
    ch = [(t, v) for (t, v), (t0, v0) in zip(song[1:], song) if v != v0]
    out = []
    for (s, v), (e, _) in zip(ch, ch[1:]):
        if v in ("00000000", "ffffffff") or e >= len(ticks):
            continue
        out.append((v[-2:], s, e, ticks[e] - ticks[s], sum(1 for t, _ in bufs if s <= t < e)))
    return out, len(ticks), len(bufs)

def plain(path, tmp):
    if not path.endswith(".zst"):
        return path
    dst = os.path.join(tmp, "oracle.log")
    with open(dst, "wb") as f:
        subprocess.run(["zstd", "-dcq", path], stdout=f, check=True)
    return dst

def pairs(globs):
    for g in globs:
        for rd in sorted(glob.glob(os.path.join(g, "**", "retail*"), recursive=True)):
            log = next((p for p in (os.path.join(rd, "oracle.log"), os.path.join(rd, "oracle.log.zst")) if os.path.exists(p)), None)
            if not log:
                continue
            base, name = os.path.split(rd)
            suf = name[len("retail"):]
            port = os.path.join(base, f"port{suf}.rand.txt")
            if not os.path.exists(port):
                port = os.path.join(base, "port.rand.txt")
            if os.path.exists(port):
                yield base, name, log, port
    for d, r, p in EXTRA:
        base = os.path.join("scratch", d)
        log = os.path.join(base, r, "oracle.log.zst")
        if os.path.exists(log) and os.path.exists(os.path.join(base, f"{p}.rand.txt")):
            yield base, f"{r}+{p}", log, os.path.join(base, f"{p}.rand.txt")

def main():
    globs = sys.argv[1:] or ["scratch/s67*/", "scratch/s68*/"]
    print(f"{'pair':32} {'song':>4} {'r.ticks':>7} {'p.ticks':>7} {'r.VI':>5} {'p.VI':>5} {'VI p/r':>7}"
          f" {'r.buf':>5} {'p.buf':>5} {'buf p/r':>7} {'r.VI/t':>6} {'p.VI/t':>6} {'r.b/VI':>6} {'p.b/VI':>6}")
    for base, name, log, port in pairs(globs):
        key = os.path.relpath(base, "scratch")
        ac = load_ai_clock("800C6674" if key in RACE else "800FA730")
        with tempfile.TemporaryDirectory() as tmp:
            if subprocess.run(["sh", "-c", f"zstd -dcfq '{log}' 2>/dev/null | grep -q -m1 'm=8010c0e0'"]).returncode:
                continue
            rw, rt, rb = windows(ac, plain(log, tmp), True)
        pw, pt, pb = windows(ac, port, False)
        tag = f"L{LEVEL.get(key, '?')} {key}/{name}"
        if not rw and not pw:
            print(f"{tag:32} none (retail {rt} ticks/{rb} bufs, port {pt} ticks/{pb} bufs)")
        for i in range(max(len(rw), len(pw))):
            r = rw[i] if i < len(rw) else None
            p = pw[i] if i < len(pw) else None
            sid = (r or p)[0] if (r and p is None) or (p and r is None) or r[0] == p[0] else f"{r[0]}/{p[0]}"
            f = lambda w, j: f"{w[j]}" if w else "-"
            rat = lambda j: f"{p[j] / r[j]:.4f}" if r and p and r[j] else "-"
            vt = lambda w: f"{w[3] / (w[2] - w[1]):.3f}" if w else "-"
            bv = lambda w: f"{w[4] / w[3]:.3f}" if w and w[3] and w[4] else "-"
            print(f"{tag:32} {sid:>4} {f(r, 2) if r is None else r[2] - r[1]:>7} {'-' if p is None else p[2] - p[1]:>7}"
                  f" {f(r, 3):>5} {f(p, 3):>5} {rat(3):>7} {f(r, 4):>5} {f(p, 4):>5} {rat(4):>7} {vt(r):>6} {vt(p):>6} {bv(r):>6} {bv(p):>6}")

main()
