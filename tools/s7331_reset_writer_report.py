#!/usr/bin/env python3
"""s7331 item 23 report: classify blocks the retail scene reset dropped that changed within 2 s (build/rs64_s7331.log).

usage: s7331_reset_writer_report.py <rs64_s7331.log> [more logs...] [--s7330 <rs64_s7330.log>]
Per log: header, positive control (boot mixer buffers 0x80169F10 / 0x8016BD50 / 0x80171EB0 must be listed changed), changed blocks
grouped by (kind, owner symbol, writer set), and the H-reuse table: blocks whose change continued AFTER a reallocation by a writer
other than the CPU (RSP/PI writing a block another owner now holds), or any RSP read after reallocation.
With --s7330 (same run, ROGUESQ_S7324_RCPREF): every freed-class audio DMA (HIT line) into a tracked block is ordered against
that block's reallocation time on the same steady clock (needs the t0=/tr= stamps, s7331 build 3): a HIT after tr is an RSP access
to memory another owner already holds (stale-owner read/write), with the new owner's first CPU change time beside it.
Changes are also split by the guest heap walk at first change (g=kind:flags: 2:1 = inside a guest FREE block, 2:6 / 2:2 = inside
a guest ALLOCATED block the host map does not model, e.g. the framebuffer / temp-pool carve).
Exit 1 when the control fails, a pre-reuse change lands in a guest FREE block outside the control set (new dangling writer), or
a stale-owner DMA follows a reallocation.
s7332 builds add per-block RSP-write attribution (wgfx/waud = gfx/audio task writes pre/post realloc, woff/wmem = block-offset and
DMEM ranges, wlast, wtask = writing task type ucode dram_stack output_buff output_buff_size data_ptr data_size yield ...).
Callers must take this script's exit status itself (zsh ${pipestatus[1]}), not a downstream grep's: s7331_abort_resetw read
grep's rc and logged report_rc=0 over 3 NEW free-memory rows.
"""
import re
import sys
from collections import defaultdict

CTL = {0x80169F10, 0x8016BD50, 0x80171EB0}


def parse(path):
    hdr, rows, quiet = None, [], []
    for ln in open(path, errors="replace"):
        ln = ln.rstrip("\n")
        if ln.startswith("s7331 "):
            hdr = ln
        elif ln.startswith("B "):
            d = dict(re.findall(r"(\w+)=(\S+)", ln))
            if "req" not in d or "own" not in d:  # torn row (pre-s7332 dumps were rewritten in place; a SIGKILL could cut one)
                continue
            d["ptr"] = int(d["ptr"], 16)
            d["w"] = {m[0]: m[1] for m in re.findall(r"((?:pre|post)_(?:cpu|rsp|pi))=(\S+ off=\S+(?: g=\S+ h=\S+)?)", ln)}
            rows.append(d)
        elif ln.startswith("Q "):
            quiet.append(dict(re.findall(r"(\w+)=(\S+)", ln)))
    return hdr, rows, quiet


def stale(rows, path):
    hits = []
    for ln in open(path, errors="replace"):
        if ln.startswith("HIT ") and "bulk=" in ln:
            d = dict(re.findall(r"(\w+)=(\S+)", ln))
            hits.append((float(d["t"]), d["dir"], int(d["x"], 16), d["len"], d["seq"], int(d["fptr"], 16), float(d["ft"])))
    n = 0
    for r in rows:
        if "tr" not in r:
            continue
        tr, t0, p, req = float(r["tr"]), float(r["t0"]), r["ptr"], int(r["req"], 16)
        mine = [h for h in hits if h[5] == p and abs(h[6] - t0) < 0.05]  # same free event: freed record = this block, free time ~ t0
        if not mine:
            continue
        last = max(h[0] for h in mine)
        after = [h for h in mine if h[0] > tr]
        pc = r["w"].get("post_cpu")
        pcf = float(re.search(r"@\+([\d.]+)ms", pc).group(1)) / 1e3 + t0 if pc else None
        print(f"  {p:08X}+{req:X} realloc by {r.get('by')} at tr; last stale DMA tr{(last - tr) * 1e3:+.3f} ms; "
              f"{len(after)}/{len(mine)} DMAs after tr" + (f"; new owner's first change tr{(pcf - tr) * 1e3:+.3f} ms" if pcf else ""))
        for h in after[:6]:
            print(f"     {h[1]} x={h[2]:08X} len={h[3]} seq={h[4]} at tr{(h[0] - tr) * 1e3:+.3f} ms")
        n += len(after)
    return n


