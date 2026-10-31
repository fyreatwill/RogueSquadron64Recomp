#!/bin/zsh
# s6696 G3d: per m6 run dir, flight-phase [g1b] medians (t>=60): tasks/s, sd_wall ms/task, sd_cpu. One line per dir, sorted by log mtime.
# usage: zsh tools/g3d_g1b_census.sh [glob] > out.tsv
cd "$(git rev-parse --show-toplevel)"
for d in scratch/agent/m6/${~1:-*}(/); do
  f=""; for c in $d/run.log $d/run.log.zst $d/run.log.gz; do [ -f $c ] && { f=$c; break; }; done
  [ -n "$f" ] || continue
  print -r -- "$(stat -f %m $f) $(stat -f %Sm -t %m-%d_%H:%M $f) $f"
done | sort -n | while read m ds f; do
  case $f in *.zst) cat=zstdcat;; *.gz) cat=gzcat;; *) cat=cat;; esac
  $cat $f 2>/dev/null | grep -a '^\[g1b\]' | awk -v m=$ds -v f=$f '
    { split($2,a,"="); t=a[2]; if (t<60) next; split($4,b,"="); split($5,c,"="); split(c[2],cw,"/"); split($6,e,"="); split(e[2],cc,"/");
      n++; tk[n]=b[2]; sw[n]=cw[1]; sc[n]=cc[1] }
    function med(x,  i,j,tmp){ for(i=1;i<=n;i++)for(j=i+1;j<=n;j++) if(x[j]<x[i]){tmp=x[i];x[i]=x[j];x[j]=tmp}; return x[int((n+1)/2)] }
    END { if (n<20) exit; printf "%s\t%d\t%.1f\t%.1f\t%.1f\t%s\n", m, n, med(tk), med(sw), med(sc), f }'
done
