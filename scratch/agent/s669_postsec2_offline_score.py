#!/usr/bin/env python3
"""s669 offline post-sec2 scorer for s668 recovery-full HOLDs.

Discriminating measurements for item -420 / HYPOTHESIS-ID m3-post-exit-fs-stall:
  H-sec2-mission-live, H-thr12-churn-normal, H-packtlut-next, H-postsec2-fs-plateau
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def analyze(logpath: Path, tag: str) -> dict:
    sec_events = []
    thr_events = []
    level_tex = []
    ok136c = []
    pack = 0
    crash = 0
    t_ms = []
    sec2_ln = thr13c = thr13d = sec3_ln = None
    sync0 = sync_pos = e9 = f7 = 0
    rdp_first = rdp_last = None
    synth_first = synth_last = None
    present_n = 0
    tris = []

    with logpath.open("r", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if "start-match: section" in line:
                sec_events.append((i, line.strip()))
                if sec2_ln is None and "section 2" in line:
                    sec2_ln = i
                elif sec2_ln and sec3_ln is None and "section 3" in line and i > sec2_ln:
                    sec3_ln = i
            if "[thr-create]" in line or (
                "[thr-destroy]" in line and "self" not in line and "signal" not in line
            ):
                thr_events.append((i, line.strip()))
                if (
                    sec2_ln
                    and thr13c is None
                    and "[thr-create]" in line
                    and "0x800495FC" in line
                    and i >= sec2_ln
                ):
                    thr13c = i
                if (
                    thr13c
                    and thr13d is None
                    and "[thr-destroy]" in line
                    and "id=13" in line
                ):
                    thr13d = i
            if "[level-tex" in line:
                level_tex.append((i, line.strip()))
            if "event=ok136c" in line and "summary" not in line:
                ok136c.append((i, line.strip()))
            if "packTlut" in line or "parseHmt" in line or "loadTextureToMemory" in line:
                pack += 1
            if "[CRASH]" in line or "[ABORT]" in line:
                crash += 1
            if "t_ms=" in line and ("heartbeat" in line or "to_zero" in line):
                m = re.search(r"t_ms=(\d+)", line)
                if m:
                    t_ms.append((i, int(m.group(1))))

            in_thr13 = thr13c and (thr13d is None or i <= thr13d) and i >= thr13c
            if in_thr13:
                if "[runner] task" in line:
                    if "syncs=0" in line:
                        sync0 += 1
                    elif "syncs=" in line:
                        sync_pos += 1
                if "fs_b0=E9" in line:
                    e9 += 1
                if "fs_b0=F7" in line:
                    f7 += 1
                if "vi-fs-decision" in line and "rdpFs=" in line:
                    m = re.search(r"synth=(\d+) rdpFs=(\d+)", line)
                    if m:
                        s, r = int(m.group(1)), int(m.group(2))
                        if rdp_first is None:
                            rdp_first, synth_first = r, s
                        rdp_last, synth_last = r, s
                if "threadPresent" in line:
                    present_n += 1
                if "dl-sync-probe" in line and "tris=" in line:
                    m = re.search(r"tris=(\d+)", line)
                    if m:
                        tris.append(int(m.group(1)))

    def t_near(ln):
        before = [t for l, t in t_ms if l <= ln]
        return before[-1] if before else None

    out = {
        "tag": tag,
        "sec2_ln": sec2_ln,
        "sec3_ln": sec3_ln,
        "thr13c": thr13c,
        "thr13d": thr13d,
        "t_sec2": t_near(sec2_ln) if sec2_ln else None,
        "t_thr13d": t_near(thr13d) if thr13d else None,
        "pack": pack,
        "crash": crash,
        "sync0": sync0,
        "sync_pos": sync_pos,
        "e9": e9,
        "f7": f7,
        "rdp_first": rdp_first,
        "rdp_last": rdp_last,
        "synth_first": synth_first,
        "synth_last": synth_last,
        "present_n": present_n,
        "tris_n": len(tris),
        "tris_mode": max(set(tris), key=tris.count) if tris else None,
        "ok136c_post": sum(1 for l, _ in ok136c if sec2_ln and l >= sec2_ln),
        "level_tex_post": [t for l, t in level_tex if sec2_ln and l >= sec2_ln - 20],
        "sections": [e for e in sec_events if sec2_ln and e[0] >= sec2_ln],
    }
    return out


def main(argv: list[str]) -> int:
    defaults = [
        (
            "att2",
            "scratch/s73_post_a_scene/s668_thr11d_2_20260811011317/run.log",
        ),
        (
            "att3",
            "scratch/s73_post_a_scene/s668_thr11d_3_20260811012532/run.log",
        ),
    ]
    pairs = []
    if len(argv) >= 3 and len(argv) % 2 == 1:
        it = iter(argv[1:])
        pairs = list(zip(it, it))
    else:
        pairs = defaults

    for tag, path in pairs:
        p = Path(path)
        if not p.exists():
            print(f"MISSING {tag} {path}")
            continue
        r = analyze(p, tag)
        print(f"======== {tag} ========")
        print(
            f"sec2@L{r['sec2_ln']} t_ms={r['t_sec2']} thr13c@L{r['thr13c']} "
            f"thr13d@L{r['thr13d']} t_ms={r['t_thr13d']} sec3@L{r['sec3_ln']}"
        )
        if r["t_sec2"] is not None and r["t_thr13d"] is not None:
            print(f"thr12 post-sec2 lifetime_ms≈{r['t_thr13d'] - r['t_sec2']}")
        print(f"sections: {[s[1] for s in r['sections']]}")
        print(f"ok136c_post={r['ok136c_post']} pack/hmt/tex={r['pack']} crash={r['crash']}")
        print(
            f"thr13 GFX: syncs=0:{r['sync0']} syncs>0:{r['sync_pos']} "
            f"fs_b0=E9:{r['e9']} fs_b0=F7:{r['f7']} present_n={r['present_n']} "
            f"tris_n={r['tris_n']} tris_mode={r['tris_mode']}"
        )
        print(
            f"rdpFs {r['rdp_first']}->{r['rdp_last']} "
            f"synth {r['synth_first']}->{r['synth_last']}"
        )
        if r["rdp_first"] is not None and r["rdp_last"] is not None:
            print(
                f"  rdpFs_delta={r['rdp_last'] - r['rdp_first']} "
                f"synth_delta={r['synth_last'] - r['synth_first']}"
            )
        for t in r["level_tex_post"][:3]:
            print(f"  level-tex: {t}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
