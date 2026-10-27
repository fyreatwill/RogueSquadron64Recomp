import sys,glob
for f in sorted(glob.glob(sys.argv[1]+'/fb_*.ppm')):
    d=open(f,'rb').read()
    p=d.split(b'\n',4); w,h=map(int,p[2].split()); px=p[4]
    m=[max(px[i*w*3:(i+1)*w*3])for i in range(h)]
    lit=[i for i,v in enumerate(m) if v>24]
    print(f.split('/')[-1],w,(lit[0],lit[-1],len(lit)) if lit else None)
