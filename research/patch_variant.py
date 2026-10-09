import pathlib,sys
mode=sys.argv[1]
p=pathlib.Path(sys.argv[2])
s=p.read_text()
assert s.count("NPY_LOCALITY_Q_STUDY") >= 1, s.count("NPY_LOCALITY_Q_STUDY")
s=s.replace("NPY_LOCALITY_Q_STUDY", "1048576" if mode=="q20" else "17")
if mode=="fused":
    pattern="""    const T mid_val = *(const T *)(arr + half * arr_str);
    for (npy_intp i = 0; i < key_len; ++i) {
        const T key_val = *(const T *)(key + i * key_str);
        *(npy_intp *)(ret + i * ret_str) = cmp(mid_val, key_val) * half;
    }
"""
    replacement="""    const T mid_val = *(const T *)(arr + half * arr_str);
    bool globally_reversed = false;
    T last_seen = *(const T *)key;
    for (npy_intp i = 0; i < key_len; ++i) {
        const T key_val = *(const T *)(key + i * key_str);
        if (i > 0 && less(key_val, last_seen)) globally_reversed = true;
        last_seen = key_val;
        *(npy_intp *)(ret + i * ret_str) = cmp(mid_val, key_val) * half;
    }
"""
    start=s.index("binsearch_locality(")
    position=s.find(pattern,start)
    assert position>=0,"locality first pass not found"
    s=s[:position]+replacement+s[position+len(pattern):]
    cond="if (!reversed && direction >= 0 && interval_length > 1)"
    assert s.count(cond)==1
    s=s.replace(cond,"if (!reversed && !globally_reversed && direction >= 0 && interval_length > 1)")
if mode=="bounded":
    # Limit extra galloping probes, but preserve binary search over the
    # remaining valid bracket. The standard binary completion stays intact.
    start=s.index("binsearch_locality(")
    gallop=s.find("                    while (true) {",start)
    assert gallop>=0,"galloping loop not found"
    s=s[:gallop]+s[gallop:].replace(
        "                    while (true) {",
        "                    for (int gallop_probe = 0; gallop_probe < 2; ++gallop_probe) {",
        1
    )
p.write_text(s)
print(f"patched {mode}: {p}")
