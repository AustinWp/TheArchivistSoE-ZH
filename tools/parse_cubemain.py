# -*- coding: utf-8 -*-
"""PD2 SOE CubeMain.txt 解析器（代码库标准版）。

把两个模式的 CubeMain.txt 解析为结构化配方数据（仅 enabled=1 行），
解码输入/输出物品（code -> 英文名，来自 Misc/Weapons/Armor/Gems/ItemTypes），
保留来源行号与 mods 摘要，输出 JSON 供页面/校验脚本使用。

用法:
    python3 tools/parse_cubemain.py --src /tmp/SOECN --out public/data/cube_recipes.json
"""
import argparse
import json
import os


def read(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return [l.rstrip("\n") for l in f]


def load_names(excel_dir):
    """code -> (英文名, 表名) 跨表合并；ItemTypes 的 Code -> ItemType 名。"""
    m = {}
    for t in ["Misc.txt", "Weapons.txt", "Armor.txt", "Gems.txt", "Runes.txt", "Sets.txt"]:
        p = os.path.join(excel_dir, t)
        if not os.path.exists(p):
            continue
        lines = read(p)
        if not lines:
            continue
        hdr = lines[0].split("\t")
        ci = next((i for i, c in enumerate(hdr) if c in ("code", "Code")), None)
        if ci is None:
            continue
        ni = next((i for i, c in enumerate(hdr) if c in ("name", "Name", "index", "FileName", "runename")), None)
        if ni is None:
            continue
        for l in lines[2:]:
            if not l.strip():
                continue
            r = l.split("\t")
            if len(r) <= max(ci, ni) or not r[ci]:
                continue
            if r[ci] not in m:
                m[r[ci]] = (r[ni], t)
    types = {}
    itp = os.path.join(excel_dir, "ItemTypes.txt")
    if os.path.exists(itp):
        lines = read(itp)
        hdr = lines[0].split("\t")
        try:
            ci = hdr.index("Code"); ni = hdr.index("ItemType")
            for l in lines[2:]:
                r = l.split("\t")
                if len(r) > max(ci, ni) and r[ci] and r[ci] not in types:
                    types[r[ci]] = r[ni]
        except ValueError:
            pass
    return m, types


def parse_file(path, names, types):
    lines = read(path)
    hdr = lines[0].split("\t")

    def f(r, name):
        i = hdr.index(name) if name in hdr else -1
        return r[i] if 0 <= i < len(r) else ""

    recs = []
    cur = "HEAD"
    for ln, l in enumerate(lines[2:], start=3):
        if not l.strip():
            continue
        r = l.split("\t")
        if len(r) < 10:
            continue
        if f(r, "enabled") == "":
            if f(r, "description").strip():
                cur = f(r, "description").strip()
            continue
        if f(r, "enabled") != "1":
            continue
        inputs = []
        for i in range(1, 8):
            raw = f(r, f"input {i}")
            if not raw:
                continue
            inputs.append(_decode(raw, names, types))
        recs.append({
            "section": cur,
            "description": f(r, "description"),
            "numinputs": f(r, "numinputs"),
            "inputs": inputs,
            "output": _decode(f(r, "output"), names, types),
            "lvl": f(r, "lvl"), "plvl": f(r, "plvl"), "ilvl": f(r, "ilvl"),
            "op": f(r, "op"), "param": f(r, "param"), "value": f(r, "value"),
            "line": ln,
            "mods": [
                {"code": f(r, f"mod {i}"), "param": f(r, f"mod {i} param"),
                 "min": f(r, f"mod {i} min"), "max": f(r, f"mod {i} max")}
                for i in range(1, 6)
                if f(r, f"mod {i}")
            ],
        })
    return recs


def _code_name(code, names, types):
    n = names.get(code) or types.get(code)
    if isinstance(n, (tuple, list)):
        return n[0]
    return n or code


def _decode(tok, names, types):
    if not tok:
        return None
    t = tok.strip().replace('"', "")
    parts = t.split(",")
    code = parts[0]
    quality = ""
    qty = 0
    for p in parts[1:]:
        if p.startswith("qty="):
            try:
                qty = int(p[4:])
            except ValueError:
                qty = p[4:]
        else:
            quality = p
    return {
        "code": code,
        "name": _code_name(code, names, types),
        "quality": quality,
        "qty": qty,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/tmp/SOECN",
                    help="SOECN 仓库根目录（含 standard-mode/damnation-mode）")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "generated", "cube_recipes.json"))
    args = ap.parse_args()

    std = os.path.join(args.src, "standard-mode", "data", "global", "excel")
    names, types = load_names(std)
    out = {}
    for mode, base in [("standard", std),
                       ("damnation", os.path.join(args.src, "damnation-mode", "data", "global", "excel"))]:
        recs = parse_file(os.path.join(base, "CubeMain.txt"), names, types)
        out[mode] = recs
        print(f"{mode}: {len(recs)} 条启用配方")

    payload = {
        "meta": {
            "source": "SOECN CubeMain.txt (standard-mode + damnation-mode)",
            "description": "结构化配方数据，仅 enabled=1 行；input/output 的 code 可与 official_zh.json 对照取官方中文名。",
        },
        "recipes": out,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"OK -> {args.out}")


if __name__ == "__main__":
    main()
