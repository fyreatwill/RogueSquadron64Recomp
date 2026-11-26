#!/usr/bin/env python3
"""s7971 class MP helper: allocate <gb> GB of INCOMPRESSIBLE memory (random bytes; zero/constant pages would just be
compressed away by the macOS compressor and apply no pressure), hold it <hold_s> seconds while re-reading one byte per
16 KB page every 2 s (keeps the hog's pages active so the kernel must compress/swap someone else's), then free and exit.
Prints 'hog ready_ms=<epoch ms> alloc_s=<s> gb=<gb>' when the allocation is complete and 'hog done' at release.
usage: s7971_mem_hog.py <gb> <hold_s>"""
import os, sys, time
gb, hold = float(sys.argv[1]), float(sys.argv[2])
CH = 64 << 20; n = int(gb * (1 << 30) // CH); t0 = time.time()
seed = os.urandom(CH)
chunks = []
for i in range(n):
    c = bytearray(seed); c[0:8] = i.to_bytes(8, 'little'); chunks.append(c)  # distinct chunk, random page content
print(f'hog ready_ms={int(time.time()*1000)} alloc_s={time.time()-t0:.2f} gb={n*CH/(1<<30):.2f}', flush=True)
end = time.time() + hold
while time.time() < end:
    for c in chunks: _ = c[::16384]
    time.sleep(2)
del chunks; print('hog done', flush=True)
