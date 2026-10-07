# Next work unit: M5 Step 9l — who writes the audio command buffer (7728 B block) records, and does the record builder ever run on it?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4213: all run_task tasks are type 2 with the real audio ucode; data_ptr = per-phase 7728 B (=96*0x50+0x30) rs_malloc block; data_size 1..3. H-misclassified refuted.

Hypotheses:
- H-cmdbuf-never-built: block is the audio command buffer but the builder never writes records into it (ASCII filename text from earlier use persists).
- H-builder-wrong-target: builder writes records elsewhere; OSTask.data_ptr points at the wrong block.
- H-text-is-header: ASCII is the 0x30 header/other field and real records sit later (we only looked at first 0x50).

Discriminator (one build, one run, phases 3-5): in rsp.cpp census also (a) hash+count nonzero-ASCII fraction of ALL 96 records at data_ptr+0x30 each task, (b) record which records changed since previous task; (c) log the guest address of the OSTask data_ptr field ((uint8_t*)task - rdram + offset) and its writer via existing guest-write watch if available; control: count changed bytes must be >0 across phase transition (new block). Outcomes: all 96 records ASCII/constant => never-built; records vary non-ASCII beyond first => H-text-is-header; builder pc seen writing a different block => wrong-target.
Any lib/ edit needs submodule-patches/export.sh + commit.
