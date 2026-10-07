"""Inject the regeneration-safe M5 body witness at guest PC 0x8008F900."""

from pathlib import Path

target = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_23.c"
text = target.read_text()
needle = "    // 0x8008F900: addiu       $a3, $a3, 0x600\n"
injection = (
    "    { extern void rs64_m5_object_body_witness(uint8_t*, recomp_context*); "
    "rs64_m5_object_body_witness(rdram, ctx); } /* PATCH: s4182 M5 object body witness */\n"
)
if text.count(injection):
    raise SystemExit("s4182 body witness already present")
if text.count(needle) != 1:
    raise SystemExit(f"expected one 0x8008F900 body marker, found {text.count(needle)}")
target.write_text(text.replace(needle, injection + needle, 1))
print(f"patched {target}")
