# -*- coding: utf-8 -*-
"""PD2 SOE 官方中文字符串表提取器。

从游戏模组自带字符串表（UTF-16 导出的 soe.txt，键值用 Tab 分隔）中提取
「键 -> 官方中文名」映射，清洗颜色控制码（\\red; \\gold; …），输出为 JSON，
作为全站术语唯一标准。

用法:
    python3 tools/extract_official_zh.py            # 默认读取 ~/Downloads/soe.txt
    python3 tools/extract_official_zh.py --src xxx.txt
    python3 tools/extract_official_zh.py --out public/data/official_zh.json
"""
import argparse
import json
import os
import re

COLOR_RE = re.compile(r"\\[a-z]+;")

def clean(text: str) -> str:
    """去掉颜色控制码与首尾空白，保留内容（含嵌套颜色码）。"""
    t = COLOR_RE.sub("", text)
    return t.strip()

def extract(src: str) -> dict:
    """返回 {key: clean_text}，仅包含含中文字符的非空条目。"""
    data = open(src, "rb").read()
    try:
        text = data.decode("utf-16")
    except UnicodeDecodeError:
        text = data.decode("utf-8-sig", errors="replace")
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        key, val = line.split("\t", 1)
        key = key.strip()
        if not key or not val.strip():
            continue
        # 仅保留含中文的条目（避免把纯英文键值当成术语）
        if not any("\u4e00" <= ch <= "\u9fff" for ch in val):
            continue
        out[key] = clean(val)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.expanduser("~/Downloads/soe.txt"))
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "public", "data", "official_zh.json"))
    args = ap.parse_args()

    names = extract(args.src)
    meta = {
        "source": "SOECN 官方中文字符串表（soe.txt，UTF-16 导出）",
        "description": "键 -> 官方中文名。颜色控制码已清除；仅含含中文的条目。",
        "count": len(names),
    }
    payload = {"meta": meta, "names": names}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"OK  {len(names)} 条 -> {args.out}")

if __name__ == "__main__":
    main()
