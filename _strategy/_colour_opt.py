"""Colour-system verification + optimisation for CanObs.
CIEDE2000 (Sharma constants) + Machado-2008 CVD simulation (deut/protan, sev 1.0).
"""
import numpy as np, itertools, random, math, json

# ---------- sRGB <-> Lab ----------
def hex2rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i+2],16) for i in (0,2,4)], float)/255.0

def rgb2hex(rgb):
    rgb = np.clip(np.round(rgb*255),0,255).astype(int)
    return '#%02X%02X%02X' % tuple(rgb)

def _lin(c):
    return np.where(c<=0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def _delin(c):
    return np.where(c<=0.0031308, c*12.92, 1.055*np.power(np.clip(c,0,None),1/2.4)-0.055)

M_RGB2XYZ = np.array([[0.4124564,0.3575761,0.1804375],
                      [0.2126729,0.7151522,0.0721750],
                      [0.0193339,0.1191920,0.9503041]])
WHITE = np.array([0.95047,1.0,1.08883])

def rgb2xyz(rgb):
    return M_RGB2XYZ @ _lin(rgb)

def xyz2lab(xyz):
    x,y,z = xyz/WHITE
    def f(t): return np.where(t>(6/29)**3, np.cbrt(t), t/(3*(6/29)**2)+4/29)
    fx,fy,fz = f(x),f(y),f(z)
    return np.array([116*fy-16, 500*(fx-fy), 200*(fy-fz)])

def hex2lab(h): return xyz2lab(rgb2xyz(hex2rgb(h)))

def lab2lch(lab):
    L,a,b = lab
    C = math.hypot(a,b); H = math.degrees(math.atan2(b,a))%360
    return np.array([L,C,H])
def lch2lab(lch):
    L,C,H = lch
    return np.array([L, C*math.cos(math.radians(H)), C*math.sin(math.radians(H))])
def lab2xyz(lab):
    L,a,b = lab
    fy=(L+16)/116; fx=fy+a/500; fz=fy-b/200
    def fi(t): return np.where(t>6/29, t**3, 3*(6/29)**2*(t-4/29))
    return np.array([fi(fx),fi(fy),fi(fz)])*WHITE
M_XYZ2RGB = np.linalg.inv(M_RGB2XYZ)
def lab2hex(lab):
    rgb = _delin(M_XYZ2RGB @ lab2xyz(lab))
    return rgb2hex(rgb)
def lab2rgb_raw(lab):
    return _delin(M_XYZ2RGB @ lab2xyz(lab))
def in_gamut(lab):
    rgb = M_XYZ2RGB @ lab2xyz(lab)
    rgb = _delin(rgb)
    return np.all(rgb>=-0.001) and np.all(rgb<=1.001)

# ---------- CIEDE2000 ----------
def ciede2000(lab1,lab2):
    L1,a1,b1=lab1; L2,a2,b2=lab2
    kL=kC=kH=1
    C1=math.hypot(a1,b1); C2=math.hypot(a2,b2)
    Cbar=(C1+C2)/2
    G=0.5*(1-math.sqrt(Cbar**7/(Cbar**7+25**7))) if Cbar>0 else 0.5
    a1p=(1+G)*a1; a2p=(1+G)*a2
    C1p=math.hypot(a1p,b1); C2p=math.hypot(a2p,b2)
    h1p=math.degrees(math.atan2(b1,a1p))%360
    h2p=math.degrees(math.atan2(b2,a2p))%360
    dLp=L2-L1; dCp=C2p-C1p
    if C1p*C2p==0: dhp=0
    elif abs(h2p-h1p)<=180: dhp=h2p-h1p
    elif h2p-h1p>180: dhp=h2p-h1p-360
    else: dhp=h2p-h1p+360
    dHp=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dhp)/2)
    Lbar=(L1+L2)/2; Cbarp=(C1p+C2p)/2
    if C1p*C2p==0: hbarp=h1p+h2p
    elif abs(h1p-h2p)<=180: hbarp=(h1p+h2p)/2
    elif h1p+h2p<360: hbarp=(h1p+h2p+360)/2
    else: hbarp=(h1p+h2p-360)/2
    T=(1-0.17*math.cos(math.radians(hbarp-30))+0.24*math.cos(math.radians(2*hbarp))
       +0.32*math.cos(math.radians(3*hbarp+6))-0.20*math.cos(math.radians(4*hbarp-63)))
    dtheta=30*math.exp(-((hbarp-275)/25)**2)
    Rc=2*math.sqrt(Cbarp**7/(Cbarp**7+25**7)) if Cbarp>0 else 0
    Sl=1+(0.015*(Lbar-50)**2)/math.sqrt(20+(Lbar-50)**2)
    Sc=1+0.045*Cbarp
    Sh=1+0.015*Cbarp*T
    Rt=-math.sin(math.radians(2*dtheta))*Rc
    return math.sqrt((dLp/(kL*Sl))**2+(dCp/(kC*Sc))**2+(dHp/(kH*Sh))**2
                     +Rt*(dCp/(kC*Sc))*(dHp/(kH*Sh)))

