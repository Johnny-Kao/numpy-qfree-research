import os,sys,time,json,statistics
import numpy as np
mode=sys.argv[1]
n=q=4096
a=np.arange(n,dtype=np.int64)
v=np.full(q,n//2,dtype=np.int64)
v[q//4:q//4+max(1,q//8)]=n//2+1
data=[]
for side in ("left","right"):
 expected=np.clip(v+(side=="right"),0,n)
 assert np.array_equal(np.searchsorted(a,v,side=side),expected)
 for iteration in range(30):
  loops=160
  t0=time.perf_counter_ns()
  for _ in range(loops):out=np.searchsorted(a,v,side=side)
  elapsed=(time.perf_counter_ns()-t0)/loops
  assert np.array_equal(out,expected)
  data.append({"side":side,"iteration":iteration,"ns":elapsed})
print(json.dumps({"mode":mode,"measurements":data}),flush=True)
