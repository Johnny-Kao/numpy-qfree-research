import hashlib,json,sys
import numpy as np
mode,outpath=sys.argv[1:3]
rng=np.random.default_rng(32895)
records=[]
def check(label,a,v,side,sorter=None):
 kw={"side":side}
 if sorter is not None:kw["sorter"]=sorter
 before=np.array(v,copy=True)
 result=np.asarray(np.searchsorted(a,v,**kw))
 assert np.array_equal(np.asarray(v),before,equal_nan=True),("mutated",label)
 digest=hashlib.sha256(np.ascontiguousarray(result,dtype=np.int64).tobytes()).hexdigest()
 records.append({"case":label,"shape":list(result.shape),"hash":digest})
def both(label,a,v,sorter=None):
 for side in ("left","right"):check(label+"-"+side,a,v,side,sorter)
for dtype in (np.int8,np.int64,np.uint64,np.float32,np.float64,np.complex128,np.bool_):
 for n in (0,1,2,17,256):
  if dtype is np.bool_:a=np.sort(rng.integers(0,2,n).astype(dtype))
  elif dtype is np.complex128:a=np.sort((rng.integers(-20,21,n)+1j*rng.integers(-4,5,n)).astype(dtype))
  elif dtype in (np.float32,np.float64):a=np.sort(rng.integers(-20,21,n).astype(dtype))
  else:a=np.sort(rng.integers(0,21,n).astype(dtype))
  if len(a):
   key=a[min(len(a)-1,len(a)//2)]
  else:key=np.array(0,dtype=dtype)[()]
  for form in ("same","one_different","random","empty","single","strided","broadcast"):
   if form=="same":v=np.full(257,key,dtype=dtype)
   elif form=="one_different":v=np.full(257,key,dtype=dtype);v[81]=np.array(1,dtype=dtype)
   elif form=="random":v=rng.choice(a,257) if len(a) else np.zeros(257,dtype=dtype)
   elif form=="empty":v=np.empty(0,dtype=dtype)
   elif form=="single":v=np.array([key],dtype=dtype)
   elif form=="strided":v=np.full(514,key,dtype=dtype)[::2]
   else:v=np.broadcast_to(np.array([key],dtype=dtype),(257,))
   both(f"boundary-{dtype.__name__}-{n}-{form}",a,v)
for kind in ("float64","complex128"):
 dtype=np.dtype(kind)
 for n in (1,17,257):
  if kind=="float64":
   a=np.sort(np.r_[rng.standard_normal(n),np.nan,np.inf,-np.inf].astype(dtype))
   values=np.array([np.nan,-np.inf,np.inf,-0.0,0.0],dtype=dtype)
  else:
   a=np.sort(np.r_[rng.standard_normal(n)+1j*rng.standard_normal(n),complex(np.nan,0),complex(0,np.nan)].astype(dtype))
   values=np.array([complex(np.nan,0),complex(0,np.nan),0j,1+1j],dtype=dtype)
  for val in values:
   for form in ("same","hidden","alternating"):
    v=np.full(129,val,dtype=dtype)
    if form=="hidden":v[41]=values[-1]
    elif form=="alternating":v[::2]=values[-1]
    both(f"special-{kind}-{n}-{repr(val)}-{form}",a,v)
for i in range(400):
 n=int(rng.integers(0,4097))
 q=int(rng.integers(0,2049))
 dtype=rng.choice(["int64","float64"])
 a=np.sort(rng.integers(-1000,1001,n).astype(dtype))
 pivot=np.array(int(rng.integers(-1000,1001)),dtype=dtype)[()]
 mode_i=int(rng.integers(0,5))
 v=np.full(q,pivot,dtype=dtype)
 if mode_i==1 and q:v[int(rng.integers(0,q))]=pivot+1
 if mode_i==2 and q:v[:]=rng.integers(-1000,1001,q).astype(dtype)
 if mode_i==3 and q:v[::2]=pivot+1
 if mode_i==4 and q:v[:]=np.sort(rng.integers(-1000,1001,q)).astype(dtype)
 if i%4==0:v=v[::-1]
 if i%17==0 and n:
  shuffled=a.copy();sorter=np.argsort(shuffled,kind="stable");both(f"mc-{i}-{mode_i}-sorter",shuffled,v,sorter)
 else:both(f"mc-{i}-{mode_i}",a,v)
if mode=="baseline":
 with open(outpath,"w") as f:json.dump(records,f)
 print("BASELINE_CASES",len(records))
else:
 with open(outpath) as f:baseline=json.load(f)
 assert len(records)==len(baseline),(len(records),len(baseline))
 errors=[(x["case"],x["hash"],y["hash"]) for x,y in zip(baseline,records) if x!=y]
 print("MONTE_CARLO_CASES",len(records),"MISMATCHES",len(errors))
 for x in errors[:10]:print("MISMATCH",x)
 assert not errors
 print("SIGNOFF_CORRECTNESS_PASS")
