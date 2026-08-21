# NEXT work unit (s2151) — remaining MORT type-0 16000 Hz and type 4

HYPOTHESIS-ID: m5-mort-sample-contract

## Work unit

s2150 closed the leftover `fake_func_*` ELF-size-`> 0xC` class as holds.
Do not re-census leftover `fake_func_*` or invent names for the five
parked `func_*` holds.

The next unit is M5 remaining-codec coverage: one host-only
`tools/mort_probe.py` four-row table covering descriptor type 0 at
16000 Hz and descriptor type 4, against the independent
`CMORTDecoder::Decode` reference already used by s2138/s2139. No game
run, audio-arm change, task ABI, output route, guard, or default
dispatch change.

## Competing hypotheses and discriminator

- `H-MORTRemainingMatches`: the four selected remaining-class rows
  decode to complete nonempty signed-16-bit PCM with stable byte counts
  and FNV hashes.
- `H-MORTRemainingMismatch`: those rows exist in the speech table but
  fail layout, endian, or codec-variant checks (empty, truncated, or
  out-of-range samples).
- `H-MORTRemainingUnavailable`: the speech table does not actually
  contain type 0 at 16000 Hz or type 4, so the remaining-class claim
  cannot be tested (would contradict the s2138 type/rate census).

The discriminator is one four-row table that includes at least one type-0
16000-Hz row and at least one type-4 row, plus the same-run speech
positive controls (`546` descriptors, all `MORT` headers, type counts
`419/59/36/17/9/6`, rates `8000:440`/`16000:106`). Complete nonempty
rows select `H-MORTRemainingMatches`; decoder/range failure selects
`H-MORTRemainingMismatch`; missing classes after the control census
selects `H-MORTRemainingUnavailable`.

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    import collections, struct
    rom = Path('build/rogue_squadron.z64').read_bytes()
    off, size = 0x583D90, 0x31D3E4
    speech = rom[off:off+size]
    count = int.from_bytes(speech[0:4], 'big')
    rows = []
    for i in range(count):
        packed = int.from_bytes(speech[4+i*4:8+i*4], 'big')
        rel = packed & 0xFFFFFF
        dtype = speech[rel+4]
        rate = int.from_bytes(speech[rel+6:rel+8], 'big')
        rows.append((i, dtype, rate))
    need = [(0, 16000), (4, 8000), (4, 16000), (0, 16000)]
    chosen = []
    used = set()
    for want_t, want_r in need:
        for i, dtype, rate in rows:
            if i in used:
                continue
            if dtype == want_t and rate == want_r:
                chosen.append(i)
                used.add(i)
                break
    print('count', count)
    print('types', collections.Counter(r[1] for r in rows))
    print('rates', collections.Counter(r[2] for r in rows))
    print('type0_16000', [i for i,t,r in rows if t==0 and r==16000][:8])
    print('type4', [(i,r) for i,t,r in rows if t==4][:12])
    print('chosen', chosen)
    Path('scratch/agent/s2151_mort_indices.txt').write_text(
        ','.join(str(i) for i in chosen) + '\n')
    PY

    python3 tools/mort_probe.py \
      --rom build/rogue_squadron.z64 \
      --speech-offset 0x583D90 \
      --speech-size 0x31D3E4 \
      --indices "$(cat scratch/agent/s2151_mort_indices.txt)" \
      --reference scratch/agent/s2138_mort/N64-Tools/N64SoundListToolUpdated/N64SoundLibrary/MORTDecoder.cpp \
      | tee scratch/agent/s2151_mort_result.txt

If the census cannot fill four remaining-class indices, stop and record
`H-MORTRemainingUnavailable` rather than padding with already-covered
type-0 8000-Hz or type-1/2/3/5 rows. Do not run the game or change
runtime, audio, task, output, guard, or mitigation behavior.
