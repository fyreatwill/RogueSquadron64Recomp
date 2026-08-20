# NEXT work unit (s1984) — dest-map stop/keyoff onto the hangar table

HYPOTHESIS-ID: hangar-frame-freeze

## What s1983 settled

`desc+0x14` / `slot+0x40` is loop length, not a flag, pointer, or
rate. 256/256 inits: oneshot `d14==0 && d10==0x11` (125), whole
sample loop `d10==0 && d14==d0c` (3), or `d14==d0c-d10` (128).
`d00` low-16 is the sample rate. `bnez slot+0x40` is the legitimate
loop skip. Live drain voices are the looping ones; they were never
stopped (`stopVoiceMarkRetrigger` 32/32 on boot `0x8018D4A0` only).

Drain is `jal 0x800B24C4` immediately after `tickCraftSelectScreen`
returns != `0x00FFFFFF` (`0x800C5EB8`).

## Competing hypotheses (who should stop the loops)

- **H-missing-pre-stop:** `tickCraftSelectScreen`'s nonzero-return
  path (or a callee) should key-off the `0x801714D0` table before
  `jal drain` and does not.
- **H-stop-unmapped:** a stop/keyoff DOES fire in that window but
  dest is the boot table / a different stride (same shape as s1982
  key-on).
- **H-drain-too-wide:** a stop never runs because drain is a
  speech-oneshot wait; `anyAudioSlotActive` ORs looping BGM in and
  the caller expects only oneshots to remain.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1982 `[keyon-w40]` / `[drain-path]` and s1983 `[init-desc]`.
On every `musyxStopVoice` / `stopVoice` / `deactivateVoice` /
`stopVoiceMarkRetrigger` store to slot+0 (or the function entry if
there is no slot+0 store), dump:

`[stop-dest] site=NAME n= dest=0x.. idx= base=0x.. val=0x.. armed=`

Same idx mapping as s1982 (`-0x6908` table, stride 136). First 8
always (positive control: MarkRetrigger already fires 32x on boot).
Then every mapped `idx<18`.

At drain entry (`drainAudioAndFinalizeSpeechBuffer` first insn)
dump one `[drain-stop-sum]` with per-site n / n_mapped_hangar /
last dest.

Outcomes:
- some site maps onto `0x801714D0` before drain, slot+0 still `0x02`
  → stop is incomplete (does not clear status); H-stop-unmapped
  half, next is why the stop did not idle the slot
- sites fire only on `0x8018D4A0` / unmapped through drain entry
  → H-missing-pre-stop / H-stop-unmapped (boot-only)
- zero stop* between hangar alloc (tickn=4) and drain
  → H-missing-pre-stop; H-drain-too-wide still open (does the
  caller believe only oneshots remain?)

Positive control: `[stop-dest] site=stopVoiceMarkRetrigger` fires
(boot, 32x in s1983), `[init-desc]` still fires, `[drain-path]
call=1 unmap=0`, last alloc `0x801714D0 count=18`. Keep
`ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- `musyxStopVoice` `0x80092368`, `stopVoice` `0x8009C2BC`,
  `deactivateVoice` `0x800924F0`, `stopVoiceMarkRetrigger` (existing
  slot-sb site). Drain entry in `funcs_30.c`.
- Incremental `apply_s1984_stop_dest` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.

## Exact test

```sh
mkdir -p scratch/agent/s1984_stop_dest
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1984_stop_dest 60 2
```
