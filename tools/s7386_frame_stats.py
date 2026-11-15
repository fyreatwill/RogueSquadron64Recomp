import glob,os,sys,statistics as st
from PIL import Image,ImageChops,ImageStat
for a in sys.argv[1:]:
    fs=sorted(glob.glob(f'{os.environ.get("RDIR","scratch/s7386")}/{a}/w_*.png'),key=lambda p:float(os.path.basename(p)[2:-4]))
    prev=None; dark=[]; stale=[]; diffs=[]
    for p in fs:
        t=float(os.path.basename(p)[2:-4]); x=Image.open(p).convert('L').resize((420,180))
        m=ImageStat.Stat(x).mean[0]
        if m<12: dark.append(round(t))
        if prev is not None:
            d=ImageStat.Stat(ImageChops.difference(x,prev)).mean[0]; diffs.append(d)
            if d<0.05 and m>=12: stale.append(round(t))
        prev=x
    print(a,'frames',len(fs),'dark',len(dark),dark[:14],'stale',len(stale),stale[:14],'median_diff %.2f'%st.median(diffs))
