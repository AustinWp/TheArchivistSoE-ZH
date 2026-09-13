# -*- coding: utf-8 -*-
"""给正文里的符文名补上编号（如「提尔」→「提尔（3号）」）。

编号取自官方串表 `r01`–`r33`。只处理**页面正文**（散文/表格），
**不处理物品数据文件**（`Uniques/Weapons/Armors/Affixes/...`）—— 那里的「艾斯」「兰姆」
多半是更长名字的一部分（艾斯屈塔的脾气 / 萨卡兰姆），加了编号会把名字写坏。

跳过条件（任一命中就原样返回）：
  - 后面已经是「（N号）」或「空格+数字」（如 Builds 里的「艾尔 1 · 索尔 12」）
  - 后面紧跟汉字（说明它是更长词的一部分，如 艾斯屈塔、萨卡兰姆）
  - 该符文名只有 1 个字（科/罗/瑟/贝，误伤风险太高）

用法:
    python3 tools/annotate_rune_numbers.py [--check]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textwalk import process_file  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TARGETS = [
    "Cube.json", "Kiln.json", "Sacreds.json", "Standard.json", "Damnation.json",
    "Mapping.json", "FateCards.json", "Essences.json", "Ascendancies.json",
    "SeasonS1.json", "Skills.json", "Corruptions.json", "Builds.json",
]

CJK = re.compile(r"[\u4e00-\u9fff]")
# 已经带编号的各种写法都要认：`（3号）` / `(3#)` / `3号` / `11#`
HAS_NUM = re.compile(r"^\s*(?:[（(]\s*\d+\s*(?:号|#)?\s*[）)]|\d+\s*(?:号|#))")

# 「名字（3号）（Tir）」→「名字（Tir，3号）」：社区写法是「名字（英文）」，合并更好看
MERGE_LATIN = re.compile(
    r"([\u4e00-\u9fff]{1,4})（(\d+)号）[（(]\s*([A-Za-z][A-Za-z0-9'’.\- ]*?)\s*[）)]")


def load_runes():
    off = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"),
                         encoding="utf-8"))["names"]
    runes = {}
    for i in range(1, 34):
        v = re.sub(r"\\[a-z]+;", "", off.get(f"r{i:02d}", "")).strip()
        v = re.sub(r"^符文：", "", v)
        if len(v) >= 2:          # 单字符文（科/罗/瑟/贝）跳过，误伤风险高
            runes[v] = i
    return runes


def annotate(text, runes, alt):
    if not text:
        return text, 0

    # 幂等：先把已存在的「（N号）」摘掉再重新标注
    cleaned = re.sub(r"（\d+号）", "", text)

    n = 0

    def repl(m):
        nonlocal n
        name = m.group(0)

        # 注意：必须在 cleaned 上取 tail（下标属于 cleaned）
        tail = cleaned[m.end():m.end() + 10]

        if HAS_NUM.match(tail):
            return name
        if tail and CJK.match(tail[0]):
            return name

        n += 1
        return f"{name}（{runes[name]}号）"

    out = alt.sub(repl, cleaned)
    out = MERGE_LATIN.sub(lambda m: f"{m.group(1)}（{m.group(3)}，{m.group(2)}号）", out)

    return out, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    runes = load_runes()
    alt = re.compile("|".join(re.escape(k) for k in sorted(runes, key=len, reverse=True)))
    print(f"符文 {len(runes)} 个（长度 ≥2，长名优先）")

    total = 0
    for fn in TARGETS:
        p = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(p):
            continue

        # 递归遍历：不假设页面 JSON 的外形（Builds.json 顶层是 dict，散文在 6 层深）
        changed = process_file(p, lambda t: annotate(t, runes, alt)[0], check=args.check,
                               strip_pattern=re.compile(r"（\d+号）"))

        if changed:
            print(f"  {fn}: {changed} 处")
            total += changed

    print(f"{'需处理' if args.check else '已处理'} {total} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
