#!/usr/bin/env python3
"""Per-arm discriminator for s1776 main-text handler revisit."""
from __future__ import annotations

import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARMS = ["hold", "a", "start"]
EXPECT_PAD = {
    "a": 0x80000000,
    "start": 0x10000000,
}
PC_LABELS = [
    ("0x800aad9c", "hangarFrm"),
    ("0x80000b20", "loadOvl"),
    ("0x80000ba8", "menuDest"),
    ("0x800c131c", "c8_ship"),
    ("0x8003dfa0", "mainLoop"),
    ("0x8000c07c", "submitGfx"),
    ("0x80001354", "vidTick"),
    ("0x8006b000", "lvlScreen"),
    ("0x8001b7f0", "pendVi"),
    ("0x8001ba9c", "swapVi"),
    ("0x80008d20", "rdpInit"),
]
NEW_PCS = [
    "0x8003dfa0",
    "0x8000c07c",
    "0x80001354",
    "0x8006b000",
    "0x8001b7f0",
    "0x8001ba9c",
    "0x80008d20",
]
PRESENTERS = [
    "0x8000c07c",
    "0x80001354",
    "0x8001ba9c",
    "0x8001b7f0",
]
OUTER = [
    "0x8003dfa0",
    "0x8006b000",
]
REQUIRED_ARMED = [addr for addr, _ in PC_LABELS]
WIDTH_RE = re.compile(
    r"^\[vi\] t=\s*([0-9.]+)s .*WIDTH\s+(\d+)\s+->\s+(\d+)\s+origin=(0x[0-9a-fA-F]+)"
)
PAD_RE = re.compile(r"^\[pad\] t=\s*([0-9.]+)s .*7C4=(0x[0-9a-fA-F]+)")
WATCH_PC_RE = re.compile(
    r"^\[oracle\] watch pc \[(0x[0-9a-fA-F]+),.*?:\s+(\d+) hit"
)
WATCH_ARM_RE = re.compile(
    r"^\[watch\] pc \[(0x[0-9a-fA-F]+),0x[0-9a-fA-F]+\) flags="
)
RDRAM_RE = re.compile(
    r"\[oracle\] watch write \[0x00000000,0x00800000\):\s+(\d+) hit"
)


def classify_origin(origin: str, width: int) -> str:
    o = int(origin, 16)
    if width == 512 and (0x006AB000 <= o <= 0x006AC000):
        return "hangar"
    if width == 512 and (0x00690000 <= o <= 0x00691000):
        return "attract"
    if width == 512 and (0x00620000 <= o <= 0x00621000):
        return "attract-int"
    if width == 640 and (0x00696000 <= o <= 0x00697000):
        return "B-frontend"
    if width == 640 and (0x006A2000 <= o <= 0x006A3000):
        return "viewer"
    if width == 1024 and (0x00790000 <= o <= 0x00791000):
        return "title-like"
    return ""


