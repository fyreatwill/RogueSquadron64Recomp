import re,statistics as S
R=[]
for l in open('scratch/agent/m6/s5683_pd2/run.log'):
    m=re.search(r"pos=([-\d.e]+),([-\d.e]+),([-\d.e]+) vel=([-\d.e]+),([-\d.e]+),([-\d.e]+) sx=([-\d.]+) sy=([-\d.]+)",l)
    if m:R.append([float(x) for x in m.groups()])
def c(a,b):
    if len(a)<3 or S.pstdev(a)==0 or S.pstdev(b)==0:return float('nan')
    ma,mb=S.mean(a),S.mean(b);return sum((x-ma)*(y-mb) for x,y in zip(a,b))/len(a)/S.pstdev(a)/S.pstdev(b)
d=[[R[i+1][k]-R[i][k] for k in range(3)] for i in range(len(R)-1)]
print(len(R))
for i in range(3):
  print('dpos'+'xyz'[i],' '.join('v%s=%.2f'%('xyz'[j],c([x[i] for x in d],[r[3+j] for r in R[1:]])) for j in range(3)),'sx=%.2f sy=%.2f'%(c([x[i] for x in d],[r[6] for r in R[1:]]),c([x[i] for x in d],[r[7] for r in R[1:]])))
for k,n in((6,'sx'),(7,'sy')):
  from collections import Counter;print(n,Counter(r[k] for r in R))
for s in(-1,0,1):
  g=[d[i][1] for i in range(len(d)) if R[i+1][7]==s];print('sy',s,len(g),S.mean(g) if g else None)
for s in(-1,0,1):
  g=[d[i][0] for i in range(len(d)) if R[i+1][6]==s];print('sx',s,len(g),S.mean(g) if g else None)
