import json,sys,statistics,collections
runs=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]
assert [r["variant"] for r in runs]==["q20","noq","fused","fused","noq","q20"]
def case(x):return (x["n"],x["q"],x["pattern"],x["side"])
merged=collections.defaultdict(lambda:collections.defaultdict(list))
for run in runs:
 for row in run["rows"]:merged[case(row)][run["variant"]].append(row["ns"])
assert all(len(v)==2 for row in merged.values() for v in row.values())
out=collections.defaultdict(list)
for k,variants in merged.items():
 base=statistics.median(variants["q20"])
 for mode in ("noq","fused"):
  out[mode].append((k,base/statistics.median(variants[mode])))
print("CASE COUNT",len(merged))
for mode,items in out.items():
 nums=[x[1] for x in items]
 print(mode,"median",round(statistics.median(nums),4),"worst",round(min(nums),4),"regress>5%",sum(x<.95 for x in nums),"/",len(nums))
 for pat in ("repeated","ordered_local","random","alternating","deceptive"):
  vals=[v for k,v in items if k[2]==pat]
  print(" ",pat,"median",round(statistics.median(vals),4),"worst",round(min(vals),4))
 for k,v in sorted(items,key=lambda x:x[1])[:4]: print(" worst case",k,round(v,4))
