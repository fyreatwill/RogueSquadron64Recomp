"""s5867b: playerXwingUpdate(slot,msg,payload) entry census by msg id (a1&0xFFFF, bucket 20+msg%16) feeding the
[plc] line of apply_s5867_callers.py, which also dumps the 0x8010CA1C gate word.  Idempotent."""
import pathlib, re, sys
T = "PATCH: s5867b msg"
if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    p = base / "funcs_31.c"; t = p.read_text()
    if T in t:
        print("already"); sys.exit(0)
    m = re.search(r"RECOMP_FUNC void playerXwingUpdate\(uint8_t\* rdram, recomp_context\* ctx\) \{\n", t)
    ins = "    { extern void rs64_s5867_hit(int, uint8_t*, uint32_t); rs64_s5867_hit(20 + ((uint32_t)ctx->r5 & 0xFFFF) % 16, rdram, 0); } /* " + T + " */\n"
    p.write_text(t[:m.end()] + ins + t[m.end():])
    print("patched")
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"; s = fp.read_text()
    if "apply_s5867b_msg" not in s:
        lst = '    "apply_s5867_callers.py",\n]\n'; assert s.count(lst) == 1
        fp.write_text(s.replace(lst, '    "apply_s5867_callers.py",\n    "apply_s5867b_msg.py",\n]\n', 1))
