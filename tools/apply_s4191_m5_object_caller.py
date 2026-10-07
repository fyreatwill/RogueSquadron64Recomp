"""Install the regeneration-safe M5 caller-continuation witness (0x8008F4C0)."""

from pathlib import Path

target = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_23.c"
text = target.read_text()
call = "    { extern void rs64_m5_object_return_witness(uint8_t*, recomp_context*, unsigned); rs64_m5_object_return_witness(rdram, ctx, 0x8008F4C0u); } /* PATCH: s4191 M5 caller continuation witness */\n"
needle = "    // 0x8008F4C0: lw          $ra, 0x18($sp)\n"
if call in text:
    raise SystemExit("s4191 caller witness already present")
if text.count(needle) != 1:
    raise SystemExit(f"expected one marker, found {text.count(needle)}")
target.write_text(text.replace(needle, call + needle, 1))
print(f"patched {target}")
