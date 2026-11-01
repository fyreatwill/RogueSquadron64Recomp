import sys,glob
from PIL import Image, ImageStat
for d in sys.argv[1:]:
    f=sorted(glob.glob(d+'/w_*.png')); n=w=s=0
    for x in f:
        t=float(x.split('w_')[1][:-4])
        if not 12<=t<=26: continue
        im=Image.open(x).convert('L').crop((0,80,1280,1024)).resize((160,118))
        st=ImageStat.Stat(im.crop((0,25,160,95))); n+=1
        if st.mean[0]>235 and st.stddev[0]<8: w+=1
        elif st.stddev[0]>25: s+=1
    print(f'{d}: caps12-26s={n} white={w} scene(std>25)={s}')