# ---------- Machado 2008 CVD (severity 1.0) ----------
# Standard published matrices (operate on linear RGB)
MACHADO = {
 'deuteranopia': np.array([[0.367322,0.860646,-0.227968],
                           [0.280085,0.672501,0.047413],
                           [-0.011820,0.042940,0.968881]]),
 'protanopia':   np.array([[0.152286,1.052583,-0.204868],
                           [0.114503,0.786281,0.099216],
                           [-0.003882,-0.048116,1.051998]]),
}
def cvd_lab(h, mode):
    if mode=='normal': return hex2lab(h)
    lin=_lin(hex2rgb(h))
    sim=MACHADO[mode]@lin
    sim=np.clip(sim,0,1)
    xyz=M_RGB2XYZ@sim
    return xyz2lab(xyz)

# ---------- contrast on white ----------
def contrast_white(h):
    lin=_lin(hex2rgb(h))
    Lum=0.2126*lin[0]+0.7152*lin[1]+0.0722*lin[2]
    return (1.0+0.05)/(Lum+0.05)

MODES=['normal','deuteranopia','protanopia']
GREY='#555555'

def min_pair(hexes, mode):
    labs=[cvd_lab(h,mode) for h in hexes]
    m=1e9; wp=None
    for i,j in itertools.combinations(range(len(hexes)),2):
        d=ciede2000(labs[i],labs[j])
        if d<m: m=d; wp=(i,j)
    return m,wp

def audit(hexes, names):
    res={}
    for mode in MODES:
        m,wp=min_pair(hexes,mode)
        res[mode]=(m, names[wp[0]], names[wp[1]])
    return res

def line_flags(hexes,names):
    flags=[]
    for h,n in zip(hexes,names):
        c=contrast_white(h)
        L=hex2lab(h)[0]
        g=ciede2000(hex2lab(h),hex2lab(GREY))
        if c<3.0: flags.append(f"{n} contrast {c:.2f}")
        if L<22: flags.append(f"{n} L*{L:.1f} near-black")
        if g<12: flags.append(f"{n} dE{g:.1f} to grey")
    return flags

# ---------- constrained optimiser ----------
def legible(lab):
    if not in_gamut(lab): return None
    h=lab2hex(lab)
    if contrast_white(h)<3.05: return None
    if ciede2000(hex2lab(h),hex2lab(GREY))<12.5: return None
    if lab[0]<22: return None
    return h

def cvd_lab_from_hex(h,mode):
    return cvd_lab(h,mode)

