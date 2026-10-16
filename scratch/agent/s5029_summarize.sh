#!/bin/zsh
# Summarize s5029 logs (retail.log can be multi-GB; one grep pass each, no copying).
D="${0:A:h}/s5029_mission_external_join"
c() { print -r -- "$1: $(grep -a -c -E "$3" "$D/$2")"; }
{
c retail_vi_control retail.log 'positive-control threshold reached'
c retail_690400 retail.log 'origin=0x00690400 width=512'
c retail_620400 retail.log 'origin=0x00620400 width=512'
c retail_consumer_800903f0 retail.log 'pc=0x800903f0'
c retail_writer_80090c80_800921e8 retail.log 'pc=0x80090c80|pc=0x800921e8'
c retail_crash retail.log 'CRASH|ABORT'
c port_hangar_6AB400 port.log 'origin=0x0*6AB400'
c port_690400 port.log 'origin=0x0*690400'
c port_620400 port.log 'origin=0x0*620400'
c port_s4534_jal_800903F0 port.log '^\[s4534-jal\].*site=800903F0'
c port_s4994_rows port.log '^\[s4994-s4540\].*kind=row'
c port_crash port.log 'CRASH|ABORT'
} | tee "$D/summary.txt"
# keep small excerpts, drop multi-GB raw logs
grep -a -E 'pc=0x80090c80|pc=0x800921e8' "$D/retail.log" | head -5 | cut -c1-260 > "$D/retail_writer_excerpt.txt"
grep -a '^\[s4994-s4540\].*kind=row' "$D/port.log" | head -4 | cut -c1-260 > "$D/port_rows_excerpt.txt"
[[ "${S5029_KEEP_RAW:-0}" = 1 ]] || rm -f "$D/retail.log" "$D/port.log"
