# NEXT work unit (s1985) — remaining stop/release family dest-map + MarkRetrigger $ra

HYPOTHESIS-ID: hangar-frame-freeze

## What s1984 settled

The four named stop sites: `musyxStopVoice` 0, `deactivateVoice` 0,
`stopVoice` 1 after the 10M drain timeout (dest `0x80153420`
unmapped). `stopVoiceMarkRetrigger` 165/165 mapped (81 boot
`0x8018D4A0`, 84 hangar `0x801714D0`). 8 hangar dests fire after
tickn=4 alloc and before drain; each is immediately followed by
`musyxInitVoiceFromSample` of the same idx then render
`slot-sb old=0x01 new=0x02`. MarkRetrigger is the retrigger path,
not a key-off. s1983's "zero on hangar" was the s1927 first-32
rate-limit.

## Competing hypotheses (who should actually idle looping BGM)

- **H-missing-song-stop:** craft-select exit should call a
  song/handle/release stop (`stopVoicesByHandle` /
  `stopVoiceByHandle` / `musyxStartVoiceRelease` /
  `beginVoiceFadeRelease` / `stopVoiceByKey` /
  `stopVoiceSlotSynced` / `stopVoiceByHandleLocked`) on the
  `0x801714D0` table and does not.
- **H-song-stop-unmapped:** one of those DOES fire in the
  tickn=4→drain window but dest is a handle / other stride (same
  shape as s1982 key-on).
- **H-drain-expects-bgm-end:** no song-stop is supposed to fire;
  drain waits for looping BGM to end, and hangar BGM is infinite
  so the spin is the legitimate (host-starved) wait. MarkRetrigger
  `$ra` in that window is the note engine, not an attempted all-off.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1984 `[stop-dest]` / `[drain-stop-sum]` and s1983 `[init-desc]`.
Add the same dest-map dump on the remaining stop/release family
(store to a slot-like dest, or function entry if there is no slot
store):

`[stop-dest] site=NAME n= dest=0x.. idx= base=0x.. val=0x.. armed= hidx= ra=0x..`

Sites: `stopVoiceByKey` `0x80086914`, `stopVoiceByHandleLocked`
`0x800894F0`, `stopVoicesByHandle` `0x8008DA98`,
`stopVoiceSlotSynced` `0x8009B268`, `stopVoiceByHandle`
`0x8009B33C`, `musyxStartVoiceRelease` `0x80092274`,
`beginVoiceFadeRelease` `0x80092490`. Extend `[drain-stop-sum]`
with per-site n / nmap / nhangar / last dest / last ra.

Also add `ra=` to the existing MarkRetrigger `[stop-dest]` (the
8 post-tickn=4 rows name the retrigger caller).

First 8 always (positive control: MarkRetrigger still fires on
boot `0x8018D4A0`). Then every mapped `idx<18` plus every
unmapped row with `n<=32` (so a handle-stride stop is not
rate-limited to silence).

Outcomes:
- a new site maps onto `0x801714D0` after tickn=4, slot+0 still
  `0x02` at drain → stop incomplete (same shape as MarkRetrigger)
- a new site fires in that window with unmapped dest →
  H-song-stop-unmapped; next is that structure
- all new sites n=0 through drain, MarkRetrigger `$ra` is a note
  engine → H-missing-song-stop / H-drain-expects-bgm-end; next is
  static jals out of `tickCraftSelectScreen`'s nonzero-return path

Positive control: `[stop-dest] site=stopVoiceMarkRetrigger` n=1
dest=`0x8018D4A0`, `[drain-stop-sum] entry=1` MarkRetrigger
n>=32 nhangar>0, `[init-desc]` still fires, last alloc
`0x801714D0 count=18`. Keep `ROGUESQ_SPIN_YIELD=1` and
`ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1985_stop_family` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Add `ra=U32(ctx->r31)` to the existing s1984 MarkRetrigger block.

## Exact test

```sh
mkdir -p scratch/agent/s1985_stop_family
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1985_stop_family 60 2
```