def optimise(items, fixed, hue_bands, L_bands, C_bands,
             adjacency, normal_floor=15.0, cvd_floor=15.0,
             cvd_all=False, seed=0, iters=60000):
    """items: list of codes. fixed: {code:hex}. *_bands: {code:(lo,hi)}.
       adjacency: set of frozenset({a,b}) requiring cvd_floor in deut+protan.
       cvd_all: if True every pair must clear cvd_floor in deut+protan (focal)."""
    rng=random.Random(seed)
    state={}  # code -> lch
    for c in items:
        if c in fixed:
            state[c]=lab2lch(hex2lab(fixed[c])); continue
        for _ in range(4000):
            L=rng.uniform(*L_bands[c]); C=rng.uniform(*C_bands[c]); H=rng.uniform(*hue_bands[c])
            if legible(lch2lab((L,C,H))): state[c]=np.array([L,C,H]); break
    def hexof(c): return lab2hex(lch2lab(state[c]))
    def loss():
        hexes={c:hexof(c) for c in items}
        labs={m:{c:cvd_lab(hexes[c],m) for c in items} for m in MODES}
        pen=0.0; gmin=1e9
        for a,b in itertools.combinations(items,2):
            dn=ciede2000(labs['normal'][a],labs['normal'][b])
            dd=ciede2000(labs['deuteranopia'][a],labs['deuteranopia'][b])
            dp=ciede2000(labs['protanopia'][a],labs['protanopia'][b])
            w3=min(dn,dd,dp); gmin=min(gmin,w3)
            if dn<normal_floor: pen+=(normal_floor-dn)**2
            need_cvd = cvd_all or frozenset((a,b)) in adjacency
            if need_cvd:
                if dd<cvd_floor: pen+=(cvd_floor-dd)**2
                if dp<cvd_floor: pen+=(cvd_floor-dp)**2
        return pen*1000 - gmin, pen, gmin
    cur=loss(); best=cur; beststate={c:state[c].copy() for c in items}
    T=8.0
    for it in range(iters):
        T*=0.99996
        c=rng.choice([x for x in items if x not in fixed])
        old=state[c].copy()
        for _ in range(30):
            ns=old.copy()
            k=rng.random()
            step=rng.gauss(0,1)
            if k<0.4: ns[0]=np.clip(old[0]+step*4,*L_bands[c])
            elif k<0.7: ns[1]=np.clip(old[1]+step*5,*C_bands[c])
            else: ns[2]=old[2]+step*6
            ns[2]=min(max(ns[2],hue_bands[c][0]),hue_bands[c][1])
            if legible(lch2lab(tuple(ns))): state[c]=ns; break
        else:
            continue
        new=loss()
        d=new[0]-cur[0]
        if d<0 or rng.random()<math.exp(-d/max(T,1e-3)):
            cur=new
            if new[0]<best[0]: best=new; beststate={x:state[x].copy() for x in items}
        else:
            state[c]=old
    state=beststate
    hexes={c:lab2hex(lch2lab(state[c])) for c in items}
    return hexes, loss_report(hexes, items, adjacency, cvd_all)

def loss_report(hexes, items, adjacency, cvd_all):
    labs={m:{c:cvd_lab(hexes[c],m) for c in items} for m in MODES}
    rep={'normal':(1e9,None),'deuteranopia':(1e9,None),'protanopia':(1e9,None)}
    adjrep={'deuteranopia':(1e9,None),'protanopia':(1e9,None)}
    for a,b in itertools.combinations(items,2):
        for m in MODES:
            d=ciede2000(labs[m][a],labs[m][b])
            if d<rep[m][0]: rep[m]=(d,(a,b))
        if cvd_all or frozenset((a,b)) in adjacency:
            for m in ['deuteranopia','protanopia']:
                d=ciede2000(labs[m][a],labs[m][b])
                if d<adjrep[m][0]: adjrep[m]=(d,(a,b))
    return rep, adjrep

