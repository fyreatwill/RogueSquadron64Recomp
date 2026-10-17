#!/usr/bin/env python3
"""s5230: rewrite hand-composed big-endian word reads of rdram[] (no ^3 swizzle,
i.e. byte-reversed values) into rs64_rdram_u32(rdram, base). Idempotent."""
import re, sys

b = r'(?P<b>[^\]]+?)'
def term(off, shift):
    o = r'' if off == 0 else r' *\+ *%d' % off
    return (r'\(?(?:static_cast<uint32_t>\(|uint32_t\()rdram\[(?:(?P=b)|%s)%s\]\)\)? *<< *%d\)?'
            % (b if off == 0 else '(?P=b)', o, shift)) if False else None

pat = re.compile(
    r'\(?\(?(?:static_cast<uint32_t>|uint32_t)\(rdram\[(?P<b>[^\]]+?)\]\)\)? *<< *24\)? *\|\s*'
    r'\(?(?:static_cast<uint32_t>|uint32_t)\(rdram\[(?P=b) *\+ *1\]\)\)? *<< *16\)? *\|\s*'
    r'\(?(?:static_cast<uint32_t>|uint32_t)\(rdram\[(?P=b) *\+ *2\]\)\)? *<< *8\)? *\|\s*'
    r'(?:static_cast<uint32_t>\(|uint32_t\()?rdram\[(?P=b) *\+ *3\]\)?')

for f in sys.argv[1:]:
    s = open(f).read()
    n = [0]
    def r(m):
        n[0] += 1
        base = m['b']
        return 'rs64_rdram_u32(rdram, %s)' % base
    s2 = pat.sub(r, s)
    print(f, n[0])
    open(f, 'w').write(s2)