def parse_arm(name: str) -> dict:
    d = OUT / name
    log = (d / "run.log").read_text(errors="replace") if (d / "run.log").exists() else ""
    rc = (d / "run.rc").read_text().strip() if (d / "run.rc").exists() else "?"
    widths = []
    pads_b = []
    pads_late = []
    pads_expect = []
    expect = EXPECT_PAD.get(name)
    for line in log.splitlines():
        m = WIDTH_RE.match(line)
        if m:
            t, a, b, origin = float(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
            widths.append((t, a, b, origin, classify_origin(origin, b)))
            continue
        m = PAD_RE.match(line)
        if m:
            t, word = float(m.group(1)), int(m.group(2), 16)
            if word == 0x40000000:
                pads_b.append((t, word))
            if t >= 118.0 and word != 0:
                pads_late.append((t, word))
            if expect is not None and word == expect and t >= 118.0:
                pads_expect.append((t, word))
    pcs = {}
    armed = set()
    for line in log.splitlines():
        m = WATCH_PC_RE.match(line)
        if m:
            pcs[m.group(1).lower()] = int(m.group(2))
        m = WATCH_ARM_RE.match(line)
        if m:
            armed.add(m.group(1).lower())
    rdram = 0
    m = RDRAM_RE.search(log)
    if m:
        rdram = int(m.group(1))
    done = ""
    for line in log.splitlines():
        if line.startswith("[oracle] done:"):
            done = line.strip()
    pos = "positive-control threshold reached" in log
    arrived_640 = any(
        t < 119.0 and a == 1024 and b == 640 and tag == "B-frontend"
        for t, a, b, _, tag in widths
    )
    hangar = any(a == 1024 and b == 512 and tag == "hangar" and t < 80.0 for t, a, b, _, tag in widths)
    broute = any(a == 512 and b == 1024 and 50.0 <= t <= 80.0 for t, a, b, _, _ in widths)
    attract = any(
        116.0 <= t <= 119.0 and a == 640 and b == 512 and tag == "attract"
        for t, a, b, _, tag in widths
    )
    post = [w for w in widths if w[0] >= 119.0]
    post126 = [w for w in widths if w[0] >= 126.0]
    left_1024 = any(w[1] == 512 and w[2] == 1024 and w[4] == "title-like" for w in post126)
    return {
        "name": name,
        "rc": rc,
        "rdram": rdram,
        "pos": pos,
        "done": done,
        "widths": widths,
        "post": post,
        "post126": post126,
        "left_1024": left_1024,
        "pads_b": pads_b,
        "pads_late": pads_late,
        "pads_expect": pads_expect,
        "pcs": pcs,
        "armed": armed,
        "arrived_640": arrived_640,
        "hangar": hangar,
        "broute": broute,
        "attract": attract,
        "b_count": len(pads_b),
    }


def width_brief(widths) -> str:
    parts = []
    for t, a, b, origin, tag in widths:
        extra = f" {tag}" if tag else ""
        parts.append(f"{t:.1f} {a}->{b} {origin}{extra}")
    return "; ".join(parts) if parts else "(no WIDTH)"


def last_phase(widths) -> str:
    if not widths:
        return "none"
    t, a, b, origin, tag = widths[-1]
    extra = f" {tag}" if tag else ""
    return f"{t:.1f} {a}->{b} {origin}{extra}"


def controls_ok(arm: dict) -> bool:
    rdram_ok = arm["rdram"] >= 10000 or arm["pos"]
    if not rdram_ok:
        return False
    if arm["b_count"] < 1:
        return False
    if not arm["hangar"] or not arm["broute"] or not arm["arrived_640"] or not arm["attract"]:
        return False
    if not arm["pcs"]:
        return False
    if not all(pc in arm["armed"] for pc in REQUIRED_ARMED):
        return False
    if arm["pcs"].get("0x800c131c", 0) <= 0:
        return False
    if arm["pcs"].get("0x800aad9c", 0) < 40:
        return False
    if arm["name"] != "hold" and not arm["pads_expect"]:
        return False
    if arm["name"] != "hold" and not arm["left_1024"]:
        return False
    return True


def classify(arm: dict, hold: dict) -> str:
    if not controls_ok(arm):
        return "INVALID"
    if arm["name"] == "hold":
        leave = any(w[1] == 512 and w[2] != 512 for w in arm["post"])
        return "H3-hold" if not leave else "hold-left"
    d_submit = arm["pcs"].get("0x8000c07c", 0) - hold["pcs"].get("0x8000c07c", 0)
    d_vid = arm["pcs"].get("0x80001354", 0) - hold["pcs"].get("0x80001354", 0)
    d_swap = arm["pcs"].get("0x8001ba9c", 0) - hold["pcs"].get("0x8001ba9c", 0)
    d_pend = arm["pcs"].get("0x8001b7f0", 0) - hold["pcs"].get("0x8001b7f0", 0)
    extra_outer = [
        pc for pc in OUTER if arm["pcs"].get(pc, 0) > hold["pcs"].get(pc, 0)
    ]
    extra_rdp = arm["pcs"].get("0x80008d20", 0) > hold["pcs"].get("0x80008d20", 0)
    all_new_flat_or_down = all(
        arm["pcs"].get(pc, 0) <= hold["pcs"].get(pc, 0) for pc in NEW_PCS
    )
    ship_drop = arm["pcs"].get("0x800c131c", 0) < hold["pcs"].get("0x800c131c", 0)
    rdp_drop = arm["pcs"].get("0x80008d20", 0) < hold["pcs"].get("0x80008d20", 0)
    tags = []
    if d_submit > 10:
        tags.append("H1-submitGfx")
    if d_vid == 1 and d_swap == 1:
        tags.append("H1-modechange")
    elif d_vid > 0 or d_swap > 0:
        tags.append("H1-vid/swap")
    if extra_outer:
        tags.append("H2:" + ",".join(extra_outer))
    if extra_rdp and d_submit <= 10 and not extra_outer:
        tags.append("H4")
    elif extra_rdp:
        tags.append("H4-also")
    if all_new_flat_or_down:
        tags.append("H3-stop-tick" if ship_drop else "H3")
    elif ship_drop and rdp_drop and extra_outer == []:
        tags.append("H3-stop-tick-rdp")
    if 0 < d_pend <= 5:
        tags.append("pendVi-vi-coupled")
    if not tags:
        tags.append("UNSPLIT")
    return "+".join(tags)


def main() -> None:
    parsed = {name: parse_arm(name) for name in ARMS}
    hold = parsed["hold"]
    lines = []
    lines.append("s1776 three-arm Rice: main-text handlers on title-like 1024")
    lines.append("HYPOTHESIS-ID: external-retail-entry-boundary")
    lines.append("secs=133  B_ROUTE=eleven-start+55/58/63:b  candidates at 119/123 only")
    lines.append(
        "controls: whole-RDRAM 10k, B pad 0x40000000, hangar then B 640, "
        "640->512 attract before 119s, hangarFrm>=40, ship-select PC nonzero, 11 PCs armed"
    )
    lines.append(
        "H1 extra submitGfx/vidTick/swapVi/pendVi; H2 extra mainLoop/lvlScreen; "
        "H3 all new main-text PCs flat or down; H4 extra rdpInit without H1/H2"
    )
    lines.append("")
    lines.append("WIDTH (debugger [vi] only)")
    for name in ARMS:
        a = parsed[name]
        armed_n = sum(1 for pc in REQUIRED_ARMED if pc in a["armed"])
        lines.append(
            f"{name:7} rc={a['rc']} rdram={a['rdram']} pos={int(a['pos'])} "
            f"Bpads={a['b_count']} hangar={int(a['hangar'])} broute={int(a['broute'])} "
            f"arrived640={int(a['arrived_640'])} attract={int(a['attract'])} "
            f"late_expect={len(a['pads_expect'])} armed={armed_n}/{len(REQUIRED_ARMED)} "
            f"ship={a['pcs'].get('0x800c131c', -1)} hangarFrm={a['pcs'].get('0x800aad9c', -1)} "
            f"left1024={int(a['left_1024'])} ok={int(controls_ok(a))}"
        )
        lines.append(f"  all:  {width_brief(a['widths'])}")
        lines.append(f"  post119: {width_brief(a['post'])}")
        lines.append(f"  post126: {width_brief(a['post126'])}")
        lines.append(f"  last: {last_phase(a['widths'])}")
        late = ", ".join(f"{t:.1f}=0x{w:08x}" for t, w in a["pads_late"]) or "none"
        lines.append(f"  pads t>=118: {late}")
        lines.append(f"  {a['done'] or '(no done)'}")
    lines.append("")
    hdr = "arm     " + "  ".join(f"{lab:>10}" for _, lab in PC_LABELS)
    lines.append("PC watches (lifetime)")
    lines.append(hdr)
    for name in ARMS:
        a = parsed[name]
        cols = []
        for addr, _ in PC_LABELS:
            cols.append(f"{a['pcs'].get(addr, -1):>10}")
        lines.append(f"{name:7} " + "  ".join(cols))
    lines.append("")
    lines.append("Delta vs hold (leave-hold; prefix-identical through 119s)")
    lines.append(
        f"{'arm':7} "
        + "  ".join(f"{lab:>10}" for _, lab in PC_LABELS)
    )
    for name in ARMS:
        a = parsed[name]
        cols = []
        for addr, _ in PC_LABELS:
            cols.append(f"{a['pcs'].get(addr, 0) - hold['pcs'].get(addr, 0):>10}")
        lines.append(f"{name:7} " + "  ".join(cols))
    lines.append("")
    lines.append("Classification")
    for name in ARMS:
        a = parsed[name]
        verdict = classify(a, hold)
        lines.append(f"  {name:7} {verdict}")
    text = "\n".join(lines) + "\n"
    (OUT / "summary.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
