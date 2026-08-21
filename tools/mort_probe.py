#!/usr/bin/env python3
"""Census selected retail MORT descriptors with an independent decoder."""

from __future__ import annotations

import argparse
import collections
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile


EXPECTED_COUNT = 546
EXPECTED_HEADER_TYPES = {0: 419, 1: 59, 2: 36, 3: 17, 4: 9, 5: 6}
EXPECTED_RATES = {8000: 440, 16000: 106}


def fail(message: str) -> int:
    print(f"[error] {message}", file=sys.stderr)
    return 2


def be16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def be32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def parse_descriptors(rom: bytes, speech_offset: int, speech_size: int):
    end = speech_offset + speech_size
    if speech_offset < 0 or speech_size <= 0 or end > len(rom):
        raise ValueError("speech span is outside the ROM")
    speech = rom[speech_offset:end]
    if len(speech) < 4:
        raise ValueError("speech span has no descriptor count")
    count = be32(speech, 0)
    if count != EXPECTED_COUNT:
        raise ValueError(f"descriptor count {count}, expected {EXPECTED_COUNT}")
    table_end = 4 + count * 4
    if table_end > len(speech):
        raise ValueError("descriptor table exceeds speech span")

    rows = []
    for index in range(count):
        packed = be32(speech, 4 + index * 4)
        table_type = packed >> 24
        relative = packed & 0xFFFFFF
        if relative + 12 > len(speech):
            raise ValueError(f"descriptor {index} header is outside speech span")
        if speech[relative : relative + 4] != b"MORT":
            raise ValueError(f"descriptor {index} has no MORT header")
        descriptor_type = speech[relative + 4]
        rate = be16(speech, relative + 6)
        word_count = be32(speech, relative + 8)
        byte_count = word_count * 4
        if word_count < 3 or relative + byte_count > len(speech):
            raise ValueError(f"descriptor {index} has an invalid word-count span")
        rows.append(
            {
                "index": index,
                "table_type": table_type,
                "relative": relative,
                "rom_offset": speech_offset + relative,
                "descriptor_type": descriptor_type,
                "rate": rate,
                "word_count": word_count,
                "compressed_bytes": byte_count - 12,
                "decode_bytes": byte_count,
            }
        )
    return rows