# ---------- vectorised CIEDE2000 (array vs single) ----------
def ciede2000_vec(L, one):
    # L: (N,3) labs ; one: (3,)
    L1=L[:,0]; a1=L[:,1]; b1=L[:,2]
    L2,a2,b2=one
    C1=np.hypot(a1,b1); C2=math.hypot(a2,b2)
    Cbar=(C1+C2)/2
    G=0.5*(1-np.sqrt(Cbar**7/(Cbar**7+25.0**7)))
    a1p=(1+G)*a1; a2p=(1+G)*a2
    C1p=np.hypot(a1p,b1); C2p=np.hypot(a2p,b2)
    h1p=np.degrees(np.arctan2(b1,a1p))%360
    h2p=np.degrees(np.arctan2(b2,a2p))%360
    dLp=L2-L1; dCp=C2p-C1p
    dh=h2p-h1p
    dhp=np.where(np.abs(dh)<=180,dh,np.where(dh>180,dh-360,dh+360))
    dhp=np.where(C1p*C2p==0,0,dhp)
    dHp=2*np.sqrt(C1p*C2p)*np.sin(np.radians(dhp)/2)
    Lbar=(L1+L2)/2; Cbarp=(C1p+C2p)/2
    hsum=h1p+h2p
    hbarp=np.where(C1p*C2p==0,hsum,
            np.where(np.abs(h1p-h2p)<=180,hsum/2,
            np.where(hsum<360,(hsum+360)/2,(hsum-360)/2)))
    T=(1-0.17*np.cos(np.radians(hbarp-30))+0.24*np.cos(np.radians(2*hbarp))
       +0.32*np.cos(np.radians(3*hbarp+6))-0.20*np.cos(np.radians(4*hbarp-63)))
    dtheta=30*np.exp(-((hbarp-275)/25)**2)
    Rc=2*np.sqrt(Cbarp**7/(Cbarp**7+25.0**7))
    Sl=1+(0.015*(Lbar-50)**2)/np.sqrt(20+(Lbar-50)**2)
    Sc=1+0.045*Cbarp; Sh=1+0.015*Cbarp*T
    Rt=-np.sin(np.radians(2*dtheta))*Rc
    return np.sqrt((dLp/Sl)**2+(dCp/Sc)**2+(dHp/Sh)**2+Rt*(dCp/Sc)*(dHp/Sh))

