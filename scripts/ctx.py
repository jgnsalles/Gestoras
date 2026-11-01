import re,glob,sys
pat=sys.argv[2].split('|'); n=int(sys.argv[3]) if len(sys.argv)>3 else 350
for f in sorted(glob.glob(sys.argv[1])):
    t=re.sub(r'\s+',' ',open(f,errors='ignore').read()); shown=0
    for w in pat:
        for m in list(re.finditer(re.escape(w),t))[:1]:
            print(f"[{f.split('/')[-1][:-4]}|{w}] …{t[max(0,m.start()-n):m.end()+n]}…"); shown+=1
