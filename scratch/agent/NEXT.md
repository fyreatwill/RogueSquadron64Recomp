# NEXT: dump romA/romB of the VI-512 list nodes that sit inside the freed block

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Context: PORTING-STATE s4528. The late-window poll (s4522 arms a/b/d, `ROGUESQ_LOG_S4526=1`) selects a list link over a voice pointer. The 40 tagged hits are list-0 node 0x80192C70 next=+0x14 = 0x8017D030, which is 0x8E0 below the freed 47664 block (0x8017D910..0x80189340) and they spend the hit cap. The uncapped chain log, same three arms, is the freed-block evidence: after a len=0 clear at width 512 the heads become 0x8017DA10 (global 0x801499B4) and 0x8017D9E0 (global 0x801499E4), then 0x8017D9F8 / 0x8017D9E0. Last-guest-pc is racy (inflate_fast, rs_memset, beginFrameDLChunk) and is not the writer. s4231's 400-row cap ends ~9 s. Do not enable `ROGUESQ_LOG_RS_MALLOC`: `scratch/s4528_holder_malloc/run.log` reached VI 1024 and died in rs_malloc (guest 0x80001C94) with zero in-range hits.

One change to the poller in `src/main/upstream_compat.cpp` (and the matching text in `tools/apply_s4527_holder_poll.py` so a re-apply cannot restore the blind cap). Keep the alive line and the chain-length line. Add a second cap, not shared with the 0x8017D000 window: when a walked node or either head is in [0x8017D910, 0x80189340), log one snapshot of the whole chain (idx, addr, word0, word1, word5) and stop after 30 snapshots. Do not log last-guest-pc as if it were the store.

Hypotheses:
- H1: romA/romB (words 0 and 1) of 0x8017DA10 / 0x8017D9E0 are odd or ASCII at the snapshot. Selects "the published node is overlay/texture bytes". Next probe is a real store watch on 0x801499B4, not another voice scan.
- H2: those rom words are even and inside the ROM. Selects "the odd do_rom_read address is computed later, not stored in the node". The stale-contents story is wrong for these heads.
- H3: no snapshot fires while the alive line and a width-512 chain-length change both occur. Refutes the s4528 chain-log reading (the heads were not really inside the block, or the route did not reach it). A crash before width 512 is not H3; it is a route failure, rerun once on the quiet s4522 recipe.

Control, same run: `[s4526-P] alive` with len 2, and a width-640 chain line whose head is 0x801F9CE0. If the alive line is absent, the poller did not run.

Run one arm, from `build/`, SIGKILL via `tools/probe.sh`. No `ROGUESQ_LOG_RS_MALLOC`, no `ROGUESQ_LOG_RS_FREE`.

```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh tools/probe.sh scratch/s4529_freed_block_nodes 160 2
```

Write the log outside `scratch/agent/` so the stop gate can cite it.
