#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"

scope=(src lib/N64ModernRuntime/librecomp/src lib/N64ModernRuntime/librecomp/include lib/N64ModernRuntime/ultramodern/src)
files=$(rg --files "${scope[@]}" -g '*.{c,cpp,h,hpp}' | sort)

printf '%s\n' '== target-field literals =='
rg -n -i '128c92|128cd0|128cd1|128cd2|128cd3|128cd4' "${scope[@]}" -g '*.{c,cpp,h,hpp}' || true

printf '%s\n' '== direct host-buffer assignments =='
rg -n 'rdram\[[^\n]+\]\s*=|\*\([^\n]*rdram[^\n]+\)\s*=|memcpy\([^\n]*rdram' "${scope[@]}" -g '*.{c,cpp,h,hpp}' || true

printf '%s\n' '== host RDRAM write macros =='
rg -n 'MEM_[BHW]\([^\n]+\)\s*=|SD\([^\n]+\)\{' "${scope[@]}" -g '*.{c,cpp,h,hpp}' || true

printf '%s\n' '== census hook call sites =='
rg -n 'rs64_m5_host_write_census|rs64_m5_exact_route_dma_write' src lib/N64ModernRuntime/librecomp -g '*.{c,cpp,h,hpp}' || true

printf '%s\n' '== files scanned =='
printf '%s\n' "$files" | awk 'END { print NR }'