def optimise_fast(items, fixed, hue_bands, L_bands, C_bands, adjacency,
                  normal_floor=15.0, cvd_floor=15.0, cvd_all=False,
                  seed=0, iters=120000):
    rng=random.Random(seed)
    n=len(items); idx={c:i for i,c in enumerate(items)}
    # cvd mask: pairs needing cvd floor
    need=np.zeros((n,n),bool)
    for a,b in itertools.combinations(items,2):
        if cvd_all or frozenset((a,b)) in adjacency:
            need[idx[a],idx[b]]=need[idx[b],idx[a]]=True
    state=np.zeros((n,3))
    fixedmask=np.zeros(n,bool)
    for c in items:
        i=idx[c]
        if c in fixed:
            state[i]=lab2lch(hex2lab(fixed[c])); fixedmask[i]=True; continue
        for _ in range(6000):
            v=np.array([rng.uniform(*L_bands[c]),rng.uniform(*C_bands[c]),rng.uniform(*hue_bands[c])])
            if legible(lch2lab(tuple(v))): state[i]=v; break
    def labs_all():
        return {m:np.array([cvd_lab(lab2hex(lch2lab(tuple(state[i]))),m) for i in range(n)]) for m in MODES}
    LAB=labs_all()
    D={m:np.full((n,n),1e9) for m in MODES}
    for m in MODES:
        for i in range(n):
            d=ciede2000_vec(LAB[m],LAB[m][i]); d[i]=1e9; D[m][i]=d
    def total_pen_gmin():
        pen=0.0; gmin=1e9
        dn=D['normal']; dd=D['deuteranopia']; dp=D['protanopia']
        iu=np.triu_indices(n,1)
        w3=np.minimum(np.minimum(dn,dd),dp)[iu]; gmin=w3.min()
        below=np.clip(normal_floor-dn[iu],0,None); pen+=np.sum(below**2)
        nm=need[iu]
        bd=np.clip(cvd_floor-dd[iu],0,None)*nm; pen+=np.sum(bd**2)
        bp=np.clip(cvd_floor-dp[iu],0,None)*nm; pen+=np.sum(bp**2)
        return pen, gmin
    pen,gmin=total_pen_gmin(); cur=pen*1000-gmin
    best=cur; beststate=state.copy()
    T=8.0
    for it in range(iters):
        T*=0.99997
        i=rng.randrange(n)
        if fixedmask[i]: continue
        c=items[i]; old=state[i].copy()
        moved=False
        for _ in range(25):
            ns=old.copy(); k=rng.random(); step=rng.gauss(0,1)
            if k<0.4: ns[0]=min(max(old[0]+step*4,L_bands[c][0]),L_bands[c][1])
            elif k<0.7: ns[1]=min(max(old[1]+step*5,C_bands[c][0]),C_bands[c][1])
            else: ns[2]=min(max(old[2]+step*7,hue_bands[c][0]),hue_bands[c][1])
            if legible(lch2lab(tuple(ns))): moved=True; break
        if not moved: continue
        # candidate row updates
        h=lab2hex(lch2lab(tuple(ns)))
        newlab={m:cvd_lab(h,m) for m in MODES}
        oldrows={m:D[m][i].copy() for m in MODES}
        oldLAB={m:LAB[m][i].copy() for m in MODES}
        for m in MODES:
            LAB[m][i]=newlab[m]
            d=ciede2000_vec(LAB[m],newlab[m]); d[i]=1e9
            D[m][i]=d; D[m][:,i]=d
        pen,gmin=total_pen_gmin(); cand=pen*1000-gmin
        dlt=cand-cur
        if dlt<0 or rng.random()<math.exp(-dlt/max(T,1e-3)):
            state[i]=ns; cur=cand
            if cand<best: best=cand; beststate=state.copy()
        else:
            for m in MODES:
                LAB[m][i]=oldLAB[m]; D[m][i]=oldrows[m]; D[m][:,i]=oldrows[m]
    state=beststate
    hexes={items[i]:lab2hex(lch2lab(tuple(state[i]))) for i in range(n)}
    return hexes, loss_report(hexes, items, adjacency, cvd_all)

# ---------- batch helpers (vectorised) ----------
def lch2lab_batch(L,C,H):
    Hr=np.radians(H)
    return np.stack([L, C*np.cos(Hr), C*np.sin(Hr)],axis=1)  # (N,3)
def lab2linrgb_batch(lab):
    L=lab[:,0];a=lab[:,1];b=lab[:,2]
    fy=(L+16)/116; fx=fy+a/500; fz=fy-b/200
    def fi(t): return np.where(t>6/29,t**3,3*(6/29)**2*(t-4/29))
    xyz=np.stack([fi(fx),fi(fy),fi(fz)],axis=1)*WHITE
    lin=xyz@M_XYZ2RGB.T
    return lin,xyz
def xyz2lab_batch(xyz):
    xn=xyz/WHITE
    def f(t): return np.where(t>(6/29)**3,np.cbrt(np.clip(t,0,None)),t/(3*(6/29)**2)+4/29)
    fx=f(xn[:,0]);fy=f(xn[:,1]);fz=f(xn[:,2])
    return np.stack([116*fy-16,500*(fx-fy),200*(fy-fz)],axis=1)
def cvd_lab_batch(linrgb, mode):
    if mode=='normal':
        xyz=linrgb@M_RGB2XYZ.T
        return xyz2lab_batch(xyz)
    sim=np.clip(linrgb@MACHADO[mode].T,0,1)
    xyz=sim@M_RGB2XYZ.T
    return xyz2lab_batch(xyz)
def ciede2000_pairwise(A,B):
    # A:(N,3) labs, B:(N,3) labs -> (N,)
    out=np.empty(len(A))
    for i in range(len(A)):
        out[i]=ciede2000(A[i],B[i])
    return out
def ciede2000_vec_b(A, one):  # A:(N,3) vs single (3,)
    return ciede2000_vec(A, one)
