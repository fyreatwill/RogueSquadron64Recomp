"""Install the regeneration-safe M5 post-loop load/use witness."""

from pathlib import Path

target = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_23.c"
text = target.read_text()
for address, marker in (("0x8008F928", "lw          $v1, -0x6638($v1)"),
                        ("0x8008F938", "addu        $v0, $v0, $v1"),
                        ("0x8008F93C", "sw          $zero, -0x18($v0)")):
    call = f"    {{ extern void rs64_m5_object_load_witness(uint8_t*, recomp_context*, unsigned); rs64_m5_object_load_witness(rdram, ctx, {address}u); }} /* PATCH: s4189 M5 object load witness */\n"
    if call in text:
        raise SystemExit("s4189 load witness already present")
    needle = f"    // {address}: {marker}\n"
    if text.count(needle) != 1:
        raise SystemExit(f"expected one {address} marker, found {text.count(needle)}")
    text = text.replace(needle, call + needle, 1)
target.write_text(text)
print(f"patched {target}")
