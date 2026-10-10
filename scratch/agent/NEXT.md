# NEXT: join the odd do_rom_read address to the successor of the VI-512 head

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Context: PORTING-STATE s4529. At the VI-512 publish (`scratch/s4529_freed_block_heads_c/run.log`, same tick as the chain log) the freed-block heads are linked nodes, not overlay bytes and not ROM pointers:

- `0x8017DA10` w0=0 w1=`0x8017D9F8` w5=`0x80195D90`
- `0x8017D9E0` w0=`0x8017D9F8` w1=0 w5=`0x80195190`

Words 0 and 1 are 0 or the adjacent 0x18-byte slot. They are even, so they cannot be the value that fails `(physical_addr & 1) == 0`. The successor named by w5 sits outside `0x8017D910..0x80189340` and its words are odd (`0x80195190` w1=`0xDE040843`, `0x80195790` w1=`0xFF2BFF57`, `0x80196390` w0=`0xEF015FAD`). None of those are ASCII. The `[s4529-H]` cap expires ~0.3 s after the first publish (t=9655); the later republish at t=11019 was not snapshotted. Do not add another poller cap. Do not enable `ROGUESQ_LOG_RS_MALLOC`.

One run. No new fields. Arm the existing odd-address scan (`ROGUESQ_LOG_S4298=1`, `ROGUESQ_LOG_DMA=1`) together with the head snapshot (`ROGUESQ_LOG_S4526=1`). `[s4298-odd]` prints the odd phys and every RDRAM word that holds it, with the neighbouring words.

Hypotheses:
- H-succ: the odd phys equals word 0 or 1 of the successor (the node at the head's w5, outside the freed block). Selects "the freed-block head is only the link; the bad ROM pair is that successor."
- H-ascii: the odd phys is four printable bytes (s4298's `6C637265` shape) and an RDRAM hit is a 6-word node inside `0x8017D910..0x80189340` other than `0x8017DA10` / `0x8017D9E0` / `0x8017D9F8` / `0x8017DA28`. Selects "the name-text node is still the source, and it is not the list head."
- H-computed: `[s4298-odd]` fires and the only hits are the DMA ring or the stack batch. Selects "the odd address is computed, not stored in a node word."
- H-head-later: the odd phys equals word 0 or 1 of `0x8017DA10` or `0x8017D9E0`. Selects "those words changed after the s4529 publish snapshot." s4529 already refutes this at publish time.

Control, same run: `[s4526-P] chain` width 640 head `0x801F9CE0`, `[s4529-H] SNAP` head `0x8017DA10` at width 512, and a `[s4298-odd] phys=` line. If `[s4298-odd]` is absent, the env did not arm; rerun once. A crash before width 512 is a route failure (the parked `fillSampleStreamRange+15116` bus error), not H-computed; rerun once.

```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_S4298=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh tools/probe.sh scratch/s4530_odd_phys_join 160 2
```

Write the log outside `scratch/agent/` so the stop gate can cite it.
