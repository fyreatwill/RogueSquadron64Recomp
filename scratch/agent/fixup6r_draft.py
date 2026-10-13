# DRAFT fixup 6r (s4743) -- NOT wired into tools/fixup_factor5_ucode.py.
# Paste after fixup 6k/6l.. block; relies on `text`, `path`, `is_main_ucode`, `re`, `sys`.
# Static facts (scratch/agent/s4743_ovl2c_static.txt, control ovl1c reproduced j 0x1268):
#   image ROM 0x27368, 0x240 B, dest 0x1DB0..0x1FF0, 144 insns, no jal, no indirect jump,
#   all in-image branch targets inside; ONLY external targets: L_10D8 (bne at 0x1DC4)
#   and L_112C (exit `j` at 0x1FE8). Inputs: r6,r17,r18,r16 (out ptr). No absolute store
#   to DMEM 0x153.
# ORIGIN: DMEM 0x153 == 0x2C at dest 0x1DB0 is the unspliced overlay 0x2C image that the
# main ucode L_1DB0 currently shadows (s4738/s4740); route, do not default-allow.
OVL2C_MARKER = "/* fixup: ovl2csplice */"
if is_main_ucode and OVL2C_MARKER not in text:
    ovl2c_path = path.parent / "factor5_ucode_ovl2c_recompiled.c"
    if not ovl2c_path.exists():
        print("fixup_factor5_ucode: FIXUP 6r INPUT MISSING: run RSPRecomp on "
              "factor5_rsp_ovl2c.toml first.", file=sys.stderr)
        sys.exit(1)
    o = ovl2c_path.read_text(encoding="utf-8")
    ms = re.search(r"^L_1DB0:\n", o, flags=re.MULTILINE)
    me = re.search(r"^do_indirect_jump:\n", o, flags=re.MULTILINE)
    if not ms or not me or me.start() <= ms.start():
        print("fixup_factor5_ucode: FIXUP 6r EXTRACTION FAILED", file=sys.stderr)
        sys.exit(1)
    region = o[ms.start():me.start()]
    labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    external = set(re.findall(r"goto (L_[0-9A-F]{4});", region)) - labels
    if external != {"L_10D8", "L_112C"}:
        print("fixup_factor5_ucode: FIXUP 6r SANITY FAILED: externals "
              f"{sorted(external)} != ['L_10D8','L_112C']", file=sys.stderr)
        sys.exit(1)
    for lbl in labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL2C_" + lbl[2:], region)
    text, n = re.subn(r"(^do_indirect_jump:\n)",
                      lambda m: OVL2C_MARKER + "\n" + region + m.group(1),
                      text, count=1, flags=re.MULTILINE)
    assert n == 1, "6r splice point"
    # route: insert before the final `goto L_1DB0;` of case 0x1DB0 (after the ovl1c line)
    anchor = re.compile(r"(            if \(RSP_MEM_BU\(0X153, 0\) == 0x28\) \{[^\n]*ovl24route \*/\n"
                        r"            goto L_1DB0;\n)")
    def _r(m):
        return ("            if (RSP_MEM_BU(0X153, 0) == 0x2C) {"
                " rs64_e9prov_ovl_route(0x2C, 0x1DB0); goto OVL2C_1DB0; }  "
                + OVL2C_MARKER + "\n" + m.group(1))
    text, n = anchor.subn(_r, text, count=1)
    if n != 1:
        print("fixup_factor5_ucode: FIXUP 6r ANCHOR FAILED (case 0x1DB0)", file=sys.stderr)
        sys.exit(1)
