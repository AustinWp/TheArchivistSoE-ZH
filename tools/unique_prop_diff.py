# -*- coding: utf-8 -*-
"""暗金属性数值 diff（官方中文名桥接的暗金件）。

- 从 Affixes.json 结构化条目构建「属性短语 → property」反向正则
- 用官方串表把游戏暗金行与本站 Uniques.json 条目桥接（221 件）
- 解析本站 displayProperties 字符串 → (property,min,max) 集合，与游戏 prop 列对比
- 输出报告（可解析率 / 差异清单 / 未解析串）

用法: python3 tools/unique_prop_diff.py
输出: tools/generated/unique_prop_diff.md
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GE = "/tmp/SOECN/standard-mode/data/global/excel"


def read(path):
    return [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8-sig", errors="replace") if l.strip()]


def main():
    zh = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
    aff = json.load(open(os.path.join(ROOT, "public", "data", "Affixes.json"), encoding="utf-8"))
    uni = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"), encoding="utf-8"))

    # ---------- 1) 解析器 ----------
    import sys as _sys
    _sys.path.insert(0, HERE)
    from unique_prop_parser import parse_props
    unparsed_sample = []

    # ---------- 2) 桥接 + diff ----------
    wname = {}
    for u in uni:
        wname.setdefault(u["index"], u)

    rows = read(os.path.join(GE, "UniqueItems.txt"))
    gh = rows[0]
    gi, ge = gh.index("index"), gh.index("enabled")
    prop_cols = []
    for i in range(1, 9):
        c, mn, mx = f"prop{i}", f"min{i}", f"max{i}"
        if c in gh and mn in gh and mx in gh:
            prop_cols.append((gh.index(c), gh.index(mn), gh.index(mx)))

    total = parsed_ok = 0
    diffs = []
    missing_zh = []
    for r in rows[1:]:
        if len(r) <= ge or r[ge] != "1":
            continue
        idx = r[gi]
        z = zh.get(idx, "")
        if not z:
            continue
        w = wname.get(z)
        if not w:
            continue
        total += 1
        gprops = set()
        for (ci, mi, xi) in prop_cols:
            c = r[ci] if ci < len(r) else ""
            if not c:
                continue
            try:
                mnv = int(r[mi]) if mi < len(r) and r[mi] else 0
                mxv = int(r[xi]) if xi < len(r) and r[xi] else 0
            except ValueError:
                continue
            gprops.add((c, mnv, mxv))
        wprops, unparsed = parse_props([str(x) for x in (w.get("displayProperties") or [])])
        if not unparsed:
            parsed_ok += 1
        def normset(props):
            out = set()
            for (c, mn, mx) in props:
                if c in ("balance1",):
                    c = "balance2"
                elif c in ("move1",):
                    c = "move2"
                if c.startswith("pierce-"):
                    mn, mx = abs(mn), abs(mx)
                if mn == 0 and mx == 0 and c in ("indestruct", "ignore-ac"):
                    mn, mx = 1, 1
                out.add((c, mn, mx))
            return out
        gprops = normset(gprops)
        wset = normset(wprops)
        MACHINE = {"sock", "silence", "socketed-text", "gold", "save"}  # 展示类/机器字段
        def meaningful(props):
            return {p for p in props if p[0] not in MACHINE and not (p[1] == 0 and p[2] == 0)}
        g_meaning = meaningful(gprops)
        w_meaning = meaningful(wset)
        g_only = sorted(g_meaning - w_meaning)
        w_only = sorted(w_meaning - g_meaning)
        # 每级格式同义映射：perlv:X 与 X/lvl 视为一致
        w_only2 = [(c, a, b) for (c, a, b) in w_only if not (c.startswith("perlv:") and f"{c.split(':')[1]}/lvl" in {x[0] for x in g_meaning})]
        g_only2 = [(c, a, b) for (c, a, b) in g_only if not (
            c.endswith("/lvl") and any(wc.startswith("perlv:") and wc.split(":")[1] == c.split("/")[0]
                                       for (wc, _, _) in w_only))]
        if g_only2 or w_only2:
            diffs.append({
                "unique": idx, "zh": z,
                "gameOnly": g_only2,
                "wikiOnly": w_only2,
                "unparsed": unparsed,
            })
        if unparsed:
            unparsed_sample.extend([(z, u) for u in unparsed[:3]])

    print(f"== 可桥接并参与 diff 的暗金：{total} 件；displayString 全解析：{parsed_ok}")
    print(f"== 存在差异：{len(diffs)} 件 ===")
    for d in diffs[:25]:
        print(f"  {d['zh']}({d['unique']}): 游戏多 {d['gameOnly'][:6]} | wiki多 {d['wikiOnly'][:6]} | 未解析 {d['unparsed'][:2]}")
    print(f"\n== 未解析串样本（前 25）==")
    for z, s in unparsed_sample[:25]:
        print(f"  [{z}] {s}")

    with open(os.path.join(HERE, "generated", "unique_prop_diff.json"), "w", encoding="utf-8") as f:
        json.dump({"total": total, "parsed_ok": parsed_ok, "diffs": diffs}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "generated", "unique_prop_diff.md"), "w", encoding="utf-8") as f:
        f.write(f"# 暗金属性 diff\n\n可桥接 {total}，全解析 {parsed_ok}，差异 {len(diffs)}\n")


if __name__ == "__main__":
    main()
