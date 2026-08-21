# NEXT work unit (s2135) — map the MORT artifact boundary

HYPOTHESIS-ID: m5-mort-boundary

## Work unit

Run one bounded static census to identify the retail audio RSP task's ROM
segment, entry/exit contract, and MORT sample-descriptor sources before
creating an artifact or adding a port instrument. Reconcile the existing
`factor5_*.toml`/`aspMain` inputs, `get_rsp_microcode` routing, generated audio
symbols, and companion decomp/sample data. This is one source/config mapping
experiment: do not build the port, change `ROGUESQ_AUDIO_UCODE`, alter task
fields, remove waits or guards, or default any dispatch arm.

## Competing hypotheses and discriminator

- `H-NewMORTRSP-segment`: the retail decoder census corresponds to a distinct
  audio RSP text/data segment not represented by the current Factor 5/ASP
  configs. The table will identify a concrete ROM offset/length, RSP text/data
  load addresses, task entry/exit convention, and MORT descriptor source. This
  selects a new opt-in MORT RSPRecomp artifact as the next implementation.
- `H-ExistingFactor5ConfigMatches`: one existing RSP config and binary input
  maps to the retail audio task's ROM range and task contract, with companion
  MORT descriptors reachable from the same data path. This selects reuse of
  that config/input after the table proves the match; it does not by itself
  authorize renaming `factor5_ucode_b` or changing the default arm.
- `H-CPUDecoderOnly`: the seven watched functions are CPU-side MORT/voice
  routines, but no distinct RSP segment or task entry can be tied to them from
  the current source/config/decomp evidence. This selects a CPU codec/data ABI
  mapping before any RSP artifact is created.
- `H-MORTBoundaryUnresolved`: the source/config census finds conflicting or
  incomplete ROM offsets, descriptor ownership, or task ABI fields. This
  selects no artifact change and requires a new ground-truth watch that names
  the missing writer/consumer boundary.

The discriminating table is one row per candidate RSP input/config and one row
per MORT descriptor source. Each row must include ROM offset and byte range,
RSP text/data load addresses, task entry/exit convention, source file/config,
and the link to the named CPU decoder or sample descriptor. The result selects
`H-NewMORTRSP-segment` only when one previously unrepresented segment has a
complete contract; selects `H-ExistingFactor5ConfigMatches` only on an exact
existing-config match; selects `H-CPUDecoderOnly` when the CPU routines are
the only mapped boundary; otherwise selects `H-MORTBoundaryUnresolved`.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    rg -n -i 'audio|audtask|aspMain|MORT|ucode|microcode|SP_TEXT|SP_DATA|text_start|data_start|rom' \
      factor5_*.toml src/rsp src/main/main.cpp syms docs \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
      /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/subtitles \
      > scratch/agent/mort_s2135_static_refs.txt
    python3 - <<'PY'
    from pathlib import Path
    rom = Path("/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64").read_bytes()
    needle = b"MORT"
    for off in range(len(rom)):
        if rom.startswith(needle, off):
            print(f"MORT magic rom=0x{off:06X}")
    PY
    rg -n 'factor5|aspMain|MORT magic|decodeAndFillVoiceBlock|filterVoiceSampleBlock|musyxSynthFrame|osAiSetNextBuffer' \
      scratch/agent/mort_s2135_static_refs.txt

Inspect only the bounded reference table and the `MORT magic` rows; do not
read generated or ledger files wholesale. The work unit ends when exactly one
of the four hypotheses is selected. If no candidate has a complete ROM/task/
descriptor row, record `H-MORTBoundaryUnresolved` and do not scaffold a new
config from guessed offsets.
