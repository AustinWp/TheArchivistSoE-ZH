# -*- coding: utf-8 -*-
"""词缀条目 ↔ 源表 `MagicPrefix.txt` / `MagicSuffix.txt` 的**配对唯一实现**（校验与修正共用）。

为什么不能只按 `(group, level, 前后缀)` 取第一个候选
--------------------------------------------------
同一个 `(group, level)` 下有**多行**，各行的官方名不同：

    组101 lvl1 → Stout(坚固之) ×3 / Blanched(白化之) / Sturdy(结实之) / Miocene(教化之) ×2

实测：1442 条词缀里有 **736 条**落在这种"多候选"键上，只取第一个等于掷骰子。
正确做法是用**属性指纹**（源表 `mod1code/mod1min/mod1max` … ×3）对上我方的
`displayProperties`（property/min/max），再配合「我方现名 == 官方名」的强锚定。

配对规则（组内贪心）：

| 证据 | 分 |
|---|---|
| 我方现名 == 该候选的官方名 | +100 |
| 属性集（code/min/max 三元组）完全一致 | +20 |
| 属性 code 有交集 | +5 |

证据不足的剩余项按顺序补齐并计入 `guessed`（供报告标注）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from client_zh import official_name  # noqa: E402
from source_repo import excel_dir  # noqa: E402

FILES = [("MagicPrefix.txt", False), ("MagicSuffix.txt", True)]
MOD_SETS = [(f"mod{i}code", f"mod{i}min", f"mod{i}max") for i in (1, 2, 3)]


def load_rows():
    """返回 [(是否后缀, 列名→下标, 行列表)]。"""
    out = []
    for fname, is_suffix in FILES:
        path = os.path.join(excel_dir(), fname)
        if not os.path.exists(path):
            continue
        lines = open(path, encoding="utf-8-sig", errors="replace").read().splitlines()
        hdr = lines[0].split("\t")
        cols = {n: hdr.index(n) for n in
                ("Name", "group", "level", "spawnable", "frequency") + tuple(c for s in MOD_SETS for c in s)
                if n in hdr}
        rows = [l.split("\t") for l in lines[1:] if l.strip()]
        out.append((is_suffix, cols, rows))
    return out


def cell(row, cols, name):
    i = cols.get(name)
    return row[i].strip() if i is not None and len(row) > i else ""


def _src_props(row, cols):
    out = set()
    for cc, mc, xc in MOD_SETS:
        code = cell(row, cols, cc)
        if code:
            out.add((code.lower(), cell(row, cols, mc), cell(row, cols, xc)))
    return out


def _our_props(item):
    return {(str(p.get("property", "")).strip().lower(), str(p.get("min", "")).strip(),
             str(p.get("max", "")).strip())
            for p in (item.get("displayProperties") or [])
            if isinstance(p, dict) and p.get("property")}


def match(table, items):
    """返回 (assign, guessed)：``assign[i]`` = (源表行, 列名→下标)。"""
    tables = load_rows()
    groups = {}
    for is_suffix, cols, rows in tables:
        for r in rows:
            if not cell(r, cols, "Name"):
                continue
            key = (cell(r, cols, "group"), cell(r, cols, "level"), is_suffix)
            groups.setdefault(key, []).append((r, cols))

    assign, guessed = {}, 0
    our_groups = {}
    for i, it in enumerate(items):
        our_groups.setdefault((str(it.get("group")), str(it.get("level")), bool(it.get("suffix"))), []).append(i)

    for key, idxs in our_groups.items():
        cands = groups.get(key, [])
        if not cands:
            continue
        used_i, used_j = set(), set()
        score = {}
        for i in idxs:
            up = _our_props(items[i])
            for j, (r, cols) in enumerate(cands):
                s = 0
                want = official_name(table, cell(r, cols, "Name"))
                if want and want == items[i].get("name"):
                    s += 100
                sp = _src_props(r, cols)
                if up and sp:
                    if up == sp:
                        s += 20
                    elif up & sp:
                        s += 5
                score[(i, j)] = s
        for (i, j), s in sorted(score.items(), key=lambda kv: -kv[1]):
            if s <= 0 or i in used_i or j in used_j:
                continue
            assign[i] = cands[j]
            used_i.add(i)
            used_j.add(j)
        for i in idxs:                      # 证据不足的按顺序补齐
            if i in used_i:
                continue
            for j, c in enumerate(cands):
                if j not in used_j:
                    assign[i] = c
                    used_j.add(j)
                    guessed += 1
                    break
    return assign, guessed
