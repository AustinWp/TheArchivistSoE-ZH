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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textwalk import process_file  # noqa: E402

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
    "Ascendancies.json",
    "SeasonS1.json",
    "Skills.json",
    "Corruptions.json",
    "Builds.json",
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


# 官方串表里符文类条目带「符文：」前缀（如 `r02 = 符文：艾德`），正文里只写名字 → 建表时去掉
CATEGORY_PREFIX_RE = re.compile(r"^(符文|宝石|护符|戒指|项链|武器|护甲|珠宝)：")


def build_eternal_names():
    """官方「基础类型」名 → code（取值链路见 official_names.py）。"""
    sys.path.insert(0, HERE)
    from official_names import OfficialNames

    on = OfficialNames()
    out = {}
    for code in on.rows:
        zh, src = on.resolve(code)
        if zh and src == "StrEternal":
            out[code] = zh
    return out


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
        # 说明：不再限制「配方里出现过的 code」——页面正文（赛季页 / 构筑攻略等）
        # 也会提到宝珠、钥匙、精华等物品；误伤由「长名优先 + 前缀排除 + 审计第 4 项」兜住
        zh = CATEGORY_PREFIX_RE.sub("", zh)
        if not (2 <= len(zh) <= 10):
            continue
        name2code.setdefault(zh, c)

    # 官方串表里以「基础类型：」形式收录的底材名（按英文名归纳）
    for code, zh in build_eternal_names().items():
        if code in images and 2 <= len(zh) <= 10:
            name2code.setdefault(zh, code)

    # 官方串表未收录、但站点在用的名称（基础游戏译名等）
    ALIAS = {
        "普通钥匙": "key",     # Misc.txt `key` = Skeleton Key（消耗品），官方串表未覆盖
    }
    for zh_name, code in ALIAS.items():
        if code in images:
            name2code.setdefault(zh_name, code)

    # 长名优先，避免短名抢先匹配
    ordered = sorted(name2code.items(), key=lambda kv: -len(kv[0]))

    # 更长的那件物品**没有**官方中文名时，长名优先也救不了（只会把短名标上），
    # 这类只能人工排除（审计第 4 项会持续盯着这类错配）
    SKIP_AMBIGUOUS = {
        "制图师",      # → 制图师凿子 / 制图师法珠
        "拉苏克谜盒",  # → 拉苏克谜盒碎片
    }

    return [(nm, code) for nm, code in ordered if nm not in SKIP_AMBIGUOUS]


CODE_SPAN_RE = re.compile(r"(`[^`]*`)")


# 由 main() 在每轮开始前按 pairs 构建（pairs 已按长名优先排序）
_NAME_ALT = None
_NAME2CODE = {}


def build_matcher(pairs):
    """把「名字 → 代码」表编译成一个长名优先的交替正则。"""
    global _NAME_ALT, _NAME2CODE
    _NAME2CODE = dict(pairs)
    _NAME_ALT = re.compile("|".join(re.escape(nm) for nm, _ in pairs))


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

        # 一次性用「全部名字」的交替正则替换：alternation 取最左最长匹配，
        # 这样「伊司（6号）」能命中「伊司」，「制图师凿子·贪婪」不会被「制图师」抢走
        def repl(m, _map=_NAME2CODE):
            nonlocal n
            name = m.group(0)
            code = _map.get(name)
            if not code:
                return name
            n += 1
            return "{{icon:%s}}%s" % (code, name)

        pieces[pi] = _NAME_ALT.sub(repl, piece)

    return "".join(pieces), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    pairs = build_name_map()
    build_matcher(pairs)
    print(f"可标注的物品名 {len(pairs)} 个（长名优先）")

    total = 0
    for fn in TARGETS:
        p = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(p):
            continue
        # 递归遍历（只改散文，不碰 name / id / code 这类标识字段）
        changed = process_file(p, lambda t: annotate(t, pairs)[0], check=args.check,
                               strip_pattern=TOKEN_RE)

        if changed:
            print(f"  {fn}: 标注 {changed} 处")
            total += changed

    print(f"{'需要标注' if args.check else '已标注'} {total} 处")
    return 0


if __name__ == "__main__":
    sys.exit(main())
