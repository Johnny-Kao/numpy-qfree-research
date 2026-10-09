import json,time,statistics,sys
import numpy as np
rng=np.random.default_rng(32895)
rows=[]
for n in (4096,65536):
    arr=np.arange(n,dtype=np.int64)
    for q in (64,4096,65536,1048576):
        for pattern in ("repeated","ordered_local","random","alternating","deceptive"):
            if pattern=="repeated":v=np.full(q,n//2,dtype=np.int64)
            elif pattern=="ordered_local":v=np.full(q,n//2,dtype=np.int64)+(np.arange(q,dtype=np.int64)*8//q)
            elif pattern=="random":v=rng.integers(0,n,size=q,dtype=np.int64)
            elif pattern=="alternating":v=np.where(np.arange(q)%2,n-1,0).astype(np.int64)
            else:
                v=np.full(q,n//2,dtype=np.int64);mask=np.arange(q)%64>2
                v[mask]=rng.integers(0,n,size=int(mask.sum()),dtype=np.int64)
            for side in ("left","right"):
                want=np.searchsorted(arr,v,side=side)
                for _ in range(2): np.searchsorted(arr,v,side=side)
                loops=max(2,min(40,300000//q))
                times=[]
                for _ in range(5):
                    st=time.perf_counter_ns()
                    for _ in range(loops):result=np.searchsorted(arr,v,side=side)
                    times.append((time.perf_counter_ns()-st)/loops)
                assert np.array_equal(result,want)
                rows.append(dict(n=n,q=q,pattern=pattern,side=side,ns=statistics.median(times)))
print(json.dumps({"variant":sys.argv[1],"rows":rows}))
