# NEXT work unit (s2140) — observe retail data_ptr+0x100 writes

HYPOTHESIS-ID: m5-retail-dataptr-output-boundary

## Work unit

Run one independent retail-oracle watch for the two `data_ptr` values already
observed in the qualified task-field census. Their physical destinations are:

| retail data_ptr | physical data_ptr+0x100 | watch index |
|---:|---:|---:|
| `0x80173B20` | `0x00173C20` | 1 |
| `0x80171CE0` | `0x00171DE0` | 2 |

The same run must include the whole-RDRAM positive control at watch index 0,
the title/hangar VI trace, writer-PC histograms, bounded post-store value
tables for both exact target watches, and bounded surrounding-range watches
for the two task buffers. Watch index 5 must cover the full retail `aspTask`
field block `0x00149470:0x001494B0` as the same-run task-route control. This is
the missing independent retail line
for the generated image's observed `field348+0x100` write relation. Do not
change the port, audio dispatch, task fields, output routing, waits, guards,
or default arm.

## Competing hypotheses and discriminator

- `H-RetailDataPtrOffset100`: after the positive control and phase gates,
  retail writes both observed task-buffer destinations at `data_ptr+0x100`,
  with writer PCs and post-store values that identify the audio task output.
- `H-RetailDataPtrOtherOffset`: retail reaches the task route and writes the
  observed buffers, but the bounded surrounding-range table shows writes that
  do not land at either `data_ptr+0x100` destination, so the generated
  relation is not the retail output relation.
- `H-RetailDataPtrNoWrite`: the task fields and title/hangar route are live,
  but neither exact `data_ptr+0x100` destination is written in the covered
  run; the downstream output edge remains unresolved rather than being
  treated as a null contract.
- `H-RetailDataPtrCoverageFailure`: the whole-RDRAM control, task route, or
  title/hangar phase gate fails, so target-watch silence cannot discriminate
  the destination hypotheses.

The one discriminating measurement is the same-run table of watch hits,
writer PCs, phase, post-store words, and final range FNV/nonzero summaries for
watch indices 1–5, paired with positive-control hit counts and VI gates.
Both target rows must have valid route coverage before a no-hit result can
select `H-RetailDataPtrNoWrite`; a hit at either exact destination selects
the corresponding observed relation, while task-route coverage plus writes
outside both exact destinations selects `H-RetailDataPtrOtherOffset`.

## Exact command

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 64 --watch-write 0x0:0x800000 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171CE0:0x171EE0 --watch-write 0x173B20:0x173D20 --watch-write 0x149470:0x1494B0 --first-watch 0 --pc-hist-watch 5 --post-value-watch 1 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 --post-value-watch 5 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/oracle_s2140_dataptr.log 2>&1
    grep -c '^\[hit\] w addr=' scratch/agent/oracle_s2140_dataptr.log
    grep -E '^\[oracle\]|^\[vi\]|^\[hit\]|post|watch' scratch/agent/oracle_s2140_dataptr.log | tail -160

Expected outcomes: target hits at either exact physical destination after the
whole-RDRAM control and hangar VI `512 @ 0x006AB400` select
`H-RetailDataPtrOffset100`; a fully covered task route with no target hits but
non-target writes in either bounded surrounding range selects
`H-RetailDataPtrOtherOffset`. A fully covered task route with neither exact
nor surrounding-range writes selects `H-RetailDataPtrNoWrite`. Missing
positive control, task-block control, or title/hangar coverage selects
`H-RetailDataPtrCoverageFailure`.
