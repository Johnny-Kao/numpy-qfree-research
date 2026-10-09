"""Diagnose exactly which hidden inversions escape sparse Q-free selectors.
No performance claims: this is a synthetic rejection screen, not native NumPy.
"""
from collections import Counter
import random
N,Q,S=8192,4097,16
A=[j*(Q-1)//S for j in range(S+1)]
def make(seed):
 r=random.Random(seed)
 base=sorted(r.randrange(1024,1250) for _ in range(Q))
 yield "ascending",base
 yield "constant",[1120]*Q
 x=base[:];x[128]=N-1;yield "single_spike",x
 x=base[:];x[129]=0;yield "single_dip",x
 x=base[:];i=(A[4]+A[5])//2;x[i]=N-1;x[i+1]=0;yield "mid_spike_dip",x
 x=base[:]
 for b in range(S):
  lo=A[b]+3;hi=A[b+1]-3
  for i in range(lo,hi):x[i]=1120+(i%2)*120
 yield "hidden_oscillation",x
 x=base[:];r.shuffle(x);yield "random_within_bucket",x
 x=base[:]
 for b in range(S):
  lo=A[b]+3;hi=A[b+1]-3
  if hi>lo:
   part=x[lo:hi];part.reverse();x[lo:hi]=part
 yield "hidden_reverse",x
def probes(kind):
 p=set(A)
 p.update(i-1 for i in A if i>0)
 if kind in ("midpoint","quartiles"):
  for l,h in zip(A,A[1:]):
   p.add((l+h)//2)
   if kind=="quartiles":p.update((l+(h-l)//4,l+3*(h-l)//4))
 return sorted(p)
def selected(x,kind):
 coarse=[v//1024 for v in x]
 p=probes(kind)
 # existing checks: 16 anchor coarse directions and predecessor raw keys.
 prev=coarse[A[0]];direction=0
 for i in A[1:]:
  delta=coarse[i]-prev
  if delta and direction and (delta>0)!=(direction>0):return False
  if delta:direction=delta
  prev=coarse[i]
 if direction<0:return False
 if kind=="existing":
  return not any(x[i]<x[i-1] for i in A[1:])
 # Additional actual key checks, plus range sampled variation.
 # Detect downward moves BETWEEN the refined sample points;
 # predecessor checks catch local boundary discontinuities.
 return not any(x[i]<x[i-1] for i in p if i>0) and not any(x[v]<x[u] for u,v in zip(p,p[1:]))
stats={k:Counter() for k in ("existing","midpoint","quartiles")}
by_pattern={k:Counter() for k in stats}
for seed in range(100):
 for name,x in make(seed):
  inversions=any(x[i]<x[i-1] for i in range(1,Q))
  for kind in stats:
   accept=selected(x,kind)
   stats[kind]["accepted"]+=accept
   stats[kind]["hidden_inversion_accepted"]+=accept and inversions
   stats[kind]["safe_accepted"]+=accept and not inversions
   by_pattern[kind][name]+=accept and inversions
print("CONFIGS",800,"NOTE proxy only; coarse-bin compression can hide large key oscillations")
for kind in stats:
 print("METHOD",kind,dict(stats[kind]),"extra_probe_count",len(probes(kind))-len(probes("existing")))
 print("FALSE_ACCEPT_BY_PATTERN",kind,dict(by_pattern[kind]))
