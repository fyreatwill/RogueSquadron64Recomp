#!/usr/bin/env python3
"""Decode a retail level DAT without using the recompiled runtime.

Unknown layouts retain raw words; only audited subtypes get semantic fields.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import zlib


def word(data, offset):
    return struct.unpack_from('>I', data, offset)[0]


def elf_offset(data, address):
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
            return offset + address - va
    raise ValueError(f'ELF address {address:08x} has no file bytes')


def elf_word(data, address):
    return word(data, elf_offset(data, address))


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
            if kind == 0 and subtype in (0x14, 0x21, 0x24):
                assert size >= 0x90
                effect = dict(zip(('counter', 'delta', 'boolean', 'value', 'counter2', 'delta2'),
                                  struct.unpack_from('>6I', data, offset + 0x70)))
                if subtype == 0x14:
                    row.update(layout='unregistered-damage-objective',
                               health_detail0=word(data, offset + 0x6c), damage_effect=effect)
                else:
                    row.update(layout='death-objective', health=word(data, offset + 0x6c),
                               activation=dict(boolean=word(data, offset + 0x60),
                                               counter=word(data, offset + 0x64),
                                               minimum=word(data, offset + 0x68)), death=effect)
            rows.append(row)
    intervals = sorted((int(r['offset'], 16), int(r['offset'], 16) + r['size']) for r in rows)
    assert all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:]))
    return rows


def level3_contract(elf, rows):
    instructions = {
        0x80047B50: 0x8C4475D8,
        0x80047B5C: 0x0C011EDC,
        0x80046878: 0xAC82000C,
        0x80046DBC: 0xAC5275D8,
        0x800C761C: 0x14800003,
        0x800C762C: 0x24638060,
        0x800C7630: 0x2482FFFF,
        0x800C7634: 0x00021080,
        0x800C7638: 0x00431021,
        0x800C7640: 0x03E00008,
        0x800C7644: 0x00000000,
        0x801034AC: 0x0C031CE4,
        0x801034B0: 0x24053A98,

        0x8003BDD8: 0x800653F4,
        0x800653F4: 0x3C048007,
        0x800653F8: 0x2484CBB0,
        0x80065688: 0xA6230006,
        0x8006CC24: 0xAE300034,
        0x8003CA30: 0x8006CF88,
        0x8006CF8C: 0x8E230034,
        0x8006CF90: 0x8E427CE4,
        0x8006CF94: 0x2473006C,
        0x8006CFA0: 0x8C420000,
        0x8006CFD4: 0x96040006,
        0x8006CFE0: 0x8C430000,
        0x8006CFE4: 0x00641823,
        0x8006CFE8: 0xAC430000,
        0x8006D274: 0x8C420000,
        0x8006D278: 0x1C400134,
        0x8006D6C8: 0x8E230034,
        0x8006D6E0: 0x8C640078,
        0x8006D6E4: 0x8C65007C,
        0x8006D6E8: 0x8C660070,
        0x8006D6EC: 0x8C670074,
        0x8006D6F0: 0x0C019645,

        0x800C73BC: 0x96020006, 0x800C73C0: 0x10430032,
        0x800C73B8: 0x3403FFFF, 0x800C7490: 0x8C437CE4,
        0x800C7494: 0x02003821, 0x800C7498: 0x00031880,
        0x800C749C: 0x00671821, 0x800C74A0: 0x8C62006C,
        0x800C74A4: 0x00521023, 0x800C74A8: 0x00408821,
        0x800C74AC: 0xAC71006C, 0x800C74B0: 0x94E30000,
        0x800C74B4: 0x24020014, 0x800C74B8: 0x1462000C,
        0x800C74BC: 0x02201021, 0x800C74C0: 0x8CE20080,
        0x800C74C4: 0xAFA20010, 0x800C74C8: 0x8CE20084,
        0x800C74CC: 0xAFA20014, 0x800C74D0: 0x8CE40078,
        0x800C74D4: 0x8CE5007C, 0x800C74D8: 0x8CE60070,
        0x800C74DC: 0x8CE70074, 0x800C74E0: 0x0C019645,
        0x800C74E4: 0,
        0x80065928: 0xA045FFFF, 0x8006592C: 0x10C00008,
        0x80065934: 0x24428060, 0x80065938: 0x24C3FFFF,
        0x8006593C: 0x00031880, 0x80065940: 0x00621821,
        0x80065944: 0x8C620000, 0x80065948: 0x00471021,
        0x8006594C: 0xAC620000,
        0x800C75B4: 0x9042FFFF, 0x800C763C: 0x8C420000,
        0x80102D14: 0x0C031D67, 0x80102D18: 0x24040004,
        0x80102D1C: 0x18400016, 0x80102D30: 0x0C031DCE,
        0x80102D78: 0x0C031D67, 0x80102D7C: 0x24040012,
        0x80102D80: 0x18400010, 0x80102D98: 0x0C031DCE,
        0x80102DC4: 0x0C031D87, 0x80102DC8: 0x24040016,
        0x80102DCC: 0x1840000C, 0x80102DEC: 0x0C031DDB,
        0x80102E00: 0x0C031D67, 0x80102E04: 0x24040015,
        0x80102E08: 0x1840000C, 0x80102E1C: 0x0C031DCE,
        0x800C7754: 0x34420004, 0x800C7788: 0x34420008,
        0x80103534: 0x2404001B, 0x8010353C: 0x0C031D87,
        0x80103544: 0x2404001C, 0x80103548: 0x0C031D87,
        0x80103554: 0x02028021, 0x80103558: 0x24040064,
        0x8010355C: 0x00902023, 0x80103560: 0x0C031DEC,
    }
    for pc, expected in instructions.items():
        actual = elf_word(elf, pc)
        if actual != expected:
            raise ValueError(f'level3 contract at {pc:08x}: expected {expected:08x}, got {actual:08x}')
    by_name = {r['name']: r for r in rows if r['kind'] == 0 and r['name']}
    for name, offset, subtype, health, effect in (
        ('City_1', '0000048c', 0x14, 2000, (28, 1, 0, 0, 0, 1)),
        ('GVT_BLDG_main', '00001548', 0x14, 6000, (28, 1, 4, 1, 0, 1)),
        ('Tech_Center_Main', '0000391c', 0x14, 5000, (7, 1, 18, 1, 0, 1)),
        ('Madine_Shuttle', '00007788', 0x24, 200, (0, 0, 21, 1, 0, 1)),
    ):
        row = by_name[name]
        fields = tuple(row['damage_effect' if subtype == 0x14 else 'death'][key]
                       for key in ('counter', 'delta', 'boolean', 'value', 'counter2', 'delta2'))
        actual = (row['offset'], row['subtype'], row['health_detail0' if subtype == 0x14 else 'health'], fields)
        if actual != (offset, subtype, health, effect):
            raise ValueError(f'level3 DAT contract changed for {name}: {actual}')
    candidates = [r for r in rows if r['kind'] == 0 and r['subtype'] == 0x14
                  and r['damage_effect']['counter'] == 28 and r['damage_effect']['delta'] == 1
                  and r['damage_effect']['boolean'] == r['damage_effect']['value'] == r['damage_effect']['counter2'] == 0]
    selected = by_name['City_1']
    if selected not in candidates:
        raise ValueError('City_1 must be a counter-only candidate')
    return dict(
        scope='static retail DAT and original ELF; no live response qualification',
        instruction_checks={f'{pc:08x}': f'{value:08x}' for pc, value in instructions.items()},
        callback=dict(loss_booleans=[4, 18, 21], success_counter=22,
                      friendlies_saved='100-(counter27+counter28)'),
        writer=dict(counter_pc='8006594c', boolean_pc='80065928'),
        route=dict(function='800c7390', branch='800c748c', effect_call='800c74e0',
                   condition='DAT runtime halfword +6 == 0xffff and subtype == 0x14',
                   health_gate=False,
                   limitation='Registered handler8006CBB0 subtracts message+6 at8006CFE8, but bgtz8006D278 skips effect8006D6F0 while health is positive; live route still needs observation'),
        selected=selected, candidates=candidates,
        excluded_controls=[by_name[n] for n in ('GVT_BLDG_main', 'Tech_Center_Main', 'Madine_Shuttle')],
        next_measurement='Join one ordinary named City_1 hit to its actual slot/handler, health, counter28 store and friendlies reader; no lethal dose assumed')


def wingman_instructions():
    return {
        0x80065510: 0x3C04800E, 0x80065514: 0x248493C0, 0x80065518: 0x02202821,
        0x8006551C: 0x24060002, 0x80065520: 0x08019599, 0x80065524: 0x2407005A,
        0x80065664: 0x0C00FFFB, 0x80065668: 0x00000000, 0x8006566C: 0x00401821,
        0x80065670: 0x3070FFFF, 0x80065674: 0x3C018004, 0x80065678: 0xC420BED4,
        0x8006567C: 0x3402FFFF, 0x80065680: 0x12020006, 0x80065684: 0xE7A00010,
        0x80065688: 0xA6230006, 0x8006568C: 0x02002021, 0x80065690: 0x24050003,
        0x80065694: 0x0C00FA37, 0x80065698: 0x27A60010, 0x800D93C0: 0x27BDFF70,
        0x800D93C4: 0xAFB3007C, 0x800D93C8: 0x00809821, 0x800D93CC: 0xAFB10074,
        0x800D93D0: 0xAFB20078, 0x800D93D4: 0x00A09021, 0x800D93D8: 0x3242FFFF,
        0x800D93DC: 0x2443FFFF, 0x800D93E0: 0x2C62000B, 0x800D93E4: 0xAFBF0084,
        0x800D93E8: 0xAFB40080, 0x800D93EC: 0xAFB00070, 0x800D93F0: 0xF7B40088,
        0x800D93F4: 0x8E700004, 0x800D93F8: 0x104002DB, 0x800D93FC: 0x00C08821,
        0x800D9400: 0x3C02800A, 0x800D9404: 0x24427A00, 0x800D9408: 0x00031880,
        0x800D940C: 0x00621821, 0x800D9410: 0x8C620000, 0x800D9414: 0x00400008,
        0x800D9418: 0x00000000, 0x800D94AC: 0xAE020030, 0x800D94B0: 0xAE110034,
        0x800D7850: 0x27BDFFD8, 0x800D7854: 0x00002821, 0x800D7858: 0xAFBF0020,
        0x800D785C: 0xAFB1001C, 0x800D7860: 0xAFB00018, 0x800D7864: 0x8C900004,
        0x800D7868: 0x24060030, 0x800D786C: 0x8E110034, 0x800D7870: 0x0C001E38,
        0x800D7874: 0x26040068, 0x800D7878: 0x8E040038, 0x800D787C: 0x2625006C,
        0x800D7880: 0x0C03C81C, 0x800D7884: 0x02203021, 0x800D7888: 0x18400012,
        0x800D9BB0: 0x8E040038, 0x800D9BB4: 0x0C03C83B, 0x800D9BB8: 0x02209021,
        0x800D9BBC: 0x18400060, 0x800D9BC0: 0x00000000, 0x800D9C4C: 0x8E040038,
        0x800D9C50: 0x96450006, 0x800D9C54: 0x0C03C848, 0x800D9C58: 0x00000000,
        0x800D9C5C: 0x1C400038, 0x800D9C60: 0x3C05800A, 0x800D9D00: 0x8E030034,
        0x800D9D04: 0x8C620080, 0x800D9D08: 0xAFA20010, 0x800D9D0C: 0x8E020034,
        0x800D9D10: 0x8C420084, 0x800D9D14: 0xAFA20014, 0x800D9D18: 0x8C640078,
        0x800D9D1C: 0x8C65007C, 0x800D9D20: 0x8C660070, 0x800D9D24: 0x8C670074,
        0x800D9D28: 0x0C019645, 0x800D9D2C: 0x00000000, 0x800F20EC: 0x908201A7,
        0x800F20F0: 0x14400008, 0x800F20F4: 0x3C028013, 0x800F20F8: 0x8C427CE4,
        0x800F20FC: 0x8C830190, 0x800F2100: 0x00021080, 0x800F2104: 0x00431021,
        0x800F2108: 0x8C420000, 0x800F210C: 0x03E00008, 0x800F2110: 0x00000000,
        0x800F2114: 0x8C820190, 0x800F2118: 0x03E00008, 0x800F211C: 0x00000000,
        0x800F2120: 0x908201A7, 0x800F2124: 0x14400009, 0x800F2128: 0x3C028013,
        0x800F212C: 0x8C437CE4, 0x800F2130: 0x8C820190, 0x800F2134: 0x00031880,
        0x800F2138: 0x00621821, 0x800F213C: 0x8C620000, 0x800F2140: 0x00451023,
        0x800F2144: 0x03E00008, 0x800F2148: 0xAC620000, 0x800F214C: 0x8C820190,
        0x800F2150: 0x00451023, 0x800F2154: 0x03E00008, 0x800F2158: 0xAC820190,
        0x80065914: 0x8FA80010, 0x80065918: 0x10800004, 0x8006591C: 0x3C028014,
        0x80065920: 0x244288A0, 0x80065924: 0x00821021, 0x80065928: 0xA045FFFF,
        0x8006592C: 0x10C00008, 0x80065930: 0x3C028014, 0x80065934: 0x24428060,
        0x80065938: 0x24C3FFFF, 0x8006593C: 0x00031880, 0x80065940: 0x00621821,
        0x80065944: 0x8C620000, 0x80065948: 0x00471021, 0x8006594C: 0xAC620000,
        0x80065950: 0x11000009, 0x80065954: 0x3C028014, 0x80065958: 0x24428060,
        0x8006595C: 0x2503FFFF, 0x80065960: 0x00031880, 0x80065964: 0x00621821,
        0x80065968: 0x8C620000, 0x8006596C: 0x8FA40014, 0x80065970: 0x00441021,
        0x80065974: 0xAC620000, 0x800C73B8: 0x3403FFFF, 0x800C73BC: 0x96020006,
        0x800C73C0: 0x10430032, 0x800C73C4: 0x24020007, 0x800C73C8: 0xA7A2001C,
        0x800C73CC: 0x0072102A, 0x800C73D0: 0xA7A30018, 0x800C73D4: 0x14400003,
        0x800C73D8: 0xA7A3001A, 0x800C73DC: 0x08031CFB, 0x800C73E0: 0xA7B2001E,
        0x800C73E4: 0x2402FFFF, 0x800C73E8: 0xA7A2001E, 0x800C73EC: 0x24050005,
        0x800C73F0: 0xAFA00020, 0x800C73F4: 0x96040006, 0x800C73F8: 0x0C00FA37,
        0x800C73FC: 0x27A60018, 0x8003BE24: 0x80065510, 0x800A7A10: 0x800D9BB0,
        0x800C7754: 0x34420004, 0x800C7788: 0x34420008,
    }


def level4_contract(elf, rows):
    instructions = {
        0x80103720: 0x27BDFFE8, 0x80103724: 0x24040010, 0x80103728: 0xAFBF0014,
        0x8010372C: 0x0C031D87, 0x80103730: 0xAFB00010, 0x80103734: 0x28420003,
        0x80103738: 0x14400003, 0x8010373C: 0x00000000, 0x80103740: 0x0C031DCE,
        0x80103744: 0x00000000, 0x80103748: 0x0C031D87, 0x8010374C: 0x2404000F,
        0x80103750: 0x28420003, 0x80103754: 0x14400003, 0x80103758: 0x00000000,
        0x8010375C: 0x0C031DCE, 0x80103760: 0x00000000, 0x80103764: 0x0C031D87,
        0x80103768: 0x2404001C, 0x8010376C: 0x1840000B, 0x80103770: 0x3C028011,
        0x80103774: 0x8C43D060, 0x80103778: 0x24020001, 0x8010377C: 0x14620007,
        0x80103780: 0x00000000, 0x80103784: 0x0C031DDB, 0x80103788: 0x00000000,
        0x8010378C: 0x0C031DAC, 0x80103790: 0x24040001, 0x80103794: 0x0C031DAC,
        0x80103798: 0x24040002, 0x8010379C: 0x0C031D67, 0x801037A0: 0x2404000C,
        0x801037A4: 0x00408021, 0x801037A8: 0x24020001, 0x801037AC: 0x1602000F,
        0x801037B0: 0x00000000, 0x801037B4: 0x0C031D67, 0x801037B8: 0x24040020,
        0x801037BC: 0x00401821, 0x801037C0: 0x1470000A, 0x801037C4: 0x3C068011,
        0x801037C8: 0x8CC2D064, 0x801037CC: 0x14400007, 0x801037D0: 0x24040031,
        0x801037D4: 0x3C054000, 0x801037D8: 0x0C031F47, 0x801037DC: 0xACC3D064,
        0x801037E0: 0x3C053F00, 0x801037E4: 0x0C031F47, 0x801037E8: 0x24040143,
        0x801037EC: 0x0C031D87, 0x801037F0: 0x2404001D, 0x801037F4: 0x28420003,
        0x801037F8: 0x1440000C, 0x801037FC: 0x00000000, 0x80103800: 0x0C031D87,
        0x80103804: 0x2404001E, 0x80103808: 0x28420003, 0x8010380C: 0x14400007,
        0x80103810: 0x3C038011, 0x80103814: 0x8C62D068, 0x80103818: 0x14400004,
        0x8010381C: 0x24020001, 0x80103820: 0xAC62D068, 0x80103824: 0x0C031F3E,
        0x80103828: 0x24040007, 0x8010382C: 0x0C031D67, 0x80103830: 0x2404001A,
        0x80103834: 0x00401821, 0x80103838: 0x24020001, 0x8010383C: 0x14620008,
        0x80103840: 0x3C048011, 0x80103844: 0x8C82D074, 0x80103848: 0x14400005,
        0x8010384C: 0x00000000, 0x80103850: 0x0C031DCE, 0x80103854: 0xAC83D074,
        0x80103858: 0x0C031F3E, 0x8010385C: 0x2404000C, 0x80103860: 0x0C031D67,
        0x80103864: 0x2404000C, 0x80103868: 0x14400012, 0x8010386C: 0x00000000,
        0x80103870: 0x0C031D87, 0x80103874: 0x2404001F, 0x80103878: 0x00401821,
        0x8010387C: 0x24020001, 0x80103880: 0x1462000C, 0x80103884: 0x3C108011,
        0x80103888: 0x8E02D06C, 0x8010388C: 0x14430009, 0x80103890: 0x00000000,
        0x80103894: 0x3C053F80, 0x80103898: 0x0C031F47, 0x8010389C: 0x2404000B,
        0x801038A0: 0x3C048010, 0x801038A4: 0x3C0540A0, 0x801038A8: 0x0C031E19,
        0x801038AC: 0x24843C30, 0x801038B0: 0xAE00D06C, 0x801038B4: 0x0C031D67,
        0x801038B8: 0x2404000C, 0x801038BC: 0x1440000E, 0x801038C0: 0x00000000,
        0x801038C4: 0x0C031D87, 0x801038C8: 0x2404001F, 0x801038CC: 0x24030002,
        0x801038D0: 0x14430009, 0x801038D4: 0x3C068011, 0x801038D8: 0x8CC3D070,
        0x801038DC: 0x24020001, 0x801038E0: 0x14620005, 0x801038E4: 0x3C048010,
        0x801038E8: 0x3C054000, 0x801038EC: 0x24843C50, 0x801038F0: 0x0C031E19,
        0x801038F4: 0xACC0D070, 0x801038F8: 0x0C031D67, 0x801038FC: 0x2404000C,
        0x80103900: 0x1440000E, 0x80103904: 0x00000000, 0x80103908: 0x0C031D87,
        0x8010390C: 0x2404001F, 0x80103910: 0x24030003, 0x80103914: 0x14430009,
        0x80103918: 0x3C038011, 0x8010391C: 0x8C62D078, 0x80103920: 0x14400006,
        0x80103924: 0x3C048010, 0x80103928: 0x24843C74, 0x8010392C: 0x3C054000,
        0x80103930: 0x24020001, 0x80103934: 0x0C031E19, 0x80103938: 0xAC62D078,
        0x8010393C: 0x0C031D67, 0x80103940: 0x2404000C, 0x80103944: 0x1440000E,
        0x80103948: 0x00000000, 0x8010394C: 0x0C031D87, 0x80103950: 0x2404001F,
        0x80103954: 0x24030005, 0x80103958: 0x14430009, 0x8010395C: 0x3C038011,
        0x80103960: 0x8C62D07C, 0x80103964: 0x14400006, 0x80103968: 0x3C048010,
        0x8010396C: 0x24843C98, 0x80103970: 0x3C054000, 0x80103974: 0x24020001,
        0x80103978: 0x0C031E19, 0x8010397C: 0xAC62D07C, 0x80103980: 0x8FBF0014,
        0x80103984: 0x8FB00010, 0x80103988: 0x00001021, 0x8010398C: 0x03E00008,
        0x80103990: 0x27BD0018, 0x80103CC4: 0x27BDFFE8, 0x80103CC8: 0x24040028,
        0x80103CCC: 0xAFBF0014, 0x80103CD0: 0x0C031D87, 0x80103CD4: 0xAFB00010,
        0x80103CD8: 0x2404000F, 0x80103CDC: 0x0C031D87, 0x80103CE0: 0x00408021,
        0x80103CE4: 0x02028021, 0x80103CE8: 0x24040006, 0x80103CEC: 0x0C031DEC,
        0x80103CF0: 0x00902023, 0x80103CF4: 0x8FBF0014, 0x80103CF8: 0x8FB00010,
        0x80103CFC: 0x00001021, 0x80103D00: 0x03E00008, 0x80103D04: 0x27BD0018,
        **wingman_instructions(),
    }
    for pc, expected in instructions.items():
        if elf_word(elf, pc) != expected:
            raise ValueError(f'level4 original instruction changed at {pc:08x}')
    by_name = {r['name']: r for r in rows if r['kind'] == 0 and r['name']}
    expected = (
        ('x_wing_hobbie', '00006a7c', 400, (40, 1, 0, 0, 0, 1)),
        ('x_wing_dack', '00006e08', 9999, (40, 1, 0, 0, 0, 1)),
        ('x_wing_corpselighter', '00006f08', 300, (40, 1, 0, 0, 0, 1)),
        ('Y_Wing_uno', '000062f4', 180, (15, 1, 5, 1, 0, 1)),
        ('Y_Wing_dos', '00006888', 300, (15, 1, 6, 1, 0, 1)),
        ('Y_Wing_tres', '00006980', 300, (15, 1, 7, 1, 0, 1)),
    )
    for name, offset, hp, effect in expected:
        row = by_name[name]
        actual = (row['offset'], row['subtype'], row['words']['6c'],
                  tuple(row['words'][f'{p:02x}'] for p in range(0x70, 0x88, 4)))
        if actual != (offset, 0x27, hp, effect):
            raise ValueError(f'level4 DAT contract changed for {name}: {actual}')
    candidates = [by_name[n] for n, _, _, effect in expected if effect[0] == 40]
    return dict(
        scope='original static contract; live ownership, damage and objective response unqualified',
        instruction_checks={f'{pc:08x}': f'{value:08x}' for pc, value in instructions.items()},
        callback=dict(friendlies_saved='6-(counter40+counter15)',
                      failure=['counter16>=3', 'counter15>=3', 'boolean26==1'],
                      success='counter28>0 and word8010D060==1',
                      counter_reads=[16, 15, 28, 29, 30, 31], boolean_reads=[12, 32, 26],
                      historical_ids=dict(id15='named loss', id5='not read as a counter; Y_Wing_uno writes Boolean5')),
        route=dict(subtype=0x27, setup='80065510', handler='800d93c0',
                   message5_table='800a7a10', message5='800d9bb0',
                   payload='node+4', descriptor='payload+0x34', actor='payload+0x38',
                   health_detail0='DAT+0x6c',
                   health_storage='actor+0x190 is detail-array pointer when actor+0x1a7==0, otherwise inline health',
                   damage_call='800d9c54', damage_writer=['800f2148', '800f2158'],
                   health_gate='prehealth>0 at800d9bbc; damage return<=0 at800d9c5c',
                   effect_call='800d9d28', counter_writer='8006594c', boolean_writer='80065928',
                   effect_tuple_order='counter,delta,boolean,value,counter2,delta2',
                   selected_effect=[40, 1, 0, 0, 0, 1],
                   limitation='Original named API selects registered message5; FFFF fallback is not this route. Live identity and detail must be observed.'),
        selected=by_name['x_wing_hobbie'], candidates=candidates,
        excluded_controls=[by_name[n] for n in ('Y_Wing_uno', 'Y_Wing_dos', 'Y_Wing_tres')],
        exclusions='Y-wings use counter15 plus Booleans5/6/7; yachts set failure Boolean26; SAM2 raw effect word+0x78 is28, distinct from counter word+0x70; its subtype is not qualified here. Unknown subtypes stay raw.',
        next_measurement='One original named API request10 on owned x_wing_hobbie; join slot/gen/node/payload/DAT/actor, message5, health writer/return and counter40 getter. No lethal dose.')


def level5_contract(elf, rows):
    instructions = {
        **wingman_instructions(),
        0x80104118: 0x27BDFFE8, 0x8010411C: 0x24040028, 0x80104120: 0xAFBF0014,
        0x80104124: 0x0C031D87, 0x80104128: 0xAFB00010, 0x8010412C: 0x24040002,
        0x80104130: 0x0C031D87, 0x80104134: 0x00408021, 0x80104138: 0x02028021,
        0x8010413C: 0x24040007, 0x80104140: 0x0C031DEC, 0x80104144: 0x00902023,
        0x80104148: 0x8FBF0014, 0x8010414C: 0x8FB00010, 0x80104150: 0x00001021,
        0x80104154: 0x03E00008, 0x80104158: 0x27BD0018, 0x8010415C: 0x27BDFFE0,
        0x80104160: 0xAFBF0010, 0x80104164: 0xF7B40018, 0x80104168: 0x0C031D87,
        0x8010416C: 0x24040002, 0x80104170: 0x28420004, 0x80104174: 0x14400011,
        0x80104178: 0x3C038011, 0x8010417C: 0x8C62D080, 0x80104180: 0x1440000E,
        0x80104184: 0x24020001, 0x80104188: 0x3C01800B, 0x8010418C: 0xC4349754,
        0x80104190: 0x0C031DCE, 0x80104194: 0xAC62D080, 0x80104198: 0x4405A000,
        0x8010419C: 0x0C031F47, 0x801041A0: 0x24040011, 0x801041A4: 0x4405A000,
        0x801041A8: 0x0C031F47, 0x801041AC: 0x240400DD, 0x801041B0: 0x3C053F00,
        0x801041B4: 0x0C031F47, 0x801041B8: 0x2404014B, 0x801041BC: 0x0C031D87,
        0x801041C0: 0x24040004, 0x801041C4: 0x28420009, 0x801041C8: 0x1440000A,
        0x801041CC: 0x3C038011, 0x801041D0: 0x8C62D084, 0x801041D4: 0x14400007,
        0x801041D8: 0x24020001, 0x801041DC: 0x0C031DDB, 0x801041E0: 0xAC62D084,
        0x801041E4: 0x0C031DAC, 0x801041E8: 0x24040001, 0x801041EC: 0x0C031DAC,
        0x801041F0: 0x24040003, 0x801041F4: 0x8FBF0010, 0x801041F8: 0xD7B40018,
        0x801041FC: 0x00001021, 0x80104200: 0x03E00008, 0x80104204: 0x27BD0020,
        0x800F2070: 0x908201A7, 0x800F2074: 0x1440000E, 0x800F2078: 0x00C03821,
        0x800F207C: 0xAC850190, 0x800F2080: 0x8CC30054, 0x800F2084: 0x3C028000,
        0x800F2088: 0x14620006, 0x800F208C: 0x3C028013, 0x800F2090: 0x8C427CE4,
        0x800F2094: 0x00021080, 0x800F2098: 0x00451021, 0x800F209C: 0x8C420000,
        0x800F20A0: 0xACC20054, 0x800F20A4: 0x8CE20054, 0x800F20A8: 0x0803C834,
        0x800F20AC: 0xAC820194, 0x800F20B0: 0x3C028013, 0x800F20B4: 0x8C427CE4,
        0x800F20B8: 0x00021080, 0x800F20BC: 0x00451021, 0x800F20C0: 0x8C430000,
        0x800F20C4: 0xAC830190, 0x800F20C8: 0x8C420000, 0x800F20CC: 0xAC820194,
        0x800F20D0: 0x3C028013, 0x800F20D4: 0x8C427CE4, 0x800F20D8: 0x00021080,
        0x800F20DC: 0x00451021, 0x800F20E0: 0x8C420000, 0x800F20E4: 0x03E00008,
        0x800F20E8: 0x00000000, 0x800D9BB0: 0x8E040038, 0x800D9BB4: 0x0C03C83B,
        0x800D9BB8: 0x02209021, 0x800D9BBC: 0x18400060, 0x800D9BC0: 0x00000000,
        0x800D9BC4: 0x0C01D894, 0x800D9BC8: 0x02202021, 0x800D9BCC: 0x920200F4,
        0x800D9BD0: 0x54400011, 0x800D9BD4: 0xA20000F4, 0x800D9BD8: 0x00002021,
        0x800D9BDC: 0x02002821, 0x800D9BE0: 0x26060024, 0x800D9BE4: 0x3C074160,
        0x800D9BE8: 0x3C01800A, 0x800D9BEC: 0xC4207AB4, 0x800D9BF0: 0x2402001B,
        0x800D9BF4: 0xAFA20018, 0x800D9BF8: 0x2402007E, 0x800D9BFC: 0xAFA2001C,
        0x800D9C00: 0x2402005A, 0x800D9C04: 0xAFA00014, 0x800D9C08: 0xAFA20020,
        0x800D9C0C: 0x0C026276, 0x800D9C10: 0xE7A00010, 0x800D9C14: 0xA20000F4,
        0x800D9C18: 0x96230000, 0x800D9C1C: 0x3402FFFF, 0x800D9C20: 0x1062000A,
        0x800D9C24: 0x00000000, 0x800D9C28: 0x0C01B265, 0x800D9C2C: 0x00002021,
        0x800D9C30: 0x96230002, 0x800D9C34: 0x3042FFFF, 0x800D9C38: 0x10620004,
        0x800D9C3C: 0x02002021, 0x800D9C40: 0x00002821, 0x800D9C44: 0x0C03602D,
        0x800D9C48: 0x00003021, 0x800D9C4C: 0x8E040038, 0x800D9C50: 0x96450006,
        0x800D9C54: 0x0C03C848, 0x800D9C58: 0x00000000, 0x800D9C5C: 0x1C400038,
        0x800D9C60: 0x3C05800A, 0x800D9C64: 0x24A57834, 0x800D9C68: 0x00003021,
        0x800D9C6C: 0xAFA00010, 0x800D9C70: 0xAFA00014, 0x800D9C74: 0x8E040030,
        0x800D9C78: 0x0C0160D8, 0x800D9C7C: 0x27A70040, 0x800D9C80: 0x02002021,
        0x800D9C84: 0x00002821, 0x800D9C88: 0xC7A00044, 0x800D9C8C: 0xC6020004,
        0x800D9C90: 0x24060003, 0x800D9C94: 0x46020001, 0x800D9C98: 0x24020002,
        0x800D9C9C: 0xA202005C, 0x800D9CA0: 0x0C03602D, 0x800D9CA4: 0xE6000058,
        0x800D9CA8: 0x0C036262, 0x800D9CAC: 0x02002021, 0x800D9CB0: 0x96040048,
        0x800D9CB4: 0x0C00F9F4, 0x800D9CB8: 0x02602821, 0x800D9CBC: 0x9604004A,
        0x800D9CC0: 0x0C00F9F4, 0x800D9CC4: 0x02602821, 0x800D9CC8: 0x9604004C,
        0x800D9CCC: 0x0C00F9F4, 0x800D9CD0: 0x02602821, 0x800D9CD4: 0x9603004E,
        0x800D9CD8: 0x3402FFFF, 0x800D9CDC: 0x10620005, 0x800D9CE0: 0x3C028014,
        0x800D9CE4: 0x00602021, 0x800D9CE8: 0x0C00F9F4, 0x800D9CEC: 0x02602821,
        0x800D9CF0: 0x3C028014, 0x800D9CF4: 0x94449574, 0x800D9CF8: 0x0C00F9A1,
        0x800D9CFC: 0x02602821, 0x800D9D00: 0x8E030034, 0x800D9D04: 0x8C620080,
        0x800D9D08: 0xAFA20010, 0x800D9D0C: 0x8E020034, 0x800D9D10: 0x8C420084,
        0x800D9D14: 0xAFA20014, 0x800D9D18: 0x8C640078, 0x800D9D1C: 0x8C65007C,
        0x800D9D20: 0x8C660070, 0x800D9D24: 0x8C670074, 0x800D9D28: 0x0C019645,
        0x800D9D2C: 0x00000000, 0x800D9D30: 0x0C03CC98, 0x800C761C: 0x14800003,
        0x800C762C: 0x24638060, 0x800C7630: 0x2482FFFF, 0x800C7634: 0x00021080,
        0x800C7620: 0x3C038014, 0x800C7624: 0x03E00008, 0x800C7628: 0x00001021,
        0x800C7638: 0x00431021, 0x800C763C: 0x8C420000, 0x800C7640: 0x03E00008,
        0x800C7644: 0x00000000,
    }
    for pc, expected in instructions.items():
        if elf_word(elf, pc) != expected:
            raise ValueError(f'level5 original instruction changed at {pc:08x}')
    by_name = {r['name']: r for r in rows if r['kind'] == 0 and r['name']}
    expected = (
        ('x_wing_kasan', '000019f4', 0x27, 9999, (40, 1, 0, 0, 0, 1)),
        ('x_wing_wedge', '00001afc', 0x27, 200, (40, 1, 0, 0, 0, 1)),
        ('x_wing_rogue_meat', '00001c04', 0x27, 100, (40, 1, 0, 0, 0, 1)),
        ('Reb_combat1', '00002070', 0x2e, 125, (2, 1, 21, 1, 0, 1)),
        ('Reb_combat2', '00002170', 0x2e, 125, (2, 1, 22, 1, 0, 1)),
        ('Reb_combat3', '00002270', 0x2e, 125, (2, 1, 23, 1, 0, 1)),
        ('Reb_combat4', '00002370', 0x2e, 125, (2, 1, 24, 1, 0, 1)),
    )
    for name, offset, subtype, hp, effect in expected:
        row = by_name[name]
        actual = (row['offset'], row['subtype'], row['words']['6c'],
                  tuple(row['words'][f'{p:02x}'] for p in range(0x70, 0x88, 4)))
        if actual != (offset, subtype, hp, effect):
            raise ValueError(f'level5 DAT contract changed for {name}: {actual}')
    return dict(
        scope='static retail DAT and original ELF only; no live availability or response qualification',
        instruction_checks={f'{pc:08x}': f'{value:08x}' for pc, value in instructions.items()},
        callback=dict(reader='80104118', callback='8010415c',
                      friendlies_saved='7-(counter40+counter2)',
                      counter_reads=[2, 4], failure='counter2>=4 and word8010D080==0 -> Bit4',
                      success='counter4>=9 and word8010D084==0 -> Bit8, Booleans1/3=1',
                      historical_id2='named friendly-loss arithmetic and failure threshold; historical writer not proven'),
        route=dict(subtype=0x27, setup='80065510', handler='800d93c0',
                   message5_table='800a7a10', message5='800d9bb0',
                   payload='node+4', descriptor='payload+0x34', actor='payload+0x38',
                   initialization='800d7880 calls800f2070 with DAT+0x6c and actor',
                   health_detail0='DAT+0x6c; actual live detail must be observed',
                   health_storage='actor+0x190 is detail-array pointer when actor+0x1a7==0, otherwise inline health',
                   damage_call='800d9c54', damage_writer=['800f2148', '800f2158'],
                   health_gate='prehealth>0 at800d9bbc; damage return<=0 at800d9c5c',
                   effect_call='800d9d28', counter_writer='8006594c', boolean_writer='80065928',
                   selected_effect=[40, 1, 0, 0, 0, 1],
                   effect_tuple_order='counter,delta,boolean,value,counter2,delta2',
                   limitation='Original named API registered message5 only; FFFF fallback differs. No live handler, identity, health or detail assumed.'),
        selected=by_name['x_wing_wedge'],
        candidates=[by_name[n] for n, _, st, _, _ in expected if st == 0x27],
        excluded_controls=[by_name[n] for n, _, st, _, _ in expected if st == 0x2e],
        exclusions='Reb_combat1..4 raw +0x70 tuples couple counter2 with Booleans21..24; their subtype0x2e damage/effect route is not qualified. No historical id2 writer attribution. Counter4 success targets excluded. Unknown layouts remain raw.',
        next_measurement='One original named API request10 on owned x_wing_wedge; join slot/gen/node/payload/DAT/actor, message5, health writer/return, counter40 original getter and friendlies arithmetic. No lethal dose.')


def level6_contract(elf, rows):
    instructions = {
        0x8003BDD8: 0x800653F4, 0x8003CA30: 0x8006CF88, 0x80046878: 0xAC82000C,
        0x80046DBC: 0xAC5275D8, 0x80047B50: 0x8C4475D8, 0x80047B5C: 0x0C011EDC,
        0x800653B4: 0x27BDFFD8, 0x800653B8: 0xAFB1001C, 0x800653BC: 0x00808821,
        0x800653C0: 0xAFBF0020, 0x800653C4: 0xAFB00018, 0x800653C8: 0x96220000,
        0x800653CC: 0x2443FFF4, 0x800653D0: 0x2C620047, 0x800653D4: 0x1040009E,
        0x800653D8: 0x3C028004, 0x800653DC: 0x2442BDB8, 0x800653E0: 0x00031880,
        0x800653E4: 0x00621821, 0x800653E8: 0x8C620000, 0x800653EC: 0x00400008,
        0x800653F0: 0x00000000, 0x800653F4: 0x3C048007, 0x800653F8: 0x2484CBB0,
        0x800653FC: 0x02202821, 0x80065400: 0x24070028, 0x80065404: 0x9622008A,
        0x80065408: 0x24060003, 0x8006540C: 0x00C23023, 0x80065410: 0x00063180,
        0x80065414: 0x34C60001, 0x80065418: 0x08019599, 0x8006541C: 0x30C6FFC1,
        0x80065664: 0x0C00FFFB, 0x80065668: 0x00000000, 0x8006566C: 0x00401821,
        0x80065670: 0x3070FFFF, 0x80065674: 0x3C018004, 0x80065678: 0xC420BED4,
        0x8006567C: 0x3402FFFF, 0x80065680: 0x12020006, 0x80065684: 0xE7A00010,
        0x80065688: 0xA6230006, 0x8006568C: 0x02002021, 0x80065690: 0x24050003,
        0x80065694: 0x0C00FA37, 0x80065698: 0x27A60010, 0x80065914: 0x8FA80010,
        0x80065918: 0x10800004, 0x8006591C: 0x3C028014, 0x80065920: 0x244288A0,
        0x80065924: 0x00821021, 0x80065928: 0xA045FFFF, 0x8006592C: 0x10C00008,
        0x80065930: 0x3C028014, 0x80065934: 0x24428060, 0x80065938: 0x24C3FFFF,
        0x8006593C: 0x00031880, 0x80065940: 0x00621821, 0x80065944: 0x8C620000,
        0x80065948: 0x00471021, 0x8006594C: 0xAC620000, 0x80065950: 0x11000009,
        0x80065954: 0x3C028014, 0x80065958: 0x24428060, 0x8006595C: 0x2503FFFF,
        0x80065960: 0x00031880, 0x80065964: 0x00621821, 0x80065968: 0x8C620000,
        0x8006596C: 0x8FA40014, 0x80065970: 0x00441021, 0x80065974: 0xAC620000,
        0x80065978: 0x03E00008, 0x8006597C: 0x00000000, 0x8006CBB0: 0x27BDFF20,
        0x8006CBB4: 0xAFB500AC, 0x8006CBB8: 0x0080A821, 0x8006CBBC: 0xAFB00098,
        0x8006CBC0: 0x30A5FFFF, 0x8006CBC4: 0x24A3FFFF, 0x8006CBC8: 0x2C62000B,
        0x8006CBCC: 0xAFBF00B4, 0x8006CBD0: 0xAFB600B0, 0x8006CBD4: 0xAFB400A8,
        0x8006CBD8: 0xAFB300A4, 0x8006CBDC: 0xAFB200A0, 0x8006CBE0: 0xAFB1009C,
        0x8006CBE4: 0xF7BC00D8, 0x8006CBE8: 0xF7BA00D0, 0x8006CBEC: 0xF7B800C8,
        0x8006CBF0: 0xF7B600C0, 0x8006CBF4: 0xF7B400B8, 0x8006CBF8: 0x8EB10004,
        0x8006CBFC: 0x1040032F, 0x8006CC00: 0x00C08021, 0x8006CC04: 0x3C028004,
        0x8006CC08: 0x2442CA20, 0x8006CC0C: 0x00031880, 0x8006CC10: 0x00621821,
        0x8006CC14: 0x8C620000, 0x8006CC18: 0x00400008, 0x8006CC1C: 0x00000000,
        0x8006CC20: 0xAEB10008, 0x8006CC24: 0xAE300034, 0x8006CF88: 0x3C128013,
        0x8006CF8C: 0x8E230034, 0x8006CF90: 0x8E427CE4, 0x8006CF94: 0x2473006C,
        0x8006CF98: 0x00021080, 0x8006CF9C: 0x00531021, 0x8006CFA0: 0x8C420000,
        0x8006CFA4: 0x184001E9, 0x8006CFA8: 0x0200B021, 0x8006CFAC: 0x8C6200A0,
        0x8006CFB0: 0x10400007, 0x8006CFB4: 0x00000000, 0x8006CFB8: 0x0C01B265,
        0x8006CFBC: 0x00002021, 0x8006CFC0: 0x96030002, 0x8006CFC4: 0x3042FFFF,
        0x8006CFC8: 0x10620008, 0x8006CFCC: 0x00000000, 0x8006CFD0: 0x8E427CE4,
        0x8006CFD4: 0x96040006, 0x8006CFD8: 0x00021080, 0x8006CFDC: 0x00531021,
        0x8006CFE0: 0x8C430000, 0x8006CFE4: 0x00641823, 0x8006CFE8: 0xAC430000,
        0x8006D264: 0x3C028013, 0x8006D268: 0x8C427CE4, 0x8006D26C: 0x00021080,
        0x8006D270: 0x00531021, 0x8006D274: 0x8C420000, 0x8006D278: 0x1C400134,
        0x8006D27C: 0x00000000, 0x8006D6B8: 0x3C028013, 0x8006D6BC: 0x90420B39,
        0x8006D6C0: 0x54400012, 0x8006D6C4: 0x02A02021, 0x8006D6C8: 0x8E230034,
        0x8006D6CC: 0x8C620080, 0x8006D6D0: 0xAFA20010, 0x8006D6D4: 0x8E220034,
        0x8006D6D8: 0x8C420084, 0x8006D6DC: 0xAFA20014, 0x8006D6E0: 0x8C640078,
        0x8006D6E4: 0x8C65007C, 0x8006D6E8: 0x8C660070, 0x8006D6EC: 0x8C670074,
        0x8006D6F0: 0x0C019645, 0x8006D6F4: 0x00000000, 0x800C73B8: 0x3403FFFF,
        0x800C73BC: 0x96020006, 0x800C73C0: 0x10430032, 0x800C7490: 0x8C437CE4,
        0x800C7494: 0x02003821, 0x800C7498: 0x00031880, 0x800C749C: 0x00671821,
        0x800C74A0: 0x8C62006C, 0x800C74A4: 0x00521023, 0x800C74A8: 0x00408821,
        0x800C74AC: 0xAC71006C, 0x800C74B0: 0x94E30000, 0x800C74B4: 0x24020014,
        0x800C74B8: 0x1462000C, 0x800C74BC: 0x02201021, 0x800C74C0: 0x8CE20080,
        0x800C74C4: 0xAFA20010, 0x800C74C8: 0x8CE20084, 0x800C74CC: 0xAFA20014,
        0x800C74D0: 0x8CE40078, 0x800C74D4: 0x8CE5007C, 0x800C74D8: 0x8CE60070,
        0x800C74DC: 0x8CE70074, 0x800C74E0: 0x0C019645, 0x800C74E4: 0x00000000,
        0x800C75B4: 0x9042FFFF, 0x800C761C: 0x14800003, 0x800C7620: 0x3C038014,
        0x800C7624: 0x03E00008, 0x800C7628: 0x00001021, 0x800C762C: 0x24638060,
        0x800C7630: 0x2482FFFF, 0x800C7634: 0x00021080, 0x800C7638: 0x00431021,
        0x800C763C: 0x8C420000, 0x800C7640: 0x03E00008, 0x800C7644: 0x00000000,
        0x800C7754: 0x34420004, 0x800C7788: 0x34420008, 0x80104210: 0x27BDFFE8,
        0x80104214: 0x24040022, 0x80104218: 0xAFBF0014, 0x8010421C: 0x0C031D87,
        0x80104220: 0xAFB00010, 0x80104224: 0x24100001, 0x80104228: 0x14500007,
        0x8010422C: 0x00000000, 0x80104230: 0x0C031DCE, 0x80104234: 0x00000000,
        0x80104238: 0x0C031F3E, 0x8010423C: 0x24040065, 0x80104240: 0x080410E3,
        0x80104244: 0x00001021, 0x80104248: 0x0C031D87, 0x8010424C: 0x24040023,
        0x80104250: 0x1050FFF7, 0x80104254: 0x00000000, 0x80104258: 0x0C031D87,
        0x8010425C: 0x24040024, 0x80104260: 0x1050FFF3, 0x80104264: 0x00000000,
        0x80104268: 0x0C031D87, 0x8010426C: 0x24040025, 0x80104270: 0x1050FFEF,
        0x80104274: 0x00000000, 0x80104278: 0x0C031D87, 0x8010427C: 0x24040026,
        0x80104280: 0x1050FFEB, 0x80104284: 0x00000000, 0x80104288: 0x0C031D87,
        0x8010428C: 0x24040027, 0x80104290: 0x1050FFE7, 0x80104294: 0x00000000,
        0x80104298: 0x0C031D87, 0x8010429C: 0x24040062, 0x801042A0: 0x24030006,
        0x801042A4: 0x1443000F, 0x801042A8: 0x00000000, 0x801042AC: 0x0C031D67,
        0x801042B0: 0x24040062, 0x801042B4: 0x1440000B, 0x801042B8: 0x24040062,
        0x801042BC: 0x0C031D50, 0x801042C0: 0x24050001, 0x801042C4: 0x24040063,
        0x801042C8: 0x0C031D7B, 0x801042CC: 0x24050001, 0x801042D0: 0x24040064,
        0x801042D4: 0x0C031F47, 0x801042D8: 0x00002821, 0x801042DC: 0x0C031DAC,
        0x801042E0: 0x24040001, 0x801042E4: 0x0C031D87, 0x801042E8: 0x24040032,
        0x801042EC: 0x24030004, 0x801042F0: 0x1443000A, 0x801042F4: 0x00000000,
        0x801042F8: 0x0C031D67, 0x801042FC: 0x24040063, 0x80104300: 0x14400006,
        0x80104304: 0x24040063, 0x80104308: 0x0C031D50, 0x8010430C: 0x24050001,
        0x80104310: 0x24040063, 0x80104314: 0x0C031D7B, 0x80104318: 0x24050001,
        0x8010431C: 0x0C031D67, 0x80104320: 0x24040028, 0x80104324: 0x24100001,
        0x80104328: 0x14500003, 0x8010432C: 0x00000000, 0x80104330: 0x0C031DAC,
        0x80104334: 0x24040002, 0x80104338: 0x0C031D67, 0x8010433C: 0x2404007D,
        0x80104340: 0x14500003, 0x80104344: 0x00000000, 0x80104348: 0x0C031DAC,
        0x8010434C: 0x24040003, 0x80104350: 0x0C031D87, 0x80104354: 0x24040063,
        0x80104358: 0x24030002, 0x8010435C: 0x1443000B, 0x80104360: 0x00001021,
        0x80104364: 0x0C031D67, 0x80104368: 0x2404000B, 0x8010436C: 0x14400007,
        0x80104370: 0x00001021, 0x80104374: 0x2404000B, 0x80104378: 0x0C031D50,
        0x8010437C: 0x24050001, 0x80104380: 0x0C031DDB, 0x80104384: 0x00000000,
        0x80104388: 0x00001021, 0x8010438C: 0x8FBF0014, 0x80104390: 0x8FB00010,
        0x80104394: 0x03E00008, 0x80104398: 0x27BD0018, 0x8010443C: 0x03E00008,
        0x80104440: 0x00001021, 0x80104444: 0x03E00008, 0x80104448: 0x00001021,
    }
    for pc, expected in instructions.items():
        if elf_word(elf, pc) != expected:
            raise ValueError(f'level6 original instruction changed at {pc:08x}')
    by_name = {r['name']: r for r in rows if r['kind'] == 0 and r['name']}
    expected = (
        ('OBJ_ConYard_Barracks', '00004a2c', 500, (50, 1, 0, 0, 90, 1)),
        ('OBJ_Factory_01', '00000af4', 650, (50, 1, 125, 1, 90, 1)),
        ('OBJ_Hangar_01', '000017a8', 500, (50, 1, 121, 1, 90, 1)),
        ('OBJ_Hangar_02', '00002274', 750, (50, 1, 40, 1, 91, 1)),
    )
    for name, offset, hp, effect in expected:
        row = by_name[name]
        actual = (row['offset'], row['subtype'], row['words']['6c'],
                  tuple(row['words'][f'{p:02x}'] for p in range(0x70, 0x88, 4)),
                  row['words']['88'], row['words']['a0'])
        if actual != (offset, 0x14, hp, effect, 1, 0):
            raise ValueError(f'level6 DAT contract changed for {name}: {actual}')
    return dict(
        scope='original static contract only; live ownership, damage and objective response unqualified',
        instruction_checks={f'{pc:08x}': f'{value:08x}' for pc, value in instructions.items()},
        dat_checked_fields=[0, 0x6c, 0x70, 0x74, 0x78, 0x7c, 0x80, 0x84, 0x88, 0xa0],
        callback=dict(callback='80104210', reader='80104444', friendlies_saved='returns 0; no counter reads',
                      counter_reads=[34, 35, 36, 37, 38, 39, 98, 50, 99],
                      boolean_reads=[98, 99, 40, 125, 11],
                      failure='any counter34..39 == 1 -> Bit4 and voice101, early return',
                      success='counter99 == 2 and Boolean11==0 -> Boolean11=1 and Bit8',
                      intermediate=['counter98==6 and Boolean98==0 -> Boolean98=1, counter99+=1, objective1 complete',
                                    'counter50==4 and Boolean99==0 -> Boolean99=1, counter99+=1',
                                    'Boolean40==1 -> objective2 complete',
                                    'Boolean125==1 -> objective3 complete'],
                      namespace_warning='Counter40 is not read here; Boolean40 is. Counter98/99 and Boolean98/99 are distinct.'),
        route=dict(subtype=0x14, setup_table='8003bdd8', setup='800653f4', handler='8006cbb0',
                   message5_table='8003ca30', message5='8006cf88',
                   payload='node+4', descriptor='payload+0x34',
                   health_storage='DAT+0x6c+4*word80137CE4; qualify detail0 only',
                   source_gate='DAT+a0==0 or message+2 differs from getPlayerField2(0); selected DAT+a0=0',
                   health_gate='prehealth>0 at8006cfa4; posthealth>0 at8006d278 skips death effect',
                   damage_writer='8006cfe8 subtracts unsigned message halfword+6',
                   effect_gate='byte80130B39==0 at8006d6bc/8006d6c0; otherwise effect skipped',
                   effect_call='8006d6f0', counter_writer='8006594c', counter2_writer='80065974',
                   boolean_writer='80065928', selected_effect=[50, 1, 0, 0, 90, 1],
                   effect_tuple_order='counter,delta,boolean,value,counter2,delta2',
                   limitation='Original named API registered message5 only; FFFF fallback800c74ac/800c74e0 subtracts then applies subtype14 effect without a death threshold. Observe actual route, detail and global effect gate.'),
        selected=by_name['OBJ_ConYard_Barracks'], candidates=[by_name['OBJ_ConYard_Barracks']],
        excluded_controls=[by_name[n] for n in ('OBJ_Factory_01', 'OBJ_Hangar_01', 'OBJ_Hangar_02')],
        exclusions='Barracks also increments counter90; its downstream uses remain unqualified. Factory sets Boolean125, hangar1 Boolean121, hangar2 Boolean40 and counter91. Wingman_01/02 have zero effect counters/Boolean. Radar_Dish subtype0x2a has raw +0x80=98 but its layout/route is unqualified; never interpret its raw tuple as the subtype14 effect.',
        selection='H-coupled: Barracks has two counters, no direct Boolean. Static route supports ordinary probing only, not lethal admission or a single-counter claim.',
        next_measurement='One ordinary original named API10 on owned OBJ_ConYard_Barracks, detail0, global80130B39=0; join slot/gen/node/payload/DAT/message/health writer and API return, original getters50/90 and actual changing-value control. No lethal dose; counter90 consumers require proof before a later destruction test.')


def level7_contract(elf, rows):
    spans = {
        0x801044E0: (
            '27bdffd0 afbf0018 afb10014 afb00010 f7b60028 f7b40020 0c031d67 24040061 '
            '00408021 24020001 1602001a 00000000 0c031d67 24040062 14400016 00000000 '
            '0c031d67 24040063 14400012 3c038011 8c62d098 1440000f 3c04800b 24849780 '
            '0c031e21 ac70d098 2404003d 3c01800b c43497b8 0c031d50 24050001 4405a000 '
            '0c031f47 2404008a 4405a000 0c031f47 2404011a 0c031d67 24040061 1440001a '
            '00000000 0c031d67 24040062 00408021 24020001 16020014 00000000 0c031d67 '
            '24040063 14400010 3c038011 8c62d090 1440000d 3c04800b 24849788 0c031e21 '
            'ac70d090 24040040 0c031d50 24050001 3c053f00 0c031f47 240402a6 3c054040 '
            '0c031f47 2404008b 0c031d67 24040061 1440001a 00000000 0c031d67 24040062 '
            '14400016 00000000 0c031d67 24040063 00401821 24020001 14620010 3c058011 '
            '8ca2d094 1440000d 3c04800b 24849790 0c031e21 aca3d094 24040043 0c031d50 '
            '24050001 3c053f00 0c031f47 240402a6 3c054040 0c031f47 2404008a 0c031d87 '
            '24040014 28420015 1440000f 00000000 0c031d67 24040061 1440000b 24040061 '
            '0c031d50 24050001 24040063 0c031d7b 24050001 0c031dac 24040002 24040078 '
            '0c031d50 24050001 0c031d87 2404001e 2842000a 1440000f 00000000 0c031d67 '
            '24040062 1440000b 24040062 0c031d50 24050001 24040063 0c031d7b 24050001 '
            '0c031dac 24040001 24040079 0c031d50 24050001 0c031d87 24040028 28420006 '
            '1440000f 00000000 0c031d67 24040063 1440000b 24040063 0c031d50 24050001 '
            '24040063 0c031d7b 24050001 0c031dac 24040003 2404007a 0c031d50 24050001 '
            '0c031d87 24040028 28420006 14400016 00000000 0c031d87 2404001e 2842000a '
            '14400011 00000000 0c031d67 2404006a 1440000d 3c038011 8c62d09c 1440000a '
            '24020001 ac62d09c 24040029 0c031d50 00402821 3c04800b 0c031e21 24849798 '
            '0c031f66 24040003 0c031d87 24040014 24030013 1443002a 00000000 0c031d67 '
            '24040062 00408021 24020001 16020024 00000000 0c031d67 24040063 00401821 '
            '1470001f 3c068011 8cc2d0a0 1440001c 24040032 24050001 0c031d50 acc3d0a0 '
            '3c04800b 0c031e21 248497ac 4480a000 4405a000 3c01800b c43697bc 0c031f47 '
            '2404023d 4405b000 0c031f47 24040155 4405a000 0c031f47 24040089 4405a000 '
            '0c031f47 24040103 4405b000 0c031f47 24040156 4405b000 0c031f47 24040149 '
            '0c031d67 24040061 00408021 24020001 16020029 00000000 0c031d87 2404001e '
            '24030008 14430024 00000000 0c031d67 24040063 00401821 1470001f 3c068011 '
            '8cc2d0a0 1440001c 24040032 24050001 0c031d50 acc3d0a0 3c04800b 0c031e21 '
            '248497ac 4480a000 4405a000 3c01800b c43697c0 0c031f47 2404023d 4405b000 '
            '0c031f47 24040155 4405a000 0c031f47 24040089 4405a000 0c031f47 24040103 '
            '4405b000 0c031f47 24040156 4405b000 0c031f47 24040149 0c031d67 24040061 '
            '00408021 24020001 16020029 00000000 0c031d67 24040062 00408821 16300024 '
            '00000000 0c031d87 24040028 24030004 1443001f 3c038011 8c62d0a0 1440001c '
            '24040032 24050001 0c031d50 ac71d0a0 3c04800b 0c031e21 248497ac 4480a000 '
            '4405a000 3c01800b c43697c4 0c031f47 2404023d 4405b000 0c031f47 24040155 '
            '4405a000 0c031f47 24040089 4405a000 0c031f47 24040103 4405b000 0c031f47 '
            '24040156 4405b000 0c031f47 24040149 0c031d87 24040063 28420003 14400003 '
            '00000000 0c031ddb 00000000 8fbf0018 8fb10014 8fb00010 d7b60028 d7b40020 '
            '00001021 03e00008 27bd0030 '
        ),
        0x80104A60: (
            '27bdffe8 24040080 afbf0014 0c031d87 afb00010 24040080 0c031d87 00408021 '
            '02028021 0c031dec 00102023 8fbf0014 8fb00010 00001021 03e00008 27bd0018 '
        ),
    }
    instructions = {
        0x8003BDD8: 0x800653F4, 0x8003CA30: 0x8006CF88, 0x80046878: 0xAC82000C,
        0x80046DBC: 0xAC5275D8, 0x80047B50: 0x8C4475D8, 0x80047B5C: 0x0C011EDC,
        0x800653B4: 0x27BDFFD8, 0x800653B8: 0xAFB1001C, 0x800653BC: 0x00808821,
        0x800653C0: 0xAFBF0020, 0x800653C4: 0xAFB00018, 0x800653C8: 0x96220000,
        0x800653CC: 0x2443FFF4, 0x800653D0: 0x2C620047, 0x800653D4: 0x1040009E,
        0x800653D8: 0x3C028004, 0x800653DC: 0x2442BDB8, 0x800653E0: 0x00031880,
        0x800653E4: 0x00621821, 0x800653E8: 0x8C620000, 0x800653EC: 0x00400008,
        0x800653F0: 0x00000000, 0x800653F4: 0x3C048007, 0x800653F8: 0x2484CBB0,
        0x800653FC: 0x02202821, 0x80065400: 0x24070028, 0x80065404: 0x9622008A,
        0x80065408: 0x24060003, 0x8006540C: 0x00C23023, 0x80065410: 0x00063180,
        0x80065414: 0x34C60001, 0x80065418: 0x08019599, 0x8006541C: 0x30C6FFC1,
        0x80065664: 0x0C00FFFB, 0x80065668: 0x00000000, 0x8006566C: 0x00401821,
        0x80065670: 0x3070FFFF, 0x80065674: 0x3C018004, 0x80065678: 0xC420BED4,
        0x8006567C: 0x3402FFFF, 0x80065680: 0x12020006, 0x80065684: 0xE7A00010,
        0x80065688: 0xA6230006, 0x8006568C: 0x02002021, 0x80065690: 0x24050003,
        0x80065694: 0x0C00FA37, 0x80065698: 0x27A60010, 0x80065914: 0x8FA80010,
        0x80065918: 0x10800004, 0x8006591C: 0x3C028014, 0x80065920: 0x244288A0,
        0x80065924: 0x00821021, 0x80065928: 0xA045FFFF, 0x8006592C: 0x10C00008,
        0x80065930: 0x3C028014, 0x80065934: 0x24428060, 0x80065938: 0x24C3FFFF,
        0x8006593C: 0x00031880, 0x80065940: 0x00621821, 0x80065944: 0x8C620000,
        0x80065948: 0x00471021, 0x8006594C: 0xAC620000, 0x80065950: 0x11000009,
        0x80065954: 0x3C028014, 0x80065958: 0x24428060, 0x8006595C: 0x2503FFFF,
        0x80065960: 0x00031880, 0x80065964: 0x00621821, 0x80065968: 0x8C620000,
        0x8006596C: 0x8FA40014, 0x80065970: 0x00441021, 0x80065974: 0xAC620000,
        0x80065978: 0x03E00008, 0x8006597C: 0x00000000, 0x8006CBB0: 0x27BDFF20,
        0x8006CBB4: 0xAFB500AC, 0x8006CBB8: 0x0080A821, 0x8006CBBC: 0xAFB00098,
        0x8006CBC0: 0x30A5FFFF, 0x8006CBC4: 0x24A3FFFF, 0x8006CBC8: 0x2C62000B,
        0x8006CBCC: 0xAFBF00B4, 0x8006CBD0: 0xAFB600B0, 0x8006CBD4: 0xAFB400A8,
        0x8006CBD8: 0xAFB300A4, 0x8006CBDC: 0xAFB200A0, 0x8006CBE0: 0xAFB1009C,
        0x8006CBE4: 0xF7BC00D8, 0x8006CBE8: 0xF7BA00D0, 0x8006CBEC: 0xF7B800C8,
        0x8006CBF0: 0xF7B600C0, 0x8006CBF4: 0xF7B400B8, 0x8006CBF8: 0x8EB10004,
        0x8006CBFC: 0x1040032F, 0x8006CC00: 0x00C08021, 0x8006CC04: 0x3C028004,
        0x8006CC08: 0x2442CA20, 0x8006CC0C: 0x00031880, 0x8006CC10: 0x00621821,
        0x8006CC14: 0x8C620000, 0x8006CC18: 0x00400008, 0x8006CC1C: 0x00000000,
        0x8006CC20: 0xAEB10008, 0x8006CC24: 0xAE300034, 0x8006CF88: 0x3C128013,
        0x8006CF8C: 0x8E230034, 0x8006CF90: 0x8E427CE4, 0x8006CF94: 0x2473006C,
        0x8006CF98: 0x00021080, 0x8006CF9C: 0x00531021, 0x8006CFA0: 0x8C420000,
        0x8006CFA4: 0x184001E9, 0x8006CFA8: 0x0200B021, 0x8006CFAC: 0x8C6200A0,
        0x8006CFB0: 0x10400007, 0x8006CFB4: 0x00000000, 0x8006CFB8: 0x0C01B265,
        0x8006CFBC: 0x00002021, 0x8006CFC0: 0x96030002, 0x8006CFC4: 0x3042FFFF,
        0x8006CFC8: 0x10620008, 0x8006CFCC: 0x00000000, 0x8006CFD0: 0x8E427CE4,
        0x8006CFD4: 0x96040006, 0x8006CFD8: 0x00021080, 0x8006CFDC: 0x00531021,
        0x8006CFE0: 0x8C430000, 0x8006CFE4: 0x00641823, 0x8006CFE8: 0xAC430000,
        0x8006D264: 0x3C028013, 0x8006D268: 0x8C427CE4, 0x8006D26C: 0x00021080,
        0x8006D270: 0x00531021, 0x8006D274: 0x8C420000, 0x8006D278: 0x1C400134,
        0x8006D27C: 0x00000000, 0x8006D6B8: 0x3C028013, 0x8006D6BC: 0x90420B39,
        0x8006D6C0: 0x54400012, 0x8006D6C4: 0x02A02021, 0x8006D6C8: 0x8E230034,
        0x8006D6CC: 0x8C620080, 0x8006D6D0: 0xAFA20010, 0x8006D6D4: 0x8E220034,
        0x8006D6D8: 0x8C420084, 0x8006D6DC: 0xAFA20014, 0x8006D6E0: 0x8C640078,
        0x8006D6E4: 0x8C65007C, 0x8006D6E8: 0x8C660070, 0x8006D6EC: 0x8C670074,
        0x8006D6F0: 0x0C019645, 0x8006D6F4: 0x00000000, 0x800C73B8: 0x3403FFFF,
        0x800C73BC: 0x96020006, 0x800C73C0: 0x10430032, 0x800C7490: 0x8C437CE4,
        0x800C7494: 0x02003821, 0x800C7498: 0x00031880, 0x800C749C: 0x00671821,
        0x800C74A0: 0x8C62006C, 0x800C74A4: 0x00521023, 0x800C74A8: 0x00408821,
        0x800C74AC: 0xAC71006C, 0x800C74B0: 0x94E30000, 0x800C74B4: 0x24020014,
        0x800C74B8: 0x1462000C, 0x800C74BC: 0x02201021, 0x800C74C0: 0x8CE20080,
        0x800C74C4: 0xAFA20010, 0x800C74C8: 0x8CE20084, 0x800C74CC: 0xAFA20014,
        0x800C74D0: 0x8CE40078, 0x800C74D4: 0x8CE5007C, 0x800C74D8: 0x8CE60070,
        0x800C74DC: 0x8CE70074, 0x800C74E0: 0x0C019645, 0x800C74E4: 0x00000000,
        0x800C75B4: 0x9042FFFF, 0x800C761C: 0x14800003, 0x800C7620: 0x3C038014,
        0x800C7624: 0x03E00008, 0x800C7628: 0x00001021, 0x800C762C: 0x24638060,
        0x800C7630: 0x2482FFFF, 0x800C7634: 0x00021080, 0x800C7638: 0x00431021,
        0x800C763C: 0x8C420000, 0x800C7640: 0x03E00008, 0x800C7644: 0x00000000,
        0x800C7754: 0x34420004, 0x800C7788: 0x34420008,
    }
    instructions.update({start + 4*i: int(value, 16)
                         for start, values in spans.items() for i, value in enumerate(values.split())})
    for pc, expected in instructions.items():
        if elf_word(elf, pc) != expected:
            raise ValueError(f'level7 original instruction changed at {pc:08x}')
    by_name = {r['name']: r for r in rows if r['kind'] == 0 and r['name']}
    expected = (
        ('20_Dest_Tanks_01', '000005d0', 50, (20, 1, 0, 0, 0, 1)),
        ('20_Dest_Tanks_03', '00000754', 50, (20, 1, 0, 0, 0, 1)),
        ('20_Dest_Tanks_04', '00000818', 50, (20, 1, 0, 0, 0, 1)),
        ('40_Destroy_Imp_Barracks_03', '00000b90', 100, (40, 1, 28, 1, 0, 1)),
        ('20_Spaceport_02', '000018b8', 300, (20, 1, 106, 1, 0, 1)),
        ('30_Sensor_Array_Main', '00001f94', 100, (30, 1, 2, 1, 0, 1)),
    )
    for name, offset, hp, effect in expected:
        row = by_name[name]
        actual = (row['offset'], row['subtype'], row['words']['6c'],
                  tuple(row['words'][f'{p:02x}'] for p in range(0x70, 0x88, 4)),
                  row['words']['88'], row['words']['a0'])
        if actual != (offset, 0x14, hp, effect, 1, 0):
            raise ValueError(f'level7 DAT contract changed for {name}: {actual}')
    selectors = {0x800c761c: set(), 0x800c759c: set()}
    for pc in range(0x801044e0, 0x80104a0c, 4):
        instruction = elf_word(elf, pc)
        if instruction >> 26 != 3:
            continue
        target = 0x80000000 | ((instruction & 0x3ffffff) << 2)
        if target in selectors:
            delay = elf_word(elf, pc + 4)
            if delay >> 16 != 0x2404:
                raise ValueError(f'nonconstant level7 objective selector at {pc:08x}')
            selectors[target].add(delay & 65535)
    if selectors != {0x800c761c: {20, 30, 40, 99}, 0x800c759c: {97, 98, 99, 106}}:
        raise ValueError('level7 callback getter census changed')
    return dict(
        scope='original ELF and retail DAT static contract only; no live ownership or response',
        instruction_checks={f'{pc:08x}': f'{v:08x}' for pc, v in instructions.items()},
        dat_checked_fields=[0, 0x6c, 0x70, 0x74, 0x78, 0x7c, 0x80, 0x84, 0x88, 0xa0],
        callback=dict(address='801044e0', end='80104a0c', reader='80104a60', reader_end='80104aa0',
                      counter_reads=sorted(selectors[0x800c761c]),
                      boolean_reads=sorted(selectors[0x800c759c]),
                      stages=[dict(counter=c, minimum=n, latch=b, complete_slot=s, extra_boolean=e)
                              for c, n, b, s, e in ((20,21,97,2,120),(30,10,98,1,121),(40,6,99,3,122))],
                      stage_effect='if counter>=minimum and Boolean latch==0: latch=1, counter99+=1, complete_slot, extra_boolean=1',
                      success='counter99>=3 -> Bit8', failure='no Bit4/failure call in this callback',
                      friendlies_saved='-(getCounter128()+getCounter128()); two separate reads, not a typo',
                      notifications=['exactly Boolean97 -> Boolean61 with word8010D098 latch',
                                     'exactly Boolean98 -> Boolean64 with word8010D090 latch',
                                     'exactly Boolean99 -> Boolean67 with word8010D094 latch',
                                     'c40>=6 and c30>=10 and Boolean106==0 and word8010D09C==0 -> Boolean41=1',
                                     'c20==19 and B98==B99==1, or c30==8 and B97==B99==1, or c40==4 and B97==B98==1 -> Boolean50=1 with shared word8010D0A0 latch'],
                      boolean_writes=[41,50,61,64,67,97,98,99,120,121,122],
                      historical_id2='not read by either callback or friendlies reader'),
        route=dict(subtype=0x14, setup='800653f4', handler='8006cbb0', message5='8006cf88',
                   payload='node+4', descriptor='payload+0x34', health='DAT+0x6c+4*detail',
                   writer='8006cfe8', prehealth_gate='blez8006cfa4',
                   source_immunity='DAT+a0 nonzero and message source matches player -> skips subtraction',
                   death_gate='bgtz8006d278 skips effect while health>0',
                   effect_gate='byte80130B39 must be zero', effect_call='8006d6f0',
                   counter_writer='8006594c', boolean_writer='80065928',
                   selected_effect=[20,1,0,0,0,1],
                   fallback='FFFF API branch800c748c subtracts and applies effect eagerly; no death gate',
                   limitation='Registered message5 ownership/detail must be observed; no FFFF or lethal admission'),
        selected=by_name['20_Dest_Tanks_01'],
        candidates=[by_name[n] for n, _, _, _ in expected[:3]],
        excluded_controls=[by_name[n] for n, _, _, _ in expected[3:]],
        typed_retail_controls=[dict(name=n, **by_name[n]['damage_effect']) for n, _, _, _ in expected],
        exclusions='Barracks03 couples Boolean28; Spaceport02 couples Boolean106 used by callback; SensorMain couples Boolean2. Turret and dish subtypes remain raw, not this damage route.',
        next_measurement='One original named API10 on owned 20_Dest_Tanks_01; join slot/generation/node/payload/DAT, message5, actual detail/health writer/return, counter20 original getter and changing-value control. No lethal or fallback request.')


def level8_contract(elf, rows):
    spans = {
        0x80104AA0: (
            '27bdffd8 f7b60020 46006586 3c04800b afbf0014 afb00010 f7b40018 0c031e28 '
            '248497e8 3c01800b c422980c 4602003e 00000000 45000014 3c038011 8c62d0b0 '
            '54400012 3c04800b 24040008 24050001 00a08021 0c031d50 ac70d0b0 00002021 '
            '0c031d98 24050001 2404015a 0c031f47 00002821 3c054000 0c031f47 24040266 '
            '3c028011 ac50d0c4 3c04800b 0c031e28 248497f8 3c01800b c4229810 4602003e '
            '00000000 45000012 3c038011 8c62d0b4 1440000f 24040006 24050001 4480a000 '
            '00a01021 0c031d50 ac62d0b4 4405a000 0c031f47 24040158 3c054000 0c031f47 '
            '24040265 4405a000 0c031f47 240400e2 0c031d67 24040005 00401821 24020001 '
            '14620015 3c048011 8c82d0b8 14400012 00000000 0c031dce ac83d0b8 3c04800b '
            '0c031e21 24849804 24040267 0c031f47 00002821 3c04800b 248497e8 3c053d4c '
            '34a5cccd 3c0740a0 0c031e5e 00003021 0c031f66 24040006 0c031d87 24040003 '
            '00401821 24020001 1462000c 3c048011 8c82d0b8 14400009 00000000 0c031dce '
            'ac83d0b8 2404015f 0c031f47 00002821 3c054000 0c031f47 240400fd 0c031d87 '
            '24040005 24030007 14430017 3c038011 8c62d0bc 14400014 24020001 0c031ddb '
            'ac62d0bc 0c031dac 24040001 0c031dac 24040002 3c04800b 248497e8 3c053ccc '
            '34a5cccd 3c0740a0 0c031e5e 00003021 3c053f80 0c031f47 2404011e 24040277 '
            '0c031f47 00002821 0c041333 4600b306 8fbf0014 8fb00010 d7b60020 d7b40018 '
            '00001021 03e00008 27bd0028 '
        ),
        0x80104D8C: (
            '27bdffe0 3c048010 24844ec8 2405000a 24060001 00003821 3c028011 ac40d0b0 '
            '3c028011 ac40d0b4 3c028011 ac40d0b8 3c028011 ac40d0bc 3c028011 ac40d0c0 '
            '3c028011 ac40d0c4 3c028011 afbf0018 ac40d0c8 0c031e0c afa00010 3c048010 '
            '24844ee4 2405000c 24060001 00003821 0c031e0c afa00010 3c048010 24844f00 '
            '2405000e 24060001 00003821 0c031e0c afa00010 3c048010 24844f1c 00002821 '
            '00a03021 24070005 24020002 0c031e0c afa20010 24040001 0c031d98 00802821 '
            '0c0413db 00000000 8fbf0018 00001021 03e00008 27bd0020 '
        ),
        0x80104E9C: (
            '27bdffe8 afbf0010 0c031d87 24040006 24040006 0c031dec 00822023 8fbf0010 '
            '00001021 03e00008 27bd0018 '
        ),
        0x800E3A28: (
            '96830004 2402000b 10620050 2402000c 14620053 00000000 '
        ),
        0x800E3AD4: (
            '8e420034 924300b1 146000bf 244400c4 3c028013 8c437ce4 00031880 00641821 '
            '96840006 8c620000 00441023 1c4000b6 ac620000 8e430034 24020001 a24200b1 '
            '8c6200bc afa20010 8e420034 8c4200c0 afa20014 8c6400b4 8c6500b8 8c6600ac '
            '8c6700b0 0c019645 '
        ),
        0x800E3CD0: (
            '8e440038 96850006 0c03c848 00000000 1c40003e '
        ),
        0x800E3D48: (
            '8e430034 8c620080 afa20010 8e420034 8c420084 afa20014 8c640078 8c65007c '
            '8c660070 8c670074 0c019645 24100001 '
        ),
        0x80065588: (
            '3c04800e 24842818 02202821 24060002 08019599 24070064 '
        ),
        0x800657DC: (
            '8c820088 10400002 24030002 24030001 03e00008 00601021 '
        ),
        0x80065854: (
            '8c830060 10600006 3c028014 244288a0 00621021 9042ffff 10400017 00000000 '
            '8c820064 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c430000 '
            '8c840068 0064182a 14600019 00001021 03e00008 24020001 '
        ),
        0x80065914: (
            '8fa80010 10800004 3c028014 244288a0 00821021 a045ffff 10c00008 3c028014 '
            '24428060 24c3ffff 00031880 00621821 8c620000 00471021 ac620000 11000009 '
            '3c028014 24428060 2503ffff 00031880 00621821 8c620000 8fa40014 00441021 '
            'ac620000 03e00008 00000000 '
        ),
        0x800A97E8: (
            '74726169 6e5f315f 656e6769 6e650000 696d705f 7472616e 73320000 63616d65 '
            '72613100 41700000 41200000 '
        ),
    }
    instructions = {
        0x8003BE44: 0x80065588,
        0x8003C0AC: 0x800657DC,
        0x8003C1CC: 0x80065854,
        0x8003BE48: 0x80065588,
        0x8003C0B0: 0x800657DC,
        0x8003C1D0: 0x80065854,
        0x8003BE4C: 0x80065588,
        0x8003C0B4: 0x800657DC,
        0x8003C1D4: 0x80065854,
        0x8009ED30: 0x8003AF68,
    }
    instructions.update({start + 4*i: int(value, 16)
                         for start, values in spans.items() for i, value in enumerate(values.split())})
    for pc, expected in instructions.items():
        if elf_word(elf, pc) != expected:
            raise ValueError(f'level8 original instruction changed at {pc:08x}')
    by_name = {r['name']: r for r in rows if r['kind'] == 0 and r['name']}
    # name, offset, subtype, hull HP (+6c), destroy tuple (+70..+84), disable tuple (+ac..+c0), disable pool detail0 (+c4)
    expected = (
        ('train_1_engine', '000006d4', 0x2f, 1000000, (0, 0, 0, 0, 0, 1), (5, 1, 0, 0, 0, 1), 20),
        ('train_2_cargo', '00000978', 0x31, 500, (3, 1, 0, 0, 0, 1), (5, 1, 0, 0, 0, 1), 18),
        ('train_3_def', '00000834', 0x30, 500, (3, 1, 0, 0, 0, 1), (5, 1, 0, 0, 0, 1), 20),
        ('train_4_cargo', '00000a78', 0x31, 500, (3, 1, 0, 0, 0, 1), (5, 1, 0, 0, 0, 1), 18),
        ('train_5_cargo', '00000b78', 0x31, 500, (3, 1, 0, 0, 0, 1), (5, 1, 0, 0, 0, 1), 18),
        ('train_6_def', '00000c78', 0x30, 500, (3, 1, 0, 0, 0, 1), (5, 1, 0, 1, 0, 1), 20),
        ('train_7_def', '00000dbc', 0x30, 500, (3, 1, 0, 0, 0, 1), (5, 1, 0, 1, 0, 1), 20),
    )
    for name, offset, subtype, hp, destroy, disable, pool in expected:
        row = by_name[name]
        w = row['words']
        actual = (row['offset'], row['subtype'], w['6c'],
                  tuple(w[f'{p:02x}'] for p in range(0x70, 0x88, 4)),
                  tuple(w[f'{p:02x}'] for p in range(0xac, 0xc4, 4)), w['c4'],
                  w['88'], w['60'], w['64'], w['68'])
        if actual != (offset, subtype, hp, destroy, disable, pool, 0, 0, 0, 0):
            raise ValueError(f'level8 DAT contract changed for {name}: {actual}')
    selectors = {0x800c761c: set(), 0x800c759c: set()}
    for pc in range(0x80104aa0, 0x80104ccc, 4):
        instruction = elf_word(elf, pc)
        if instruction >> 26 != 3:
            continue
        target = 0x80000000 | ((instruction & 0x3ffffff) << 2)
        if target in selectors:
            delay = elf_word(elf, pc + 4)
            if delay >> 16 != 0x2404:
                raise ValueError(f'nonconstant level8 objective selector at {pc:08x}')
            selectors[target].add(delay & 65535)
    if selectors != {0x800c761c: {3, 5}, 0x800c759c: {5}}:
        raise ValueError('level8 callback getter census changed')
    names = [n for n, *_ in expected]
    return dict(
        scope='original ELF and retail DAT static contract only; no live ownership or response',
        instruction_checks={f'{pc:08x}': f'{v:08x}' for pc, v in instructions.items()},
        dat_checked_fields=[0, 0x60, 0x64, 0x68, 0x6c, 0x70, 0x74, 0x78, 0x7c, 0x80, 0x84, 0x88,
                            0xac, 0xb0, 0xb4, 0xb8, 0xbc, 0xc0, 0xc4],
        callback=dict(address='80104aa0', end='80104ccc', init='80104d8c', friendlies='80104e9c',
                      counter_reads=sorted(selectors[0x800c761c]),
                      boolean_reads=sorted(selectors[0x800c759c]),
                      success='counter5==7 (exact) with latch word8010D0BC -> Bit8, complete slots1+2',
                      failures=['counter3==1 with latch word8010D0B8 -> Bit4',
                                'Boolean5==1 with the same latch word8010D0B8 -> Bit4, camera1 cue, effect on train_1_engine'],
                      proximity=['train_1_engine XZ<=15.0 (800A980C) -> Boolean8, hidden flag0, word8010D0B0/D0C4',
                                 'imp_trans2 <=10.0 (800A9810) -> Boolean6, word8010D0B4'],
                      handles=['Boolean10 -> 80104EC8', 'Boolean12 -> 80104EE4', 'Boolean14 -> 80104F00',
                               'counter5>=2 (a3=5, arg5=2; semantics single-source) -> 80104F1C'],
                      friendlies_saved='6 - counter6',
                      tail_call='80104ccc (labelled lv9_triggerEventOnPlayerProximity; name not checked)'),
        route=dict(subtypes=[0x2f, 0x30, 0x31], setup='80065588 -> npcTrainCarUpdate 800e2818',
                   spawn='parseDatSpawnPositions case800657DC: DAT+88==0 -> category2 condition list',
                   gate='isDatItemConditionMet case80065854: DAT+60 Boolean/+64 counter>=+68; all zero = ungated',
                   message_select='msg+4==12 -> disable route; 11 from own source skipped; others -> hull route',
                   disable_route='DAT+c4+4*detail(80137CE4) -= msg+6; <=0 and payload+177==0 -> latch, apply +ac tuple (counter5+1) at800e3b38',
                   hull_route='dealDamageToNpc800f2120 <=0 -> apply +70 tuple (counter3+1 on non-engine cars) at800e3d70',
                   kind12='weapon-name table 8009ED00[12] = ion_laser (inferred mapping, single-source)'),
        selected=by_name['train_3_def'],
        candidates=[by_name[n] for n in names],
        excluded_controls=[],
        next_measurement='Live: confirm train cars register (desc+6 != FFFF) on the scripted route, then one ordinary kind-12 (ion) damage message to a registered car that drains the disable pool; read counter5 via original getter with a same-run changing-value control. Never send hull damage (counter3==1 fails the mission).')


def run_level6_original_slice(elf, counts=None, booleans=None, fallback=False):
    """Execute the checked integer slice; external presentation calls are recorded."""
    memory, regs, calls, writes = {}, [0] * 32, [], []

    def store(address, value, size):
        for i in range(size):
            memory[address + i] = (value >> (8 * (size - i - 1))) & 255

    def load(address, size):
        if any(address + i not in memory for i in range(size)):
            raise ValueError(f'uninitialized slice read {address:08x}')
        return int.from_bytes(bytes(memory[address + i] for i in range(size)), 'big')

    for i in range(128):
        store(0x80138060 + 4*i, (counts or {}).get(i+1, 0), 4)
        store(0x801388a0 + i, (booleans or {}).get(i+1, 0), 1)
    store(0x8010ca20, 0, 4)
    store(0x8010c9e0, 0, 4)
    regs[29], regs[31] = 0x81001000, 0x7ffffffc
    pc, end = 0x80104210, 0x7ffffffc
    if fallback:
        pc, end = 0x800c748c, 0x800c74e8
        regs[16], regs[18] = 0x81002000, 10
        store(0x80137ce4, 0, 4)
        store(regs[16], 0x14, 2)
        store(regs[16]+0x6c, 500, 4)
        for i, value in enumerate((50, 1, 0, 0, 90, 1)):
            store(regs[16]+0x70+4*i, value, 4)
    allowed = ((0x80104210, 0x8010439c), (0x800c7540, 0x800c7568),
               (0x800c759c, 0x800c7648), (0x800c7738, 0x800c77a0),
               (0x80065914, 0x80065980), (0x800c748c, 0x800c74e8))
    external = {0x800c7cf8, 0x800c7d1c, 0x800c7c6c, 0x800c76b0, 0x80067938}

    def instruction(at, delay=False):
        if not any(a <= at < b for a,b in allowed):
            raise ValueError(f'outside audited slice {at:08x}')
        w = elf_word(elf, at)
        op, rs, rt, rd = w >> 26, w >> 21 & 31, w >> 16 & 31, w >> 11 & 31
        imm = w & 65535
        signed = imm if imm < 32768 else imm - 65536
        target = None
        if op in (2, 3):
            target = ((at+4) & 0xf0000000) | ((w & 0x3ffffff) << 2)
            if op == 3:
                regs[31] = at+8
        elif op in (4, 5):
            take = (regs[rs] == regs[rt]) == (op == 4)
            target = at+4+signed*4 if take else at+8
        elif op == 0 and w & 63 == 8:
            target = regs[rs]
        elif op == 0 and w & 63 == 0:
            regs[rd] = regs[rt] << (w >> 6 & 31) & 0xffffffff
        elif op == 0 and w & 63 in (0x21, 0x23):
            regs[rd] = (regs[rs] + (regs[rt] if w & 63 == 0x21 else -regs[rt])) & 0xffffffff
        elif op == 9:
            regs[rt] = (regs[rs] + signed) & 0xffffffff
        elif op == 15:
            regs[rt] = imm << 16
        elif op == 13:
            regs[rt] = regs[rs] | imm
        elif op in (35, 36, 37):
            regs[rt] = load((regs[rs]+signed) & 0xffffffff, {35:4,36:1,37:2}[op])
        elif op in (43, 40):
            address = (regs[rs]+signed) & 0xffffffff
            size = 4 if op == 43 else 1
            store(address, regs[rt], size)
            writes.append(dict(pc=f'{at:08x}', address=f'{address:08x}', value=regs[rt], size=size))
        else:
            raise ValueError(f'unsupported slice instruction {at:08x}:{w:08x}')
        regs[0] = 0
        if target is not None:
            if delay:
                raise ValueError('control transfer in slice delay slot')
            instruction(at+4, True)
            if op == 3:
                calls.append(dict(pc=f'{at:08x}', target=f'{target:08x}', a0=regs[4], a1=regs[5]))
                if target in external:
                    regs[2] = 1
                    return at+8
            return target
        return at+4

    for _ in range(3000):
        if pc == end:
            break
        pc = instruction(pc)
    else:
        raise ValueError('slice instruction budget exhausted')
    return dict(counts={i:load(0x80138060+4*(i-1),4) for i in (50,90,99)},
                booleans={i:load(0x801388a0+i-1,1) for i in (11,98,99)},
                hud_bits=load(0x8010c9e0,4), calls=calls, writes=writes,
                health=load(0x8100206c,4) if fallback else None,
                limitation='Original integer slice with presentation/audio calls stubbed; static fixture, not a game run')


def level6_safety_contract(elf, rows):
    contract = level6_contract(elf, rows)
    spans = {
        0x80065828: (
            '94820000 2443fff4 2c620047 10400032 3c028004 2442c140 00031880 00621821 '
            '8c620000 00400008 00000000 8c830060 10600006 3c028014 244288a0 00621021 '
            '9042ffff 10400017 00000000 8c820064 1040000a 3c038014 24638060 2442ffff '
            '00021080 00431021 8c430000 8c840068 0064182a 14600019 00001021 03e00008 '
            '24020001 8c830034 10600008 3c028014 244288a0 00621021 9042ffff 14400003 '
            '00000000 03e00008 00001021 8c820038 1040fff2 3c038014 24638060 2442ffff '
            '00021080 00431021 8c430000 8c84003c 08019627 0064182a 24020001 03e00008 '
            '00000000'
        ),
        0x800c748c: (
            '3c028013 8c437ce4 02003821 00031880 00671821 8c62006c 00521023 00408821 '
            'ac71006c 94e30000 24020014 1462000c 02201021 8ce20080 afa20010 8ce20084 '
            'afa20014 8ce40078 8ce5007c 8ce60070 8ce70074 0c019645 00000000'
        ),
        0x800c7540: (
            '14800003 3c028014 03e00008 24020001 244288a0 2483ffff 00621821 90620000 '
            '03e00008 a0650000'
        ),
        0x800c759c: (
            '14800003 3c028014 03e00008 24020001 244288a0 00821021 9042ffff 03e00008 '
            '00000000 14800003 3c028014 03e00008 00001021 24428060 2483ffff 00031880 '
            '00621821 8c620000 03e00008 ac650000 14800003 3c028014 03e00008 00001021 '
            '24428060 2483ffff 00031880 00621821 8c620000 00451021 03e00008 ac620000 '
            '14800003 3c038014 03e00008 00001021 24638060 2482ffff 00021080 00431021 '
            '8c420000 03e00008 00000000'
        ),
        0x800c7738: (
            '3c028011 8c42ca20 27bdffe8 14400006 afbf0010 3c038011 8c62c9e0 34420004 '
            '0c019e4e ac62c9e0 8fbf0010 03e00008 27bd0018 3c028011 8c42ca20 27bdffe8 '
            '14400006 afbf0010 3c038011 8c62c9e0 34420008 0c019e4e ac62c9e0 8fbf0010 '
            '03e00008 27bd0018'
        ),
        0x800f9fd0: (
            '27bdffd0 f7b40028 46006506 afb20018 00009021 3c028011 afb10014 2451c6e0 '
            '3c028014 afb40020 245488a0 3c028014 afb3001c 24538060 afb00010 2630000d '
            'afbf0024 92050001 24020001 54a20037 26520001 9202ffff 10400005 00000000 '
            '10450024 00000000 0803e83f 26520001 9202fff7 10400005 00541021 9043ffff '
            '9202fff8 54620029 26520001 9202fff9 1040001f 00000000 9204fffa 14800008 '
            '2442ffff 00021080 00531021 8c420000 8e03fffb 0043102a 5440001c 26520001 '
            '14850013 00000000 9202fff9 8e03fffb 2442ffff 00021080 00531021 8c420000 '
            '0043102a 50400011 26520001 0803e838 00000000 c600fff7 46140001 44801000 '
            '4600103c 00000000 45010007 e600fff7 92020000 14400004 a2000001 8e220000 '
            '0040f809 00000000 26520001 26100010 2a420030 1440ffc3 26310010 8fbf0024 '
            '8fb40020 8fb3001c 8fb20018 8fb10014 8fb00010 d7b40028 24020001 03e00008 '
            '27bd0030'
        ),
        0x800fa15c: (
            '00805021 00001821 3c028011 2448c6e0 01002021 93a90017 9082000e 10400006 '
            '24020030 24630001 28620030 1440fffa 24840010 24020030 1062000f 24020001 '
            '00031900 00681821 00402021 a064000e a060000d a060000c ac6a0000 a0650004 '
            'a0660005 a0670006 8fa40010 a0690007 03e00008 ac640008 03e00008 00001021'
        ),
        0x8010439c: (
            '3c01800b c42c9778 27bdffe0 afbf001c 0c031f3b afb00018 3c048010 2484444c '
            '00002821 00a03021 24070014 24100001 0c031e0c afb00010 3c048010 2484447c '
            '00002821 00a03021 24070015 0c031e0c afb00010 3c048010 24844498 00002821 '
            '00a03021 2407000d 0c031e0c afb00010 3c048010 248444b4 2405007f 02003021 '
            '00003821 0c031e0c afa00010 8fbf001c 8fb00018 00001021 03e00008 27bd0020'
        ),
        0x800a8a20: (
            '800f3320 800f3344 800f339c 800f33dc 800f33f0 800f3418 800f3434'
        ),
        0x800f32d8: (
            '8e220024 24150001 24530054 24500058 8e240024 8e020008 8e630000 00829021 '
            '2463ffff 2c620007 1040005f 00031080 3c07800b 24e78a20 00471021 8c420000 '
            '00400008 00000000'
        ),
        0x800f339c: (
            'c6000000 4600010d 44022000 18400038 2442ffff 00021080 00571021 c6000004 '
            '8c420000 4600010d 44032000 0043102a 14400030 26100010 0803ccfd 02402021'
        ),
        0x800f4350: (
            '8ca30040 10600009 3c028014 24428060 2463ffff 00031880 00621821 8c620000 '
            '8ca40044 00441021 ac620000 8ca40048 10800005 3c028014'
        ),
        0x8003c140: (
            '80065854 80065854 80065854 80065854 80065900 80065900 80065854 80065854 '
            '80065854 80065900 80065900 80065900 80065900 800658ac 80065900 80065900 '
            '80065900 80065900 80065854 80065854 80065900 80065854 80065900 80065900 '
            '80065854 80065854 80065900 80065854 80065854 80065854 80065854 80065854 '
            '80065854 80065854 80065854 80065854 80065854 80065854 80065854 80065854 '
            '80065854 80065854 80065854 80065854 80065900 80065900 80065900 80065854 '
            '80065854 80065854 80065854 80065900 80065854 80065854 80065854 80065854 '
            '80065854 80065900 80065854 80065854 80065854 80065900 80065854 80065854 '
            '80065854 80065854 80065900 80065854 80065854 80065900 80065854'
        ),
        0x80065874: (
            '8c820064 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c430000 '
            '8c840068 0064182a 14600019 00001021 03e00008 24020001'
        ),
        0x800658d4: (
            '8c820038 1040fff2 3c038014 24638060 2442ffff 00021080 00431021 8c430000 '
            '8c84003c 08019627 0064182a 24020001 03e00008 00000000'
        ),
        0x80065928: (
            'a045ffff 10c00008 3c028014 24428060 24c3ffff 00031880 00621821 8c620000 '
            '00471021 ac620000 11000009 3c028014 24428060 2503ffff'
        ),
        0x8006594c: (
            'ac620000 11000009 3c028014 24428060 2503ffff 00031880 00621821 8c620000 '
            '8fa40014 00441021 ac620000 03e00008 00000000 94830000'
        ),
        0x800659c4: (
            '8c82002c 1040000c 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c830030 0043102a 1440ffea 30a300ff 08019681 24020001'
        ),
        0x80065a0c: (
            '8cc30000 10600009 3c028014 24428060 2463ffff 00031880 00621821 8c620000 '
            '8cc40004 00441021 ac620000 8cc40008 1080ffd6 3c028014'
        ),
        0x8007b310: (
            '8e420074 1040000b 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8e430078 0043102a 14400002 24020001 a262017c c6600130'
        ),
        0x8007cb2c: (
            '8c8200c0 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c8300c4 0043102a 14400084 00001021 8e440038 0c03ca62'
        ),
        0x800afd44: (
            '3c028014 245588a0 3c028014 24548060 8c6275d8 8c430004 00111080 00431021 '
            '8c500000 96020000 54560025 3c038013 8e020060 10400004'
        ),
        0x800c55d8: (
            '3c028014 245e88a0 3c028014 24578060 3c028011 2455c000 8eb10000 8e220030 '
            '18400004 24040001 005e1021 9042ffff 0002202b 8e220034'
        ),
        0x800c75c4: (
            '3c028014 03e00008 00001021 24428060 2483ffff 00031880 00621821 8c620000 '
            '03e00008 ac650000 14800003 3c028014 03e00008 00001021'
        ),
        0x800c75f0: (
            '3c028014 03e00008 00001021 24428060 2483ffff 00031880 00621821 8c620000 '
            '00451021 03e00008 ac620000 14800003 3c038014 03e00008'
        ),
        0x800c7620: (
            '3c038014 03e00008 00001021 24638060 2482ffff 00021080 00431021 8c420000 '
            '03e00008 00000000 3c028014 244299f8 00822021 90820000'
        ),
        0x800d98c0: (
            '8c820064 1040000f 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c830068 0043102a 10400007 02002021 96640016 0c00fb5d'
        ),
        0x800e0be8: (
            '8c82012c 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c830130 0043102a 1440002a 00000000 92a200b3 14400015'
        ),
        0x800e3c10: (
            '8c820120 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c830124 0043102a 14400068 00000000 924300b2 24020003'
        ),
        0x800e3c74: (
            '8c8200cc 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c8300d0 0043102a 1440004f 00000000 8e440038 0c03ca1f'
        ),
        0x800e8084: (
            '8c820064 1040000f 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c830068 0043102a 10400006 00000000 96840016 0c00fb5d'
        ),
        0x800ecd5c: (
            '8ca2008c 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8ca30090 0043102a 14400011 24020001 44050000 0c03b1bc'
        ),
        0x800ecf30: (
            '8c820038 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c83003c 0043102a 14400075 24020001 8e030000 8c620030'
        ),
        0x800edc20: (
            '3c028014 3c038014 90a2c2f7 24638060 2442ffff 00021080 00431021 8c420000 '
            '00041823 0043102a 1440000c 00001021 03e00008 00000000'
        ),
        0x800edc50: (
            '03e00008 00000000 90a3c2f7 24428060 2463ffff 00031880 00621821 8c630000 '
            '0064182a 1460fff6 00001021 03e00008 24020001 00001021'
        ),
        0x800f32b4: (
            '245e88a0 3c028014 afb7006c 24578060 afbf0074 afb50064 afb3005c afb20058 '
            'afb00050 8e220024 24150001 24530054 24500058 8e240024'
        ),
        0x800f3d0c: (
            '8e22002c 1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8e230030 0043102a 144000ef 00001021 8e24003c 10800005'
        ),
        0x800f3d58: (
            '8e230034 10600009 3c028014 24428060 2463ffff 00031880 00621821 8c620000 '
            '8e240038 00441021 ac620000 96020000 2443ffe6 2c620035'
        ),
        0x800f3ff4: (
            '8c820050 1040000d 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8c830054 0043102a 14400004 00000000 a3a00018 0803d010'
        ),
        0x800f41f4: (
            '92a200fe 1040000c 3c038014 24638060 2442ffff 00021080 00431021 8c420000 '
            '8ea30100 0043102a 10400003 00000000 0803d120 241e0001'
        ),
        0x800f9ff8: (
            '245488a0 3c028014 afb3001c 24538060 afb00010 2630000d afbf0024 92050001 '
            '24020001 54a20037 26520001 9202ffff 10400005 00000000'
        ),
        0x800fa3e8: (
            '34420080 ae22ca1c 3c048014 24848060 00002821 24060200 3c028013 a0407cf4 '
            '3c028014 a0408890 3c028014 a0408925 3c028014 a0408838'
        ),
    }
    base_sites = {
        0x80065880: 0x24638060,
        0x800658e0: 0x24638060,
        0x80065934: 0x24428060,
        0x80065958: 0x24428060,
        0x800659d0: 0x24638060,
        0x80065a18: 0x24428060,
        0x8007b31c: 0x24638060,
        0x8007cb38: 0x24638060,
        0x800afd50: 0x24548060,
        0x800c55e4: 0x24578060,
        0x800c75d0: 0x24428060,
        0x800c75fc: 0x24428060,
        0x800c762c: 0x24638060,
        0x800d98cc: 0x24638060,
        0x800e0bf4: 0x24638060,
        0x800e3c1c: 0x24638060,
        0x800e3c80: 0x24638060,
        0x800e8090: 0x24638060,
        0x800ecd68: 0x24638060,
        0x800ecf3c: 0x24638060,
        0x800edc2c: 0x24638060,
        0x800edc5c: 0x24428060,
        0x800f32c0: 0x24578060,
        0x800f3d18: 0x24638060,
        0x800f3d64: 0x24428060,
        0x800f4000: 0x24638060,
        0x800f4200: 0x24638060,
        0x800f435c: 0x24428060,
        0x800fa004: 0x24538060,
        0x800fa3f4: 0x24848060,
    }
    expected = {int(pc,16):int(value,16) for pc,value in contract['instruction_checks'].items()}
    for start, words in spans.items():
        expected.update({start+4*i:int(value,16) for i,value in enumerate(words.split())})
    expected.update(base_sites)
    for pc, value in expected.items():
        if elf_word(elf, pc) != value:
            raise ValueError(f'level6 safety instruction changed at {pc:08x}')
    found = {pc:elf_word(elf,pc) for start,end in
             ((0x80000440,0x800a5130),(0x800a5130,0x8010b6d0))
             for pc in range(start,end,4)
             if elf_word(elf,pc) >> 26 == 9 and elf_word(elf,pc) & 65535 == 0x8060}
    if found != base_sites:
        raise ValueError('counter-base candidate census changed')
    classes = {
        'DAT condition read, subtype-dispatched; source offsets64/38': [0x80065880,0x800658e0],
        'effect read/modify/write, input selectors': [0x80065934,0x80065958,0x80065a18,0x800f3d64,0x800f435c],
        'DAT trigger condition read, offset2c': [0x800659d0],
        'NPC/actor condition read, runtime descriptor; reachability unresolved':
            [0x8007b31c,0x8007cb38,0x800d98cc,0x800e0bf4,0x800e3c1c,0x800e3c80,
             0x800e8090,0x800ecd68,0x800ecf3c,0x800f3d18,0x800f4000,0x800f4200],
        'scene activation indexed read, DAT64': [0x800afd50],
        'radar condition indexed read, contact34/40': [0x800c55e4],
        'public set/add/get, parameter selector': [0x800c75d0,0x800c75fc,0x800c762c],
        'music condition read, request-dependent selector': [0x800edc2c,0x800edc5c],
        'typed script opcode3, float selector converted to integer': [0x800f32c0],
        'objective handle indexed read, record+6': [0x800fa004],
        'initialization, memset512 bytes': [0x800fa3f4],
    }
    if sorted(pc for sites in classes.values() for pc in sites) != sorted(found):
        raise ValueError('unclassified or duplicated counter-base candidate')
    controls = {}
    for label, counters, booleans in (
        ('below', {50:3,99:1}, {}), ('threshold', {50:4,99:1}, {}),
        ('latched', {50:4,99:1}, {99:1}), ('one_stage', {50:4}, {}),
        ('both_stages', {50:4,98:6}, {}), ('failure', {34:1,50:4,99:1}, {}),
        ('counter90_only', {90:1}, {})):
        controls[label] = run_level6_original_slice(elf,counters,booleans)
    if not (controls['below']['hud_bits'] == 0 and controls['threshold']['hud_bits'] == 8
            and controls['threshold']['counts'][99] == 2 and controls['threshold']['booleans'][99] == 1
            and controls['latched']['hud_bits'] == 0 and controls['one_stage']['hud_bits'] == 0
            and controls['one_stage']['counts'][99] == 1 and controls['both_stages']['hud_bits'] == 8
            and controls['failure']['hud_bits'] == 4 and controls['counter90_only']['hud_bits'] == 0):
        raise ValueError('original c50->Boolean99->counter99->Bit8 control failed')
    fallback = run_level6_original_slice(elf, fallback=True)
    if (fallback['health'], fallback['counts'][50], fallback['counts'][90]) != (490,1,1):
        raise ValueError('FFFF ordinary-request eager effect control failed')
    margin_hit = run_level6_original_slice(elf, {50:3,99:1}, fallback=True)
    margin_callback = run_level6_original_slice(elf, margin_hit['counts'])
    if margin_callback['hud_bits'] != 8:
        raise ValueError('FFFF request at c50 margin did not reach original Bit8 gate')
    # Table dispatch makes the +64 field typed, rather than a raw-word search.
    typed = []
    for row in rows:
        if row['kind'] != 0 or not 12 <= row['subtype'] <= 82:
            continue
        target = elf_word(elf,0x8003c140+4*(row['subtype']-12))
        if target not in (0x80065854,0x800658ac):
            continue
        field = 0x64 if target == 0x80065854 else 0x38
        selector = row['words'][f'{field:02x}']
        typed.append(dict(name=row['name'],offset=row['offset'],subtype=row['subtype'],
                          dispatch=f'{target:08x}',field=f'{field:02x}',counter=selector,
                          threshold=row['words'][f'{field+4:02x}']))
    getters = []
    for start, end in ((0x80000440,0x800a5130),(0x800a5130,0x8010b6d0)):
        for pc in range(start,end,4):
            if elf_word(elf,pc) != 0x0c031d87:
                continue
            selector, evidence = None, None
            for at in range(pc+4,max(start,pc-32)-1,-4):
                value = elf_word(elf,at)
                op, rt, rd = value >> 26, value >> 16 & 31, value >> 11 & 31
                if op in (2,3,4,5,6,7) or (op == 0 and value & 63 in (8,9)):
                    if at != pc:
                        break
                    continue
                if op in (9,13) and rt == 4 and (value >> 21 & 31) == 0:
                    selector, evidence = value & 65535, f'{at:08x}'
                    break
                if (op in (9,13,15,32,33,35,36,37) and rt == 4) or (op == 0 and rd == 4):
                    break
            getters.append(dict(pc=f'{pc:08x}',counter=selector,constant_at=evidence,
                                classification='constant selector' if selector is not None else 'unresolved reaching definition'))
    condition_summary = Counter((r['counter'],r['threshold']) for r in typed)
    if condition_summary != Counter({(0,0):154,(17,1):4,(18,1):3,(19,1):3,(16,1):2,(14,1):1}):
        raise ValueError('typed level6 DAT condition census changed')
    contract['instruction_checks'] = {f'{pc:08x}':f'{value:08x}' for pc,value in sorted(expected.items())}
    contract['safety_audit'] = dict(
        selection='H-unresolved: no complete consumer graph or live fallback safety admission',
        base_candidates=[dict(pc=f'{pc:08x}',classification=kind) for kind,sites in classes.items() for pc in sites],
        census_scope='Every ADDIU immediate8060 in resident text and mission overlay. Not an alias/pointer proof; shifted bases and indirect calls remain outside the census.',
        original_slice_controls=controls, fallback_control=fallback,
        fallback_margin_control=dict(hit=margin_hit,callback=margin_callback),
        direct_getter_calls=getters,
        typed_DAT_conditions=typed,
        typed_counter90_conditions=[r for r in typed if r['counter']==90],
        script_edge=dict(dispatch_table='800a8a20',opcode=3,entry='800f339c',read='800f33bc',
                         selector='trunc.w.s(record+0x58+16*i)',threshold='trunc.w.s(record+0x5c+16*i)',
                         effect='counter >= threshold selects pipe-delimited DAT name; no direct terminal store in this slice',
                         unresolved='owner at effect-context+24 and its original constructor/record bounds not yet joined to retail DAT'),
        handle_edge=dict(selector='byte at record+6',threshold='signed word record+8',
                         effect='mode0 >= threshold, mode1 < threshold; calls record function pointer',
                         level6_initializer_counters=[20,21,13,0],
                         unresolved='other handle producers/callback reachability not exhaustively qualified'),
        unresolved=['Runtime descriptor selectors at NPC/actor, radar, music and effect readers need typed ownership proofs.',
                    'Script owner+24 constructor and embedded records need typed retail DAT join.',
                    'Aliases, shifted base materializations, indirect getObjectiveCount callers and other handle producers are not excluded.'],
        safety='FFFF API10 changes c50 AND c90 with health500->490. Repeated requests can reach c50==4 success-stage gate; no destruction boundary protects it. No live request authorized.',
        evidence='Original ELF instructions and retail DAT fields corroborate static contracts; slice execution is same-source, not independent hardware/runtime evidence.')
    return contract


def decode_type3_scripts(rows):
    names = {}
    for row in rows:
        if row['name']:
            names.setdefault(row['name'], []).append(row)
    result = []
    for row in rows:
        if row['kind'] != 3 or row['subtype'] != 3:
            continue
        raw = b''.join(struct.pack('>I', row['words'][f'{i:02x}'])
                       for i in range(0, row['size'] - 3, 4))
        if len(raw) != row['size'] or len(raw) < 0xd4:
            raise ValueError('type3 script slots exceed record')
        slots = []
        for index in range(8):
            at = 0x54 + 16 * index
            opcode, a, b, relative = struct.unpack_from('>IffI', raw, at)
            slot = dict(index=index, opcode=opcode, operand_words=[word(raw, at+4), word(raw, at+8)],
                        token_offset=relative, targets=[])
            if opcode == 3:
                if not all(math.isfinite(x) and -2147483648 <= x < 2147483648 for x in (a,b)):
                    raise ValueError('script float outside TRUNC.W.S qualified domain')
                slot.update(counter=int(a), threshold=int(b), reads_counter=int(a) > 0)
            if opcode in (1,2,3,4,5,7):
                if not 0xd4 <= relative < len(raw) or b'\0' not in raw[relative+1:]:
                    raise ValueError('script token outside owning record')
                token = raw[relative+1:].split(b'\0', 1)[0].decode('ascii')
                slot.update(token_count=raw[relative], token=token)
                for name in token.split('|'):
                    matches = names.get(name, [])
                    slot['targets'].append(dict(name=name,
                        matches=[dict(offset=r['offset'], kind=r['kind'], subtype=r['subtype']) for r in matches]))
            slots.append(slot)
        result.append(dict(name=row['name'], offset=row['offset'], size=row['size'],
                           slots=slots, field50=word(raw,0x50),
                           completion_effect=dict(counter=word(raw,0x40), delta=word(raw,0x44),
                                                  boolean=word(raw,0x48), value=word(raw,0x4c))))
    return result


def level6_scripts_contract(elf, rows):
    spans = {
        0x800f947c: (
            '27bdffd8 00804021 afb00018 00a08021 24020001 afb1001c 25110008 afbf0020 '
            'a1020112 ae300024 ae200028 8e02001c 44861000 3c01800b c4248f2c ad020008 '
            '8e020020 ae220004 8e04001c 8e030020 ae200014 ae200010 ae20000c ae200034 '
            'ae200020 ae200018 e624001c e6220048 e6220050 00041040 00441021 00021080 '
            '00621821 ae230008'
        ),
        0x800f9674: (
            '27bdffd8 00804021 afb1001c 00a08821 24020001 afb00018 25100008 afbf0020 '
            'a1020112 ae110024 ae000028 8e22001c 44861000 3c01800b c4248f48 ad020008 '
            '8e220020 ae020004 8e24001c 8e230020 ae000014 ae000010 ae00000c ae000034 '
            'ae000020 ae000018 e604001c e6020048 e6020050 00041040 00441021 00021080 '
            '00621821 ae030008'
        ),
        0x80046abc: (
            '8e420018 1040001f 00008821 8e42001c 8e430018 02422821 1060001b ae45001c '
            '00a02021 8c820000 00a21821 ac830000 8c62000c 10400002 00621021 ac62000c '
            '8c620020 10400002 00621021 ac620020 8c620028 10400004 00000000 8c62002c '
            '00621021 ac62002c 8e420018 26310001 0222102b 1440ffeb 24840004 08011ad1 '
            '00000000 ae40001c'
        ),
        0x800f3290: (
            '27bdff88 afb60068 0080b021 afb10054 00a08821 afb40060 0000a021 3c028014 '
            'afbe0070 245e88a0 3c028014 afb7006c 24578060 afbf0074 afb50064 afb3005c '
            'afb20058 afb00050 8e220024 24150001 24530054 24500058 8e240024 8e020008 '
            '8e630000 00829021 2463ffff 2c620007 1040005f 00031080 3c07800b 24e78a20 '
            '00471021 8c420000 00400008 00000000 c6000000 8e230034 4600010d 44022000 '
            '0043102a 14400056 26100010 0803cd28 00000000 c6000000 4600010d 44052000 '
            '14a00003 28a20081 0803ccdf 24020001 10400004 00be1021 9042ffff 0803ccdf '
            '0002102b 0c03cc96 02c02021 c6000004 304300ff 4600010d 44022000 14620040 '
            '26100010 0803ccfd 02402021 c6000000 4600010d 44022000 18400038 2442ffff '
            '00021080 00571021 c6000004 8c420000 4600010d 44032000 0043102a 14400030 '
            '26100010 0803ccfd 02402021 02402021 0c03cc51 27a50010 0803cd00 00000000 '
            '02402021 00002821 0c03cc2b 27a60010 0c011ed2 27a40010 ae220028 24020001 '
            '0803cd2b ae200034 c6000000 4600010d 44022000 50550001 a2d501a5 0803cd2b '
            '00001021 02402021 00002821 0c03cc2b 27a60010 0c011ed2 27a40010 ae220028 '
            'ae200034 c6000000 e6200104 8c420050 14550012 24020001 c6200014 3c01800b '
            'c4228a3c 46020000 0803cd2b e6200014 ae240028 0803cd2b 24020001 26100010 '
            '26940001 2a820008 1440ff93 26730010 8e230024 24020001 ae230028'
        ),
        0x800f30ac: (
            '24840001 90820000 10400020 00001821 2407007c 24a80001 14470003 00000000 '
            '0803cc38 24840001 90820001 14400002 00000000 24630001 54650011 24840001 '
            '90820000 50400009 a0c00000 50470007 a0c00000 24840001 a0c20000 90820000 '
            '1440fffa 24c60001 a0c00000 90830000 10600007 00001021 03e00008 01001021 '
            '90820000 1440ffe4 00000000 00001021 03e00008 00000000'
        ),
        0x800f3144: (
            '27bdffe0 afb00010 00808021 afbf0018 afb10014 92020000 10400037 00a08821 '
            '0c000d0c 00000000 02202821'
        ),
        0x800d9604: (
            '8e220094 00512021 90830000 2402002d 1062001b 3c028014 0c011ed2 00000000 '
            '8e050034 c4a000a0 e7a00010 8e030034 3c01800a c4207a54 c46200a4 e7a00018 '
            'e7a20014 8e040038 8ca60098 8ca700a8 0c03e51f 00402821'
        ),
        0x800f4110: (
            'afb7018c 0080b821'
        ),
        0x800f4150: (
            '0c010057 26f50008'
        ),
        0x800f4340: (
            '8ea20034 8ea50024 24420001 aea20034 8ca30040 10600009 3c028014 24428060 '
            '2463ffff 00031880 00621821 8c620000 8ca40044 00441021 ac620000 8ca40048 '
            '10800005 3c028014 244288a0 90a3004f 00821021 a043ffff 02e02021 0c03cca4 '
            '02a02821'
        ),
        0x800f43ec: (
            'c6a00048 aea20024 8ea30024 8ea50024 26a600d0 aea00028'
        ),
    }
    expected = {start+4*i:int(value,16) for start,values in spans.items()
                for i,value in enumerate(values.split())}
    for pc,value in expected.items():
        if elf_word(elf,pc) != value:
            raise ValueError(f'type3 ownership instruction changed at {pc:08x}')
    scripts = decode_type3_scripts(rows)
    active = [(r['name'],s['index'],s['opcode'],s.get('token'))
              for r in scripts for s in r['slots'] if s['opcode']]
    if len(scripts) != 21 or active != [
            ('ATAT_Spline_01',0,5,'ATAT_Spline_02'),
            ('Wingman_Spline_01',0,5,'Wingman_Loop'),
            ('Shuttle_Escape_01',0,6,None)]:
        raise ValueError('level6 typed script census changed')
    if any(r['completion_effect']['counter'] or r['completion_effect']['boolean'] for r in scripts):
        raise ValueError('level6 type3 completion effect selector changed')
    for record in scripts:
        for slot in record['slots']:
            for target in slot['targets']:
                if len(target['matches']) != 1 or target['matches'][0]['kind'] != 3:
                    raise ValueError('level6 script target not uniquely owned type3')
    contract = level6_safety_contract(elf, rows)
    contract['instruction_checks'].update({f'{pc:08x}':f'{v:08x}' for pc,v in expected.items()})
    audit = contract['safety_audit']
    audit['script_edge'] = dict(
        selection='H-DAT for kind3/subtype3 script sources; no full counter90 safety proof',
        constructors=['800f94a0','800f9698'], context='actor+8', source='context+24 = unmodified a1',
        named_source_example='800d9604..9658: DAT+94 relative name -> getLevelDatItemByName -> constructor a1',
        relocation='80046abc..6b40: DAT header18/1c count/table; table-relative records; only record0c/20/2c relocated',
        bounds='eight fixed slots at record54+16*i, end-exclusive d4; field50 is not a count',
        selector='opcode3 trunc.w.s(record58+16*i); <=0 skips read; positive counter >= trunc.w.s(record5c+16*i)',
        tokens='record-relative offset60+16*i; copyPipeDelimitedField skips leading count byte',
        transition='resolver stores named lookup in context28; executor43f0 copies it to context24',
        scripts=scripts, opcode3_slots=[], completion_effects_enabled=0,
        unresolved='No dynamic activation proof or exhaustive constructor-argument proof. Other subtypes, arbitrary named-source API inputs and other computed reader families are outside this census.')
    audit['unresolved'] = [x for x in audit['unresolved'] if not x.startswith('Script owner+24')]
    audit['unresolved'].append('Typed type3 script family closed statically for level6; constructor live arguments and other record kinds remain unqualified.')
    return contract


def check_script_decoder_controls(rom):
    data,_ = extract(rom,1)
    rows = inventory(data)
    def selected(current):
        return next(r for r in decode_type3_scripts(current) if r['name']=='x_wing_vs_probe_d')['slots'][0]
    control = selected(rows)
    if (control['opcode'],control['counter'],control['threshold'],control['token']) != (3,10,3,'x_wing_to_rendezvous'):
        raise ValueError('retail nonzero opcode3 control failed')
    if len(control['targets'][0]['matches']) != 1 or control['targets'][0]['matches'][0]['kind'] != 3:
        raise ValueError('retail nonzero control target join failed')
    owner = next(r for r in rows if r['name']=='x_wing_vs_probe_d')
    start = int(owner['offset'],16)
    controls = []
    for value,wanted in ((90.0,90),(10.75,10),(-1.75,-1),(0.0,0)):
        changed=bytearray(data)
        struct.pack_into('>f',changed,start+0x58,value)
        slot=selected(inventory(changed))
        if slot['counter'] != wanted or slot['reads_counter'] != (wanted>0):
            raise AssertionError('script selector sensitivity/truncation control failed')
        controls.append(dict(input=value,counter=slot['counter'],reads_counter=slot['reads_counter']))
    rejected=[]
    for label,field,value in (('token OOB',0x60,owner['size']),('token in header',0x60,0x40),
                              ('nonfinite selector',0x58,0x7fc00000)):
        changed=bytearray(data);struct.pack_into('>I',changed,start+field,value)
        try:
            selected(inventory(changed))
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('accepted '+label)
    changed=bytearray(data)
    struct.pack_into('>I',changed,start+0xc4,3)
    struct.pack_into('>ffI',changed,start+0xc8,90.0,1.0,owner['words']['60'])
    last=next(r for r in decode_type3_scripts(inventory(changed)) if r['name']==owner['name'])['slots'][7]
    if last['counter']!=90 or last['token']!=control['token']:
        raise AssertionError('eighth script slot control failed')
    return dict(retail_level=1,nonzero_control=control,selector_controls=controls,
                last_slot_control=last,rejected=rejected,
                evidence='retail bytes and original ELF contracts; synthetic decoder mutations are same-source, not runtime evidence')


def decode_spline_events(rows):
    tables = {kind: {r['index']: r for r in rows if r['kind'] == kind} for kind in (3,7)}
    decoded = []
    for row in tables[3].values():
        if row['subtype'] != 3:
            continue
        raw = b''.join(struct.pack('>I', row['words'][f'{i:02x}'])
                       for i in range(0, row['size'] - 3, 4))
        if len(raw) < 0xdc or len(raw) != row['size']:
            raise ValueError('spline event header outside record')
        count, events_at = word(raw,0x28), word(raw,0x2c)
        remap_count, relative = struct.unpack_from('>II',raw,0xd4)
        remap_at = 0xd4 + relative
        points_at = word(raw,0x20)
        if (relative < 8 or remap_at + 4*remap_count != points_at
                or points_at > len(raw)):
            raise ValueError('spline remap span does not end at point array')
        if count and (events_at < points_at or events_at + 8*count > len(raw)):
            raise ValueError('spline events outside owning record')
        events = []
        for index in range(count):
            at = events_at + 8*index
            time, unused, remap_index = struct.unpack_from('>fHH',raw,at)
            if not math.isfinite(time) or remap_index >= remap_count:
                raise ValueError('spline event time/remap index outside qualified domain')
            mapped_at = remap_at + 4*remap_index
            kind, target_index = struct.unpack_from('>HH',raw,mapped_at)
            if kind != 7 or target_index not in tables[7]:
                raise ValueError('spline remap does not select an owned kind7 record')
            target = tables[7][target_index]
            if target['size'] < 0x44:
                raise ValueError('spline effect common prefix outside target')
            fields = {label: target['words'][f'{offset:02x}'] for label,offset in
                      (('boolean_condition',0x28),('counter',0x2c),('threshold',0x30),
                       ('effect_counter',0x34),('delta',0x38),('effect_boolean',0x3c),('value',0x40))}
            events.append(dict(index=index,at=at,time=time,unused=unused,remap_index=remap_index,
                               remap_at=mapped_at,kind=kind,target_index=target_index,
                               target_offset=target['offset'],target_name=target['name'],
                               subtype=target['subtype'],fields=fields,
                               reads_counter=fields['counter'] != 0,
                               writes_counter=fields['effect_counter'] != 0))
        decoded.append(dict(name=row['name'],offset=row['offset'],size=row['size'],
                            count=count,events_at=events_at,remap_at=remap_at,
                            remap_count=remap_count,points_at=points_at,events=events))
    return decoded


def level6_events_contract(elf, rows):
    spans = {
        0x80046c24: (
            '8e420038 10400017 00008821 8e42003c 8e430038 02422821 10600013 ae45003c '
            '3406ffff 00a02021 8c820000 00a21821 ac830000 8c62000c 10400003 00621021 '
            'ac62000c a4660006 8e420038 26310001 0222102b 1440fff4 24840004 08011b23 '
            '00000000 ae40003c '
        ),
        0x800f4450: (
            'e6b40014 aea0003c 8c620028 10400005 00000000 8c62002c c4400000 0803d120 '
            'e6a00040 3c01800b c4208bd4 e6a00040 '
        ),
        0x800f4648: (
            'c6a20030 c6a00040 4602003e 00000000 45000026 00000000 8ea30024 8c6400d8 '
            '8ea2003c 248400d4 00642021 8c63002c 000210c0 00431021 3c038013 94420006 '
            '8c6375d8 00021080 00441021 94420002 8c63003c 00021080 00431021 8c450000 '
            '0c03cf2c 02e02021 8ea3003c 8ea50024 24640001 aea4003c 8ca30028 0083182a '
            '10600007 a3a20168 8ca2002c 000418c0 00621821 c4600000 0803d1bd e6a00040 '
            '3c01800b c4208be0 e6a00040 '
        ),
        0x800f3cb0: (
            '27bdffc0 afb20038 00809021 afb00030 00a08021 afbf003c afb10034 8e050028 '
            '10a0000e 02008821 28a20081 10400006 3c028014 244288a0 00a21021 9042ffff '
            '0803cf40 0002102b 0c03cc96 02402021 304200ff 104000fb 00001021 8e22002c '
            '1040000a 3c038014 24638060 2442ffff 00021080 00431021 8c420000 8e230030 '
            '0043102a 144000ef 00001021 8e24003c 10800005 3c028014 244288a0 92230043 '
            '00821021 a043ffff 8e230034 10600009 3c028014 24428060 2463ffff 00031880 '
            '00621821 8c620000 8e240038 00441021 ac620000 96020000 2443ffe6 2c620035 '
            '104000d7 3c02800b 24428ac8 00031880 00621821 8c620000 00400008 00000000 '
        ),
    }
    expected = {start+4*i:int(value,16) for start,values in spans.items()
                for i,value in enumerate(values.split())}
    for pc,value in expected.items():
        if elf_word(elf,pc) != value:
            raise ValueError(f'spline event instruction changed at {pc:08x}')
    decoded = decode_spline_events(rows)
    signature = [(r['name'],e['index'],e['remap_index'],e['target_index'],e['subtype'])
                 for r in decoded for e in r['events']]
    wanted = [('Wingman_Spline_01',0,0,46,27),('Wingman_Spline_01',1,1,47,27),
              ('Shuttle_Escape_01',0,1,42,34),('Shuttle_Escape_01',1,4,39,27),
              ('Shuttle_Escape_01',2,0,38,26),('Shuttle_Escape_01',3,3,40,27),
              ('Shuttle_Escape_01',4,2,41,27),('AT_ST_Spline_01',0,0,44,34),
              ('AT_ST_Spline_02',0,0,45,34),('Hangar_ATST_Spline_01',0,0,48,34)]
    if len(decoded) != 21 or signature != wanted:
        raise ValueError('level6 spline event ownership census changed')
    for record in decoded:
        for event in record['events']:
            if event['fields'] != dict(boolean_condition=0,counter=0,threshold=0,
                                      effect_counter=0,delta=1,effect_boolean=0,value=1):
                raise ValueError('level6 spline event common effect changed')
    contract = level6_scripts_contract(elf,rows)
    contract['instruction_checks'].update({f'{pc:08x}':f'{v:08x}' for pc,v in expected.items()})
    contract['safety_audit']['spline_events'] = dict(
        selection='H-typed for kind3/subtype3 spline events; no complete counter90 safety proof',
        source='context24; source28 count/source2c relocated event array, stride8, event+6 unsigned remap index',
        remap='source+d4+word(source+d8)+4*index; halfword+2 selects DAT header3c kind7 table',
        bounds='Offline file bounds only: remap span ends at source20 point array; every event/index/target is within its owner. Original consumer does not enforce remap bounds.',
        relocation='46c24..6c88 relocates kind7 table, table-relative records and names only; common selectors stay unmodified',
        prefix='F3CB0 uses unshifted a1: +28 Boolean gate, +2c counter >= signed +30, +34 counter += +38, +3c Boolean := byte+43; all before subtype dispatchF3D84',
        records=decoded,events=10,enabled_counter_conditions=0,enabled_counter_effects=0,
        unresolved='Static typed inputs only; no live activation/all-constructor-arguments proof. Other kind7 producers, subtype-specific effects and NPC/radar/music/handle readers remain outside this closure.')
    return contract


def check_event_decoder_controls(rom):
    data,_ = extract(rom,3)
    rows = inventory(data)
    def event(current,name,index):
        return next(r for r in decode_spline_events(current) if r['name']==name)['events'][index]
    condition = event(rows,'Madine_TO',0)
    effect = event(rows,'CS_New_Wedge',0)
    if (condition['target_index'],condition['fields']['counter'],condition['fields']['threshold'],
            effect['target_index'],effect['fields']['effect_counter'],effect['fields']['delta']) != (88,26,3,54,16,1):
        raise ValueError('retail nonzero spline event controls failed')
    changed = bytearray(data)
    struct.pack_into('>I',changed,int(condition['target_offset'],16)+0x2c,90)
    struct.pack_into('>I',changed,int(effect['target_offset'],16)+0x34,90)
    c,e = event(inventory(changed),'Madine_TO',0),event(inventory(changed),'CS_New_Wedge',0)
    if c['fields']['counter'] != 90 or e['fields']['effect_counter'] != 90:
        raise AssertionError('synthetic spline counter90 not detected')
    disabled = bytearray(data)
    struct.pack_into('>I',disabled,int(condition['target_offset'],16)+0x2c,0)
    struct.pack_into('>I',disabled,int(effect['target_offset'],16)+0x34,0)
    if event(inventory(disabled),'Madine_TO',0)['reads_counter'] or event(inventory(disabled),'CS_New_Wedge',0)['writes_counter']:
        raise AssertionError('disabled spline selector treated as enabled')
    owner = next(r for r in decode_spline_events(rows) if r['name']=='Madine_TO')
    at = int(owner['offset'],16)
    rejected=[]
    for label,offset,fmt,value in (
            ('event span OOB',0x2c,'I',owner['size']),
            ('remap span OOB',0xd8,'I',owner['size']),
            ('remap count',0xd4,'I',owner['remap_count']+1),
            ('event index OOB',condition['at']+6,'H',owner['remap_count']),
            ('remap kind',condition['remap_at'],'H',6),
            ('target index OOB',condition['remap_at']+2,'H',65535),
            ('nonfinite time',condition['at'],'I',0x7fc00000)):
        mutated=bytearray(data);struct.pack_into('>'+fmt,mutated,at+offset,value)
        try:
            decode_spline_events(inventory(mutated))
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('accepted '+label)
    return dict(retail_level=3,condition_control=condition,effect_control=effect,
                synthetic90=dict(condition=c,effect=e),disabled_selectors=True,rejected=rejected,
                evidence='Retail DAT and original instructions support static interpretation only; controls are not live/hardware evidence')



def decode_pending_song_sources(rows):
    decoded = []
    for row in rows:
        if row['kind'] not in (0, 6) or row['subtype'] != 16:
            continue
        if row['size'] < 0xac:
            raise ValueError('short subtype16 pending-song owner')
        fields = row['words']
        threshold = fields['a0']
        threshold = threshold if threshold < 0x80000000 else threshold-0x100000000
        decoded.append(dict(kind=row['kind'], index=row['index'], name=row['name'],
                            offset=row['offset'], subtype=16,
                            eager_spawn=bool(fields['34'] & 0x80),
                            handler_boolean=fields['84'], handler_value=fields['88'],
                            handler_counter=fields['8c'], handler_threshold=fields['90'],
                            pending_boolean=fields['94'] & 255,
                            pending_value=fields['98'] & 255,
                            counter=fields['9c'] & 255, threshold=threshold,
                            predicate='count < -threshold' if threshold < 0 else 'count >= threshold'))
    return decoded


def run_pending_song_slice(elf, row, count=0, boolean=1, pending=True):
    """Execute original selector transfers and reader, excluding scheduling/spatial gates."""
    memory, regs, stores = {}, [0]*32, []
    def put(at, value, size):
        for i in range(size):
            memory[at+i] = (value >> (8*(size-1-i))) & 255
    def get(at, size):
        try:
            return int.from_bytes(bytes(memory[at+i] for i in range(size)), 'big')
        except KeyError:
            raise ValueError(f'uninitialized pending-song slice read {at:08x}') from None
    def signed(value):
        return value if value < 0x80000000 else value-0x100000000
    def step(pc, delay=False):
        w=elf_word(elf,pc)
        op,rs,rt,rd=w>>26,w>>21&31,w>>16&31,w>>11&31
        imm=w&65535; imm=imm if imm<32768 else imm-65536
        target=None
        if op == 15: regs[rt]=(w&65535)<<16
        elif op == 9: regs[rt]=(regs[rs]+imm)&0xffffffff
        elif op in (35,36): regs[rt]=get((regs[rs]+imm)&0xffffffff,4 if op==35 else 1)
        elif op in (40,43):
            at=(regs[rs]+imm)&0xffffffff; size=1 if op==40 else 4
            put(at,regs[rt],size); stores.append(dict(pc=f'{pc:08x}',address=f'{at:08x}',size=size,value=regs[rt]))
        elif op == 0:
            fn=w&63
            if fn==0: regs[rd]=(regs[rt]<<(w>>6&31))&0xffffffff
            elif fn==0x21: regs[rd]=(regs[rs]+regs[rt])&0xffffffff
            elif fn==0x23: regs[rd]=(regs[rs]-regs[rt])&0xffffffff
            elif fn==0x2a: regs[rd]=int(signed(regs[rs])<signed(regs[rt]))
            elif fn==0x2b: regs[rd]=int(regs[rs]<regs[rt])
            elif fn==8: target=regs[rs]
            else: raise ValueError(f'unsupported pending-song special {pc:08x}')
        elif op in (4,5):
            take=(regs[rs]==regs[rt])==(op==4)
            target=pc+4+imm*4 if take else pc+8
        elif op==1 and rt==1:
            target=pc+4+imm*4 if signed(regs[rs])>=0 else pc+8
        else: raise ValueError(f'unsupported pending-song instruction {pc:08x}:{w:08x}')
        regs[0]=0
        if target is not None:
            if delay: raise ValueError('transfer in delay slot')
            step(pc+4,True)
            return target
        return pc+4
    dat, stack, request=0x80200000,0x81001000,0x8010c230
    for field,value in row['words'].items(): put(dat+int(field,16),value,4)
    for i in range(0x40): put(stack+0x38+i,0,1)
    for i in range(0x30): put(request+i,0,1)
    regs[4],regs[29],regs[3]=dat,stack,1
    for pc in range(0x800ecbc8,0x800ecbf0,4): step(pc)
    regs[16],regs[4]=stack+0x38,request
    for pc in range(0x800ef724,0x800ef74c,4): step(pc)
    regs[16]=request
    for pc in range(0x800ee16c,0x800ee19c,4): step(pc)
    step(0x800ee1a0)
    selector=get(0x8010c2f7,1); threshold=get(0x8010c2f8,4)
    put(0x8010c2f1,int(pending),1)
    if selector: put(0x80138060+4*(selector-1),count,4)
    bool_selector=get(0x8010c2f5,1)
    if bool_selector: put(0x801388a0+bool_selector-1,boolean,1)
    regs[31]=0x7ffffffc; pc=0x800edbb0
    for _ in range(100):
        if pc==regs[31]: break
        pc=step(pc)
    else: raise ValueError('pending-song reader budget exhausted')
    return dict(counter=selector,threshold=signed(threshold),switch=regs[2],stores=stores,
                limitation='Selected original load/store slices plus complete reader; no live spatial gate, scheduler, or song-switch execution')


def level6_music_contract(elf, rows):
    spans = {
        0x80046b44: (
            '8e420030 10400035 00008821 8e420034 8e430030 02429821 10600031 ae530034 '
            '3416ffff 24150004 24140005 02608021 8e020000 02621821 ae030000 8c62000c '
            '10400003 00621021 ac62000c a4760006 94620000 10550005 00000000 1054000e '
            '00000000 08011b01 26100004 '
        ),
        0x8004723c: (
            '8e420030 10400010 00008821 8e420034 00111880 00621821 8c640000 8c820034 '
            '30420080 10400003 00000000 0c0194ed 00000000 8e420030 26310001 0222102b '
            '1440fff2 00000000 '
        ),
        0x800653c8: (
            '96220000 2443fff4 2c620047 1040009e 3c028004 2442bdb8 00031880 00621821 '
            '8c620000 00400008 00000000 '
        ),
        0x80065558: (
            '3c04800f 2484cc28 02202821 24060001 08019599 24070064 '
        ),
        0x80065664: (
            '0c00fffb 00000000 00401821 3070ffff 3c018004 c420bed4 3402ffff 12020006 '
            'e7a00010 a6230006 02002021 24050003 0c00fa37 27a60010 '
        ),
        0x800ecc80: (
            'ae020008 ac860004 c4c00010 e4800008 c4c00014 e480000c c4c00018 00c01821 '
        ),
        0x800ecd30: (
            '8c850004 8ca30084 c4c00000 10600007 3c028014 244288a0 00621021 9043ffff '
            '8ca20088 1462001d 24020001 8ca2008c 1040000a 3c038014 24638060 2442ffff '
            '00021080 00431021 8c420000 8ca30090 0043102a 14400011 24020001 44050000 '
            '0c03b1bc 00000000 '
        ),
        0x800ecbc8: (
            '90820097 a3a2006b 9082009b a3a2006c 9082009f a3a2006d 8c8200a0 27a40038 '
            'a3a30068 afa20070 0c03bd44 00000000 '
        ),
        0x800ec970: (
            '90820097 a3a2006b 9082009b a3a2006c 9082009f a3a2006d 8c8200a0 a3a00068 '
            'afa20070 '
        ),
        0x800ef6d8: (
            '9202002e 2464c230 a0820028 c6000000 e460c230 c6000004 e4800004 8e020008 '
            'ac820018 8e02000c ac82001c 96020022 a4820020 96020024 a4820022 96020026 '
            'a4820024 92020030 a0820026 92020033 a0820029 92020034 a082002a 92020035 '
            '3c058011 a082002b 8e030038 00001021 ac83002c 92060031 24030001 a0a3c262 '
            'a0860027 '
        ),
        0x800ee050: (
            '3c128011 9242c267 145100c0 3c038011 3c138011 2670c230 92020028 1440003a '
            '3c028011 '
        ),
        0x800ee158: (
            'a040c2f3 3c028011 a040c2f2 3c028011 a051c2f1 92030029 3c028011 a043c2f5 '
            '9203002a 3c028011 a043c2f6 9203002b 3c028011 a043c2f7 8e03002c 92040027 '
            '3c028011 14910005 ac43c2f8 3c028011 a040c2fd 3c028011 a040c2fc '
        ),
        0x800edbb0: (
            '3c028011 9043c2f1 24020001 14620024 00001021 3c038011 9062c2f5 1040000b '
            '3c028014 9063c2f5 244288a0 00621821 3c028011 9063ffff 9042c2f6 10620007 '
            '3c058011 03e00008 00001021 3c028011 9042c2f7 1040001f 3c058011 90a2c2f7 '
            '1040001a 3c028011 8c44c2f8 0481000e 3c028014 3c038014 90a2c2f7 24638060 '
            '2442ffff 00021080 00431021 8c420000 00041823 0043102a 1440000c 00001021 '
            '03e00008 00000000 90a3c2f7 24428060 2463ffff 00031880 00621821 8c630000 '
            '0064182a 1460fff6 00001021 03e00008 24020001 00001021 03e00008 00000000 '
        ),
    }
    expected={start+4*i:int(v,16) for start,values in spans.items() for i,v in enumerate(values.split())}
    expected[0x8003bdb8+4*(16-12)]=0x80065558
    for pc,value in expected.items():
        if elf_word(elf,pc)!=value: raise ValueError(f'pending-song instruction changed at {pc:08x}')
    decoded=decode_pending_song_sources(rows)
    wanted=[('MUSICRNG_ATATs','0000fddc',90,-3),('MUSICRNG_ATSTs','0000fed8',91,-1),
            ('MUSICRNG_LevelSettings','0000ffd4',0,0)]
    if [(r['name'],r['offset'],r['counter'],r['threshold']) for r in decoded]!=wanted:
        raise ValueError('level6 pending-song census changed')
    if any(not r['eager_spawn'] or (r['handler_boolean'],r['handler_value'],r['handler_counter'],
            r['handler_threshold'],r['pending_boolean'],r['pending_value'])!=(0,1,0,0,0,1) for r in decoded):
        raise ValueError('level6 pending-song gates changed')
    controls=[]
    for record in decoded:
        row=next(r for r in rows if r['offset']==record['offset'])
        for count in (0,1,2,3,4):
            result=run_pending_song_slice(elf,row,count)
            want=int(count < -record['threshold']) if record['threshold']<0 else 0
            if (result['counter'],result['threshold'],result['switch'])!=(record['counter'],record['threshold'],want):
                raise ValueError('original pending-song reader boundary failed')
            controls.append(dict(name=record['name'],count=count,**result))
    contract=level6_events_contract(elf,rows)
    contract['instruction_checks'].update({f'{pc:08x}':f'{v:08x}' for pc,v in expected.items()})
    contract['safety_audit']['pending_song']=dict(
        selection='H-typed: retail level6 has pending-song counter90; no complete consumer safety proof',
        records=decoded,original_slice_controls=controls,
        ownership='kind6 table header30/34 -> flag34 bit80 -> setup table subtype16 ->65558 ->ECC28; constructor stores unmodified a2 at payload+4; tickECD90 passes same payload toEC6F0',
        copies='DAT+97/+9b/+9f/+a0 -> stack request+33/+34/+35/+38 -> C230+29/+2a/+2b/+2c -> C2F5/F6/F7/F8; selector unsigned low byte, threshold signed word',
        queue_distinction='C170 holds the 0x24-byte song handle/config, C230 holds conditions; copies of C170 toC110/C400 do not supply condition selectors. EED7C builds background-song config, not these C230 fields.',
        effect='With pending state1 and Boolean gate disabled: negative threshold switches while count < -threshold; nonnegative threshold switches at count >= threshold. Both selectors disabled returns0.',
        counter90_consequence='ATATs condition passes at c90=0..2, blocks at >=3, conditional on spatial/handler/pending state. No mission win or live activation inferred.',
        unresolved=['Grid/deferred dynamic activation and arbitrary descriptor/indirect aliases are not exhaustively joined.',
                    'Other NPC/actor/radar/handle readers remain unresolved; FFFF c50/90 eager effect stays inadmissible.'],
        evidence='Original ELF plus retail DAT establish static contracts; slice execution and mutation controls are same-source, not independent dynamic evidence.')
    return contract


def check_music_decoder_controls(elf, rom):
    data,_=extract(rom,1); rows=inventory(data)
    control=next(r for r in rows if r['kind']==6 and r['subtype']==16 and r['name']=='MUSICRNG_Zone01')
    result=run_pending_song_slice(elf,control,2)
    assert (result['counter'],result['threshold'],result['switch'])==(110,-3,1)
    controls=[dict(name='retail level1 Zone01',**result)]
    for selector,threshold,count,pending,bgate,bvalue,observed,want in (
        (90,-3,2,True,0,1,1,1),(90,-3,3,True,0,1,1,0),
        (90,3,2,True,0,1,1,0),(90,3,3,True,0,1,1,1),
        (0,3,3,True,0,1,1,0),(90,-3,2,False,0,1,1,0),
        (90,-3,2,True,7,1,0,0),(90,-3,2,True,7,1,1,1),
        (0,0,0,True,7,1,1,1),(0x1234005a,-3,2,True,0,1,1,1)):
        changed=dict(control,words=dict(control['words']))
        for field,value in (('9c',selector),('a0',threshold&0xffffffff),('94',bgate),('98',bvalue)):
            changed['words'][field]=value
        result=run_pending_song_slice(elf,changed,count,observed,pending)
        assert (result['counter'],result['threshold'],result['switch'])==(selector&255,threshold,want)
        controls.append(dict(input=[selector,threshold,count,pending,bgate,bvalue,observed],**result))
    changed=bytearray(data); struct.pack_into('>I',changed,int(control['offset'],16)+0x9c,90)
    assert next(r for r in decode_pending_song_sources(inventory(changed)) if r['name']==control['name'])['counter']==90
    short=dict(control,size=0xa8)
    try: decode_pending_song_sources([short])
    except ValueError: pass
    else: raise AssertionError('short music owner accepted')
    return dict(controls=controls,synthetic90_decoded=True,short_owner_rejected=True,live_qualified=False)


def check_contract_mutations(elf, data, contract, qualify):
    rejected = []
    for pc in contract['instruction_checks']:
        changed = bytearray(elf)
        offset = elf_offset(elf, int(pc, 16))
        changed[offset + 3] ^= 1
        try:
            qualify(changed, inventory(data))
        except ValueError:
            rejected.append('ELF:' + pc)
        else:
            raise AssertionError('accepted mutated instruction ' + pc)
    for row in contract['candidates'] + contract['excluded_controls']:
        for field in contract.get('dat_checked_fields', (0, 0x6c, 0x70, 0x74, 0x78, 0x7c, 0x80, 0x84)):
            changed = bytearray(data)
            changed[int(row['offset'], 16) + field + (1 if field == 0 else 3)] ^= 1
            try:
                qualify(elf, inventory(changed))
            except ValueError:
                rejected.append(f"DAT:{row['name']}:{field:02x}")
            else:
                raise AssertionError(f"accepted mutated DAT {row['name']}:{field:02x}")
    scripts = contract.get('safety_audit', {}).get('script_edge', {}).get('scripts', [])
    for record in scripts:
        for slot in record['slots']:
            changed = bytearray(data)
            at = int(record['offset'],16) + 0x54 + 16*slot['index']
            struct.pack_into('>I',changed,at,3 if slot['opcode'] != 3 else 0)
            try:
                qualify(elf,inventory(changed))
            except ValueError:
                rejected.append(f"script-op:{record['offset']}:{slot['index']}")
            else:
                raise AssertionError('accepted changed script opcode')
    event_records = contract.get('safety_audit', {}).get('spline_events', {}).get('records', [])
    mutations = set()
    for record in event_records:
        start = int(record['offset'],16)
        for field in (0x20,0x28,0xd4,0xd8) + ((0x2c,) if record['count'] else ()):
            mutations.add((start+field,'I'))
        for event in record['events']:
            mutations.add((start+event['at']+6,'H'))
            mutations.add((start+event['remap_at']+2,'H'))
            for field in range(0x28,0x44,4):
                mutations.add((int(event['target_offset'],16)+field,'I'))
    for at,fmt in sorted(mutations):
        changed=bytearray(data)
        value=struct.unpack_from('>'+fmt,changed,at)[0]
        struct.pack_into('>'+fmt,changed,at,value+1)
        try:
            qualify(elf,inventory(changed))
        except ValueError:
            rejected.append(f'spline-event:{at:08x}')
        else:
            raise AssertionError(f'accepted changed spline event {at:08x}')
    for record in contract.get('safety_audit', {}).get('pending_song', {}).get('records', []):
        for field in (0x34,0x84,0x88,0x8c,0x90,0x94,0x98,0x9c,0xa0):
            changed=bytearray(data); at=int(record['offset'],16)+field
            struct.pack_into('>I',changed,at,word(changed,at)^0x80 if field==0x34 else word(changed,at)^1)
            try: qualify(elf,inventory(changed))
            except ValueError: rejected.append(f'music:{record["offset"]}:{field:02x}')
            else: raise AssertionError('accepted changed music field')
    if 'safety_audit' in contract:
        conditions = contract['safety_audit']['typed_DAT_conditions']
        for selector in (0,14,16,17,18,19):
            row = next(r for r in conditions if r['counter'] == selector)
            for field in (int(row['field'],16), int(row['field'],16)+4):
                changed = bytearray(data)
                struct.pack_into('>I',changed,int(row['offset'],16)+field,90)
                try:
                    qualify(elf,inventory(changed))
                except ValueError:
                    rejected.append(f"typed-DAT:{row['offset']}:{field:02x}->90")
                else:
                    raise AssertionError('accepted changed typed condition')
    return dict(rejected=len(rejected), mutations=rejected, live_qualified=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, default=Path('build/rogue_squadron.z64'))
    ap.add_argument('--elf', type=Path, default=Path('../rogue_squadron64/build/roguesquadron.elf'))
    ap.add_argument('--level', type=int, default=2)
    ap.add_argument('--log', type=Path)
    ap.add_argument('--check-level2', action='store_true')
    ap.add_argument('--check-level3', action='store_true')
    ap.add_argument('--check-level4', action='store_true')
    ap.add_argument('--mutation-check-level4', action='store_true')
    ap.add_argument('--check-level7', action='store_true')
    ap.add_argument('--mutation-check-level7', action='store_true')
    ap.add_argument('--check-level8', action='store_true')
    ap.add_argument('--mutation-check-level8', action='store_true')
    ap.add_argument('--check-level5', action='store_true')
    ap.add_argument('--mutation-check-level5', action='store_true')
    ap.add_argument('--check-level6-music', action='store_true')
    ap.add_argument('--mutation-check-level6-music', action='store_true')
    ap.add_argument('--check-level6-events', action='store_true')
    ap.add_argument('--mutation-check-level6-events', action='store_true')
    ap.add_argument('--check-level6-scripts', action='store_true')
    ap.add_argument('--mutation-check-level6-scripts', action='store_true')
    ap.add_argument('--check-level6-safety', action='store_true')
    ap.add_argument('--mutation-check-level6-safety', action='store_true')
    ap.add_argument('--check-level6', action='store_true')
    ap.add_argument('--mutation-check-level6', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    rom, elf = args.rom.read_bytes(), args.elf.read_bytes()
    assert rom[:4] == bytes.fromhex('80371240')
    assert elf[:4] == b'\x7fELF' and elf[5] == 2
    data, source = extract(rom, args.level)
    rows = inventory(data)
    contract = None
    if args.check_level3:
        if args.level != 3:
            ap.error('--check-level3 requires --level 3')
        contract = level3_contract(elf, rows)
    if args.check_level4 or args.mutation_check_level4:
        if args.level != 4:
            ap.error('--check-level4 requires --level 4')
        contract = level4_contract(elf, rows)
        if args.mutation_check_level4:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level4_contract)
    if args.check_level7 or args.mutation_check_level7:
        if args.level != 7:
            ap.error('--check-level7 requires --level 7')
        contract = level7_contract(elf, rows)
        if args.mutation_check_level7:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level7_contract)
    if args.check_level8 or args.mutation_check_level8:
        if args.level != 8:
            ap.error('--check-level8 requires --level 8')
        contract = level8_contract(elf, rows)
        if args.mutation_check_level8:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level8_contract)
    if args.check_level5 or args.mutation_check_level5:
        if args.level != 5:
            ap.error('--check-level5 requires --level 5')
        contract = level5_contract(elf, rows)
        if args.mutation_check_level5:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level5_contract)
    if args.check_level6 or args.mutation_check_level6:
        if args.level != 6:
            ap.error('--check-level6 requires --level 6')
        contract = level6_contract(elf, rows)
        if args.mutation_check_level6:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level6_contract)
    if args.check_level6_safety or args.mutation_check_level6_safety:
        if args.level != 6:
            ap.error('--check-level6-safety requires --level 6')
        contract = level6_safety_contract(elf, rows)
        if args.mutation_check_level6_safety:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level6_safety_contract)
    if args.check_level6_scripts or args.mutation_check_level6_scripts:
        if args.level != 6:
            ap.error('--check-level6-scripts requires --level 6')
        contract = level6_scripts_contract(elf, rows)
        contract['script_decoder_controls'] = check_script_decoder_controls(rom)
        if args.mutation_check_level6_scripts:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level6_scripts_contract)
    if args.check_level6_events or args.mutation_check_level6_events:
        if args.level != 6:
            ap.error('--check-level6-events requires --level 6')
        contract = level6_events_contract(elf, rows)
        contract['event_decoder_controls'] = check_event_decoder_controls(rom)
        if args.mutation_check_level6_events:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level6_events_contract)
    if args.check_level6_music or args.mutation_check_level6_music:
        if args.level != 6:
            ap.error('--check-level6-music requires --level 6')
        contract = level6_music_contract(elf, rows)
        contract['music_decoder_controls'] = check_music_decoder_controls(elf, rom)
        if args.mutation_check_level6_music:
            contract['mutation_checks'] = check_contract_mutations(elf, data, contract, level6_music_contract)
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
    if contract is not None:
        report[f'level{args.level}_contract'] = contract
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    summary = dict(items=len(rows), counts=report['counts'], targets=[r['name'] for r in targets],
                   positive_controls=[r['name'] for r in known], changing_booleans=len(controls))
    if contract is not None:
        summary[f'level{args.level}'] = dict(selected=contract['selected']['name'],
                                candidates=len(contract['candidates']),
                                instruction_checks=len(contract['instruction_checks']),
                                live_qualified=False)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
