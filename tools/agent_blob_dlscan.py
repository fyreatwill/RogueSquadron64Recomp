#!/usr/bin/env python3
"""Scan s4511-style child-DL data blobs for embedded F5 display-list residue.

A blob that contains 'e7 00 00 00 00 00 00 00' (RDP pipe sync) followed by
'06 00 00 00 80 xx xx xx' (F3DSWRS_DL call) is a working display-list buffer,
not static vertex data, so a cross-side byte diff of it is not a vertex diff.
Usage: python3 tools/agent_blob_dlscan.py scratch/agent/s4511
"""
import glob, sys
D = sys.argv[1]
SYNC = bytes.fromhex('e700000000000000')
for p in sorted(glob.glob(D + '/*_w512_0_c*_d*_op04.bin')):
    b = open(p, 'rb').read()
    offs = [i for i in range(0, len(b) - 8, 4) if b[i:i+8] == SYNC]
    print(p.split('/')[-1], 'sync_at=', offs[:6], 'n=', len(offs))
