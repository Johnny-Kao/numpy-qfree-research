import json,time,statistics,sys
import numpy as np
rng=np.random.default_rng(32895)
rows=[]
for n in (4096,65536):
 arr=np.arange(n,dtype=np.int64)
 for q in (64,4096,65536,1048576):
  for pattern in ("repeated","near_equal","anchors_equal_hidden","ordered_local","random","alternating","deceptive"):
   if pattern=="repeated": v=np.full(q,n//2,dtype=np.int64)
   elif pattern=="near_equal":
    v=np.full(q,n//2,dtype=np.int64)
    v[q//2]=n//2+1
   elif pattern=="anchors_equal_hidden":
    v=np.full(q,n//2,dtype=np.int64)
    v[q//4:n//4 if False else q//4+max(1,q//8)]=n//2+1
   elif pattern=="ordered_local":v=np.full(q,n//2,dtype=np.int64)+(np.arange(q,dtype=np.int64)*8//q)
   elif pattern=="random":v=rng.integers(0,n,size=q,dtype=np.int64)
   elif pattern=="alternating":v=np.where(np.arange(q)%2,n-1,0).astype(np.int64)
   else:
    v=np.full(q,n//2,dtype=np.int64)
    mask=np.arange(q)%64>2
    v[mask]=rng.integers(0,n,size=int(mask.sum()),dtype=np.int64)
   accepted=bool(np.all(v==v[0]))
   if accepted: route="fast"
   elif v[0]!=v[q//2] or v[0]!=v[-1]:route="anchor_reject"
   else:route="scan_reject"
   for side in ("left","right"):
    result=np.searchsorted(arr,v,side=side)
    assert np.array_equal(result,np.clip(v+(side=="right"),0,n))
    loops=max(2,min(40,300000//q))
    for _ in range(2):np.searchsorted(arr,v,side=side)
    times=[]
    for _ in range(5):
     start=time.perf_counter_ns()
     for _ in range(loops):result=np.searchsorted(arr,v,side=side)
     times.append((time.perf_counter_ns()-start)/loops)
    rows.append(dict(n=n,q=q,pattern=pattern,side=side,ns=statistics.median(times),route=route))
print(json.dumps({"variant":sys.argv[1],"rows":rows}))
