#!/usr/bin/env python3
"""s7588 class OW-2: ownership census of the Apple ObjC/ObjC++ TUs (the s7587 census covered plume_metal.cpp only).

For every *.m / *.mm under src/ and lib/rt64/src (examples excluded): compiled? (build/compile_commands.json), ARC or MRC, and every
ownership-relevant site (alloc/new/copy +1, retain/release/autorelease, CF Create/Copy vs CFRelease, IOKit Get/Release, strdup,
main-queue dispatch), each classified from a hand table keyed by (file, needle). Exit 1 on an UNCLASSIFIED site in a compiled TU or
on a row marked OPEN. --controls: a planted MRC TU with an unbalanced alloc and a raw dispatch_async must read UNCLASSIFIED.
"""
import json, os, re, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r'\b(alloc|new\w*|copy\w*|retain|release|autorelease|CFRelease|IOObjectRelease|\w+Create\w*|\w+Copy\w*|strdup|'
                 r'dispatch_async|dispatch_sync|NSHomeDirectory|autoreleasepool)\b')
# (file suffix, needle) -> (verdict, note). Verdicts: OK, ONCE (startup/rare, bounded), FIXED (s7588), OPEN.
TABLE = {
 ('rt64_apple.mm', 'NSHomeDirectory'): ('ONCE', 'only when $HOME is unset (rt64_user_paths.cpp:41); +0 string, strdup copy owned by caller'),
 ('plume_apple.mm', 'IORegistryEntrySearchCFProperty'): ('OK', '+1 CF property released by CFRelease in the same function'),
 ('plume_apple.mm', 'CFRelease'): ('OK', 'pairs IORegistryEntrySearchCFProperty'),
 ('plume_apple.mm', 'IOObjectRelease'): ('OK', 'entry + parent released on both paths'),
 ('plume_apple.mm', 'dispatch_sync'): ('ONCE', 'CocoaWindow ctor off-main only (forceSync=true)'),
 ('plume_apple.mm', 'rs64S7588Post'): ('FIXED', 'per-present off-main getters: block runs in its own pool (ROGUESQ_APPLE_POOL, s7588)'),
 ('plume_apple.mm', 'dispatch_async'): ('OK', 'toggleFullscreen off-main: user key press only, AppKit call on the main queue'),
 ('nfd_cocoa.m', '*'): ('OK', 'upstream nativefiledialog, balanced (alloc/release pairs, urls/enumerator retain freed by NFD_PathSet_Free*); only reachable from RT64 gui file dialogs (user action)'),
 ('plume_apple.mm', 's7588'): ('OK', 's7588 instrument (gauge/plant/pool)'),
 ('rs64_display_mac.mm', 'autoreleasepool'): ('OK', 'every entry point wraps its +0 AppKit queries in @autoreleasepool'),
}
def classify(fname, line):
    if 'S7588' in line or 's7588' in line or 'rs64S7588' in line and 'Post(' not in line:
        return TABLE.get((fname, 's7588'), ('UNCLASSIFIED', ''))
    for (f, needle), v in TABLE.items():
        if fname == f and needle in line and needle != 's7588': return v
    if fname == 'rs64_display_mac.mm': return TABLE[(fname, 'autoreleasepool')]
    if (fname, '*') in TABLE: return TABLE[(fname, '*')]
    return ('UNCLASSIFIED', '')
def scan(files, compiled):
    bad = 0; rows = []
    for path in files:
        rel = os.path.relpath(path, ROOT); fname = os.path.basename(path)
        info = compiled.get(os.path.realpath(path))
        state = 'not-built' if info is None else ('ARC' if info else 'MRC')
        n = 0
        for i, ln in enumerate(open(path, errors='replace'), 1):
            code = ln.split('//')[0]
            if not PAT.search(code): continue
            n += 1
            v, note = classify(fname, code) if state != 'not-built' else ('NOT-BUILT', '')
            if v in ('UNCLASSIFIED', 'OPEN'): bad += 1
            if v != 'NOT-BUILT': rows.append(f'  {rel}:{i} {v:12s} {code.strip()[:90]}' + (f'  -- {note}' if note and v != 'OK' else ''))
        print(f'{rel}: {state}, {n} sites')
    for r in rows: print(r)
    return bad
def compiled_map():
    cc = json.load(open(os.path.join(ROOT, 'build/compile_commands.json')))
    m = {}
    for e in cc:
        f = e['file']
        if f.endswith(('.m', '.mm')):
            c = e.get('command') or ' '.join(e.get('arguments', []))
            m[os.path.realpath(f)] = ('-fobjc-arc' in c)
    return m
def main():
    files = []
    for base in ('src', 'lib/rt64/src'):
        for d, _, fs in os.walk(os.path.join(ROOT, base)):
            if '/examples' in d: continue
            files += [os.path.join(d, f) for f in fs if f.endswith(('.m', '.mm'))]
    files.sort(); cm = compiled_map()
    bad = scan(files, cm)
    if '--controls' in sys.argv:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, 'ctl_plant.mm')
            open(p, 'w').write('id x = [[NSObject alloc] init];\ndispatch_async(dispatch_get_main_queue(), ^{});\n')
            print('control:'); cb = scan([p], {os.path.realpath(p): False})
            print(f'CONTROL {"FIRED" if cb == 2 else "FAILED"} ({cb}/2 unclassified)')
            if cb != 2: return 2
    print(f'UNCLASSIFIED/OPEN={bad}')
    return 1 if bad else 0
sys.exit(main())
