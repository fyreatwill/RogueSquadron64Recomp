"""Install the regeneration-safe M5 loop-branch witness."""

from pathlib import Path

target = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_23.c"
text = target.read_text()
call = "    { extern void rs64_m5_object_branch_witness(uint8_t*, recomp_context*, unsigned); rs64_m5_object_branch_witness(rdram, ctx, 0x8008F91Cu); } /* PATCH: s4187 M5 object branch witness */\n"
if call in text:
    raise SystemExit("s4187 branch witness already present")
needle = "    // 0x8008F91C: bne         $v0, $zero, L_8008F8FC\n"
if text.count(needle) != 1:
    raise SystemExit(f"expected one branch marker, found {text.count(needle)}")
target.write_text(text.replace(needle, call + needle, 1))
print(f"patched {target}")
