"""s7802: planted controls for the retained-input contract of tools/s7753_rdp_output_gate.py and tools/s7756_hstate_gate.py.
  P1 one planted absent input among the real set -> RED rc 1 (partial loss of a retained set is not a fresh clone)
  P2 every input absent (fresh clone)            -> NEEDS-INPUT rc 4 (the sweep's NEEDS_INPUT text still matches)
  P3 a real .zst-only input resolves             -> rs64_zopen.resolve returns the .zst, materialize gives the raw header
Exit 0 CONTROLS PASS, 3 FAIL."""
import contextlib, importlib, io, os, re, struct, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs64_zopen
ok = []
for mod, tab in (("s7753_rdp_output_gate", "SNAPS"), ("s7756_hstate_gate", "PAIRS")):
    m = importlib.import_module(mod); real = dict(getattr(m, tab)); v = next(iter(real.values()))
    for name, table, want_rc, want in (("P1", {**real, "scratch/s7802/planted_absent.bin": v}, 1, r"^RED partial retained input: 1/"),
                                       ("P2", {"scratch/s7802/absent_%d.bin" % i: v for i in range(3)}, 4, r"^NEEDS-INPUT 3/3 ")):
        setattr(m, tab, table); b = io.StringIO()
        with contextlib.redirect_stdout(b):
            rc = m.main()
        setattr(m, tab, real)
        good = rc == want_rc and re.search(want, b.getvalue(), re.M) is not None
        ok.append(good); print(f"{mod} {name} rc={rc} want={want_rc} -> {'PASS' if good else 'FAIL'}  {b.getvalue().strip()[:120]}")
    s0 = os.path.join(m.ROOT, next(iter(real)))
    r = rs64_zopen.resolve(s0); d = tempfile.mkdtemp(prefix="s7802_")
    hdr = open(rs64_zopen.materialize(s0, d), "rb").read(4) if r else b""
    good = bool(r) and (r.endswith(".zst") or os.path.exists(s0)) and struct.unpack("<I", hdr)[0] == 0x31353753
    ok.append(good); print(f"{mod} P3 resolve={r and os.path.basename(r)} header={'S751' if good else hdr} -> {'PASS' if good else 'FAIL'}")
print(f"CONTROLS {'PASS' if all(ok) else 'FAIL'} {sum(ok)}/{len(ok)}")
sys.exit(0 if all(ok) else 3)
