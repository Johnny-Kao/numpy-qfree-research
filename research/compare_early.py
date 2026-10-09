import json,sys,statistics,collections
runs=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]
modes=["baseline","precheck","coarse_reuse","work_reduction"]
assert [r["mode"] for r in runs]==modes+modes[::-1]
def key(x):return (x["seed"],x["n"],x["q"],x["pattern"],x["side"])
d=collections.defaultdict(lambda:collections.defaultdict(list))
for run in runs:
 for row in run["cases"]:d[key(row)][run["mode"]].append(row["ns"])
print("CONFIGS",len(d))
for mode in modes[1:]:
 a=[(k,statistics.median(v["baseline"])/statistics.median(v[mode])) for k,v in d.items()]
 print("MODE",mode,"MEDIAN",round(statistics.median(x for _,x in a),4),"MIN",round(min(x for _,x in a),4),"REGRESS_GT5",sum(x<.95 for _,x in a))
 for pattern in ("ordered_local","random","deceptive","interior_reverse","interior_oscillate"):
  z=[x for k,x in a if k[3]==pattern]
  print("PATTERN",mode,pattern,"MEDIAN",round(statistics.median(z),4),"MIN",round(min(z),4),"REGRESS_GT5",sum(x<.95 for x in z))
 for k,x in sorted(a,key=lambda kv:kv[1])[:5]:print("WORST",mode,k,round(x,4))