def make_reference_runner(reference: Path, build_dir: Path) -> Path:
    source = reference.read_text(encoding="utf-8")
    header_path = reference.with_name("MORTDecoder.h")
    if not header_path.is_file():
        raise ValueError(f"reference header missing: {header_path}")
    if "bool CMORTDecoder::Decode(" not in source:
        raise ValueError("reference does not expose CMORTDecoder::Decode")
    if '#include "MORTDecoder.h"' not in source:
        raise ValueError("reference source does not include its decoder header")

    compat = r'''
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
using CString = const char*;
using BOOL = int;
inline int MessageBox(void*, const char*, const char*, unsigned int) { return 0; }
'''
    decoder_source = source.replace('#include "StdAfx.h"', '#include "mort_compat.h"', 1)
    decoder_source = decoder_source.replace("unsigned __int64", "unsigned long long")
    runner = r'''
#include "mort_compat.h"
#include "MORTDecoder.h"
#include <fstream>
#include <iostream>
#include <limits>
#include <string>

static unsigned long read_u32(const char* text) {
    return std::stoul(text, nullptr, 0);
}

static int signed_sample(unsigned short value) {
    return value < 0x8000 ? static_cast<int>(value)
                          : static_cast<int>(value) - 0x10000;
}

static unsigned int fnv_pcm(const std::vector<unsigned short>& samples) {
    unsigned int hash = 2166136261u;
    for (unsigned short sample : samples) {
        hash ^= (sample >> 8) & 0xff;
        hash *= 16777619u;
        hash ^= sample & 0xff;
        hash *= 16777619u;
    }
    return hash;
}

int main(int argc, char** argv) {
    if (argc < 4 || ((argc - 2) % 2) != 0) return 2;
    std::ifstream file(argv[1], std::ios::binary);
    if (!file) return 3;
    std::vector<unsigned char> rom((std::istreambuf_iterator<char>(file)), {});
    for (int arg = 2, row = 0; arg < argc; arg += 2, ++row) {
        unsigned long address = read_u32(argv[arg]);
        unsigned long length = read_u32(argv[arg + 1]);
        if (address > rom.size() || length > rom.size() - address) return 4;
        CMORTDecoder decoder;
        std::vector<unsigned short> samples;
        if (!decoder.Decode(rom.data(), static_cast<int>(rom.size()), address,
                            length, samples) || samples.empty()) return 5;
        int minimum = std::numeric_limits<int>::max();
        int maximum = std::numeric_limits<int>::min();
        int first = signed_sample(samples.front());
        int last = signed_sample(samples.back());
        size_t nonzero = 0;
        for (unsigned short sample : samples) {
            int value = signed_sample(sample);
            minimum = std::min(minimum, value);
            maximum = std::max(maximum, value);
            if (value != 0) ++nonzero;
        }
        std::cout << "{\"row\":" << row
                  << ",\"samples\":" << samples.size()
                  << ",\"decoded_bytes\":" << samples.size() * 2
                  << ",\"nonzero\":" << nonzero
                  << ",\"fnv\":" << fnv_pcm(samples)
                  << ",\"min\":" << minimum
                  << ",\"max\":" << maximum
                  << ",\"first\":" << first
                  << ",\"last\":" << last << "}\n";
    }
    return 0;
}
'''
    (build_dir / "mort_compat.h").write_text(compat)
    (build_dir / "MORTDecoder.h").write_text(header_path.read_text(encoding="utf-8"))
    (build_dir / "MORTDecoder.cpp").write_text(decoder_source)
    (build_dir / "runner.cpp").write_text(runner)
    compiler = os.environ.get("CXX", "c++")
    binary = build_dir / "mort_reference_runner"
    command = [
        compiler,
        "-std=c++17",
        "-O2",
        str(build_dir / "MORTDecoder.cpp"),
        str(build_dir / "runner.cpp"),
        "-o",
        str(binary),
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(
            "reference compile failed:\n" + (result.stderr or result.stdout)
        )
    return binary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--speech-offset", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--speech-size", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--indices", required=True)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()

    try:
        rom = args.rom.read_bytes()
        rows = parse_descriptors(rom, args.speech_offset, args.speech_size)
        header_types = collections.Counter(row["descriptor_type"] for row in rows)
        rates = collections.Counter(row["rate"] for row in rows)
        if dict(header_types) != EXPECTED_HEADER_TYPES:
            raise ValueError(f"header type distribution {dict(header_types)}")
        if dict(rates) != EXPECTED_RATES:
            raise ValueError(f"sample-rate distribution {dict(rates)}")
        indices = [int(value, 0) for value in args.indices.split(",") if value]
        if len(indices) != 4 or len(set(indices)) != len(indices):
            raise ValueError("exactly four distinct indices are required")
        selected = [rows[index] for index in indices]
        with tempfile.TemporaryDirectory(prefix="mort_probe_") as temp:
            runner = make_reference_runner(args.reference, Path(temp))
            command = [str(runner), str(args.rom)]
            for row in selected:
                command.extend([hex(row["rom_offset"]), hex(row["decode_bytes"])])
            result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode:
            raise RuntimeError(
                f"reference decoder failed with rc={result.returncode}: "
                f"{result.stderr or result.stdout}"
            )
        decoded = [json.loads(line) for line in result.stdout.splitlines() if line]
        if len(decoded) != len(selected):
            raise RuntimeError("reference returned an incomplete row table")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        return fail(str(error))

    print(
        "[control] descriptors=546 headers=MORT "
        "header_type_counts=0:419,1:59,2:36,3:17,4:9,5:6 "
        "rates=8000:440,16000:106"
    )
    selected_rates = sorted({row["rate"] for row in selected})
    print(f"[control] selected_indices={indices} selected_rates={selected_rates}")
    for row, output in zip(selected, decoded):
        print(
            "[row] "
            + " ".join(
                [
                    f"index={row['index']}",
                    f"rom=0x{row['rom_offset']:X}",
                    f"table_type={row['table_type']}",
                    f"descriptor_type={row['descriptor_type']}",
                    f"rate={row['rate']}",
                    f"word_count={row['word_count']}",
                    f"compressed_bytes={row['compressed_bytes']}",
                    f"decoded_samples={output['samples']}",
                    f"decoded_bytes={output['decoded_bytes']}",
                    f"nonzero={output['nonzero']}",
                    f"fnv=0x{output['fnv']:08X}",
                    f"min={output['min']}",
                    f"max={output['max']}",
                    f"first={output['first']}",
                    f"last={output['last']}",
                ]
            )
        )
    print("[verdict] H-MORTReferenceMatches selected for the four decoded rows")
    if set(selected_rates) != set(EXPECTED_RATES):
        print(
            "[warning] mandated four-row selection does not cover both global "
            "sample-rate classes; the 16000-Hz class remains open"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
