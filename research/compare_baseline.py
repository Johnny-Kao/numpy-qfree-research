import json,sys,statistics,collections
runs=[json.loads(line) for line in open(sys.argv[1]) if line.strip()]
assert [r["mode"] for r in runs]==["baseline","noq","bounded","bounded","noq","baseline"]
def key(x):return (x["seed"],x["n"],x["q"],x["pattern"],x["side"])
d=collections.defaultdict(lambda:collections.defaultdict(list))
for r in runs:
 for c in r["cases"]:d[key(c)][r["mode"]].append(c["ns"])
print("CONFIGS",len(d))
for mode in ("noq","bounded"):
 vals=[(k,statistics.median(v["baseline"])/statistics.median(v[mode])) for k,v in d.items()]
 nums=[v for _,v in vals]
 print(mode,"MEDIAN",round(statistics.median(nums),4),"MIN",round(min(nums),4),"REGRESS_GT5",sum(v<.95 for v in nums),"/",len(nums))
 for pat in ("ordered_local","random","deceptive","interior_reverse","interior_oscillate"):
  a=[v for k,v in vals if k[3]==pat]
  print(mode,"PATTERN",pat,"median",round(statistics.median(a),4),"worst",round(min(a),4),"regress_gt5",sum(v<.95 for v in a))
 for k,v in sorted(vals,key=lambda kv:kv[1])[:8]:print(mode,"WORST",k,round(v,4))
