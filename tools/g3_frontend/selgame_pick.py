import sys, collections
def rnd(s): return ((s*0xA8351D63)&0xffffffff)
def val(s): return (rnd(s)>>6)&0x7FFF
def load(p, retail):
    rows=[]
    for l in open(p, errors='replace'):
        if retail:
            if not l.startswith('[xtrace] '): continue
            f=l.split()[1:]
            # n vi ra peek pc= v0=
            site=int(f[2],16)-8
        else:
            f=l.split(); site=int(f[2],16)
        if len(f)<4: continue
        rows.append((int(f[0]),int(f[1]),site,int(f[3],16)))
    return rows
for p,r in ((sys.argv[1],1),(sys.argv[2],0)):
    rows=load(p,r)
    print('==', 'retail' if r else 'port', len(rows), 'calls')
    c=collections.Counter(x[2] for x in rows)
    print('  sites', [(hex(k),v) for k,v in c.most_common(8)])
    for i,x in enumerate(rows):
        if x[2]==0x800C5764:
            print('  PICK idx',i,'vi',x[1],'seed %08x'%x[3],'backdrop',val(x[3])%18, 'first vi', rows[0][1])
    if rows: print('  first rows', [(hex(x[2]),x[1]) for x in rows[:5]])
