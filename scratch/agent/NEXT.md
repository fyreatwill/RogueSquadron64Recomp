# NEXT work unit (s2005) — RESUME: s2004 payload-hash census

HYPOTHESIS-ID: m5-audio-dma-pcm-contract

## Status at session start

Session 2004 died before any code was written. Session 2003's instrument is
the current state: `AudioDmaRange` in `librecomp/src/rsp.cpp` tracks dram
address, length, DMEM source, and declared-field overlap flags for every DMA
write during a sampled audio task. No payload hash or nonzero count exists
yet. No `queue_samples` hook exists in `ultramodern/src/audio.cpp`. All PCM
in both arms is `all_zero=1`; treatment shows 248 DMEM-to-RDRAM ranges
(DMEM 0x6F0/0xCB0); control shows 0.

## Competing hypotheses

- **H-task-staging:** treatment DMA payloads are zero or structurally invalid;
  `queue_samples` is never given a nonzero buffer.
- **H-guest-buffer-selection:** payloads are nonzero but the AI callback
  receives a different or zero RDRAM range.
- **H-bridge:** payload nonzero reaches `queue_samples` but samples differ or
  `pcm-sanity` stays silent.
- **H-audio-path-valid:** payload nonzero, same bytes reach `queue_samples`,
  `pcm-sanity` becomes nonzero — RSP/bridge boundary closed.

## Discriminating measurement

One phase-gated table joined by task row n: payload FNV hash + nonzero byte
count from rdram[dram..dram+len] immediately after the DMA write (in rsp.cpp),
versus AI-buffer FNV hash + nonzero count from the buffer handed to
`queue_samples` (in audio.cpp). With retail oracle and `[audtask-dispatch]`
as positive controls.

- Payload nonzero + bridge nonzero + same hash → H-audio-path-valid.
- Payload nonzero + bridge zero → H-guest-buffer-selection.
- Payload nonzero + bridge nonzero + hash mismatch → H-bridge.
- Payload zero/null → H-task-staging.

## Exact commands

### Step 1 — extend `AudioDmaRange` in rsp.cpp

In `librecomp/src/rsp.cpp`, add to the `AudioDmaRange` struct:
```cpp
    uint32_t payload_fnv;   // FNV-1a hash of rdram[dram..dram+len]
    uint32_t payload_nz;    // nonzero byte count in rdram[dram..dram+len]
```

In `rs64_probe_audio_dma_write`, after pushing the range, compute the hash
and nz count from `rdram` (add `uint8_t* rdram` as a parameter and update all
callers), using the same FNV-1a constants already present in rsp.cpp:
```cpp
    uint32_t h = 2166136261u, nz = 0;
    for (uint32_t i = 0; i < len; i++) {
        uint8_t b = rdram[S32(dram_addr + i) & 0x7FFFFF];
        h = (h * 16777619u) ^ b;
        nz += (b != 0);
    }
    probe->ranges.back().payload_fnv = h;
    probe->ranges.back().payload_nz = nz;
```

Update the `[audtask-ranges]` printf to include `payload_fnv=%08x nz=%u`.

### Step 2 — add `queue_samples` hook in audio.cpp

In `ultramodern/src/audio.cpp`, immediately before the
`audio_callbacks.queue_samples(...)` call (line ~34), add:

```cpp
    extern "C" uint32_t rs64_phase_ord();
    extern "C" uint32_t rs64_vi_committed_width();
    extern "C" uint32_t rs64_vi_committed_origin();
    static int s_log_pcm_bridge = -1;
    if (s_log_pcm_bridge < 0) {
        const char* e = getenv("ROGUESQ_LOG_ALL");
        s_log_pcm_bridge = (e && e[0] == '1') ? 1 : 0;
    }
    if (s_log_pcm_bridge && sample_count > 0) {
        const uint8_t* p = reinterpret_cast<const uint8_t*>(
            TO_PTR(int16_t, audio_data_));
        uint32_t h = 2166136261u, nz = 0;
        for (int32_t i = 0; i < sample_count * 2; i++) {
            h = (h * 16777619u) ^ p[i]; nz += (p[i] != 0);
        }
        printf("[pcm-bridge] phase=%u w=%u org=%08x rdram=%08x bytes=%d fnv=%08x nz=%u\n",
               rs64_phase_ord(), rs64_vi_committed_width(),
               rs64_vi_committed_origin(), (uint32_t)audio_data_,
               sample_count * 2, h, nz);
    }
```

### Step 3 — export patches and build

```sh
./submodule-patches/export.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

### Step 4 — run oracle positive control first

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 45 --watch-write 0x0:0x800000 --watch-write 0x14974C:0x149750 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start > scratch/agent/s2005-oracle.log 2>&1
```

Require nonzero whole-RDRAM and aligned-watch hits before proceeding.

### Step 5 — run A/B concurrently

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2005-control 30 12 > scratch/agent/s2005-control.log 2>&1 &
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_SPBOOT=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2005-treatment 30 12 > scratch/agent/s2005-treatment.log 2>&1 &
wait
```

If control crashes before VI 1024, rerun it standalone and then rerun
treatment; use the standalone control. Do not interpret treatment rows
without a valid control.

### Step 6 — analyze

From both logs, extract:
- `[audtask-ranges]` rows: per-range dram/len/dmem/payload_fnv/nz
- `[pcm-bridge]` rows: phase/rdram/bytes/fnv/nz
- `[audtask-dispatch]` count (positive control)
- `[pcm-sanity]` count

Join on phase: if treatment ranges have nz>0 and pcm-bridge has nz>0 and
FNVs match → H-audio-path-valid. Apply the discriminator table above.

## Phase gates

VI 1024/origin 0x00790400 and VI 512/origin 0x006AB400 only.
