#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC_OUT="$ROOT/scratch/agent/s2306_m5_temporal_recurrence"
OUT="$ROOT/scratch/agent/s2307_m5_cross_phase_join"
mkdir -p "$OUT"

zsh "$ROOT/scratch/agent/run_s2306_m5_temporal_recurrence.sh"
run_rc=$?
print "source_driver_rc=$run_rc" > "$OUT/driver.log"
print "raw_logs=$SRC_OUT/port.log,$SRC_OUT/oracle.log" >> "$OUT/driver.log"

grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2|writer-pc pc=' "$SRC_OUT/oracle.log" | tail -80 >> "$OUT/driver.log" || true
grep -a -E 'oracle_rc=|temporal_counts|verdict=' "$SRC_OUT/driver.log" | tail -20 >> "$OUT/driver.log" || true

awk -v table="$OUT/cross-phase-table.tsv" -v summary="$OUT/destination-summary.tsv" '
function val(name,    i) {
    for (i=1; i<=NF; i++) if (index($i,name"=")==1) return substr($i,length(name)+2)
    return ""
}
function norm(v) { sub(/^0[xX]/,"",v); return tolower(v) }
function hexnum(v,    s,i,c,d,n) {
    s=norm(v); n=0
    for (i=1; i<=length(s); i++) {
        c=substr(s,i,1); d=index("0123456789abcdef",c)-1
        if (d<0) return -1
        n=n*16+d
    }
    return n
}
function phys(v) {
    v=norm(v)
    if (length(v)==8 && substr(v,1,2)=="80") v=substr(v,3)
    return v
}
function scope(p,w,o) { return (p+0)"|"(w+0)"|"norm(o) }
function tuple(d,l,f,n) { return hexnum(phys(d))"|"(l+0)"|"hexnum(f)"|"(n+0) }
function abs(v) { return v<0 ? -v : v }
BEGIN {
    print "stage_phase\tpcm_phase\twidth\torigin\ttask_ordinal\tstage_event\tpcm_event\tkind\tdest\tlen\tstage_fnv\tstage_nz\tpcm_fnv\tpcm_nz\tevent_delta\texact_tuple\tstage_before_pcm" > table
    print "dest\tstage_rows\texact_source\texact_consumer\tcross_source\tcross_consumer\tmismatch_source\tmismatch_consumer\tstage_only_rows" > summary
}
$1=="[audtask-image-stage-row]" {
    if ((val("nz")+0)==0 || (val("width")+0)!=512 || norm(val("origin"))!="6ab400") next
    ++sn
    ss[sn]=val("phase")+0; sw[sn]=512; so[sn]=norm(val("origin")); stask[sn]=val("ordinal")+0
    sev[sn]=val("event")+0; sdest[sn]=phys(val("dest")); slen[sn]=hexnum(val("len"))
    sfnv[sn]=norm(val("fnv")); snz[sn]=val("nz")+0; stok[sn]=tuple(sdest[sn],slen[sn],sfnv[sn],snz[sn])
    ++sum_rows[sdest[sn]]
    next
}
$1=="[audio-join-pcm]" {
    if ((val("width")+0)!=512 || norm(val("origin"))!="6ab400") next
    ++pn
    pk["p",pn]=val("phase")+0; pk["w",pn]=512; pk["o",pn]=norm(val("origin")); pk["n",pn]=val("n")+0
    pe["p",pn]=val("event")+0; pkind["p",pn]=val("kind"); pd["p",pn]=phys(val("guest"))
    plen["p",pn]=val("bytes")+0; pfnv["p",pn]=norm(val("fnv")); pnz["p",pn]=val("nz")+0
    pt["p",pn]=tuple(pd["p",pn],plen["p",pn],pfnv["p",pn],pnz["p",pn])
    next
}
END {
    for (s=1; s<=sn; s++) {
        src_exact=0; con_exact=0; cross_src=0; cross_con=0; src_mis=0; con_mis=0
        for (p=1; p<=pn; p++) {
            if (pd["p",p]!=sdest[s]) continue
            exact=(pt["p",p]==stok[s] ? "yes" : "no")
            before=(sev[s]<pe["p",p] ? "yes" : "no")
            delta=pe["p",p]-sev[s]
            if (pkind["p",p]=="source") {
                if (exact=="yes") { src_exact++; if (pk["p",p]!=ss[s]) cross_src++ }
                else src_mis++
            } else if (pkind["p",p]=="consumer") {
                if (exact=="yes") { con_exact++; if (pk["p",p]!=ss[s]) cross_con++ }
                else con_mis++
            }
            if (exact=="yes" || (pkind["p",p]=="source" && src_mis>0)) {
                print ss[s]"\t"pk["p",p]"\t512\t0x"so[s]"\t"stask[s]"\t"sev[s]"\t"pe["p",p]"\t"pkind["p",p]"\t0x"sdest[s]"\t0x"sprintf("%x",slen[s])"\t"sfnv[s]"\t"snz[s]"\t"pfnv["p",p]"\t"pnz["p",p]"\t"delta"\t"exact"\t"before >> table
            } else if (exact=="no" && (pkind["p",p]=="source" || pkind["p",p]=="consumer")) {
                print ss[s]"\t"pk["p",p]"\t512\t0x"so[s]"\t"stask[s]"\t"sev[s]"\t"pe["p",p]"\t"pkind["p",p]"\t0x"sdest[s]"\t0x"sprintf("%x",slen[s])"\t"sfnv[s]"\t"snz[s]"\t"pfnv["p",p]"\t"pnz["p",p]"\t"delta"\t"exact"\t"before >> table
            }
        }
        if (src_exact==0 && con_exact==0) sum_only[sdest[s]]++
        sum_src[sdest[s]]+=src_exact; sum_con[sdest[s]]+=con_exact
        sum_cross_src[sdest[s]]+=cross_src; sum_cross_con[sdest[s]]+=cross_con
        sum_src_mis[sdest[s]]+=src_mis; sum_con_mis[sdest[s]]+=con_mis
        if (ss[s]==10) {
            phase10++
            if (cross_src>0 && cross_con>0) phase10_cross_both++
            if (src_exact==0 && con_exact==0) {
                phase10_only++
                if (src_mis+con_mis>0) phase10_mismatch++
            }
        }
    }
    for (d in sum_rows) print "0x"d"\t"sum_rows[d]+0"\t"sum_src[d]+0"\t"sum_con[d]+0"\t"sum_cross_src[d]+0"\t"sum_cross_con[d]+0"\t"sum_src_mis[d]+0"\t"sum_con_mis[d]+0"\t"sum_only[d]+0 >> summary
    print "stage_rows="sn" phase10_rows="phase10+0" phase10_cross_both="phase10_cross_both+0" phase10_stage_only="phase10_only+0" phase10_stage_only_with_mismatch="phase10_mismatch+0" pcm_rows="pn"" > "'$OUT'/cross-phase-counts.txt"
}' "$SRC_OUT/port.log"

