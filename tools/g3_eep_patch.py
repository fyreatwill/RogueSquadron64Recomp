#!/usr/bin/env python3
"""s6748: patch a Rogue Squadron 64 EEPROM image and re-sign it.

Layout (from the oracle and owner saves): two copies 0xC8 apart starting at 0x20. Per copy:
  +0x00 adler32(+0x18..+0xC8)  (the 0xB0-byte payload; header at 0x18 gives length 0x00B0)
  +0x04 adler32(+0x08..+0x18)
  +0x31 selected mission (0 = Ambush at Mos Eisley; owner save 5 = The Jade Moon)
A copy with a bad checksum is rejected (the game shows SELECT GAME with empty TRAINEE slots).
usage: g3_eep_patch.py IN OUT [--set OFF=VAL ...] (OFF relative to the copy start, hex ok)
"""
import sys, struct, zlib
COPIES = (0x20, 0xE8)
def sign(b):
    for c in COPIES:
        struct.pack_into('>I', b, c, zlib.adler32(bytes(b[c+0x18:c+0xC8])))
        struct.pack_into('>I', b, c+4, zlib.adler32(bytes(b[c+0x08:c+0x18])))
def check(b):
    return all(struct.unpack_from('>I', b, c)[0] == zlib.adler32(bytes(b[c+0x18:c+0xC8])) and
               struct.unpack_from('>I', b, c+4)[0] == zlib.adler32(bytes(b[c+0x08:c+0x18])) for c in COPIES)
if __name__ == '__main__':
    a = sys.argv[1:]; b = bytearray(open(a[0], 'rb').read())
    print('input checksums ok:', check(b))
    for kv in a[a.index('--set')+1:] if '--set' in a else []:
        o, v = (int(x, 0) for x in kv.split('='))
        for c in COPIES: b[c+o] = v
    sign(b); assert check(b)
    open(a[1], 'wb').write(b); print('wrote', a[1])
