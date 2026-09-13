# -*- coding: utf-8 -*-
"""给页面数据里的物品名加上图标标记。

在文本里，凡是出现「official_zh.json 有官方中文名」且「ItemImages.json 有贴图」的物品名，
就在名字前面插入 `{{icon:CODE}}` 标记；前端 `renderInlineMarkdown` 会把标记渲染成小图标。

安全性：
- 只处理**长度 ≥ 2** 的名字，且**长名优先**（避免「拉尔」被更长的名字截断）；
- 只处理出现在**配方输入/输出**里的物品代码（即「制作配方用到的物品」），避免误伤普通叙述；
- 已经带标记的位置会跳过（幂等，可重复运行）。

用法:
    python3 tools/annotate_item_icons.py            # 应用
    python3 tools/annotate_item_icons.py --check    # 只看会改哪些文件
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 需要处理的页面数据（list，元素含 text: 字符串或字符串数组）
TARGETS = [
    "Cube.json",
    "Kiln.json",
    "Sacreds.json",
    "Standard.json",
    "Damnation.json",
    "Mapping.json",
    "FateCards.json",
    "Essences.json",
    "Ascendancies.json",
]

TOKEN_RE = re.compile(r"\{\{icon:([A-Za-z0-9_]+)\}\}")


def clean(v):
    return re.sub(r"\\[a-z]+;", "", str(v)).strip()


def load_recipe_codes():
    """配方数据里出现过的全部物品代码（输入 + 输出）。"""
    p = os.path.join(HERE, "generated", "cube_recipes.json")
    if not os.path.exists(p):
        return set()
    recs = json.load(open(p, encoding="utf-8"))["recipes"]
    codes = set()
    for mode_recs in recs.values():
        for r in mode_recs:
            for i in r.get("inputs") or []:
                if i and i.get("code"):
                    codes.add(i["code"].lower())
            o = r.get("output")
            if o and o.get("code"):
                codes.add(o["code"].lower())
    return codes


def build_name_map():
    official = {k: clean(v) for k, v in
                json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"),
                               encoding="utf-8"))["names"].items()}
    images = json.load(open(os.path.join(ROOT, "public", "data", "ItemImages.json"),
                            encoding="utf-8"))["images"]
    codes = load_recipe_codes()

    name2code = {}
    for code, zh in official.items():
        c = code.lower()
        if c not in images:
            continue
        if c not in codes:          # 只标注配方里真正用到的物品
            continue
        if not (2 <= len(zh) <= 10):
            continue
        name2code.setdefault(zh, c)

    # 官方串表未收录、但站点在用的名称（基础游戏译名等）
    ALIAS = {
        "普通钥匙": "key",     # Misc.txt `key` = Skeleton Key（消耗品），官方串表未覆盖
    }
    for zh_name, code in ALIAS.items():
        if code in images:
            name2code.setdefault(zh_name, code)

    # 长名优先，避免短名抢先匹配
    ordered = sorted(name2code.items(), key=lambda kv: -len(kv[0]))

    # 若某个名字是另一个物品名的前缀（如「制图师」⊂「制图师凿子·贪婪」），
    # 直接标注会挂错图标 → 这类短名一律跳过
    all_names = [nm for nm, _ in ordered]
    safe = []
    for nm, code in ordered:
        if any(other != nm and other.startswith(nm) for other in all_names):
            continue
        safe.append((nm, code))

    # 补充：更长的那件物品**没有**官方中文名时，上面的前缀规则发现不了，
    # 只能人工列出来（审计第 4 项会持续盯着这类错配）
    SKIP_AMBIGUOUS = {
        "制图师",      # → 制图师凿子 / 制图师法珠
        "拉苏克谜盒",  # → 拉苏克谜盒碎片
    }

    return [(nm, code) for nm, code in safe if nm not in SKIP_AMBIGUOUS]


CODE_SPAN_RE = re.compile(r"(`[^`]*`)")


def annotate(text, pairs):
    """标注一行文本；**跳过反引号代码段**（那里是字面标识符，不渲染图标）。

    先剥掉已有标记再重新标注 —— 这样名称规则变了（比如发现图标挂错了）能自动纠正。
    """
    if not text:
        return text, 0

    text = TOKEN_RE.sub("", text)

    n = 0
    pieces = CODE_SPAN_RE.split(text)

    for pi, piece in enumerate(pieces):
        if piece.startswith("`") and piece.endswith("`"):
            continue

        out = piece
        for name, code in pairs:
            pattern = re.compile(r"(?<!\{icon:%s\})%s" % (re.escape(code), re.escape(name)))

            def repl(m, _code=code, _name=name):
                nonlocal n
                n += 1
                return "{{icon:%s}}%s" % (_code, _name)

            out = pattern.sub(repl, out)

        pieces[pi] = out

    return "".join(pieces), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pairs = build_name_map()
    print(f"可标注的物品名 {len(pairs)} 个（长名优先）")

    total = 0
    for fn in TARGETS:
        p = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(p):
            continue
        data = json.load(open(p, encoding="utf-8"))
        if not isinstance(data, list):
            continue

        changed = 0
        for item in data:
            txt = item.get("text")
            if isinstance(txt, str):
                new, _k = annotate(txt, pairs)
                if new != txt:          # 注意：剥掉失效标记也要回写
                    item["text"] = new
                    changed += 1
            elif isinstance(txt, list):
                for idx, line in enumerate(txt):
                    if not isinstance(line, str):
                        continue
                    new, _k = annotate(line, pairs)
                    if new != line:
                        txt[idx] = new
                        changed += 1

        if changed:
            print(f"  {fn}: 标注 {changed} 处")
            total += changed
            if not args.check:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.write("\n")

    print(f"{'需要标注' if args.check else '已标注'} {total} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