cat "$OUT/cross-phase-counts.txt" >> "$OUT/driver.log"
cat "$OUT/destination-summary.tsv" >> "$OUT/driver.log"

controls=$(grep -a -c 'oracle_controls=passed whole_rdram=10000 title=1 hangar=1' "$SRC_OUT/driver.log")
writers=$(grep -a -c 'retail_writer=1' "$SRC_OUT/driver.log")
port_hangar=$(grep -a -c 'port_hangar=1' "$SRC_OUT/driver.log")
counts=$(cat "$OUT/cross-phase-counts.txt")
stage_rows=$(print "$counts" | sed -n 's/.*stage_rows=\([0-9]*\).*/\1/p')
phase10_cross=$(print "$counts" | sed -n 's/.*phase10_cross_both=\([0-9]*\).*/\1/p')
phase10_only=$(print "$counts" | sed -n 's/.*phase10_stage_only=\([0-9]*\).*/\1/p')
phase10_mismatch=$(print "$counts" | sed -n 's/.*phase10_stage_only_with_mismatch=\([0-9]*\).*/\1/p')
print "controls=$controls writers=$writers port_hangar=$port_hangar $counts" | tee -a "$OUT/driver.log"
if (( controls==0 || writers==0 || port_hangar==0 || stage_rows==0 )); then
    verdict=H-CoverageInvalid
elif (( phase10_cross>0 )); then
    verdict=H-CrossPhaseExact
elif (( phase10_only>0 && phase10_mismatch>0 )); then
    verdict=H-PayloadTupleMismatch
else
    verdict=H-TrulyUnconsumed
fi
print "verdict=$verdict" | tee -a "$OUT/driver.log"
exit 0
