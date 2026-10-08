# Next work unit: M5 Step 9m — who sets OSTask.data_ptr for the audio task, and where does the audio command list really live?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4214: data_ptr block = menu heap block with ASCII filenames + pointer structs (0x28 stride), not audio records. H-builder-wrong-target selected.

Hypotheses:
- H-task-struct-stale: OSTask struct (in guest) is built correctly but our runtime reads it from the wrong place/offset (data_ptr field misread, e.g. struct layout/endianness).
- H-builder-skipped: game builds the task with a real audio list elsewhere but a stubbed audio setup function leaves data_ptr uninitialised (pointing to freed memory reused by the menu).
- H-ucode-uses-other-ptr: the real list is reached via ucode data (udata 0x800A4E00) or output_buff, and data_ptr is irrelevant.

Discriminator (one build, one run): in run_task dump the whole OSTask (64 bytes) + guest address of the task struct, and use the existing guest-write watch (s4211 ring approach) to log the PC that last wrote task+0x30 (data_ptr) and task+0x34 (size); also dump words at the task struct's neighbours (output_buff, yield_data_ptr). Control: watch must fire on a known-written field (e.g. task+0x0 type). Outcomes: writer PC in a stubbed/audio-setup func => builder-skipped; fields consistent with layout but another pointer nonzero and sensible => ucode-uses-other-ptr; layout mismatch => stale.
Any lib/ edit needs submodule-patches/export.sh + commit.
