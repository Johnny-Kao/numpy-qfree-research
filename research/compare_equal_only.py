import json,sys,statistics,collections
runs=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]
assert [r["variant"] for r in runs]==["baseline","equal_only","equal_only","baseline"]
def key(x):return (x["n"],x["q"],x["pattern"],x["side"])
data=collections.defaultdict(lambda:collections.defaultdict(list))
for r in runs:
 for x in r["rows"]:data[key(x)][r["variant"]].append(x["ns"])
print("CASES",len(data))
ratios=[]
for k,d in data.items():
 assert len(d["baseline"])==len(d["equal_only"])==2
 ratios.append((k,statistics.median(d["baseline"])/statistics.median(d["equal_only"])))
v=[x for _,x in ratios]
print("OVERALL median",round(statistics.median(v),4),"worst",round(min(v),4),"regress_gt5",sum(x<.95 for x in v))
for p in ("repeated","ordered_local","random","alternating","deceptive"):
 x=[val for k,val in ratios if k[2]==p]
 print("PATTERN",p,"median",round(statistics.median(x),4),"worst",round(min(x),4),"regress_gt5",sum(i<.95 for i in x),"/",len(x))
for k,v in sorted(ratios,key=lambda kv:kv[1])[:8]:print("WORST",k,round(v,4))
