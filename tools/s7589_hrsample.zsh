#!/bin/zsh
# s7589 class HR: outside-the-process host-resource sampler for the one live game (tools/rs64_game_pid.zsh). No build needed.
# usage: zsh tools/s7589_hrsample.zsh <outdir> <max_s> [interval_s=15]
# <outdir>/hr.tsv: t_s fds fd_reg fd_pipe fd_sock fd_kq fd_other threads ports iosurf_n ioaccel_g_n foot_mb
#   fds/fd_* from lsof (by TYPE), threads from ps -M, ports = top #PORTS (lsmp needs root), iosurf_n / ioaccel_g_n = vmmap
#   --summary IOSurface / IOAccelerator (graphics) region counts, foot_mb = footprint phys_footprint. Score with tools/s7589_hr_report.py.
cd "$(git rev-parse --show-toplevel)" || exit 1
O=$1; M=$2; I=${3:-15}; mkdir -p $O; source tools/rs64_game_pid.zsh
pid=""; for i in $(seq 1 120); do pid=$(rs64_game_pid 2>/dev/null) && break; /bin/sleep 1; done
[[ -z $pid ]] && { echo "no game" > $O/hr.err; exit 1; }
t0=$(date +%s); print "t_s\tfds\tfd_reg\tfd_pipe\tfd_sock\tfd_kq\tfd_other\tthreads\tports\tiosurf_n\tioaccel_g_n\tfoot_mb" > $O/hr.tsv
while kill -0 $pid 2>/dev/null; do t=$(( $(date +%s) - t0 )); (( t > M )) && break
  fl=$(lsof -n -P -p $pid 2>/dev/null | awk 'NR>1 && $4 ~ /^[0-9]+/ {n++; ty=$5; if(ty=="REG")r++; else if(ty=="PIPE")p++; else if(ty ~ /IPv|unix|systm/)s++; else if(ty=="KQUEUE")k++; else o++} END{printf "%d\t%d\t%d\t%d\t%d\t%d", n,r,p,s,k,o}')
  th=$(ps -M -p $pid 2>/dev/null | awk 'NR>1' | wc -l | tr -d ' ')
  po=$(top -l 1 -pid $pid -stats pid,ports 2>/dev/null | awk -v p=$pid '$1==p{print $2; exit}')
  io=$(vmmap --summary $pid 2>/dev/null | awk '$1=="IOSurface"{s=$NF} /^IOAccelerator \(graphics\)/{g=$NF} END{printf "%s\t%s", (s==""?"na":s), (g==""?"na":g)}')
  f=$(footprint -p $pid 2>/dev/null | awk '/phys_footprint:/{v=$2;u=$3; if(u=="GB")v*=1024; if(u=="KB")v/=1024; print v; exit}')
  print "$t\t$fl\t$th\t${po:-na}\t$io\t${f:-na}" >> $O/hr.tsv
  (( t >= 60 )) && [[ ! -f $O/lsof_60.txt ]] && lsof -n -P -p $pid > $O/lsof_60.txt 2>/dev/null
  /bin/sleep $I; done
lsof -n -P -p $pid > $O/lsof_end.txt 2>/dev/null
echo "sampler end t=$(( $(date +%s) - t0 ))" >> $O/hr.log
