import json,sys,statistics,collections
runs=[json.loads(s) for s in open(sys.argv[1]) if s.strip()]
assert [r["mode"] for r in runs]==["q20","noq","noq","q20"]
def key(c):return (c["seed"],c["n"],c["q"],c["pattern"],c["side"])
data=collections.defaultdict(lambda:collections.defaultdict(list))
for r in runs:
 for c in r["cases"]:data[key(c)][r["mode"]].append(c["ns"])
ratios=[]
for k,v in data.items():
 assert all(len(v[mode])==2 for mode in ("q20","noq"))
 ratios.append((k,statistics.median(v["q20"])/statistics.median(v["noq"])))
print("CONFIGS",len(ratios))
print("MEDIAN_SPEEDUP",round(statistics.median(v for _,v in ratios),4))
print("REGRESS_GT5",sum(v<.95 for _,v in ratios))
print("MIN_SPEEDUP",round(min(v for _,v in ratios),4))
for p in ("ordered_local","random","deceptive","interior_reverse","interior_oscillate"):
 vals=[v for k,v in ratios if k[3]==p]
 print("PATTERN",p,"COUNT",len(vals),"MEDIAN",round(statistics.median(vals),4),"WORST",round(min(vals),4),"REGRESS_GT5",sum(v<.95 for v in vals))
for k,v in sorted(ratios,key=lambda t:t[1])[:12]:print("WORST",k,round(v,4))
