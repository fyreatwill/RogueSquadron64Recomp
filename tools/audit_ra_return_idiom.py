#!/usr/bin/env python3
"""Census late r31 writes around generated jr $ra return blocks."""

import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
FUNC_RE = re.compile(r"^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC\s+.*?\b([A-Za-z0-9_]+)\s*\([^\n]*\)\s*\{", re.M)  # s7420: weak-aware
JR_RE = re.compile(r"^\s*//\s+(0x[0-9A-F]+):\s+jr\s+\$ra\s*$", re.M)
CALL_RE = re.compile(r"^\s*//\s+(0x[0-9A-F]+):\s+jalr?\b", re.M)
ASSIGN_RE = re.compile(r"^\s*ctx->r31\s*=\s*([^;]+);", re.M)


def line_at(text, pos):
    return text.count("\n", 0, pos) + 1


def main():
    files = sorted(ROOT.glob("funcs_*.c"))
    body_count = assignment_count = return_count = return_with_assignment = call_count = 0
    return_classes = {"restore": 0, "link-or-computed": 0, "other": 0, "no-prior-assignment": 0}
    late = []

    for path in files:
        text = path.read_text()
        funcs = list(FUNC_RE.finditer(text))
        body_count += len(funcs)
        for i, fn in enumerate(funcs):
            end = funcs[i + 1].start() if i + 1 < len(funcs) else len(text)
            body = text[fn.start():end]
            assignment_count += len(ASSIGN_RE.findall(body))
            call_count += len(CALL_RE.findall(body))
            for ret in JR_RE.finditer(body):
                return_count += 1
                prior = list(ASSIGN_RE.finditer(body, 0, ret.start()))
                if not prior:
                    return_classes["no-prior-assignment"] += 1
                    continue
                return_with_assignment += 1
                rhs = prior[-1].group(1).strip()
                if "MEM_W(ctx->r29" in rhs:
                    cls = "restore"
                elif re.fullmatch(r"(?:ADD32\()?ctx->r1(?:\))?", rhs):
                    cls = "link-or-computed"
                else:
                    cls = "other"
                return_classes[cls] += 1

                calls = list(CALL_RE.finditer(body, 0, ret.start()))
                last_call = calls[-1].start() if calls else -1
                writes_after_call = [a for a in ASSIGN_RE.finditer(body, last_call, ret.start())]
                non_restore = [a for a in writes_after_call if "MEM_W(ctx->r29" not in a.group(1)]
                if non_restore:
                    for a in non_restore:
                        late.append((path.name, fn.group(1), line_at(text, fn.start()), ret.group(1), line_at(text, fn.start() + a.start()), a.group(1).strip()))

    print(f"root={ROOT}")
    print(f"files={len(files)} functions={body_count} r31_assignments={assignment_count} jal_or_jalr_comments={call_count} jr_ra_comments={return_count}")
    print("return_class_counts=" + ", ".join(f"{k}:{v}" for k, v in return_classes.items()))
    print(f"return_blocks_with_prior_r31={return_with_assignment} late_non_restore_writes={len(late)}")
    for row in late:
        print("LATE", *row)

    controls = {
        "ordinary_saved_ra": "loadOverlay",
        "tail_or_indirect_return": "audioMixStereoBlock8",
    }
    for label, name in controls.items():
        match = next((f for p in files for f in FUNC_RE.finditer(p.read_text()) if f.group(1) == name), None)
        print(f"control_{label}={name}:{'present' if match else 'MISSING'}")


if __name__ == "__main__":
    main()
