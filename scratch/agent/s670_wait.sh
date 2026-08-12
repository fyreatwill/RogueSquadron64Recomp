#!/bin/bash
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
elapsed=0
timeout=580
while true; do
  if grep -q "VERDICT" scratch/agent/s670_logs/wrapper.stdout 2>/dev/null; then
    break
  fi
  if [ "$elapsed" -ge "$timeout" ]; then
    break
  fi
  sleep 5
  elapsed=$((elapsed+5))
done
echo "=== waited ${elapsed}s ==="
tail -60 scratch/agent/s670_logs/wrapper.stdout
