# Stream-node block lifetime: what s4298-s4317 already settle (written s4524)

Question carried in NEXT.md at s4523: does an audio stub/gate skip an unlink so
`musyxSynthFrame` keeps walking nodes after the teardown free? Answer from the
ledger and the retail oracle logs (no new run):

| Hypothesis | Verdict | Evidence |
|---|---|---|
| A: a port stub/gate skips the unlink | REFUTED | s4301: recompiled `waitForAnyAudioSlot` (funcs_15.c:7898) has no unregister or shutdown call, only the 3 `rs_free`; guard never fires on the natural exit; same free in both arms. |
| B: retail does not walk the block / does not reuse it | REFUTED | s4302/s4303: retail executes the same free, synth runs 2,820x afterwards, 1.14M accesses in 0x17D000..0x17E200. Retail writers in that range (scratch/agent/s4303_retail_oracle_48s.log:177-215) include rs_malloc/rs_memset (0x80001C18.., 0x80007670 n=2048), a 128-record initialiser (0x8001FAxx / 0x8001E2C0, n=128 each) and the synth's own node rebuild (0x8008FBB4/0x8008FBEC n=12415). |
| C: a gated path resets the list head | no evidence | s4301 listing; no head writer found outside retail code. |
| D (survivor): retail also overlays the block but rebuilds nodes each synth frame, so the overlay is overwritten before use; the port's overlay leaves romA/romB (node +0..+7) as ASCII | OPEN, single-source layout reading | s4306/s4317: retail vs port post-free layouts differ from ordinal 0 (retail `0x8008FADC,0x17DA1C`; port `0x8008FCE8,0x17D9E0`). |

So the free is retail behaviour; the divergence is the post-free layout/order.
Do not look for an audio stub that skips an unlink.

Discriminator for D (next): the address of the 128-record array written by
retail PCs 0x8001FAxx versus the port's `ltex_cache_N` array (0x24-stride), each
relative to the node array (6-word stride, romA/romB first). If retail's array
never covers node +0..+7 of live nodes, the port's allocator/heap layout is the
cause (then ask why `rs_malloc` returns a different base: earlier allocation
history). If it does cover them, retail's rebuild (0x8008FBB4) is what the port
fails to run.
