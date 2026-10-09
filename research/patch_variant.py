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
if mode=="baseline":
    start=s.index("    constexpr npy_intp LOCALITY_MIN_KEYS =")
    end=s.index("\n}",start)
    replacement="""    binsearch_current<Tag, side>(arr, key, ret, arr_len, key_len, arr_str,
                                 key_str, ret_str);"""
    s=s[:start]+replacement+s[end:]
if mode=="strict":
    # Require all deterministic coarse anchors to share the same three-pass
    # bracket. This is a sufficient signal for a *candidate*, not a proof:
    # unsampled queries may still differ; their correctness is protected by
    # per-query refinement.
    needle="    if (!reversed && direction >= 0 && interval_length > 1) {"
    assert s.count(needle)==1
    s=s.replace(needle,"    if (!reversed && direction == 0 && interval_length > 1) {",1)
if mode=="rejectfirst":
    # Check monotonicity across sampled keys and each sampled predecessor.
    needle="""        for (npy_intp j = 0; j <= LOCALITY_SAMPLES && !reversed; ++j) {
            const npy_intp i = (j * last) >> 4;
            if (i > 0) {
                const T key_val = *(const T *)(key + i * key_str);
                const T prev_key_val =
                        *(const T *)(key + (i - 1) * key_str);
                if (less(key_val, prev_key_val)) {
                    reversed = true;
                }
            }
        }
"""
    replacement="""        T prev_sample_val = *(const T *)key;
        for (npy_intp j = 1; j <= LOCALITY_SAMPLES && !reversed; ++j) {
            const npy_intp i = (j * last) >> 4;
            const T key_val = *(const T *)(key + i * key_str);
            const T prev_key_val =
                    *(const T *)(key + (i - 1) * key_str);
            if (less(key_val, prev_key_val) ||
                    less(key_val, prev_sample_val)) {
                reversed = true;
            }
            prev_sample_val = key_val;
        }
"""
    assert s.count(needle)==1,"predecessor check mismatch"
    s=s.replace(needle,replacement)
if mode=="variation":
    # Conservative rejector: coarse-anchor direction plus original-query
    # predecessor, midpoint, and cross-sample directional variation.
    needle="""    if (!reversed && direction >= 0 && interval_length > 1) {"""
    assert s.count(needle)==1
    additional="""    if (!reversed && direction >= 0) {
        T prior = *(const T *)key;
        for (npy_intp j = 0; j < LOCALITY_SAMPLES; ++j) {
            const npy_intp lo = (j * last) >> 4;
            const npy_intp hi = ((j + 1) * last) >> 4;
            const npy_intp mid = lo + ((hi - lo) >> 1);
            const T start = *(const T *)(key + lo * key_str);
            const T middle = *(const T *)(key + mid * key_str);
            const T finish = *(const T *)(key + hi * key_str);
            if (less(start, prior) || less(middle, start) ||
                    less(finish, middle)) {
                reversed = true;
                break;
            }
            prior = finish;
        }
    }

"""
    s=s.replace(needle,additional+needle)
if mode=="rejectforced":
    # Execute the existing selector but prohibit the locality path.
    needle="    if (!reversed && direction >= 0 && interval_length > 1) {"
    assert s.count(needle)==1
    s=s.replace(needle,"    volatile bool allow_locality = false;\n    if (allow_locality && !reversed && direction >= 0 && interval_length > 1) {",1)
if mode in ("precheck","coarse_reuse","work_reduction"):
    # Query-space anchor check before any batched passes. No Q threshold.
    needle="""    binsearch_locality<Tag, side>(arr, key, ret, arr_len, key_len, arr_str,
                                  key_str, ret_str);"""
    pre="""    bool precheck_ok = true;
    const npy_intp sample_last = key_len - 1;
    T previous_sample = *(const T *)key;
    for (npy_intp j = 1; j <= 16; ++j) {
        const npy_intp idx = (j * sample_last) >> 4;
        const T current = *(const T *)(key + idx * key_str);
        const T neighbor = *(const T *)(key + (idx - 1) * key_str);
        if (Tag::less(current, previous_sample) ||
                Tag::less(current, neighbor)) {
            precheck_ok = false;
            break;
        }
        previous_sample = current;
    }
    if (!precheck_ok) {
        binsearch_current<Tag, side>(arr, key, ret, arr_len, key_len, arr_str,
                                     key_str, ret_str);
        return;
    }

"""
    assert s.count(needle)==1
    s=s.replace(needle,pre+needle)
    if mode in ("coarse_reuse","work_reduction"):
        gate="    if (!reversed && direction >= 0 && interval_length > 1) {"
        assert s.count(gate)==1
        # Coarse reuse: at least two adjacent sampled anchors must share a bucket.
        # Work reduction: all sampled anchors share a coarse bucket, an
        # especially conservative indication of low search-position spread.
        check = """    bool useful_coarse = false;
    npy_intp previous_coarse = *(npy_intp *)ret;
    for (npy_intp j = 1; j <= LOCALITY_SAMPLES; ++j) {
        const npy_intp idx = (j * last) >> 4;
        const npy_intp current_coarse =
                *(npy_intp *)(ret + idx * ret_str);
        if (current_coarse == previous_coarse) useful_coarse = true;
        previous_coarse = current_coarse;
    }
"""
        if mode=="work_reduction":
            check=check.replace("bool useful_coarse = false;","bool useful_coarse = true;").replace("if (current_coarse == previous_coarse) useful_coarse = true;","if (current_coarse != previous_coarse) useful_coarse = false;")
        s=s.replace(gate,check+"    if (useful_coarse && !reversed && direction >= 0 && interval_length > 1) {",1)
if mode=="equal_only":
    # Exact allowlist: all queries must be comparator-equivalent.
    # Three anchor checks reject typical nonmatches before an O(Q) verification.
    start=s.index("    constexpr npy_intp LOCALITY_MIN_KEYS =")
    end=s.index("\n}",start)
    replacement="""    if (key_len > 1 &&
            key_str == (npy_intp)sizeof(T)) {
        const T first = *(const T *)key;
        const npy_intp middle = key_len >> 1;
        const T mid = *(const T *)(key + middle * key_str);
        const T last_value = *(const T *)(key + (key_len - 1) * key_str);
        const bool anchor_equal =
                !Tag::less(first, mid) && !Tag::less(mid, first) &&
                !Tag::less(first, last_value) && !Tag::less(last_value, first);
        if (anchor_equal) {
            bool all_equal = true;
            for (npy_intp i = 1; i < key_len; ++i) {
                const T val = *(const T *)(key + i * key_str);
                if (Tag::less(val, first) || Tag::less(first, val)) {
                    all_equal = false;
                    break;
                }
            }
            if (all_equal) {
                binsearch_current<Tag, side>(arr, key, ret, arr_len, 1,
                                             arr_str, key_str, ret_str);
                const npy_intp answer = *(npy_intp *)ret;
                for (npy_intp i = 1; i < key_len; ++i) {
                    *(npy_intp *)(ret + i * ret_str) = answer;
                }
                return;
            }
        }
    }
    binsearch_current<Tag, side>(arr, key, ret, arr_len, key_len,
                                 arr_str, key_str, ret_str);
"""
    s=s[:start]+replacement+s[end:]
p.write_text(s)
print(f"patched {mode}: {p}")
