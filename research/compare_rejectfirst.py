import json,sys,statistics,collections
runs=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]
assert [r["mode"] for r in runs]==["baseline","noq","rejectfirst","rejectfirst","noq","baseline"]
k=lambda x:(x["seed"],x["n"],x["q"],x["pattern"],x["side"])
d=collections.defaultdict(lambda:collections.defaultdict(list))
for r in runs:
 for x in r["cases"]:d[k(x)][r["mode"]].append(x["ns"])
print("CONFIGS",len(d))
for mode in ("noq","rejectfirst"):
 a=[(key,statistics.median(v["baseline"])/statistics.median(v[mode])) for key,v in d.items()]
 print(mode,"MEDIAN",round(statistics.median(x for _,x in a),4),"MIN",round(min(x for _,x in a),4),"REGRESS_GT5",sum(x<.95 for _,x in a))
 for pat in ("ordered_local","random","deceptive","interior_reverse","interior_oscillate"):
  b=[v for k,v in a if k[3]==pat]
  print(mode,pat,"median",round(statistics.median(b),4),"min",round(min(b),4),"regress_gt5",sum(v<.95 for v in b))
 for key,x in sorted(a,key=lambda v:v[1])[:8]:print(mode,"WORST",key,round(x,4))
