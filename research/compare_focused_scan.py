import json,sys,statistics
rows=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]
assert len(rows)==12,[(r["mode"],len(r["measurements"])) for r in rows]
for side in ("left","right"):
 for mode in ("baseline","equal_only"):
  batches=[statistics.median(x["ns"] for x in row["measurements"] if x["side"]==side) for row in rows if row["mode"]==mode]
  assert len(batches)==6
  print("BATCH",side,mode,[round(x,1) for x in batches])
 b=[x["ns"] for row in rows if row["mode"]=="baseline" for x in row["measurements"] if x["side"]==side]
 p=[x["ns"] for row in rows if row["mode"]=="equal_only" for x in row["measurements"] if x["side"]==side]
 print("FOCUSED",side,"baseline_ns",round(statistics.median(b),1),"pr_ns",round(statistics.median(p),1),"speedup",round(statistics.median(b)/statistics.median(p),4))
