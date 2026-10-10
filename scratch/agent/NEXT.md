# NEXT: does retail write 0x6C617465 at physical 0x1724F4

HYPOTHESIS-ID: odd-dma-retail-voice-word

s4535 selected H-neither and closed the two named stores. Do not re-probe `0x80090C80` or `0x800921E8`. Do not re-read the four jals. Do not grep the tree for another writer of voice+0x34. Do not add a skip.

The port's bad voice is stable across s4534 and s4535: `0x801724C0`. The word at +0x34 is `0x6C617465` when `0x800903F0` runs, on the 512-to-640 edge (origin `0x006A2900`). Physical address of that word: `0x1724F4`. `0x6C617465` is not a legitimate cart offset.

One oracle run. The port cannot witness this. Rice is required; dummy video never leaves width 320. `--vi-trace` is the phase control. Watch 0 is the whole-RDRAM positive control and must print hits. Watch 1 is the one word. `--post-value-watch 1` arms at title `0x00790400` or hangar `0x006AB400` and stays armed, so the later 640 edge is inside the sample window (256 samples, 64 unique values). `--post-value-pc` forces samples for the two named store PCs past that budget. If `post-value` reports `overflow` nonzero and `0x6C617465` is absent, that absence is not a result.

```
tools/oracle/build/rs64_oracle \
  --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" \
  --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 180 --vi-trace --hit-cap 4 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x1724F4:0x1724F8 \
  --first-watch 1 \
  --pc-hist-watch 1 \
  --pc-hist-phase 0x6ab400:512 \
  --pc-hist-phase 0x6a2900:640 \
  --post-value-watch 1 \
  --post-value-pc 0x80090C80,0x800921E8 \
  --post-value-pc-detail \
  --post-value-pc-detail-phase 0x6a2900:640 \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,117:start,130:start'
```

Write stdout to `scratch/s4536_retail_voice_word_<stamp>.log`. Do not start a second game.

Outcomes:

- `[vi]` shows origin `0x6a2900` at width 640, watch 0 printed hits, and a `post-value` row for watch 1 is `value=0x6C617465`: selects H-retail. Quote the `post-value-pc` line for that value, or the `post-target-class` `last_value` if the writer is `0x80090C80` or `0x800921E8`. The word is the game's. Stop. Do not add a skip. If that PC is one of the two named stores, the port's copy of that store diverged; say so and stop.
- The same phase is reached, watch 0 fired, watch 1's `post-value` `overflow=0`, and no value is `0x6C617465`: selects H-port-only. Retail did not write that word to this address in the armed window. Stop. Do not grep. The writer on the port is still unnamed.
- `post-target-summary` for `0x80090C80` or `0x800921E8` has `seen=0`, and some other watch-1 writer PC has the value: that other PC is the retail writer. Quote it. Stop. Do not grep.
- No `[vi]` line with origin `0x6a2900`: the edge was missed. Not a result about the word. Do not conclude absence.
- Watch 0 prints no hit: the instrument is dead. Not a result.
- `post-value` `overflow` is nonzero and `0x6C617465` is absent: the sample budget filled. Not H-port-only. Do not re-run the same command hoping the value appears.
