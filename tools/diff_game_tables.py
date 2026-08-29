# -*- coding: utf-8 -*-
"""全表差异报告：游戏仓库（SOECN） vs 本站页面数据。

第一阶段只产出报告（不改数据），按数据集输出：
  新增（游戏有/站点无） / 缺失（站点有/游戏无） / 字段不一致

用法: python3 tools/diff_game_tables.py [--src /tmp/SOECN]
输出: tools/generated/table_diff.md
"""
import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read(path):
    return [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8-sig", errors="replace") if l.strip()]


def rows_by(path, key):
    rows = read(path)
    if not rows:
        return {}
    hdr = rows[0]
    ki = hdr.index(key) if key in hdr else None
    if ki is None:
        return {}
    return {r[ki]: r for r in rows[1:] if len(r) > ki and r[ki]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/tmp/SOECN")
    args = ap.parse_args()
    GE = os.path.join(args.src, "standard-mode", "data", "global", "excel")
    out = []

    def h(line):
        out.append(line)

    h("# 游戏仓库 vs 本站数据 差异报告（第一阶段：存在性与关键字段）\n")

    # ---------------- 1) 暗金 ----------------
    h("## 1. 暗金装备（UniqueItems.txt vs Uniques.json）")
    g = read(os.path.join(GE, "UniqueItems.txt"))
    gh = g[0]
    gi = gh.index("index"); gc = gh.index("code"); ge = gh.index("enabled")
    gl = gh.index("level") if "level" in gh else None
    gr = gh.index("rarity") if "rarity" in gh else None
    game = {}
    for r in g[1:]:
        if len(r) <= max(gi, gc) or r[ge] != "1":
            continue
        if any(k in r[gi] for k in ("Ascend", "Map", "Trophy", "Dev", "unused", "Reserved")):
            continue
        game[r[gi]] = r
    wiki = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"), encoding="utf-8"))
    # wiki 按 code 聚组（同名暗金不同底材可能同 index? wiki index=中文，用 code+level 匹配游戏）
    wby = {}
    for w in wiki:
        wby.setdefault(w["code"], []).append(w)
    # 游戏侧（index 英文加 zh 名取不到）——先报数量
    h(f"- 游戏启用真实暗金（去任务/升华/奖杯等特殊行）：**{len(game)}**；本站收录：**{len(wiki)}**")
    # 用 soe 官方译名交叉：官方名在 wiki 缺失 = 0（此前已验证）；这轮核对字段级
    zm = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
    names = set(w["index"] for w in wiki)
    nozh = [i for i in game if i not in zm]
    h(f"- 官方串表未提供中文名的游戏暗金：**{len(nozh)}**（页面对这些保留现有译名/英文名）")
    # 已核对暗金名（官方名覆盖的）都在 wiki；统计 level 不一致
    lvl_diff = 0
    for gi_, g in game.items():
        z = zm.get(gi_)
        if z and z in names and gl is not None:
            candidates = [w for w in wiki if w["index"] == z]
            if candidates and any(str(w.get("level")) != g[gl] for w in candidates):
                lvl_diff += 1
    h(f"- level 字段不一致（官方中文名可匹配的条目中）：{lvl_diff}（样本略，详见后续报告）")
    h("")

    # ---------------- 2) 符文之语 ----------------
    h("## 2. 符文之语（Runes.txt vs Runewords.json）")
    gr = read(os.path.join(GE, "Runes.txt"))
    gh = gr[0]
    ci_name = gh.index("Name"); ci_rn = gh.index("Rune Name") if "Rune Name" in gh else None
    runes = {}
    for r in gr[1:]:
        if len(r) <= 2 or r[2] != "1":
            continue
        runes[r[ci_name]] = r
        if ci_rn is not None and r[ci_rn]:
            runes.setdefault(r[ci_rn], r)
    rw = json.load(open(os.path.join(ROOT, "public", "data", "Runewords.json"), encoding="utf-8"))
    zm = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
    # wiki 侧候选 key：name(RunewordN) / runewordName(中译)
    def wiki_key(x):
        hits = [k for k in (x.get("name"),) if k in runes]
        # 中文名反查官方英文名
        en = [k2 for k2, v in zm.items() if v and x.get("runewordName") == v and k2 in runes]
        if hits:
            return hits[0]
        if en:
            return en[0]
        return None
    unmatched = [x["name"] for x in rw if wiki_key(x) is None]
    h(f"- 游戏 complete=1：**{len(set(g[ci_name] for g in runes.values()))} 条符文之语**；本站：**{len(rw)}**（匹配键 {len(runes)} 个）")
    h(f"- 本站未能对应到游戏行的条目（name 或中译均不匹配）：**{len(unmatched)}** {unmatched}")
    seq_diff = []
    for x in rw:
        g = runes.get(wiki_key(x) or "")
        if not g:
            continue
        grune = [g[gh.index(f"Rune{i}")] for i in range(1, 7) if len(g) > gh.index(f"Rune{i}") and g[gh.index(f"Rune{i}")]]
        wrune = [x[k] for k in ("firstRune", "secondRune", "thirdRune", "fourthRune", "fifthRune", "sixthRune") if x.get(k)]
        if grune != wrune:
            seq_diff.append((x["name"], "仓库:" + ",".join(grune), "本站:" + ",".join(wrune)))
    h(f"- 符文序列不一致：**{len(seq_diff)}**")
    for e in seq_diff[:20]:
        h(f"  - {e[0]}: {e[1]} vs {e[2]}")
    h("")

    # ---------------- 3) 套装 ----------------
    h("## 3. 套装（Sets.txt / SetItems.txt vs 本站 SetItems.txt）")
    sets_g = rows_by(os.path.join(GE, "Sets.txt"), "index")
    si_g = rows_by(os.path.join(GE, "SetItems.txt"), "index")
    si_w = rows_by(os.path.join(ROOT, "public", "data", "standard", "SetItems.txt"), "index")
    h(f"- 游戏套装数：{len(sets_g)}；游戏套装部件：{len(si_g)}；本站套装部件：{len(si_w)}")
    # 套装部件 key 用 code 列对齐
    def code_map(path):
        rows = read(path)
        hdr = rows[0]
        ci = next((hdr.index(c) for c in ("code", "item", "*item") if c in hdr), 1)
        return Counter(r[ci] for r in rows[1:] if len(r) > ci and r[ci])
    cg, cw = code_map(os.path.join(GE, "SetItems.txt")), code_map(os.path.join(ROOT, "public", "data", "standard", "SetItems.txt"))
    only_g = {c: n for c, n in cg.items() if n > cw.get(c, 0)}
    only_w = {c: n for c, n in cw.items() if n > cg.get(c, 0)}
    h(f"- 部件 code 仅游戏有（x 数量差）：{only_g if only_g else '无'}")
    h(f"- 部件 code 仅本站有：{only_w if only_w else '无'}")
    h("")

    # ---------------- 4) 技能 ----------------
    h("## 4. 技能（Skills.txt vs Skills.json）")
    sk = read(os.path.join(GE, "Skills.txt"))
    skh = sk[0]
    h(f"- 技能表列（前12）：{skh[:12]}")
    skip = [r for r in sk[1:] if r and r[0]]
    h(f"- 游戏技能行数：{len(skip)}")
    try:
        wiki_sk = json.load(open(os.path.join(ROOT, "public", "data", "Skills.json"), encoding="utf-8"))
        h(f"- 本站 Skills.json：{len(wiki_sk)} 条；首条字段：{list(wiki_sk[0].keys())[:10] if wiki_sk else '空'}")
    except Exception as e:
        h(f"- 本站 Skills.json 读取失败：{e}")
    h("")

    # ---------------- 5) 词缀 ----------------
    h("## 5. 词缀（MagicPrefix/Suffix、RarePrefix/Suffix、UniquePrefix/Suffix、AutoMagic）")
    for f in ["MagicPrefix.txt", "MagicSuffix.txt", "RarePrefix.txt", "RareSuffix.txt", "UniquePrefix.txt", "UniqueSuffix.txt", "AutoMagic.txt"]:
        rows = read(os.path.join(GE, f))
        hdr = rows[0]
        enabled_i = hdr.index("enabled") if "enabled" in hdr else None
        cnt = len(rows) - 1
        if enabled_i is not None:
            cnt = sum(1 for r in rows[1:] if len(r) > enabled_i and r[enabled_i] == "1")
        h(f"- {f}: 启用 {cnt}")
    try:
        aff = json.load(open(os.path.join(ROOT, "public", "data", "Affixes.json"), encoding="utf-8"))
        h(f"- 本站 Affixes.json：{len(aff)} 条；首条字段：{list(aff[0].keys())[:12] if aff else '空'}")
    except Exception as e:
        h(f"- 本站 Affixes.json 读取失败：{e}")
    h("")

    # ---------------- 6) 底材/物品 ----------------
    h("## 6. 底材与杂项（已核对过行数的补充说明）")
    for f in ["Weapons.txt", "Armor.txt", "Misc.txt", "ItemTypes.txt", "Gems.txt", "Belts.txt"]:
        gm = len(read(os.path.join(GE, f))) - 1
        wm = len(read(os.path.join(ROOT, "public", "data", "standard", f))) - 1 if os.path.exists(os.path.join(ROOT, "public", "data", "standard", f)) else "-"
        h(f"- {f}: 游戏 {gm} / 本站 {wm}")

    rep = "\n".join(out)
    with open(os.path.join(HERE, "generated", "table_diff.md"), "w", encoding="utf-8") as f:
        f.write(rep)
    print(rep)
    print("\n>>> 报告已写入 tools/generated/table_diff.md")


if __name__ == "__main__":
    main()
