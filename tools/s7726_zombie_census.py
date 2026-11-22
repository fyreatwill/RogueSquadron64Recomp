#!/usr/bin/env python3
"""s7726: whole-process Objective-C over-release census from NSZombieEnabled=YES + OBJC_DEBUG_MISSING_POOLS=YES game logs.

A freed object that is later autoreleased/flushed shows up as `class _NSZombie_<Cls>` in a MISSING POOLS line; a freed object that
is messaged prints `message sent to deallocated instance`. Lines are split into BOOT (before the level-select cursorMask line the
owner route prints) and FLIGHT (after it), so a flight-only over-release is not hidden under the boot count.

usage: s7726_zombie_census.py --arm DEFAULT_LOG --control CONTROL_LOG [--control-class MTLTextureDescriptorInternal]
       [--mark REGEX] [--segments REGEX]
s7727: --mark replaces the boot/flight split regex (hangar route: 'hangarmenu-a0-entry', boot = before the first SELECT YOUR
CRAFT entry). --segments REGEX also prints per-segment zombie counts, a new segment starting at every match (e.g.
'hangarmenu-a0-entry|initMission\\] call' = hangar entry / mission load), so the control shows which re-entries it covered.
rc 0: control arm shows >=1 zombie of the control class (positive control: the s7725 MTL_OWN=0 over-release) AND the default arm
      shows 0 zombies of any class in any phase.
rc 1: default arm has a zombie (names the class -> the next writer).
rc 3: CONTROL FAIL (the control arm shows none: the instrument is blind, a default-arm zero means nothing).
"""
import argparse, collections, io, re, subprocess, sys

ZRE = re.compile(rb'class _NSZombie_([A-Za-z0-9_]+)')
DEAD = re.compile(rb'message sent to deallocated instance')
MARK = re.compile(rb'cursorMask\)=0x')


def bopen(path):
    # s7801: retained captures are *.zst; reading them raw gave 0 lines and a false CONTROL FAIL (rc 3), so the gate sweep
    # could never re-score them. zstd is a pure spawn for s7651's cache.
    if str(path).endswith('.zst'):
        return io.BytesIO(subprocess.run(['zstd', '-dcq', str(path)], capture_output=True, check=True).stdout)
    return open(path, 'rb')


def scan(path, mark=None, segre=None):
    mk = re.compile(mark.encode()) if mark else MARK
    sg = re.compile(segre.encode()) if segre else None
    seg, segs = 0, collections.Counter()
    phase = 'boot'
    c = {'boot': collections.Counter(), 'flight': collections.Counter()}
    dead = {'boot': 0, 'flight': 0}
    missing = {'boot': 0, 'flight': 0}
    with bopen(path) as f:
        for ln in f:
            if phase == 'boot' and mk.search(ln):
                phase = 'flight'
            if sg and sg.search(ln):
                seg += 1
            if b'MISSING POOLS' in ln:
                missing[phase] += 1
            m = ZRE.search(ln)
            if m:
                c[phase][m.group(1).decode()] += 1
                segs[seg] += 1
            if DEAD.search(ln):
                dead[phase] += 1
    return c, dead, missing, phase == 'flight', (seg, segs)


def show(tag, r):
    c, dead, missing, reached, (nseg, segs) = r
    for ph in ('boot', 'flight'):
        cls = ' '.join(f'{k}:{v}' for k, v in c[ph].most_common()) or '-'
        print(f'{tag} {ph} missing_pools={missing[ph]} zombies={sum(c[ph].values())} dead_msgs={dead[ph]} classes={cls}')
    print(f'{tag} flight_reached={int(reached)}')
    if nseg:
        print(f'{tag} segments={nseg} zombies_per_segment=' + ','.join(str(segs[i]) for i in range(nseg + 1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--control', required=True)
    ap.add_argument('--control-class', default='MTLTextureDescriptorInternal')
    ap.add_argument('--mark', help='phase-split regex (default: level-select cursorMask line)')
    ap.add_argument('--segments', help='regex starting a new counted segment at every match')
    a = ap.parse_args()
    d, k = scan(a.arm, a.mark, a.segments), scan(a.control, a.mark, a.segments)
    show('default', d)
    show('control', k)
    kc = k[0]['boot'][a.control_class] + k[0]['flight'][a.control_class]
    if kc == 0:
        print(f's7726 CONTROL FAIL: control arm has 0 {a.control_class} zombies')
        return 3
    print(f's7726 CONTROL PASS: control {a.control_class} zombies={kc}')
    if not (d[3] and k[3]):
        print('s7726 NOTE: an arm never reached the level-select marker; flight phase not covered')
    nd = sum(d[0]['boot'].values()) + sum(d[0]['flight'].values()) + d[1]['boot'] + d[1]['flight']
    if nd:
        print(f's7726 VERDICT H-more: default arm has {nd} zombie lines')
        return 1
    print('s7726 VERDICT H-clean: default arm 0 zombies' + (' (boot+flight)' if d[3] else ' (boot only)'))
    return 0 if d[3] else 4


if __name__ == '__main__':
    sys.exit(main())
