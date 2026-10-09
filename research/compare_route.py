import json,sys,statistics,collections
runs=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]
assert [r["variant"] for r in runs]==["baseline","equal_only","equal_only","baseline"]
def key(x):return (x["n"],x["q"],x["pattern"],x["side"])
d=collections.defaultdict(lambda:collections.defaultdict(list))
routes={}
for run in runs:
 for row in run["rows"]:
  k=key(row);d[k][run["variant"]].append(row["ns"]);routes[k]=row["route"]
print("CONFIGS",len(d))
groups=collections.defaultdict(list)
for k,v in d.items():
 assert len(v["baseline"])==len(v["equal_only"])==2
 speed=statistics.median(v["baseline"])/statistics.median(v["equal_only"])
 groups[routes[k]].append((k,speed))
 groups["all"].append((k,speed))
for name,items in groups.items():
 vals=[x for _,x in items]
 print("ROUTE",name,"count",len(vals),"pct",round(100*len(vals)/len(d),2),"median",round(statistics.median(vals),4),"min",round(min(vals),4),"regress_gt5",sum(x<.95 for x in vals),"not_faster",sum(x<=1 for x in vals))
 for k,x in sorted(items,key=lambda kv:kv[1])[:5]:print("ROUTE_WORST",name,k,round(x,4))
for p in ("repeated","near_equal","anchors_equal_hidden","ordered_local","random","alternating","deceptive"):
 vals=[speed for k,speed in groups["all"] if k[2]==p]
 print("PATTERN",p,"median",round(statistics.median(vals),4),"min",round(min(vals),4),"regress_gt5",sum(x<.95 for x in vals))
