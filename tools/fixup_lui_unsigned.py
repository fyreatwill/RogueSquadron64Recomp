#!/usr/bin/env python3
"""s7580 class LU: N64Recomp emits LUI as S32(0X8011 << 16): a signed-int left shift whose result does not fit int, which
is C17 6.5.7p4 undefined behaviour for every immediate >= 0x8000 (22,669 generated sites + fixup-patch copies). UBSan
(build_ubsans, -fsanitize=shift) reported 7,136 executed sites at L1 boot, every one this idiom. Rewrite the literal to
unsigned (S32(0X8011u << 16)): the shift is then defined and the int32 conversion is clang's documented modulo, so the
machine code is unchanged (tools/s7580_lui_identity.py compiles every TU both ways at the real -O2 flags: 0 object diffs).
Idempotent; runs last in fixup_game_funcs_vendored.py. usage: fixup_lui_unsigned.py <RecompiledFuncs dir>"""
import pathlib, re, sys
RX = re.compile(r'S32\((0[xX][0-9A-Fa-f]{1,4}|[0-9]{1,5}) << 16\)')
# (c) hand-written LUI in a patch (s4192-era funcs_24 vagn base): (int32_t)(0X8015 << 16)
RX2 = re.compile(r'\(int32_t\)\((0[xX][0-9A-Fa-f]{1,4}) << 16\)')
# s7580 residuals (same UBSan run, after the LUI rewrite): two fixup-patch shift-base sites. (a) s6882/s7009 spannarrow shifts a
# negative int64 row (left shift of negative value, L1/L4/L12): use the equal multiply. (b) s4192 audio-wait-spin loop shifts an
# int-promoted u16 (65535 << 16 overflows int): shift it as uint32_t.
EXACT = [('((int64_t)(int32_t)ctx->r5 << (g_rs64_ww ? 7 : 6))', '((int64_t)(int32_t)ctx->r5 * (g_rs64_ww ? 128 : 64))'),
         ('((int64_t)(int32_t)ctx->r5 << 6)', '((int64_t)(int32_t)ctx->r5 * 64)'),
         ('S32(MEM_HU(S32(0X8015u << 16), -0X6676) << 16)', 'S32((uint32_t)MEM_HU(S32(0X8015u << 16), -0X6676) << 16)')]
def rewrite(s):
    s, n = RX.subn(lambda m: f'S32({m.group(1)}u << 16)', s)
    s, n2 = RX2.subn(lambda m: f'(int32_t)({m.group(1)}u << 16)', s); n += n2
    for a, b in EXACT:
        n += s.count(a); s = s.replace(a, b)
    return s, n
def main():
    d = pathlib.Path(sys.argv[1]); tot = files = 0
    for p in sorted(d.glob('*.c')):
        s = p.read_text(errors='surrogateescape'); t, n = rewrite(s)
        if n: p.write_text(t, errors='surrogateescape'); tot += n; files += 1
    print(f'fixup_lui_unsigned: {tot} LUI literals made unsigned in {files} files')
if __name__ == '__main__':
    main()
