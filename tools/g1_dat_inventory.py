#!/usr/bin/env python3
"""Decode a retail level DAT without using the recompiled runtime.

Unknown layouts retain raw words; only audited subtypes get semantic fields.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib


def word(data, offset):
    return struct.unpack_from('>I', data, offset)[0]


def elf_word(data, address):
    wide = data[4] == 2
    ph = struct.unpack_from('>Q' if wide else '>I', data, 32 if wide else 28)[0]
    size, count = struct.unpack_from('>HH', data, 54 if wide else 42)
    for i in range(count):
        fields = struct.unpack_from('>IIQQQQQQ' if wide else '>IIIIIIII', data, ph + i * size)
        if wide:
            kind, _, offset, va, _, length, _, _ = fields
        else:
            kind, offset, va, _, length, _, _, _ = fields
        va &= 0xffffffff
        if kind == 1 and va <= address and address + 4 <= va + length:
            return word(data, offset + address - va)
    raise ValueError(f'ELF address {address:08x} has no file bytes')


def extract(rom, level):
    base = 0x144380
    block, _, size = struct.unpack_from('>IHH', rom, base)
    entries = []
    stack = []
    for index, pos in enumerate(range(base + block, base + block + size, 32)):
        while stack and index >= stack[-1][1]:
            stack.pop()
        offset, length, compressed, flags, _, directory, raw = struct.unpack_from('>IIIBBH16s', rom, pos)
        name = raw.split(b'\0')[0].decode('ascii')
        path = '/'.join([x[0] for x in stack] + [name])
        if flags == 0x80:
            assert directory >= 32 and directory % 32 == 0
            end = index + directory // 32
            assert not stack or end <= stack[-1][1]
            stack.append((name, end))
        else:
            entries.append((path, offset, length, compressed))
    assert 0 <= level <= 20
    code = '0123456789abcdefghijk'[level]
    selected = [e for e in entries if e[0] == f'level/lv_{code}/dat']
    assert len(selected) == 1, selected
    path, offset, length, compressed = selected[0]
    start = base + offset
    if compressed == 0xffffffff:
        data = rom[start:start + length]
    else:
        stream = zlib.decompressobj()
        data = stream.decompress(rom[start:start + compressed - 10]) + stream.flush()
        assert stream.eof and not stream.unused_data
    assert len(data) == length
    return data, dict(path=path, rom_offset=f'{start:08x}', length=length,
                      compressed_size=compressed, sha256=hashlib.sha256(data).hexdigest())


def inventory(data):
    rows = []
    for kind in range(8):
        count, base = struct.unpack_from('>II', data, kind * 8)
        assert count == 0 or 0x48 <= base <= len(data) - count * 4
        for index in range(count):
            offset = base + word(data, base + index * 4)
            subtype, _, item, _, size, name_offset = struct.unpack_from('>HHHHII', data, offset)
            assert size >= 16 and offset + size <= len(data)
            assert not name_offset or 16 <= name_offset < size
            name = None
            if name_offset:
                raw = data[offset + name_offset:offset + size]
                assert b'\0' in raw
                name = raw.split(b'\0')[0].decode('ascii')
            row = dict(kind=kind, index=index, offset=f'{offset:08x}', subtype=subtype,
                       item=item, size=size, name=name, layout='unclassified',
                       words={f'{p:02x}': word(data, offset + p) for p in range(0, size - 3, 4)})
            if kind == 0 and subtype in (0x21, 0x24):
                assert size >= 0x90
                row.update(layout='death-objective', health=word(data, offset + 0x6c),
                           activation=dict(boolean=word(data, offset + 0x60),
                                           counter=word(data, offset + 0x64),
                                           minimum=word(data, offset + 0x68)),
                           death=dict(zip(('counter', 'delta', 'boolean', 'value', 'counter2', 'delta2'),
                                          struct.unpack_from('>6I', data, offset + 0x70))))
            rows.append(row)
    intervals = sorted((int(r['offset'], 16), int(r['offset'], 16) + r['size']) for r in rows)
    assert all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, default=Path('build/rogue_squadron.z64'))
    ap.add_argument('--elf', type=Path, default=Path('../rogue_squadron64/build/roguesquadron.elf'))
    ap.add_argument('--level', type=int, default=2)
    ap.add_argument('--log', type=Path)
    ap.add_argument('--check-level2', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    rom, elf = args.rom.read_bytes(), args.elf.read_bytes()
    assert rom[:4] == bytes.fromhex('80371240')
    assert elf[:4] == b'\x7fELF' and elf[5] == 2
    data, source = extract(rom, args.level)
    rows = inventory(data)
    tables = {f'{a:08x}': f'{elf_word(elf, a):08x}' for a in
              (0x8003bdb8 + 24 * 4, 0x8003bed8 + 24 * 4,
               0x8003c140 + 24 * 4, 0x8003bff0 + 36 * 4, 0x800a74c8 + 4 * 4)}
    watch = {i: [] for i in (1, 2, 3, 7, 8, 9, 21, 22, 23, 59)}
    controls = []
    epoch = {}
    if args.log:
        with args.log.open(errors='replace') as f:
            active = False
            for line, text in enumerate(f, 1):
                if text.startswith('[objresp-epoch]'):
                    if epoch:
                        break
                    epoch['start'] = dict(line=line, event=text.strip())
                    active = True
                if active and text.startswith('[objresp-done]'):
                    epoch['end'] = dict(line=line, event=text.strip())
                    break
                if not active or not text.startswith('[objresp-bool]'):
                    continue
                event = {k: int(v) for k, v in re.findall(r'(epoch|vi|arm|id|old|new|initialized)=(\d+)', text)}
                event['line'] = line
                if event['id'] in watch:
                    watch[event['id']].append(event)
                if event['initialized'] and event['old'] != event['new']:
                    controls.append(event)
    targets = [r for r in rows if r.get('death', {}).get('counter') == 40]
    known = [r for r in rows if r.get('death', {}).get('counter') == 71]
    if args.check_level2:
        assert args.level == 2
        assert len(rows) == 401 and Counter(r['kind'] for r in rows) == {0: 127, 3: 59, 6: 99, 7: 116}
        assert [r['name'] for r in known] == ['SHIP_01', 'SHIP_02', 'SHIP_03']
        assert [r['activation']['boolean'] for r in targets] == [21, 22, 23]
        assert all(r['subtype'] == 0x24 and r['health'] == 2000 and r['death']['delta'] == 1 for r in targets)
        assert list(tables.values()) == ['800654c8', '80065708', '80065854', '800657dc', '800d49fc']
        assert elf_word(elf, 0x800D3920) == 0xAE320034
        assert elf_word(elf, 0x800D4BA8) == 0x0C019645
        assert elf_word(elf, 0x800A95F4) == 0x42c80000
        for pc, instruction in {0x800FA618: 0xAC600000, 0x800FA924: 0xE4A00000,
                                0x800C76E4: 0x2442C9F8, 0x800C76F0: 0xC4800000,
                                0x800C7714: 0xAC850000, 0x80102194: 0x4600103E,
                                0x800D4B0C: 0x0C03C848, 0x800D4B14: 0x1C40002A,
                                0x801020B8: 0x0C031D87, 0x801020BC: 0x24040028,
                                0x801020C0: 0x18400013, 0x801020D8: 0x0C031D50,
                                0x801020E8: 0x0C031D50}.items():
            assert elf_word(elf, pc) == instruction, hex(pc)
        if args.log:
            assert controls and 'end' in epoch
            assert all(watch[i] and all(e['new'] == 0 for e in watch[i]) for i in (21, 22, 23))
    report = dict(source=source, rom_sha256=hashlib.sha256(rom).hexdigest(),
                  elf_sha256=hashlib.sha256(elf).hexdigest(), counts=dict(Counter(r['kind'] for r in rows)),
                  original_tables=tables, targets=targets, positive_controls=known,
                  log=str(args.log) if args.log else None, epoch=epoch,
                  boolean_watch=watch, changing_boolean_controls=controls, rows=rows)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(items=len(rows), counts=report['counts'], targets=[r['name'] for r in targets],
                          positive_controls=[r['name'] for r in known], changing_booleans=len(controls))))


if __name__ == '__main__':
    main()
