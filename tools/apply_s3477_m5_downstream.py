"""Install the regeneration-safe M5 downstream store census."""
from pathlib import Path


MARKER = "PATCH: s3477 M5 downstream store census"


def apply(text: str):
    if MARKER in text:
        return text, False, "s3477 downstream census already present"
    start = text.index("RECOMP_FUNC void rs_free(")
    end = text.index("\nRECOMP_FUNC void ", start + 1)
    body = text[start:end]
    sites = {
        "0x80001D10": ("H", "U32(ADD32(ctx->r4, 0X0))", "U32(ctx->r9)"),
        "0x80001D3C": ("W", "U32(ADD32(ctx->r4, 0X4))", "U32(ctx->r2)"),
        "0x80001D70": ("W", "U32(ADD32(ctx->r8, 0X4))", "U32(ctx->r2)"),
        "0x80001DFC": ("H", "U32(ADD32(ctx->r4, 0X0))", "U32(ctx->r9)"),
        "0x80001E28": ("W", "U32(ADD32(ctx->r4, 0X4))", "U32(ctx->r2)"),
        "0x80001E5C": ("W", "U32(ADD32(ctx->r8, 0X4))", "U32(ctx->r2)"),
        "0x80001EE4": ("H", "U32(ADD32(ctx->r5, 0X0))", "U32(ctx->r9)"),
        "0x80001F10": ("W", "U32(ADD32(ctx->r5, 0X4))", "U32(ctx->r2)"),
        "0x80001F48": ("W", "U32(ADD32(ctx->r8, 0X4))", "U32(ctx->r2)"),
    }
    sites = {key.lower(): value for key, value in sites.items()}
    lines = body.splitlines(True)
    out = []
    pc = None
    inserted = 0
    for line in lines:
        if line.startswith("    // 0x") and ":" in line:
            pc = line.split("// ", 1)[1].split(":", 1)[0].lower()
        out.append(line)
        if pc in sites and line.lstrip().startswith("MEM_") and " = " in line:
            width, addr, value = sites[pc]
            out.append(
                f"    rs64_m5_downstream_store(rdram, ctx, '{width}', {pc}u, "
                f"{addr}, {value}); /* {MARKER} */\n"
            )
            inserted += 1
            pc = None
    expected = sum(body.lower().count(f"// {pc}:") for pc in sites)
    if inserted != expected:
        raise RuntimeError(f"s3477 matched {inserted}/{expected} downstream stores")
    return text[:start] + "".join(out) + text[end:], True, f"funcs_0.c: s3477 downstream stores patched x{inserted}"


if __name__ == "__main__":
    path = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
    updated, changed, message = apply(path.read_text())
    if changed:
        path.write_text(updated)
    print(message)
