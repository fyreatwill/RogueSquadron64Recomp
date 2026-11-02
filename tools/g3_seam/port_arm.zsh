#!/bin/zsh
# s6793: port AT THE MOVIES playlist (s6792 presses), window shots only (no RDP dump), extra env via XE2; ends at SECS.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=${1:?}; mkdir -p $O
AP=$(sed -n 's/^port AP: //p' scratch/s6792/mov/press.txt)
env SAVE_FROM=scratch/s6779/r1/lvl1.eep SECS=${SECS:-700} CAP0=${CAP0:-340} AP="$AP" XE="${XE2:-}" zsh tools/g3_port_capture.sh $O/port
