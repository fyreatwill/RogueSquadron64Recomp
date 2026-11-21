# s7752 offline port-ucode task replay + angrylion task renderer

Three-way RDP-output comparison on one captured gfx task (ROGUESQ_S7751_SNAP .bin, see tools/s7751_cxd4_task/README.md):

1. Build: `zsh tools/s7752_port_task/build.sh` (harness links the live build's factor5_ucode_lean.cpp.o: rebuild the game
   first after a ucode fixup edit; rdp_render links the 16 MB angrylion core from tools/angrylion_replay/build16.sh).
2. Port replay: `env ROGUESQ_UCODE_CAP=1048576 ROGUESQ_G5B_TG_FIX=<0|1> tools/s7752_port_task/harness <snap.bin> <out.rdp>`.
   CAP must be the live dd>1 policy value (main.cpp sets 1048576 at dd>1); at the 65536 default the cap fires and the
   stream is a truncated prefix. TG_FIX=1 is the live dd>1 default (s6896 TriGen s16 edge clamp), 0 = retail ucode input.
   Positive control: TG_FIX=1 output must equal the snap's own live tail byte for byte (3/3 tasks in s7752).
3. Command diff: `python3 tools/s7752_rdp_residual.py <snap.bin|a.rdp> <b.rdp>` (difflib over whole commands).
4. Render: `tools/s7752_port_task/rdp_render <snap.bin> <stream.rdp|snap.bin> <out.ram>`, then
   `python3 tools/s7752_render_diff.py <stream> <a.ram> <b.ram> [--ctl]` (per-image differing px + 5-bit channel delta
   histogram; --ctl flips one pixel and must report it).
