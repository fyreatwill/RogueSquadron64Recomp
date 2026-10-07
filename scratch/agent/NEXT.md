# Next work unit: M5 Step 9k — is the "audio" task with data_ptr in a 7728 B menu block really audio?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4212: data_ptr pairs are ordinary rs_malloc 7728 B blocks (menu initializer, alloc at phase entry, free at phase exit). No double ownership.

Hypotheses:
- H-misclassified: task classified as audio (rsp.cpp is_audio_task) is actually a gfx/other task whose data_ptr is the menu double buffer.
- H-stale-ptr: audio thread submits a real audio task whose OSTask data_ptr field was never refreshed and aliases freed/reused heap.
- H-menu-uses-audio-ucode: menu code legitimately builds a Factor5 audio-format buffer there (unlikely: contents are ASCII names).

Discriminator (one run): at the is_audio_task hook in lib/N64ModernRuntime/librecomp/src/rsp.cpp log task type, ucode_boot, ucode, ucode_data, data_ptr, data_size and g_rs64_last_guest_pc, plus at rs_malloc entry (funcs_0.c, via fixup script) log g_rs64_last_guest_pc for size==7728. Positive control: log all tasks incl. gfx. Outcomes: ucode ptr equals gfx ucode => H-misclassified; ucode is audio ucode and data_ptr in freed/reused block => H-stale-ptr. Any lib/ edit needs submodule-patches/export.sh + commit.
