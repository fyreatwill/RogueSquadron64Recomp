#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s2304_m5_task_stage_ordinal_join"
TABLE="$OUT/ordinal-table.tsv"
ORACLE="$OUT/oracle.log"
PORT="$OUT/port.log"

oracle_controls=0
if grep -a -q 'positive-control threshold reached: watch index 0 callbacks=10000' "$ORACLE" &&
   grep -a -q 'origin=0x00790400 width=1024' "$ORACLE" &&
   grep -a -qi 'origin=0x006ab400 width=512' "$ORACLE"; then
    oracle_controls=1
fi
retail_writer=0
if grep -a -q '^\[oracle\] writer-pc-phase origin=0x006ab400 width=512 watch=2 range=' "$ORACLE" &&
   grep -a -q '^\[oracle\] writer-pc pc=0x8008eb8c n=' "$ORACLE" &&
   grep -a -q '^\[oracle\] writer-pc pc=0x8008ebbc n=' "$ORACLE" &&
   grep -a -q '^\[oracle\] writer-pc pc=0x80094648 n=' "$ORACLE"; then
    retail_writer=1
fi
port_title=0
port_hangar=0
grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$PORT" && port_title=1
grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$PORT" && port_hangar=1

table_rows=$(awk -F '\t' 'NR > 1 { n++ } END { print n + 0 }' "$TABLE")
dma_ok=$(awk -F '\t' 'NR > 1 && $11 == 1 { n++ } END { print n + 0 }' "$TABLE")
source_ok=$(awk -F '\t' 'NR > 1 && $12 == 1 { n++ } END { print n + 0 }' "$TABLE")
consumer_ok=$(awk -F '\t' 'NR > 1 && $13 == 1 { n++ } END { print n + 0 }' "$TABLE")
ordered_ok=$(awk -F '\t' 'NR > 1 && $14 == "yes" { n++ } END { print n + 0 }' "$TABLE")
bad_rows=$(awk -F '\t' 'NR > 1 && ($11 != 1 || $12 != 1 || $13 != 1 || $14 != "yes") { n++ } END { print n + 0 }' "$TABLE")
native_stage_only=$(grep -a -E -c '^\[audtask-image-join\].*stage_nz=[1-9].*classification=stage-only' "$PORT" || true)

{
    print -- "--- controls ---"
    print "oracle_controls=$oracle_controls retail_writer=$retail_writer port_title=$port_title port_hangar=$port_hangar"
    print -- "--- complete ordinal table ---"
    sed -n '1,10000p' "$TABLE"
    print -- "--- independent native join line ---"
    print "native_nonzero_stage_only=$native_stage_only"
    print -- "--- counts ---"
    print "table_rows=$table_rows dma_ok=$dma_ok source_ok=$source_ok consumer_ok=$consumer_ok ordered_ok=$ordered_ok bad_rows=$bad_rows"
    if (( oracle_controls == 0 || retail_writer == 0 || port_title == 0 || port_hangar == 0 || table_rows == 0 )); then
        print "verdict=H-CoverageInvalid"
    elif (( bad_rows == 0 )); then
        print "verdict=H-TaskStageConsumerComplete"
    else
        print "verdict=H-TaskStageOutputGap"
    fi
} > "$OUT/recheck.log"
tail -8 "$OUT/recheck.log"
