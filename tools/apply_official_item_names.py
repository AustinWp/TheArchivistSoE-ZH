# -*- coding: utf-8 -*-
"""把「底材物品名」对齐到游戏官方中文串表。

游戏取名链路：物品行 `namestr` 非空 → 用 namestr 作字符串键；否则用 `code` 作键。
本工具按这条链路去 `official_zh.json`（由 soe.txt 生成）取值，凡是官方有中文的，
就把 `Weapons.json` / `Armors.json` / `Uniques.json`（含嵌套的 base 名）里的旧译改掉。

用法:
    python3 tools/apply_official_item_names.py            # 应用
    python3 tools/apply_official_item_names.py --check    # 只看差异
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TABLES = ["Weapons.txt", "Armor.txt", "Misc.txt"]

# 取值链路的唯一实现（namestr/code → StrEternal<英文名>）都在这里，别再手写一遍
sys.path.insert(0, HERE)
from official_names import OfficialNames  # noqa: E402


def clean(v):
    return re.sub(r"\\[a-z]+;", "", str(v)).strip()


def load_rows(name):
    p = os.path.join(ROOT, "public", "data", "standard", name)
    rows = open(p, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
    while rows and not rows[-1].strip():
        rows.pop()
    return [r.split("\t") for r in rows]


def build_eternal_map():
    """英文物品名 → 官方「基础类型」名。

    官方串表里每个基础物品有一条 `StrEternal<英文名去掉空格/连字符>` 的条目，
    值形如 `基础类型：巧工弩`。**很多物品的 namestr/code 在串表里根本没有条目**
    （例如 `8rx` Chu-Ko-Nu），这时就只能靠这条规律取官方中文名。
    """
    official = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"),
                              encoding="utf-8"))["names"]

    eternal = {}
    for k, v in official.items():
        if not k.startswith("StrEternal"):
            continue
        s = clean(v)
        if s.startswith("基础类型："):
            eternal[k[len("StrEternal"):]] = s[len("基础类型："):]

    out = {}
    for t in TABLES:
        rows = load_rows(t)
        hdr = rows[0]
        if "code" not in hdr or "name" not in hdr:
            continue
        ci, ni = hdr.index("code"), hdr.index("name")
        for r in rows[1:]:
            if len(r) <= max(ci, ni) or not r[ci].strip():
                continue
            key = re.sub(r"[^A-Za-z0-9]", "", r[ni].strip())
            if key in eternal:
                out[r[ci].strip().lower()] = eternal[key]
    return out


def build_key_map():
    """code → 游戏实际使用的字符串键（namestr 优先）。"""
    out = {}
    for t in TABLES:
        rows = load_rows(t)
        hdr = rows[0]
        if "code" not in hdr:
            continue
        ci = hdr.index("code")
        ni = hdr.index("namestr") if "namestr" in hdr else None
        for r in rows[1:]:
            if len(r) <= ci or not r[ci]:
                continue
            ns = r[ni].strip() if ni is not None and len(r) > ni else ""
            out[r[ci].lower()] = (ns or r[ci]).lower()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    official = {k: clean(v) for k, v in
                json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"),
                               encoding="utf-8"))["names"].items()}
    _on = OfficialNames()

    def want(code):
        """取名优先级：namestr/code 键 → `StrEternal<英文名>` 基础类型名。"""
        return _on.resolve(code)[0]

    changes = 0
    for fn, top in [("Weapons.json", "name"), ("Armors.json", "name")]:
        p = os.path.join(ROOT, "public", "data", fn)
        data = json.load(open(p, encoding="utf-8"))
        for it in data:
            w = want(it.get("code"))
            got = it.get(top)
            if w and got and w != got:
                print(f"  {fn}: {it.get('code')} 「{got}」→「{w}」")
                changes += 1
                if not args.check:
                    it[top] = w
        if not args.check:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")

    # 暗金里嵌套的 base 名（weaponBase / armorBase / jeweleryBase）
    p = os.path.join(ROOT, "public", "data", "Uniques.json")
    data = json.load(open(p, encoding="utf-8"))
    for u in data:
        for field in ("weaponBase", "armorBase", "jeweleryBase"):
            b = u.get(field)
            if not isinstance(b, dict):
                continue
            w = want(b.get("code"))
            if not w:
                continue
            for sub in ("name", "displayName"):
                got = b.get(sub)
                if got and w != got:
                    print(f"  Uniques.json[{u.get('displayName')}].{field}.{sub}: 「{got}」→「{w}」")
                    changes += 1
                    if not args.check:
                        b[sub] = w
    if not args.check:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    print(f"{'需要修正' if args.check else '已修正'} {changes} 处底材名")
    return 0


if __name__ == "__main__":
    sys.exit(main())
