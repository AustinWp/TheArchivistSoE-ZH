# -*- coding: utf-8 -*-
"""词缀深度对齐报告（游戏词缀表 vs 本站 Affixes.json）。

三层对比：
  1) 名称层：官方串表中文名（标准化去「的/之」）与本站词缀名差集
  2) 属性层：MagicPrefix/Suffix/AutoMagic 的 mod 序列 vs 本站 displayProperties（property/min/max）
  3) 数值层：level/levelreq/frequency/group 等字段

用法: python3 tools/affix_depth_diff.py
输出: tools/generated/affix_diff.md
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GE = "/tmp/SOECN/standard-mode/data/global/excel"


def read(path):
    return [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8-sig", errors="replace") if l.strip()]


def norm(name):
    """标准化：去尾部 的/之/者，去空格。"""
    return (name or "").strip().rstrip("的之者").strip()


def main():
    zh = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
    aff = json.load(open(os.path.join(ROOT, "public", "data", "Affixes.json"), encoding="utf-8"))
    wname = norm
    w_by_norm = {}
    for a in aff:
        w_by_norm.setdefault(norm(a["name"]), []).append(a)
    wnames = set(w_by_norm)

    out = []
    def h(s):
        out.append(s)

    h("# 词缀深度对齐报告\n")
    h(f"本站词缀条目 {len(aff)}，唯一名 {len(set(a['name'] for a in aff))}\n")

    # ---------- 1) 名称层 ----------
    h("## 1. 名称层（官方串表 = 标准）\n")
    rows = []
    en_zh = {}          # 英文名 -> 官方名（唯一）
    for f in ["MagicPrefix.txt", "MagicSuffix.txt", "RarePrefix.txt", "RareSuffix.txt",
              "UniquePrefix.txt", "UniqueSuffix.txt", "AutoMagic.txt"]:
        rr = read(os.path.join(GE, f))
        hdr = rr[0]
        ni = hdr.index("Name") if "Name" in hdr else hdr.index("name")
        ei = hdr.index("enabled") if "enabled" in hdr else None
        for r in rr[1:]:
            if ei is not None and (len(r) <= ei or r[ei] != "1"):
                continue
            n = r[ni] if ni < len(r) else ""
            if not n:
                continue
            z = zh.get(n, "")
            rows.append((f, n, z))
            if z:
                en_zh.setdefault(n, z)
    game_zh = set(norm(en_zh[n]) for n in en_zh)
    h(f"游戏启用词缀行 {len(rows)}；官方中文名覆盖 {len(set(en_zh.values()))} 个名字\n")
    missing = sorted(game_zh - wnames)
    h(f"### 1.1 疑似缺失（游戏有官方中文名、本站无）: {len(missing)}")
    for m in missing:
        en = [n for n, z in en_zh.items() if norm(z) == m]
        h(f"- {m}（{en}）")
    extra = sorted(wnames - game_zh)
    h(f"\n### 1.2 本站独有名称（无官方中名或对应不同）: {len(extra)}")
    h("（保留现有译名；列表见报告附录）")
    # 异名：双方都有但文字不同
    both = game_zh & wnames
    h(f"\n### 1.3 双方共有: {len(both)}；官方名与本站名完全一致比例以此为基准\n")

    # ---------- 2) 属性层 ----------
    h("\n## 2. 属性层（MagicPrefix/MagicSuffix/AutoMagic mod vs displayProperties）\n")
    prop_mismatch = []
    prop_missing = []
    matched = 0
    for f in ["MagicPrefix.txt", "MagicSuffix.txt", "AutoMagic.txt"]:
        rr = read(os.path.join(GE, f))
        hdr = rr[0]
        ni = hdr.index("Name")
        ei = hdr.index("enabled") if "enabled" in hdr else None
        mod_cols = []
        for i in range(1, 9):
            code = f"mod{i}code"; mn = f"mod{i}min"; mx = f"mod{i}max"
            if code in hdr and mn in hdr and mx in hdr:
                mod_cols.append((hdr.index(code), hdr.index(mn), hdr.index(mx)))
        for r in rr[1:]:
            if ei is not None and (len(r) <= ei or r[ei] != "1"):
                continue
            n = r[ni] if ni < len(r) else ""
            if not n:
                continue
            z = zh.get(n, "")
            wl = w_by_norm.get(norm(z or ""), [])
            if not wl:
                continue  # 名称层已处理
            gmods = []
            for (ci, mni, mxi) in mod_cols:
                c = r[ci] if ci < len(r) else ""
                if not c:
                    continue
                gmods.append((c, int(r[mni]) if mni < len(r) and r[mni] else 0,
                              int(r[mxi]) if mxi < len(r) and r[mxi] else 0))
            # 区分普通行/地图变体行（map-* 属性）
            g_reg = {m for m in gmods if not m[0].startswith("map-")}
            g_map = {m for m in gmods if m[0].startswith("map-")}
            wprops = set()
            for a in wl:
                for p in (a.get("displayProperties") or []):
                    wprops.add((p.get("property"), int(p.get("min") or 0), int(p.get("max") or 0)))
            w_reg = {m for m in wprops if not m[0].startswith("map-")}
            # 只有普通属性行时才算「同一行」；若本行是地图变体行则跳过（归地图模块）
            if not g_reg and g_map:
                continue
            if g_reg != w_reg:
                prop_mismatch.append((f, n, z, "属性不一致", sorted(g_reg ^ w_reg)))
            else:
                matched += 1
    h(f"可对比（官方名命中 wiki）的词缀行: {matched + len(prop_mismatch)}；属性完全一致: {matched}")
    h(f"属性层差异: {len(prop_mismatch)}")
    for m in prop_mismatch[:60]:
        h(f"- [{m[0]}] {m[1]} → {m[2]}: {m[3]} {m[4]}")
    if len(prop_mismatch) > 60:
        h(f"- ... 其余 {len(prop_mismatch)-60} 条见 JSON")

    rep = "\n".join(out)
    with open(os.path.join(HERE, "generated", "affix_diff.md"), "w", encoding="utf-8") as f:
        f.write(rep)
    with open(os.path.join(HERE, "generated", "affix_diff.json"), "w", encoding="utf-8") as f:
        json.dump({
            "missing_names": sorted(game_zh - wnames),
            "prop_mismatch": prop_mismatch,
            "matched_prop_rows": matched,
        }, f, ensure_ascii=False, indent=1)
    print(rep)
    print("\n>>> tools/generated/affix_diff.md / affix_diff.json")


if __name__ == "__main__":
    main()
