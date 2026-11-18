"""s7558: wrap-tolerant anchors for the standalone fixup_*.py steps.

The vendored chain (fixup_game_funcs_vendored.py) replays apply_s7484_loadwatch / s7487 / s7488 BEFORE the standalone
fixup_*.py steps it check_calls, so a guest load line the fixups anchor on reads
    { RS64_S7484_LD(0x800B29D4u, ctx->r1, 0X5734, 4); ctx->f0.u32l = MEM_W(ctx->r1, 0X5734); }
in a regen but was bare when the fixup was written (the live tree got the wrappers later). Bare-only anchors made every
regen abort (s7558: fixup_menu_worker s6781, fixup_fps60_scrape s6819). site_re(site) matches the site with any of its
code lines optionally wrapped by one RS64_S74xx_* hook; sub_once(s, site, new_suffix) appends text after the one match.
"""
import re

WRAP_OPEN = r"(?:\{ RS64_S74\d\d_[A-Z]+\([^;{}]*\); )?"
WRAP_CLOSE = r"(?: \})?"


def site_re(site):
    parts = []
    for line in site.splitlines(True):
        body = line.rstrip("\n")
        nl = "\n" if line.endswith("\n") else ""
        if body.startswith("    ") and not body.lstrip().startswith("//"):
            parts.append("    " + WRAP_OPEN + re.escape(body[4:]) + WRAP_CLOSE + re.escape(nl))
        else:
            parts.append(re.escape(line))
    return re.compile("".join(parts))


def count(s, site):
    return len(site_re(site).findall(s))


def span(s, site, start=0, end=None):
    """(start, end) of the first (possibly wrapped) match of site in s[start:end], or None."""
    m = site_re(site).search(s, start, len(s) if end is None else end)
    return m.span() if m else None


def sub_once(s, site, suffix):
    """Insert suffix after the single (possibly wrapped) match of site. Caller checks count()==1 first."""
    return site_re(site).sub(lambda m: m.group(0) + suffix, s, count=1)


if __name__ == "__main__":
    site = "    // 0x800B29D4: lwc1        $f0, 0x5734($at)\n    ctx->f0.u32l = MEM_W(ctx->r1, 0X5734);\n"
    bare = "x\n" + site + "y\n"
    wrap = "x\n    // 0x800B29D4: lwc1        $f0, 0x5734($at)\n    { RS64_S7484_LD(0x800B29D4u, ctx->r1, 0X5734, 4); ctx->f0.u32l = MEM_W(ctx->r1, 0X5734); }\n" + "y\n"
    other = site.replace("0X5734);", "0X5738);")
    assert count(bare, site) == 1 and count(wrap, site) == 1 and count(other, site) == 0
    assert sub_once(wrap, site, "Z\n").endswith("}\nZ\ny\n") and sub_once(bare, site, "Z\n") == "x\n" + site + "Z\ny\n"
    print("rs64_anchor selftest ok")
