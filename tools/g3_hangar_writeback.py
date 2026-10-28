#!/usr/bin/env python3
"""Summarize phase/source joined hangar colour-writeback witnesses."""
import argparse
import collections
import json
from pathlib import Path
import re


def summarize(path):
    groups = collections.defaultdict(lambda: dict(writebacks=0, overlaps=0,
        changes=0, changed_bytes=0, control_changes=0, outside_overlap_changes=0,
        fingerprints=0, source_nonzero=0, matching_post_hashes=0))
    posts = {}
    fps = []
    flip_sources = {}
    copies = {}
    dumps = []
    current_phase = 0
    injected = False
    crashes = 0
    with open(path, errors='replace') as log:
        for line in log:
            crashes += bool(re.search(r'CRASH|SIGSEGV|SIGBUS|Assertion failed|Abort trap', line))
            if '[fb-band-wb-control]' in line:
                injected |= 'identical=0 injected=1' in line
            if '[fb-flip-range]' in line:
                f = dict(re.findall(r'(\w+)=([^\s]+)', line))
                current_phase = int(f['phase'])
                width, height = map(int, f['size'].split('x'))
                copies[(current_phase, int(f['fb'], 16), width)] = height
                flip_sources[(current_phase, int(f['vi_origin'], 16))] = int(f['fb'], 16)
            if '[fbdump]' in line:
                f = dict(re.findall(r'(\w+)=([^\s]+)', line))
                width = int(f['stride'])
                address = int(f['fb'], 16) & 0xffffff
                height = copies.get((current_phase, address, width))
                ppm = Path(path).parent / 'fbd' / f"fb_{int(f['n']):07d}_w{width}.ppm"
                if height is not None and ppm.exists():
                    with ppm.open('rb') as image:
                        image.readline()
                        size = image.readline()
                        while size.startswith(b'#'): size = image.readline()
                        dw, dh = map(int, size.split())
                    dumps.append(dict(phase=current_phase, source=f'0x{address:06X}',
                        file=str(ppm), dump_width=dw, dump_height=dh,
                        source_height=height, rows_past_source=max(0, dh-height)))
            if '[fb-band-wb]' in line:
                fields = dict(re.findall(r'(\w+)=([^\s]+)', line))
                key = (int(fields['phase']), int(fields['source'], 16), int(fields['width']))
                g = groups[key]
                g['writebacks'] += 1
                overlap, changed = int(fields['overlap_bytes']), int(fields['changed_bytes'])
                g['overlaps'] += overlap > 0
                g['changes'] += changed > 0
                g['changed_bytes'] += changed
                g['control_changes'] += int(fields['control_changed']) > 0
                g['outside_overlap_changes'] += changed > 0 and overlap == 0
                posts[key] = fields['post']
            elif '[fb-source-fp]' in line:
                f = dict(re.findall(r'(\w+)=([^\s]+)', line))
                f['source_address'] = flip_sources.get((int(f['phase']), int(f['origin'], 16)))
                key = (int(f['phase']), f['source_address'], int(f['width']))
                f['preceding_post_match'] = f['hash'] == posts.get(key)
                fps.append(f)
    for f in fps:
        key = (int(f['phase']), f['source_address'] if f['source_address'] is not None else int(f['origin'], 16), int(f['width']))
        g = groups[key]
        g['fingerprints'] += 1
        g['source_nonzero'] += int(f['nonzero']) > 0
        g['matching_post_hashes'] += f['preceding_post_match']
    return dict(log=str(path), injected_control=injected, crash_lines=crashes, dump_ranges=dumps,
        sources=[dict(phase=k[0], source=f'0x{k[1]:06X}', width=k[2], **g)
                 for k, g in sorted(groups.items())],
        limitation='Changes bracket colour writeback; concurrent guest writes remain possible. '
        'No coverage before first VI source registration or after the per-phase budget. '
        'Fingerprint nonzero/transition counts alone do not prove an image defect.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logs', nargs='+')
    args = parser.parse_args()
    print(json.dumps([summarize(path) for path in args.logs], indent=2))
