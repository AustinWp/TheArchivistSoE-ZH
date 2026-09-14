# -*- coding: utf-8 -*-
"""暗金条目 ↔ 源表 `UniqueItems.txt` 的**配对唯一实现**（校验与修正共用）。

为什么不能按 `(code, lvl)` 查表
------------------------------
源表 606 条启用行里有 **26 组共 130 行撞车**（同名基底、同等级 —— 全是戒指/项链/手套
这类饰品，最多一组 35 行）。直接查表会把「乌鸦之霜」配成 `Dwarf Star`、
「大君之怒」配成 `Rising Sun`（2026-09-14 实测踩过，而且差点把 421 处正文一起改错）。

也不能只靠顺序：我方 47 条的顺序与源表不一致。

配对规则
--------
按 `(code, lvl)` 分组，组内打分后贪心指派：

| 证据 | 分 |
|---|---|
| 我方现名 == 客户端官方名（本身就是"已经对了"的强证据） | +100 |
| `displayProperties` 与源表 prop/min/max 相交 | +10 |
| `rarity` 相同 | +5 |
| `requiredLevel` == 源表 `lvl req` | +3 |
| `carryOne` == 源表 `carry1` | +1 |

无法由证据决定的剩余项按组内顺序补齐，并计入 `guessed`（供报告标注「推定」）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from client_zh import official_name  # noqa: E402
from source_repo import excel_dir  # noqa: E402

WANT_COLS = ("index", "code", "lvl", "enabled", "rarity", "lvl req", "carry1")


def load_enabled_rows():
    """读源表 → (列名→下标, 启用行列表, prop 三元组下标表)。"""
    path = os.path.join(excel_dir(), "UniqueItems.txt")
    if not os.path.exists(path):
        return {}, [], []
    lines = open(path, encoding="utf-8-sig", errors="replace").read().splitlines()
    hdr = lines[0].split("\t")
    cols = {n: hdr.index(n) for n in WANT_COLS if n in hdr}
    rows = [l.split("\t") for l in lines[1:] if l.strip()]
    enabled = [r for r in rows if len(r) > cols.get("enabled", -1) and r[cols["enabled"]].strip() == "1"]
    props = [(hdr.index(f"prop{i}"), hdr.index(f"min{i}"), hdr.index(f"max{i}"))
             for i in range(1, 13) if f"prop{i}" in hdr]
    return cols, enabled, props


def cell(row, cols, name):
    i = cols.get(name)
    return row[i].strip() if i is not None and len(row) > i else ""


def _src_props(row, props):
    out = set()
    for pi, mi, xi in props:
        if len(row) > xi and row[pi].strip():
            out.add((row[pi].strip().lower(), row[mi].strip(), row[xi].strip()))
    return out


def _our_props(item):
    return {(str(p.get("property", "")).strip().lower(), str(p.get("min", "")).strip(),
             str(p.get("max", "")).strip())
            for p in (item.get("displayProperties") or [])
            if isinstance(p, dict) and p.get("property")}


def match(table, items):
    """返回 (assign, guessed)：``assign[i]`` = 源表行；``guessed`` = 按顺序推定的条数。"""
    cols, src_rows, props = load_enabled_rows()
    src_groups = {}
    for r in src_rows:
        src_groups.setdefault((cell(r, cols, "code"), cell(r, cols, "lvl")), []).append(r)

    assign, guessed = {}, 0
    used_rows = set()

    # 0) **全局锚定**：我方现名与某源表行的官方名**完全相同**时，直接配 ——
    #    这是最强证据，且必须跨组做。反例：彩虹刻面的 4 个变体行（`Rainbow Facet Ltng`…）
    #    与普通 `Rainbow Facet` 行不在同一 (code,lvl) 组里，只按组配对会把
    #    「彩虹刻面·闪电」配成普通行、改成「彩虹刻面」（实测踩过）。
    by_name = {}
    for j, r in enumerate(src_rows):
        n = official_name(table, cell(r, cols, "index"))
        if n:
            by_name.setdefault(n, []).append(j)
    anchored = set()
    for i, it in enumerate(items):
        cands = [j for j in by_name.get(it.get("displayName"), [])
                 if j not in used_rows
                 # 名字相同还要 (code,lvl) 也对得上：我方历史上出现过**同名不同物**
                 # （两条「警戒之墙」，其中一条其实是 `Lidless Wall`），
                 # 只按名字锚定会把先出现的那条锚到别人的行上。
                 and cell(src_rows[j], cols, "code") == it.get("code")
                 and cell(src_rows[j], cols, "lvl") == str(it.get("level"))]
        if len(cands) == 1:
            assign[i] = src_rows[cands[0]]
            used_rows.add(cands[0])
            anchored.add(i)

    for gkey in {(it.get("code"), str(it.get("level"))) for it in items}:
        idxs = [i for i, it in enumerate(items)
                if (it.get("code"), str(it.get("level"))) == gkey and i not in anchored]
        cands = [r for r in src_groups.get(gkey, []) if id(r) not in {id(x) for x in used_rows}]
        if not cands:
            continue
        if len(cands) == 1:
            for i in idxs:
                assign[i] = cands[0]
            continue
        score = {}
        for i in idxs:
            u = items[i]
            up = _our_props(u)
            for j, r in enumerate(cands):
                s = 0
                want = official_name(table, cell(r, cols, "index"))
                if want and want == u.get("displayName"):
                    s += 100
                if up and up & _src_props(r, props):
                    s += 10
                if cell(r, cols, "rarity") and str(u.get("rarity", "")).strip() == cell(r, cols, "rarity"):
                    s += 5
                if cell(r, cols, "lvl req") and str(u.get("requiredLevel", "")).strip() == cell(r, cols, "lvl req"):
                    s += 3
                if cell(r, cols, "carry1") and str(u.get("carryOne", "")).strip() == cell(r, cols, "carry1"):
                    s += 1
                score[(i, j)] = s
        used_i, used_j = set(), set()
        for (i, j), s in sorted(score.items(), key=lambda kv: -kv[1]):
            if s <= 0 or i in used_i or j in used_j:
                continue
            assign[i] = cands[j]
            used_i.add(i)
            used_j.add(j)
        for i in idxs:                                   # 证据不足的按顺序补齐
            if i in used_i:
                continue
            for j, r in enumerate(cands):
                if j not in used_j:
                    assign[i] = r
                    used_j.add(j)
                    used_rows.add(id(r))
                    guessed += 1
                    break
    return assign, guessed, cols
