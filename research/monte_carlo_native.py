import numpy as np,json,time,statistics,sys
mode=sys.argv[1]
cases=[]
for seed in (22,73,32895):
    rng=np.random.default_rng(seed)
    for n in (4096,65536):
        a=np.arange(n,dtype=np.int64)
        for q in (64,4096,65536,1048576):
            if q>=1048576 and seed!=22:continue
            for pattern in ("ordered_local","random","deceptive","interior_reverse","interior_oscillate"):
                if pattern=="ordered_local":v=np.full(q,n//2,dtype=np.int64)+(np.arange(q,dtype=np.int64)*8//q)
                elif pattern=="random":v=rng.integers(0,n,size=q,dtype=np.int64)
                elif pattern=="deceptive":
                    v=np.full(q,n//2,dtype=np.int64)
                    mask=np.arange(q)%64>2
                    v[mask]=rng.integers(0,n,size=int(mask.sum()),dtype=np.int64)
                else:
                    v=np.full(q,n//2,dtype=np.int64)
                    # Keep anchor and predecessor points apparently benign;
                    # hide large reversed/alternating blocks well inside them.
                    step=max(1,(q-1)//16)
                    if step>5:
                        for b in range(16):
                            lo=b*step+2;hi=min((b+1)*step-2,q)
                            if lo>=hi:continue
                            if pattern=="interior_reverse":
                                v[lo:hi]=np.linspace(n-1,0,hi-lo).astype(np.int64)
                            else:v[lo:hi]=np.where(np.arange(hi-lo)%2,n-1,0)
                for side in ("left","right"):
                    for _ in range(2):np.searchsorted(a,v,side=side)
                    loops=max(2,min(25,200000//q))
                    samples=[]
                    for _ in range(3):
                        t=time.perf_counter_ns()
                        for k in range(loops):got=np.searchsorted(a,v,side=side)
                        samples.append((time.perf_counter_ns()-t)/loops)
                    # Independent oracle for a = arange(n), including duplicates and bounds.
                    expected=np.clip(v+(1 if side=="right" else 0),0,n)
                    assert np.array_equal(got,expected), (mode,seed,n,q,pattern,side)
                    cases.append(dict(seed=seed,n=n,q=q,pattern=pattern,side=side,ns=statistics.median(samples)))
print(json.dumps({"mode":mode,"cases":cases}))
