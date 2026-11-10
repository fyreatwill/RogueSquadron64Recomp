# NEXT: owner reports first; otherwise per-shim return semantics vs the ROM routine each one replaces
HYPOTHESIS-ID: host-shim-semantics-census
Context: s7088 closed the o32 ABI layer of the 55 called `*_recomp` shims (tools/s7088_shim_abi_census.py; 0 live) and
found one semantic gap by reading the ROM (osAiSetFrequency rounding, fixed). The ROM still contains every replaced
libultra routine: `mips64-elf-objdump -d ../rogue_squadron64/build/roguesquadron.elf --start-address=<fn>`.
Unit (offline, one tool, no game run unless a live defect is found):
1. For each of the 55 called shims, list which guest registers / memory the callers READ after the call (v0, v1, out-
   pointer args): walk the generated code after each `X_recomp(rdram, ctx)` site in ../N64Recomp/RecompiledFuncs up to the
   next write of v0/v1 (reads before write = consumed). Shims whose results nobody reads are done.
2. For consumed results, compare the shim's value with the ROM routine's: return codes (osRecvMesg/osSendMesg/osJamMesg
   -1 on full/empty with NOBLOCK, osSetTimer 0, osEepromLongRead/Write 0 or CONT_NO_RESPONSE_ERROR, osContInit bitpattern,
   osEepromProbe type, osPfs* NOPACK, __osDisableInt previous mask, osContGetQuery status bytes).
3. Discriminator per shim: {result unread, matches ROM, differs-unreachable, differs-live}. A differs-live finding gets
   a fix + host test + a live check in the same session; lib/ edits need ./submodule-patches/export.sh + commit.
Positive control: the pre-s7088 osAiSetFrequency text must show as differs (22 inputs); negative: __osDisableInt with v0
unread by every caller must come out "result unread".
