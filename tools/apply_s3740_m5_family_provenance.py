#!/usr/bin/env python3
"""Replay the M5 family call/entry provenance instrumentation."""

from pathlib import Path


ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3740 M5 family provenance"


def call_line(pc: str, target: str) -> str:
    return (
        f'    {{ extern void rs64_m5_family_provenance(const char*, const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); '
        f'rs64_m5_family_provenance("call", "{target}", {pc}u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r2)); }} /* {MARKER} */\n'
    )


def main() -> None:
    files = {p: p.read_text(encoding="utf-8") for p in ROOT.glob("funcs_*.c")}
    if any(MARKER in text for text in files.values()):
        print("s3740 family provenance already present")
        return

    entry_specs = {
        ROOT / "funcs_2.c": (
            "RECOMP_FUNC void rs_strncpy(uint8_t* rdram, recomp_context* ctx) {\n",
            "rs_strncpy",
            "0x80007640",
        ),
        ROOT / "funcs_6.c": (
            "RECOMP_FUNC void initTextureLUTAndAllocBuffers(uint8_t* rdram, recomp_context* ctx) {\n",
            "initTextureLUTAndAllocBuffers",
            "0x8001E230",
        ),
    }
    for path, (anchor, family, pc) in entry_specs.items():
        text = files[path]
        if text.count(anchor) != 1:
            raise SystemExit(f"entry anchor is not unique: {path}")
        hook = (
            f'    {{ extern void rs64_m5_family_provenance(const char*, const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); '
            f'rs64_m5_family_provenance("entry", "{family}", {pc}u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r2)); }} /* {MARKER} */\n'
        )
        files[path] = text.replace(anchor, anchor + hook, 1)

    call_specs = {
        "0x80002640": "rs_strncpy",
        "0x80003AEC": "rs_strncpy",
        "0x80003B84": "rs_strncpy",
        "0x8005512C": "rs_strncpy",
        "0x80055590": "rs_strncpy",
        "0x800555A8": "rs_strncpy",
        "0x8001FAA8": "rs_strncpy",
        "0x80022B44": "rs_strncpy",
        "0x80018004": "initTextureLUTAndAllocBuffers",
    }
    for path, text in list(files.items()):
        lines = text.splitlines(keepends=True)
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            out.append(line)
            matched = next((pc for pc in call_specs if f"// {pc}: jal" in line), None)
            if matched is not None:
                target = call_specs[matched]
                j = i + 1
                while j < len(lines) and f"{target}(rdram, ctx);" not in lines[j]:
                    j += 1
                if j >= len(lines):
                    raise SystemExit(f"call target not found after {matched} in {path}")
                # The delay-slot assignment is already emitted before the call.
                out.extend(lines[i + 1:j])
                out.append(call_line(matched, target))
                out.append(lines[j])
                i = j
            i += 1
        files[path] = "".join(out)

    for path, text in files.items():
        if MARKER in text:
            path.write_text(text, encoding="utf-8")
    print("s3740 family provenance patched generated funcs")


if __name__ == "__main__":
    main()