def main():
    bad = 0
    s30 = None
    args = sys.argv[1:]
    if "--s7330" in args:
        i = args.index("--s7330"); s30 = args[i + 1]; del args[i:i + 2]
    for path in args:
        hdr, rows, quiet = parse(path)
        print(f"== {path}\n{hdr}")
        seen = {r["ptr"] for r in rows if r["w"]}
        ok = CTL <= seen
        print(f"ctl boot mixer buffers changed: {sorted(hex(x) for x in CTL & seen)} -> {'PASS' if ok else 'FAIL'}")
        bad |= not ok
        grp = defaultdict(list)
        for r in rows:
            own = re.sub(r"\+0x[0-9a-f]+$", "", r.get("own", "?"))
            ws = ",".join(sorted(k.split("=")[0] for k in r["w"]))
            grp[(r["kind"], own, ws or "rd-only")].append(r)
        print("changed / RSP-touched blocks by (kind, allocator, writers):")
        for (k, own, ws), rs in sorted(grp.items(), key=lambda kv: -len(kv[1])):
            syncs = sorted({int(r["sync"]) for r in rs})
            ex = rs[0]
            print(f"  {k} {own:40s} {ws:30s} n={len(rs):4d} syncs={syncs[:8]}{'...' if len(syncs) > 8 else ''} e.g. {ex['ptr']:08X}+{ex['req']} "
                  + " ".join(f"{a}={b}" for a, b in ex["w"].items()) + f" rsp_rd={ex.get('rsp_rd')} rsp_wr={ex.get('rsp_wr')}"
                  + (f" realloc={ex['realloc']} by={ex.get('by')}" if "realloc" in ex else ""))
        reuse = []
        for r in rows:
            post = [k for k in r["w"] if k.startswith(("post_rsp", "post_pi"))]
            rd_post = int(r.get("rsp_rd", "0/0").split("/")[1]) + int(r.get("rsp_wr", "0/0").split("/")[1])
            if post or rd_post:
                reuse.append((r, post, rd_post))
        print(f"post-realloc RSP/PI touches (new-owner traffic unless the stale-owner check below flags them): {len(reuse)}")
        for r, post, rd in reuse[:12]:
            print(f"  sync={r['sync']} {r['kind']} {r['ptr']:08X}+{r['req']} own={r.get('own')} realloc={r.get('realloc')} by={r.get('by')} "
                  f"{' '.join(post)} rsp_rd={r.get('rsp_rd')} rsp_wr={r.get('rsp_wr')}")
        gsplit = defaultdict(int)
        for r in rows:
            for k, v in r["w"].items():
                if k.startswith("pre_"):
                    m = re.search(r"g=(-?\d+):(\w+):", v)
                    gsplit[(k, m.group(0)[2:-1] if m else "?")] += 1
        print("pre-reuse changes by guest walk class:", dict(gsplit))
        newfree = [r for r in rows if r["ptr"] not in CTL and any(k.startswith("pre_") and " g=2:1:" in v for k, v in r["w"].items())]
        own_ctl = {re.sub(r"\+0x\w+$", "", r.get("own", "")) for r in rows if r["ptr"] in CTL}
        newfree_x = [r for r in newfree if re.sub(r"\+0x\w+$", "", r.get("own", "")) not in own_ctl]
        print(f"pre-reuse changes inside guest FREE memory: {len(newfree)} blocks ({len(newfree) - len(newfree_x)} same allocator as the control); "
              f"other owners: {len(newfree_x)}")
        for r in newfree_x[:10]:
            print(f"  NEW sync={r['sync']} {r['ptr']:08X}+{r['req']} own={r.get('own')} " + " ".join(f"{k}={v}" for k, v in r["w"].items()))
            if "wtask" in r:  # s7332 RSP-write attribution: gfx/aud split [pre/post], block offsets, DMEM source, writing task's OSTask fields
                print("      " + " ".join(f"{k}={r[k]}" for k in ("wgfx", "waud", "woff", "wmem", "wlast", "wtask")))
        bad |= bool(newfree_x)
        if s30:
            ns = stale(rows, s30)
            print(f"stale-owner audio DMAs after reallocation: {ns}")
            bad |= ns > 0
        nq = sum(int(q["unchanged"]) for q in quiet)
        print(f"unchanged (negative class): {nq} blocks over {len(quiet)} (sync,kind) groups")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
