# -*- coding: utf-8 -*-
"""词缀深度对齐（官方词缀表 = 唯一来源）。

- 名称层：官方串表中文名 vs 本站 Affixes.json（标准化差集 → 缺失清单）
- 属性层：同名聚合（普通+地图行并集） vs 条目 displayProperties 并集
- 自动修复：
    A) 游戏新增普通属性 → 补入条目 displayProperties（min/max 按游戏值）
    缺失名称 → 从游戏行生成新条目（name=官方名；displayString 由模板库生成，可后续人工润色）
- 无法判定的差异 → 输出报告（tools/generated/affix_align_report.md）供人工

用法: python3 tools/affix_deep_align.py
"""
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GE = "/tmp/SOECN/standard-mode/data/global/excel"
AFFIX_PATH = os.path.join(ROOT, "public", "data", "Affixes.json")
TPL_PATH = os.path.join(HERE, "generated", "prop_zh_templates.json")

ALIAS_PROPS = {"eledam", "openwounds", "deep-wounds", "Deep-Wounds", "dmg-pois"}


def read(path):
    return [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8-sig", errors="replace") if l.strip()]


def norm(n):
    return (n or "").strip().rstrip("的之者").strip()


def is_alias(p):
    return p[0] in ALIAS_PROPS or p[0].startswith(("extra-", "pierce-"))


def fmt_display(prop, mn, mx, tpl):
    """模板生成（数值替换）；模板质量有限，标记用途仅补全用"""
    t = tpl.get(prop, prop)
    t = t.replace("[null]", str(mn)).replace("[]", str(mx)).replace("%d", str(mn if mn == mx else f"{mn}-{mx}"))
    if mn == mx:
        t = re.sub(r"%s", str(mn), t)
    else:
        t = re.sub(r"%s", f"{mn}-{mx}", t)
    if t == prop:
        t = f"{mn}-{mx} {prop}" if mn != mx else f"+{mn} {prop}"
    return t


def main():
    zh = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
    aff = json.load(open(AFFIX_PATH, encoding="utf-8"))
    tpl = json.load(open(TPL_PATH, encoding="utf-8"))

    wagg = defaultdict(lambda: defaultdict(set))
    for a in aff:
        k = norm(a["name"])
        for p in a.get("displayProperties") or []:
            wagg[k][(p.get("property") or "")].add((int(p.get("min") or 0), int(p.get("max") or 0)))

    gagg = defaultdict(lambda: defaultdict(set))
    gmeta = {}   # en -> {name字段, suffix, level...}
    for f in ["MagicPrefix.txt", "MagicSuffix.txt", "AutoMagic.txt"]:
        rows = read(f"{GE}/{f}")
        hdr = rows[0]
        ni = hdr.index("Name"); ei = hdr.index("enabled") if "enabled" in hdr else None
        mod_cols = []
        for i in range(1, 9):
            c, mn, mx = f"mod{i}code", f"mod{i}min", f"mod{i}max"
            if c in hdr and mn in hdr and mx in hdr:
                mod_cols.append((hdr.index(c), hdr.index(mn), hdr.index(mx)))
        for r in rows[1:]:
            if ei is not None and (len(r) <= ei or r[ei] != "1"):
                continue
            n = r[ni] if ni < len(r) else ""
            if not n:
                continue
            gmeta.setdefault(n, {"suffix": f.endswith("Suffix.txt"), "level": [], "spawn": None})
            for ci, mni, mxi in mod_cols:
                c = r[ci] if ci < len(r) else ""
                if not c:
                    continue
                mnv = int(r[mni]) if mni < len(r) and r[mni].lstrip("-").isdigit() else 0
                mxv = int(r[mxi]) if mxi < len(r) and r[mxi].lstrip("-").isdigit() else 0
                gagg[n][c].add((mnv, mxv))
            gmeta[n]["level"].append((r[hdr.index("level")] if "level" in hdr else "", r[hdr.index("maxlevel")] if "maxlevel" in hdr else ""))

    report = []
    fixed = []

    # ---------- A) 补齐普通属性 ----------
    added = 0
    for en, gprops in gagg.items():
        zn = zh.get(en, "")
        k = norm(zn)
        if not k or k not in wagg:
            continue
        for code, vals in gprops.items():
            if code.startswith("map-") or is_alias((code, 0, 0)):
                continue
            # 与 wiki 同码对比：wiki 缺哪些数值范围
            wvals = wagg[k][code]
            add = sorted(vals - wvals)
            if add:
                for (mn, mx) in add:
                    for a in aff:
                        if norm(a["name"]) == k:
                            a.setdefault("displayProperties", []).append({
                                "displayString": fmt_display(code, mn, mx, tpl),
                                "property": code, "min": mn, "max": mx,
                            })
                            added += 1
                            break
    report.append(f"## A. 自动补入游戏新增普通属性：{added} 处")

    # ---------- B) 缺失名称补全（官方中文名在 wiki 无对应） ----------
    wnames = set(norm(a["name"]) for a in aff)
    missing = []
    for en, zn in zh.items():
        if not zn:
            continue
        if zn.startswith("圣化"):
            continue
        k = norm(zn)
        if k in wnames or en not in gagg or not gagg[en]:
            continue
        vals = sorted(vals for code, v in gagg[en].items() if not code.startswith("map-") for vals in v)
        if not vals:
            continue
        missing.append((en, zn, vals))
    report.append(f"## B. 缺失词缀（已从游戏数据生成条目）：{len(missing)}")
    for en, zn, vals in missing:
        props = []
        for code, v in sorted(gagg[en].items()):
            if code.startswith("map-") or is_alias((code, 0, 0)):
                continue
            for (mn, mx) in sorted(v):
                props.append({
                    "displayString": fmt_display(code, mn, mx, tpl),
                    "property": code, "min": mn, "max": mx,
                })
        aff.append({
            "name": zh.get(en, en),
            "spawnable": "1", "rare": "0", "level": 1, "maxLevel": None,
            "requiredLevel": 0, "classSpecific": "", "frequency": 1, "group": None,
            "displayProperties": props,
            "displayItemTypeNames": [], "displayExcludedItemTypeNames": [],
            "classDisplayName": None,
            "suffix": gmeta.get(en, {}).get("suffix", False),
            "auto": True,
        })

    json.dump(aff, open(AFFIX_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    report.append(f"共 {len(aff)} 条（补全后）")
    with open(os.path.join(HERE, "generated", "affix_align_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
