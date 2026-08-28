# Substitution record

1. The planned retail-vs-port VI-mode discriminator could not run because the
   oracle's debugger-enabled mupen64plus core was missing. The first command
   also used a stale unsupported `--positive-rdram` flag.

2. This iteration's evidence: the corrected oracle command exited rc 1 before
   emulation with `dlopen(.../libmupen64plus.dylib): no such file`; local
   searches found no core or Rice plugin. The port arm independently ran for
   90 seconds and logged four calls (320, 2, 640, 640), with zero width-1024
   calls, but that cannot substitute for retail ground truth.

3. The single experiment that would refute this explanation is to build or
   install the debugger-enabled core and Rice plugin, then rerun the corrected
   oracle command with the whole-RDRAM watch. If it still cannot load or fails
   before its positive-control hits, the dependency explanation remains
   supported; if it reaches title/hangar, this iteration was only a path/setup
   failure and the discriminator can proceed.
