#!/bin/zsh
# s7946: run the three F6-panel witnesses back to back (one game at a time) for one screen shape and print one row each:
#   s7942 pad cursor (pixel band vs logged rect), s7944 pad Clear/Reset drawn text + pixels, s7937 mouse/key e2e (HID).
# Usage: env PANEL_ASPECT=<4:3|16:9|21:9|unset> PANEL_FS=<0|1> zsh tools/s7946_panel_witness_all.zsh
# Needs: unlocked screen, Screen Recording + Accessibility for this shell, no other game instance. Exit 0 only if all 3 PASS.
set -u
R=$PWD; tot=0; ok=0
pgrep -f 'RogueSquadron64Recomp rogue_squadron.z64' >/dev/null && { echo "another game instance is running"; exit 2; }
for w in s7942_pad_cursor_witness s7944_pad_text_witness s7937_panel_e2e; do
  out=$(zsh $R/tools/$w.zsh 2>&1); tot=$((tot+1))
  tag=$(print -r -- "$out" | grep '^tag=' | tail -1)
  if print -r -- "$out" | grep -q 'VERDICT PASS' || print -r -- "$tag" | grep -q 'alive=1 checks=[1-9][0-9]* fail=0$'; then
    v=PASS; ok=$((ok+1)); else v=FAIL; fi
  echo "$v $w | $tag"
  sleep 1
done
echo "tag=s7946_panel_witness_all aspect=${PANEL_ASPECT:-retail} fs=${PANEL_FS:-0} pass=$ok/$tot"
(( ok == tot ))
