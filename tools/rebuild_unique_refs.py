# -*- coding: utf-8 -*-
"""重建 Weapons.json / Armors.json 里「该基底上的暗金」列表。

这两个文件里的 `uniques` 字段是早期遗留的**手写快照**，暗金改名后没有跟着更新
（实测 67 件物品挂着旧名，例如「巫野之弦」实际叫「狂野之弦」）。
这里改为从 `Uniques.json`（权威）按基底 code 反向重建。

用法:
    python3 tools/rebuild_unique_refs.py [--check]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def build_map():
    """基底 code → [暗金显示名]（按 Uniques.json 顺序）。"""
    uniques = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"),
                             encoding="utf-8"))
    out = {}
    for u in uniques:
        base = u.get("weaponBase") or u.get("armorBase") or u.get("jeweleryBase") or {}
        code = str(base.get("code") or "").lower()
        name = u.get("displayName") or u.get("index")
        if code and name:
            out.setdefault(code, []).append(name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    want = build_map()
    changes = 0

    for fn in ("Weapons.json", "Armors.json"):
        p = os.path.join(ROOT, "public", "data", fn)
        data = json.load(open(p, encoding="utf-8"))

        for it in data:
            code = str(it.get("code", "")).lower()
            names = want.get(code, [])
            current = [x.get("uniqueName") for x in (it.get("uniques") or [])]

            if current == names:
                continue

            changes += 1
            if changes <= 10 and args.check:
                print(f"  {fn} {code} {it.get('name')}: {current} → {names}")

            if not args.check:
                it["uniques"] = [{"uniqueName": nm, "uniqueCode": it["code"]} for nm in names]

        if not args.check:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")

    print(f"{'需重建' if args.check else '已重建'} {changes} 件物品的暗金引用")
    return 0


if __name__ == "__main__":
    sys.exit(main())
