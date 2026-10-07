"""Install the regeneration-safe M5 post-loop return/caller witness."""

from pathlib import Path

target = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_23.c"
text = target.read_text()
calls = (
    ("    { extern void rs64_m5_object_return_witness(uint8_t*, recomp_context*, unsigned); rs64_m5_object_return_witness(rdram, ctx, 0x8008F8A8u); } /* PATCH: s4190 M5 object return witness */\n",
     "    // 0x8008F8A8: lui         $a0, 0x8015\n"),
    ("    { extern void rs64_m5_object_return_witness(uint8_t*, recomp_context*, unsigned); rs64_m5_object_return_witness(rdram, ctx, 0x8008F958u); } /* PATCH: s4190 M5 object return witness */\n",
     "    return;\n    // 0x8008F958: nop\n"),
)
for call, needle in calls:
    if call in text:
        raise SystemExit("s4190 return witness already present")
    if text.count(needle) != 1:
        raise SystemExit(f"expected one marker, found {text.count(needle)}: {needle.strip()}")
    text = text.replace(needle, call + needle, 1)
target.write_text(text)
print(f"patched {target}")
