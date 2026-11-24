#!/bin/zsh
# s7900: build the cxd4 task replay with an SP DMA read log (which RDRAM bytes the F5 ucode fetched, and at what RDP output
# offset). Copies the cxd4 tree to a scratch build dir and patches one hook line into SP_DMA_READ; the vendored cxd4 is untouched.
set -e
H=${0:A:h}; C=${CXD4:-$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4}; A=${C:h}/mupen64plus-core/src/api
B=${H:h:h}/scratch/s7900_cxd4_build; rm -rf $B; mkdir -p $B; cp -R $C/ $B/
python3 - $B/su.c <<'PY'
import sys; p = sys.argv[1]; s = open(p).read()
k = 'void SP_DMA_READ(void)\n{\n'
assert s.count(k) == 1, 'SP_DMA_READ anchor'
s = s.replace(k, 'extern void s7900_dma_hook(unsigned int, unsigned int, unsigned int);\n' + k +
              '    s7900_dma_hook(*CR[0x1], *CR[0x0], GET_RCP_REG(SP_RD_LEN_REG));\n', 1)
open(p, 'w').write(s)
PY
cc -O2 -w -DM64P_PLUGIN_API -I$B -I$A -o $H/replay_dma $H/replay_dma.c $B/osal_dynamiclib_unix.c
echo built $H/replay_dma
