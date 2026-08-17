#!/usr/bin/env python3
"""Per-arm discriminator for s1792 submitGfxFrame-caller revisit."""
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
    ("0x8006d900", "idleSave"),
    ("0x800af3c0", "craftSel"),
    ("0x800b47d0", "menuIn"),
    ("0x800bf830", "rndBack"),
    ("0x800c30c8", "sub02"),
    ("0x800c5ef8", "results"),
    ("0x800c9bf0", "modelVw"),
    ("0x800aad9c", "hangarFrm"),
    ("0x80000b20", "loadOvl"),
    ("0x800c131c", "c8_ship"),
    ("0x8000c07c", "submitGfx"),
]
UNWATCHED = [
    "0x8006d900",
    "0x800af3c0",
    "0x800b47d0",
    "0x800bf830",
    "0x800c30c8",
    "0x800c5ef8",
    "0x800c9bf0",
]
OVERLAY_CALLERS = [
    "0x800af3c0",
    "0x800b47d0",
    "0x800bf830",
    "0x800c30c8",
    "0x800c5ef8",
    "0x800c9bf0",
]
IDLE_PC = "0x8006d900"
SUBMIT_PC = "0x8000c07c"
HANGAR_PC = "0x800aad9c"
SHIP_PC = "0x800c131c"
REQUIRED_ARMED = [addr for addr, _ in PC_LABELS]
PC_NAME = {addr: lab for addr, lab in PC_LABELS}
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
    if arm["pcs"].get(SHIP_PC, 0) <= 0:
        return False
    if arm["pcs"].get(HANGAR_PC, 0) < 40:
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
    d_submit = arm["pcs"].get(SUBMIT_PC, 0) - hold["pcs"].get(SUBMIT_PC, 0)
    d_idle = arm["pcs"].get(IDLE_PC, 0) - hold["pcs"].get(IDLE_PC, 0)
    d_hangar = arm["pcs"].get(HANGAR_PC, 0) - hold["pcs"].get(HANGAR_PC, 0)
    ship_drop = arm["pcs"].get(SHIP_PC, 0) < hold["pcs"].get(SHIP_PC, 0)
    overlay_risers = []
    overlay_rise_sum = 0
    for pc in OVERLAY_CALLERS:
        d = arm["pcs"].get(pc, 0) - hold["pcs"].get(pc, 0)
        if d > 10:
            overlay_risers.append((pc, d))
            overlay_rise_sum += d
    unwatched_flat_or_down = all(
        arm["pcs"].get(pc, 0) <= hold["pcs"].get(pc, 0) for pc in UNWATCHED
    )
    hangar_flat = abs(d_hangar) <= 2
    tags = []
    if d_submit > 10:
        tags.append("submitGfx+{0}".format(d_submit))
        near105 = 80 <= d_submit <= 130
        if len(overlay_risers) == 1 and d_idle <= 10 and hangar_flat:
            name = PC_NAME[overlay_risers[0][0]]
            tags.append("H1-{0}+{1}".format(name, overlay_risers[0][1]))
        elif d_idle > 10 and not overlay_risers:
            tags.append("H2-idleSave+{0}".format(d_idle))
        elif unwatched_flat_or_down:
            tags.append("H3-no-unwatched-rise")
        else:
            risers = list(overlay_risers)
            if d_idle > 10:
                risers.append((IDLE_PC, d_idle))
            if len(risers) >= 2:
                rise_sum = sum(d for _, d in risers)
                names = ",".join("{0}+{1}".format(PC_NAME[pc], d) for pc, d in risers)
                if near105 and abs(rise_sum - d_submit) <= 15:
                    tags.append("H4-{0}=sum{1}".format(names, rise_sum))
                else:
                    tags.append("H4-split-{0}=sum{1}".format(names, rise_sum))
            elif overlay_risers and not hangar_flat:
                tags.append("UNSPLIT-hangar-moved")
            else:
                tags.append("UNSPLIT")
    else:
        tags.append("NO-SUBMIT-DELTA")
        if unwatched_flat_or_down:
            tags.append("unwatched-flat")
    if ship_drop:
        tags.append("ship-drop")
    if not hangar_flat:
        tags.append("hangar{0:+d}".format(d_hangar))
    if not tags:
        tags.append("UNSPLIT")
    return "+".join(tags)


def main() -> None:
    parsed = {name: parse_arm(name) for name in ARMS}
    hold = parsed["hold"]
    lines = []
    lines.append("s1792 three-arm Rice: unwatched submitGfxFrame callers on title-like 1024")
    lines.append("HYPOTHESIS-ID: external-retail-entry-boundary")
    lines.append("secs=133  B_ROUTE=eleven-start+55/58/63:b  candidates at 119/123 only")
    lines.append(
        "controls: whole-RDRAM 10k, B pad 0x40000000, hangar then B 640, "
        "640->512 attract before 119s, hangarFrm>=40, ship-select PC nonzero, 11 PCs armed"
    )
    lines.append(
        "H1 one overlay caller +~105 matching submitGfx; H2 idleSave +~105; "
        "H3 all seven unwatched flat/down with submitGfx still +105; "
        "H4 two+ unwatched rise and deltas sum ~+105"
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
            f"ship={a['pcs'].get(SHIP_PC, -1)} hangarFrm={a['pcs'].get(HANGAR_PC, -1)} "
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
