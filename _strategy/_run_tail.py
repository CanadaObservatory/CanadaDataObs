from _colour_opt import *
import json, sys

def fit_tails(focal_hex, tail_bands, seed=0):
    """focal_hex: {code:hex} 6 focal. tail_bands: {code:(hue_lo,hue_hi,L_lo,L_hi,C_lo,C_hi)}.
       Each tail maximises min worst-of-3 dE to the 6 focal AND to already-placed tails
       (tail-tail soft floor 12 normal), hard floor vs focal = 15 in all 3 modes."""
    rng=random.Random(seed)
    focal_lab={m:{c:cvd_lab(focal_hex[c],m) for c in focal_hex} for m in MODES}
    placed={}  # code->hex
    out={}
    order=list(tail_bands.keys())
    for c in order:
        hlo,hhi,Llo,Lhi,Clo,Chi=tail_bands[c]
        best=None
        for _ in range(28000):
            H=rng.uniform(hlo,hhi); L=rng.uniform(Llo,Lhi); C=rng.uniform(Clo,Chi)
            lab=lch2lab((L,C,H))
            h=legible(lab)
            if not h: continue
            labm={m:cvd_lab(h,m) for m in MODES}
            # NORMAL-vision min vs focal (the binding distinctness when activated)
            mf_n=min(ciede2000(labm['normal'],focal_lab['normal'][fc]) for fc in focal_hex)
            # CVD min vs focal (soft — maximise but not a hard gate; dichromatic ceiling)
            mf_cvd=min(ciede2000(labm[m],focal_lab[m][fc])
                       for fc in focal_hex for m in ['deuteranopia','protanopia'])
            mt=1e9
            for pc,ph in placed.items():
                d=ciede2000(hex2lab(h),hex2lab(ph)); mt=min(mt,d)
            ok_f = mf_n>=15
            # primary: clear focal in NORMAL (>=15); then keep a comfort margin but
            # stay MATTE (chroma bands cap saturation) and maximise tail spacing + CVD
            comfort = 1 if mf_n>=16.5 else 0
            score=(1 if ok_f else 0, comfort, 0.45*min(mt,26) + 0.12*mf_cvd + 0.05*mf_n)
            if best is None or score>best[0]:
                best=(score,h,mf_n,mt,mf_cvd)
        out[c]=best[1]; placed[c]=best[1]
        flag='' if best[2]>=15 else '  <<< NORMAL FAIL'
        print(f'  {c} {best[1]}  normalVSfocal={best[2]:.1f} VStail={best[3]:.1f} cvdVSfocal={best[4]:.1f}{flag}')
    return out

def verify_tails(focal_hex, tails):
    fl={m:{c:cvd_lab(focal_hex[c],m) for c in focal_hex} for m in MODES}
    wn=1e9;wnp=None; wc=1e9;wcp=None
    for tc,th in tails.items():
        for fc in focal_hex:
            dn=ciede2000(cvd_lab(th,'normal'),fl['normal'][fc])
            if dn<wn: wn=dn; wnp=(tc,fc)
            for m in ['deuteranopia','protanopia']:
                d=ciede2000(cvd_lab(th,m),fl[m][fc])
                if d<wc: wc=d; wcp=(tc,fc,m)
    # tail-tail normal min
    tt=1e9;ttp=None; ts=list(tails.items())
    for i in range(len(ts)):
        for j in range(i+1,len(ts)):
            d=ciede2000(hex2lab(ts[i][1]),hex2lab(ts[j][1]))
            if d<tt: tt=d; ttp=(ts[i][0],ts[j][0])
    print(f'  tail-vs-focal NORMAL min dE00={wn:.2f} {wnp}')
    print(f'  tail-vs-focal CVD    min dE00={wc:.2f} {wcp}')
    print(f'  tail-vs-tail NORMAL  min dE00={tt:.2f} {ttp}')
    print('  flags',line_flags(list(tails.values()),list(tails.keys())))
    return wn

if __name__=='__main__':
    pass

def fit_tails_vec(focal_hex, tail_bands, seed=0, N=120000):
    rng=np.random.default_rng(seed)
    focal_lab={m:{c:cvd_lab(focal_hex[c],m) for c in focal_hex} for m in MODES}
    greylab=hex2lab(GREY)
    placed={}; out={}
    for c in tail_bands:
        hlo,hhi,Llo,Lhi,Clo,Chi=tail_bands[c]
        H=rng.uniform(hlo,hhi,N); L=rng.uniform(Llo,Lhi,N); C=rng.uniform(Clo,Chi,N)
        lab=lch2lab_batch(L,C,H)
        lin,xyz=lab2linrgb_batch(lab)
        ok=np.all((lin>=-0.001)&(lin<=1.001),axis=1)
        lin=np.clip(lin,0,1)
        lum=lin@np.array([0.2126,0.7152,0.0722])
        contrast=(1.05)/(lum+0.05)
        labn=cvd_lab_batch(lin,'normal')
        gdist=ciede2000_vec(labn,greylab)
        ok=ok&(contrast>=3.05)&(gdist>=12.5)&(lab[:,0]>=22)
        idx=np.where(ok)[0]
        if len(idx)==0:
            raise RuntimeError(f'no legible candidate for {c}')
        labn=labn[idx]; lin_ok=lin[idx]
        labd=cvd_lab_batch(lin_ok,'deuteranopia'); labp=cvd_lab_batch(lin_ok,'protanopia')
        # min normal vs focal
        mf_n=np.full(len(idx),1e9); mf_cvd=np.full(len(idx),1e9)
        for fc in focal_hex:
            mf_n=np.minimum(mf_n, ciede2000_vec(labn,focal_lab['normal'][fc]))
            mf_cvd=np.minimum(mf_cvd, ciede2000_vec(labd,focal_lab['deuteranopia'][fc]))
            mf_cvd=np.minimum(mf_cvd, ciede2000_vec(labp,focal_lab['protanopia'][fc]))
        # tail spacing (normal) vs already placed
        mt=np.full(len(idx),1e9)
        for ph in placed.values():
            mt=np.minimum(mt, ciede2000_vec(labn, hex2lab(ph)))
        okf=mf_n>=15
        comfort=mf_n>=16.5
        score=np.where(okf,1,0)*1e6 + np.where(comfort,1,0)*1e3 \
              + 0.45*np.minimum(mt,26) + 0.12*mf_cvd + 0.05*mf_n
        bi=int(np.argmax(score))
        # reconstruct hex from the (normal-mode) Lab of the chosen sample
        h=lab2hex(labn[bi])
        out[c]=h; placed[c]=h
        print(f'  {c} {h}  normalVSfocal={mf_n[bi]:.1f} VStail={mt[bi]:.1f} cvdVSfocal={mf_cvd[bi]:.1f}'
              + ('' if mf_n[bi]>=15 else '  <<< NORMAL FAIL'))
    return out
