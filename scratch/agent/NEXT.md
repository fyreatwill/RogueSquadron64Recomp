# NEXT work unit (s2023)

HYPOTHESIS-ID: m5-port-status-writer-read-join

## RESUME: s2022 body census

s2022 selected H2 in one phase-valid run. The independent s2020 controls
emitted 1,988 service entries and exits; all 1,988 s2022 branch rows had
`gate=0x01 path=body`; all 1,988 loop rows were slot 0 with `status=0x00`
and `zero_skip=1`; the independent s2022 store edge emitted zero rows.
The run later hit the known PI `do_rom_read` abort. Retail ground truth
independently executed the branch and loop PCs 3,033 times each and the
store PC twice, so the next question is port-side status production/read
ordering, not whether retail enters the function.

## Work unit

Run the existing seven-site status-writer census in the same phase-valid
capture as the s2022 body census. Keep all behavior unchanged. Apply the
existing s2007 shutdown-reach hook and s2008 writer hook during regeneration;
arm `ROGUESQ_LOG_S2008_STATUS_WRITERS=1` at runtime. Retain s2020 entry/exit,
s2006 entry/exit/store, and s2022 branch/loop/store rows as positive controls.
The writer rows must be joined by phase, slot/address, old/new byte, host
thread, and shutdown call. Do not add another direct-entry or `get_function`
witness.

## Competing hypotheses and discriminator

- H1 `never-written`: with s2020/s2022 controls live, no port writer reaches
  slot 0 with new status `0x03`; service reads `0x00` because the status-3
  lead never occurs on the port.
- H2 `transient-cleared`: a port writer reaches slot 0 with new status
  `0x03`, then a later service row reads slot 0 as `0x00` before the s2022
  store edge; the writer and reader can be joined by phase/thread/shutdown
  call.
- H3 `other-slot-or-table`: the writer census fires only for other slots or
  addresses outside the service's `0x80154620 + slot*0x1228` table, so the
  service's slot-0 zero is an indexing/table-base mismatch.

The discriminating measurement is one same-run timeline of all s2008 status
writer rows and the s2022 slot-0 reads. H1 is selected by live service
controls plus no slot-0 `new=0x03`; H2 by a slot-0 `new=0x03` followed by a
zero service read; H3 by writer activity confined to other slots/addresses.
A slot-0 service row with nonzero status or an independent s2022 store row
closes this unit in favor of the already-defined store/writer join. If the
writer census is zero while its shutdown positive control is live, classify
that as a census-anchor failure rather than a status conclusion.

## Ground truth before the build

Run the oracle whole-RDRAM positive control first; retain the s2022 exact
retail target result as the independent body contract. Do not interpret a
new port writer null without a live positive control.

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 8 --watch-write 0x0:0x800000 --hit-cap 1 > scratch/agent/oracle_s2023_whole_control.log 2>&1
```

## Regeneration, build, and run

```sh
set -e
backup_dir=$(mktemp -d /tmp/rs64-s2023-recompiled.XXXXXX)
cp -a /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/. "$backup_dir/"
find /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -mindepth 1 -maxdepth 1 -type f -delete
cd /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/N64Recomp
build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
env RS64_S2006_STATUS3=1 python3 fixup_game_funcs.py
env RS64_S2007_STATUS3_REACH=1 python3 fixup_game_funcs.py
env RS64_S2008_STATUS_WRITERS=1 python3 fixup_game_funcs.py
env RS64_S2022_SERVICE_BODY=1 python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_S2008_STATUS_WRITERS=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2023-status-writer 30 12
```

Extract with bounded aggregates:

```sh
RUN=scratch/s73_post_a_scene/s2023-status-writer/run.log
rg -n -e '\[s2008-status-writer\]' -e '\[s2008-status-control\]' -e '\[s2022-svc\]' -e '\[s2020-svc\]' -e '\[s2007-shut\]' -e '\[s2007-spin\]' "$RUN" | tail -320
```
