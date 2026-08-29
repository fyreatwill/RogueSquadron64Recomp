# Session 3239 — MusyX pointer allocation and teardown audit

Selected hypothesis: `H-NullConsumer` (static selection, not a runtime
occurrence). `rs_malloc` initializes its return accumulator (`s2`) to zero at
`0x80001AE4`. The no-fit path reaches `0x80001C74` without assigning `s2`,
then copies it to `v0` and returns. There is no fatal call or non-returning
failure branch in the allocator.

## Writer / consumer / free table

| Address | Role | Evidence | Ordering result |
| --- | --- | --- | --- |
| `0x8008F228` | `allocateSongChannelArray` publishes the second allocation result to `0x80149758` (`-0x68A8`) | `rs_malloc` at `0x8008F210` returns in `v0`; the next instruction sequence stores it unconditionally | A zero result can be published; no success check |
| `0x80091060` | `musyxBuildVoiceCommandList` loads the selected channel pointer from `0x80149758 + 4 * index` | indexed `lw` followed by `0x80091074` publication to `0x80149750` and `sh zero, 0(v0)` at `0x80091078` | A null selected pointer is immediately dereferenced |
| `0x80091074` | publishes the selected/derived command-list head to `0x80149750` (`-0x68B0`) | unconditional store after the indexed load | Does not validate the loaded pointer |
| `0x8009123C` | `musyxSynthFrame` parent | called from the live synth path and explicitly pumped by shutdown/wait in this tree | Consumer-side null handling is not present in the audited chain |
| `0x80091E28` | `shutdownAudioEngine` frees `0x80149758` | free occurs after a `musyxSynthFrame` dispatch at `0x80091D84` and after the wait countdown pump | No clear of `0x80149758` is visible before or after free |
| `0x80091F78` | `waitForMusyXAudioTaskDone` frees `0x80149758` | wait path also dispatches/pumps `musyxSynthFrame` before the free sequence | No clear of `0x80149758` is visible; a post-return consumer edge is not proven |

The allocator result is capable of being zero and reaching a consumer that
dereferences it. This selects `H-NullConsumer` over `H-AllocatorNeverNull`.
`H-TeardownStale` remains unresolved: the recovered code proves missing
visible clears, but does not prove a consumer after either free or a
concurrent teardown race.

No patch was landed. The audit identifies the writer and the illegitimate
failure value, but does not establish that this failure occurs in the
validated port route or provide a semantics-preserving replacement for the
whole generated command-list function. A future guard must be a patches/
override and define legitimate skip/recovery behavior at the consumer;
changing `rs_malloc` globally would conceal the origin.

ORIGIN: `rs_malloc` at `0x80001C74` produces zero on the no-fit path; the
published null is not a legitimate MusyX channel pointer. Stale-after-free
legitimacy remains unproven.
