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


def check_level4_mutations(elf, data, contract):
    rejected = []
    for pc in contract['instruction_checks']:
        changed = bytearray(elf)
        offset = elf_offset(elf, int(pc, 16))
        changed[offset + 3] ^= 1
        try:
            level4_contract(changed, inventory(data))
        except ValueError:
            rejected.append('ELF:' + pc)
        else:
            raise AssertionError('accepted mutated instruction ' + pc)
    for row in contract['candidates'] + contract['excluded_controls']:
        for field in (0, 0x6c, 0x70, 0x74, 0x78, 0x7c, 0x80, 0x84):
            changed = bytearray(data)
            changed[int(row['offset'], 16) + field + (1 if field == 0 else 3)] ^= 1
            try:
                level4_contract(elf, inventory(changed))
            except ValueError:
                rejected.append(f"DAT:{row['name']}:{field:02x}")
            else:
                raise AssertionError(f"accepted mutated DAT {row['name']}:{field:02x}")
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
            contract['mutation_checks'] = check_level4_mutations(elf, data, contract)
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
