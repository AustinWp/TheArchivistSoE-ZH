# -*- coding: utf-8 -*-
"""从游戏表**重新生成** `Weapons.json` / `Armors.json`，保留中文列。

为什么需要它
------------
这两个文件是早期 `translate_data.py`（已废弃）的产物，之后一直**手工维护** ——
结果反复出问题：名字改一半（`name` 改了 `displayName` 没改）、阶位码写错、
整行缺失、属性被写成单个字符……**根因就是「数据靠手改」**。

本工具的职责边界
----------------
- **结构数值**（伤害/防御/等级/需求/孔数/阶位码…）**一律以游戏表为准**，重新生成；
- **中文内容**：物品名走 `tools/official_names.py`（唯一解析入口），
  `itemType` 之类表里没有中文的对象从**现有 JSON 收割**，不丢翻译；
- **派生字段**：`itemTier` 由阶位码推导，`uniques` 由 `Uniques.json` 反查；
- 新增/删除的物品**自动跟随游戏表**（例：`smn`/`smx` 曾整行缺失）。

用法:
    python3 tools/build_item_tables.py --check    # 只报告会怎么变
    python3 tools/build_item_tables.py            # 写入
"""
import argparse
import json
import os
import re
import sys

CJK = re.compile(r"[\u4e00-\u9fff]")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from official_names import OfficialNames  # noqa: E402

# JSON 字段 ← 游戏表列
WEAPON_MAP = [
    ("type", "type"), ("secondType", "type2"), ("code", "code"),
    ("minDamage", "mindam"), ("maxDamage", "maxdam"),
    ("oneOrTwoHanded", "1or2handed"), ("twoHanded", "2handed"),
    ("twoHandedMinDamage", "2handmindam"), ("twoHandedMaxDamage", "2handmaxdam"),
    ("minMissileDamage", "minmisdam"), ("maxMissileDamage", "maxmisdam"),
    ("speed", "speed"), ("requiredStrength", "reqstr"), ("requiredDexterity", "reqdex"),
    ("noDurability", "nodurability"), ("durability", "durability"),
    ("level", "level"), ("requiredLevel", "levelreq"),
    ("normalTierCode", "normcode"), ("exceptionalTierCode", "ubercode"),
    ("eliteTierCode", "ultracode"), ("maxSockets", "gemsockets"),
]

ARMOR_MAP = [
    ("type", "type"), ("secondType", "type2"), ("code", "code"),
    ("minDefense", "minac"), ("maxDefense", "maxac"), ("block", "block"),
    ("minDamage", "mindam"), ("maxDamage", "maxdam"),
    ("requiredStrength", "reqstr"), ("durability", "durability"),
    ("level", "level"), ("requiredLevel", "levelreq"),
    ("normalTierCode", "normcode"), ("exceptionalTierCode", "ubercode"),
    ("eliteTierCode", "ultracode"), ("maxSockets", "gemsockets"),
]

# 这些字段表里没有（或是中文化的），从现有 JSON 收割，不重新生成
HARVEST = ["itemType", "secondItemType", "onlyClassDisplayText", "highlight",
           "dontDisplay", "itemTier"]


