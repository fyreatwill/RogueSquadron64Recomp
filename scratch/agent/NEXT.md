# NEXT: at the first ALLOW_WILD_FL, record buffer size and the image command

HYPOTHESIS-ID: allow-wild-fl-writeback

Context: PORTING-STATE s4530. The odd-phys join did not run. Both runs of the s4529 recipe died at VI 640 on the first `[ost-wb] ALLOW_WILD_FL` (s659 policy in `lib/rt64/src/hle/rt64_state.cpp`: a width outside {320,512,640,1024} whose byte range covers freelist phys `0x1F3CC0` is written back anyway).

- `scratch/s4530_odd_phys_join/run.log`: color `w=913 siz=3 addr=0x14CEB9`. VI stayed 640 until the 180 s phase timeout. No signal. `[s4298-rtw] n=1` and the width-640 chain (`head=801F9CE0`) fired.
- `scratch/s4530_odd_phys_join_b/run.log`: depth `w=1185 siz=2 addr=0x150000 range=[0x19C608,0x214266)`. SIGSEGV in `NativeTarget::copyToRAM`. `x2=0x77C5E` equals that range. Dest low bits are `0x19C608`. Source `0x11E7C4608` is unmapped (`si_code=2`). Stack is `copyToRAM` <- `copyNativeToRAM`. `last-guest-pc 0x8000834c` is the audio thread, not the fault.
- `[cimg-oob-1]` logged zero WIDTH lines in both runs. Widths 913 and 1185 are not stable and are not legitimate modes. Do not add a skip and do not change the allow policy.
- Not an A/B: `scratch/s4529_freed_block_heads_c/run.log` reached VI 1024 with zero `ALLOW_WILD_FL`. s4529's signal-10 deaths also each have one ALLOW, but their faulting PC is `fillSampleStreamRange`. Leave that bus error parked.

`copyToRAM` (`lib/rt64/src/render/rt64_native_target.cpp`) memcpy's `bufferSize` bytes from `contents()+bufferOffset` and does not compare that to `nativeReadbackBufferSize`. Whether the allocation is short is unmeasured.

One build, one run. Before the memcpy, one log line carries every field below. If the DPC submission is no longer in scope at writeback, save the last `0xFF`/`0xFE` `w0`/`w1` at the set-image call (one static) and print it on this line. That is part of this instrument, not a later iteration. An edit under `lib/` requires `./submodule-patches/export.sh` in the same iteration.

Fields: tag, addr, w, siz, row start, row end, fb width, fb height, `nativeReadbackBufferSize`, `bufferOffset`, `bufferSize`, and the saved or in-submission `0xFF`/`0xFE` word whose `(w0 & 0xFFF)+1` equals `w` (or `none`).

Hypotheses:
- H-short: `nativeReadbackBufferSize < bufferOffset+bufferSize`. Selects "the SIGSEGV reads past the readback allocation".
- H-dangling: `nativeReadbackBufferSize >= bufferOffset+bufferSize`. Selects "the allocation is large enough; `contents()` is not a live base".
- H-cmd: a `0xFF` or `0xFE` word has width == `w`. Selects "the width is a microcode image command the head-only `[cimg-oob-1]` scan missed".
- H-field: no matching command, and fb width == `w`. Selects "the framebuffer width word changed after the last image command".

H-short and H-cmd can both be true. Report each separately. Do not land a guard from this run.

Control, same run: `[s4298-rtw] n=1`, and the `ALLOW_WILD_FL` line contains the new fields. If that line fires without them, the patch did not land; fix and rerun once. A run that reaches VI 1024 with zero ALLOW is the known surviving route, not a failed instrument; rerun once. No `ROGUESQ_LOG_RS_MALLOC`.

```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_S4298=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh tools/probe.sh scratch/s4531_wild_fl_fields 160 2
```

Write the log outside `scratch/agent/` so the stop gate can cite it.
