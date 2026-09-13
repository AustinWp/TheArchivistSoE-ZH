# -*- coding: utf-8 -*-
"""生成物品贴图映射表 public/data/ItemImages.json。

来源：**本站自带的游戏数据表**（`public/data/standard/{Weapons,Armor,Misc}.txt`）中的
`invfile` / `uniqueinvfile` / `setinvfile` 三列 —— 即游戏客户端里库存贴图（DC6）的文件名。
不依赖任何外部站点；贴图文件本身由 `tools/fetch_item_images.py` 拉取。

输出格式（尽量紧凑）：
    {
      "generatedFrom": "public/data/standard/{Weapons,Armor,Misc}.txt",
      "images": { "hax": {"b": "invhax", "u": "invhaxu", "s": "invhaxu"}, ... }
    }
b = 普通/基础（invfile 或备用 invfile2..6）、u = 暗金（uniqueinvfile）、s = 套装（setinvfile）。

用法: python3 tools/build_item_images.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TABLES = ["Weapons.txt", "Armor.txt", "Misc.txt"]
OUT = os.path.join(ROOT, "public", "data", "ItemImages.json")


def read_rows(path):
    lines = open(path, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    return [l.split("\t") for l in lines]


def cell(row, hdr, name):
    if name not in hdr:
        return ""
    i = hdr.index(name)
    return row[i].strip() if i < len(row) else ""


def main():
    images = {}
    for t in TABLES:
        p = os.path.join(ROOT, "public", "data", "standard", t)
        if not os.path.exists(p):
            print(f"跳过（不存在）: {t}")
            continue
        rows = read_rows(p)
        hdr = rows[0]
        if "code" not in hdr:
            print(f"跳过（无 code 列）: {t}")
            continue
        for row in rows[1:]:
            code = cell(row, hdr, "code").lower()
            if not code:
                continue
            base = cell(row, hdr, "invfile") or cell(row, hdr, "invfile2")
            uni = cell(row, hdr, "uniqueinvfile")
            st = cell(row, hdr, "setinvfile")
            if not (base or uni or st):
                continue
            rec = images.setdefault(code, {})
            if base:
                rec.setdefault("b", base)
            if uni:
                rec.setdefault("u", uni)
            if st:
                rec.setdefault("s", st)

    used = set()
    for rec in images.values():
        used.update(rec.values())

    payload = {
        "generatedFrom": "public/data/standard/{Weapons,Armor,Misc}.txt（invfile / uniqueinvfile / setinvfile）",
        "note": "贴图文件位于 public/item-images/<name>.png；由 tools/fetch_item_images.py 获取。",
        "imageCount": len(used),
        "images": dict(sorted(images.items())),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")

    print(f"OK -> {OUT}")
    print(f"   物品代码 {len(images)} 个 · 唯一贴图 {len(used)} 张")
    with open(os.path.join(HERE, "generated", "item_images.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(used)) + "\n")


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "generated"), exist_ok=True)
    main()