def load_txt(name):
    p = os.path.join(ROOT, "public", "data", "standard", name)
    rows = [l.split("\t") for l in
            open(p, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
            if l.strip()]
    return rows[0], rows[1:]


def cell(row, header, name):
    if name not in header:
        return ""
    i = header.index(name)
    return row[i].strip() if i < len(row) else ""


# 不收录的物品：投掷药水（含 TPot 内部占位）与任务物品 —— 早期数据也是这么排除的
SKIP_TYPES = {"tpot"}


def infer_types(old_rows, fields):
    """按旧数据的实际类型决定新值怎么转换（旧数据里是 int 就写 int，别写成字符串）。"""
    out = {}
    for f in fields:
        vals = [r[f] for r in old_rows if isinstance(r, dict) and isinstance(r.get(f), (int, float))
                and not isinstance(r.get(f), bool)]
        strs = [r[f] for r in old_rows if isinstance(r, dict) and isinstance(r.get(f), str) and r.get(f) != ""]
        # 旧数据里该字段可能是 None（例如弩没有近战伤害）—— 只看有值的那些
        out[f] = int if (vals and not strs) else (float if vals else str)
    return out


def convert(raw, typ, prev=None):
    """按旧数据的类型与「空值表示」还原字段值。

    旧数据对「空」有两种写法（`None` 与 `''`），逐个字段统一会造成整表噪音，
    所以空单元格一律沿用该物品原来的写法。
    """
    if raw == "":
        if prev is None or prev == "":
            return prev
        return None if typ is not str else ""
    if typ is str:
        return raw
    try:
        return int(float(raw)) if typ is int else float(raw)
    except ValueError:
        return None


def tier_of(code, norm, uber, ultra):
    c = str(code or "").lower()
    uber = str(uber or "").lower()
    ultra = str(ultra or "").lower()
    if uber and c == uber:
        return "扩展"
    if ultra and c == ultra:
        return "精英"
    return "普通"


def build(tbl, json_name, mapping, on, uniques_by_code):
    header, rows = load_txt(tbl)
    old = json.load(open(os.path.join(ROOT, "public", "data", json_name), encoding="utf-8"))
    old_by_code = {x["code"].lower(): x for x in old}

    types = infer_types(old, [f for f, _ in mapping])

    out = []
    skipped = []
    for r in rows:
        code = cell(r, header, "code")
        if not code or not cell(r, header, "type"):
            continue

        # 排除投掷药水与任务物品（与早期数据的收录范围一致）
        if cell(r, header, "type") in SKIP_TYPES:
            continue
        # 任务物品照收（它们是游戏里真实存在的物品，能搜到比搜不到好）；
        # 只排除投掷药水 / TPot 内部占位（上面按 type 过滤）

        prev = old_by_code.get(code.lower(), {})
        item = {}

        # ① 结构数值：以游戏表为准（类型与旧数据保持一致）
        for field, col in mapping:
            item[field] = convert(cell(r, header, col), types.get(field, str), prev.get(field))

        # ② 中文名：唯一解析入口
        zh, _src = on.resolve(code)
        item["name"] = zh or prev.get("name") or cell(r, header, "name")
        item["displayName"] = item["name"]

        # ③ 三个阶位的显示名
        for field, col in (("normalItemDisplayName", "normcode"),
                           ("exceptionalItemDisplayName", "ubercode"),
                           ("eliteItemDisplayName", "ultracode")):
            tcode = cell(r, header, col)
            if not tcode:
                name = prev.get(field)          # 没有这一阶（例如护符），沿用旧值（通常是 None）
            elif tcode.lower() == code.lower():
                name = item["name"]             # 该阶就是它自己（自定义基底，如 7cr2）
            else:
                name = on.resolve(tcode)[0] or prev.get(field) or ""
            item[field] = name

        item["itemTier"] = tier_of(code, item.get("normalTierCode", ""),
                                   item.get("exceptionalTierCode", ""),
                                   item.get("eliteTierCode", ""))

        # 名字必须含中文：查不到官方中文名的物品不收录（页面上不出现英文名）
        final_name = zh or prev.get("name") or ""
        if not CJK.search(final_name):
            skipped.append((code, cell(r, header, "name")))
            continue

        # ④ 表里没有的字段：从旧数据收割（保住中文化的 itemType 等）
        for k in HARVEST:
            if k in ("itemTier",):
                continue
            if k in prev:
                item[k] = prev[k]

        # ⑤ 各基底上的暗金：由 Uniques.json 反查
        names = uniques_by_code.get(code.lower(), [])
        if names:
            item["uniques"] = [{"uniqueName": nm, "uniqueCode": code} for nm in names]
        else:
            # 该基底没有暗金：旧数据用 None 表示，保持一致
            item["uniques"] = None if prev.get("uniques") is None else []

        out.append(item)

    return old, out, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    on = OfficialNames()
    uniq = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"), encoding="utf-8"))
    uniques_by_code = {}
    for u in uniq:
        b = u.get("weaponBase") or u.get("armorBase") or u.get("jeweleryBase") or {}
        c = str(b.get("code") or "").lower()
        nm = u.get("displayName") or u.get("index")
        if c and nm:
            uniques_by_code.setdefault(c, []).append(nm)

    total_changed = 0
    for tbl, json_name, mapping in (("Weapons.txt", "Weapons.json", WEAPON_MAP),
                                    ("Armor.txt", "Armors.json", ARMOR_MAP)):
        old, new, skipped = build(tbl, json_name, mapping, on, uniques_by_code)
        old_by = {x["code"].lower(): x for x in old}
        new_by = {x["code"].lower(): x for x in new}

        added = sorted(set(new_by) - set(old_by))
        removed = sorted(set(old_by) - set(new_by))
        field_diff = {}
        for c in set(old_by) & set(new_by):
            a, b = old_by[c], new_by[c]
            for k in set(a) | set(b):
                if a.get(k) != b.get(k):
                    field_diff.setdefault(k, 0)
                    field_diff[k] += 1

        print(f"=== {json_name}: 旧 {len(old)} 条 → 新 {len(new)} 条")
        if added:
            print(f"   新增 {len(added)} 条: {added}")
        if removed:
            print(f"   移除 {len(removed)} 条: {removed}")
        if skipped:
            print(f"   因查不到官方中文名而跳过 {len(skipped)} 条: {[s[0] for s in skipped]}")
        if field_diff:
            print(f"   字段变化: {dict(sorted(field_diff.items(), key=lambda kv: -kv[1])[:10])}")
        changed = len(added) + len(removed) + sum(field_diff.values())
        total_changed += changed

        if not args.check and changed:
            with open(os.path.join(ROOT, "public", "data", json_name), "w", encoding="utf-8") as f:
                json.dump(new, f, ensure_ascii=False, indent=2)
                f.write("\n")

    print(f"\n{'需变更' if args.check else '已重建'}（{total_changed} 处）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
