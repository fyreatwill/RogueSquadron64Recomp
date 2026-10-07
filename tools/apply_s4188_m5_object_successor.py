"""Install the regeneration-safe M5 loop-exit successor witness."""

from pathlib import Path

target = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_23.c"
text = target.read_text()
call = "    { extern void rs64_m5_object_successor_witness(uint8_t*, recomp_context*, unsigned); rs64_m5_object_successor_witness(rdram, ctx, 0x8008F924u); } /* PATCH: s4188 M5 object successor witness */\n"
if call in text:
    raise SystemExit("s4188 successor witness already present")
needle = "L_8008F924:\n    // 0x8008F924: lui         $v1, 0x8015\n"
if text.count(needle) != 1:
    raise SystemExit(f"expected one loop-exit marker, found {text.count(needle)}")
target.write_text(text.replace(needle, "L_8008F924:\n" + call + "    // 0x8008F924: lui         $v1, 0x8015\n", 1))
print(f"patched {target}")
