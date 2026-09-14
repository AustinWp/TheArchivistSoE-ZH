# -*- coding: utf-8 -*-
"""把「暗金名 / 符文之语名 / 词缀名」对齐到**国服客户端串表**（游戏里真正显示的名字）。

为什么需要它
------------
底材（武器/护甲）的名字有唯一取值链路（`official_names.py` → `official_zh.json`），
只要串表全就能被 `refresh_data.py` 自动修正。但这三类**没有生成器**，名字是历史数据：

| 数据集 | key | 关联方式 |
|---|---|---|
| `Uniques.json`（含 `damnation/` 镜像） | 英文暗金名 | 我方 `(code, level)` ↔ 源表 `UniqueItems.txt` 的 `(code, lvl)` |
| `Runewords.json` | `Runeword1`… | 我方 `name` 直接就是键 |
| `Affixes.json` | 源表词缀名 | 我方 `(group, level, 前缀/后缀)` ↔ 源表 `MagicPrefix/Suffix.txt` |

2026-09-14 用国服客户端串表实测：暗金 **320/582**、符文之语 **24/126**、词缀 **1222/1442**
与游戏显示不一致（大量是早期翻译脚本的另一套命名，例如 `Sturdy` 官方「结实之」我方「魁梧的」）。

用法::

    python3 tools/apply_client_zh.py --check    # 只看会改什么
    python3 tools/apply_client_zh.py            # 应用
    python3 tools/apply_client_zh.py --only uniques,runewords

应用后请跑 `python3 tools/refresh_data.py`（会同步 `rebuild_unique_refs` 重建基底↔暗金引用）。
"""
import argparse
import json
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from client_zh import (  # noqa: E402
    client_value,
    load_client_table,
    norm,
    official_name,
    strip_english,
)
from source_repo import excel_dir  # noqa: E402
from uniques_match import cell, match  # noqa: E402
from affixes_match import match as affix_match  # noqa: E402

GEN = os.path.join(HERE, "generated")


def read_excel(fname):
    path = os.path.join(excel_dir(), fname)
    if not os.path.exists(path):
        return [], []
    lines = open(path, encoding="utf-8-sig", errors="replace").read().splitlines()
    return lines[0].split("\t"), [l.split("\t") for l in lines[1:] if l.strip()]


class Changer:
    def __init__(self, check):
        self.check = check
        self.log = []

    def set(self, section, path, field, old, new, ctx=""):
        if old == new:
            return False
        self.log.append({"section": section, "file": os.path.relpath(path, ROOT),
                         "field": field, "old": old, "new": new, "ctx": ctx})
        return True


def fix_uniques(table, ch):
    """暗金名对齐（配对规则见 tools/uniques_match.py，校验与修正共用同一实现）。"""
    for fn in ["Uniques.json", os.path.join("damnation", "Uniques.json")]:
        path = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(path):
            continue
        items = json.load(open(path, encoding="utf-8"))
        assign, guessed, cols = match(table, items)
        changed = 0
        renames = {}
        for i, it in enumerate(items):
            row = assign.get(i)
            if row is None:
                continue
            want = official_name(table, cell(row, cols, "index"))
            if not want:
                continue
            if it.get("displayName") and it["displayName"] != want:
                renames[it["displayName"]] = want
            for field in ("index", "displayName"):
                if ch.set("uniques", path, field, it.get(field), want, cell(row, cols, "index")):
                    it[field] = want
                    changed += 1
        # ⚠️ 不要给「地狱锻铸·X」变体套用基础名的新译：客户端对狱铸变体用的是
        #    **旧基础名 + 前缀**（`Hellforged Spirit Ward` = 「地狱锻铸·灵魂守卫」，
        #    而基础暗金是「魂系结界」）。它们有各自的源表行，正常配对已经是对的（实测改错 5 条）。
        if changed and not ch.check:
            json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"  暗金 {fn}: {changed} 处（配对 {len(assign)}/{len(items)}，按顺序推定 {guessed}）")


def fix_runewords(table, ch):
    path = os.path.join(ROOT, "public", "data", "Runewords.json")
    items = json.load(open(path, encoding="utf-8"))
    changed = 0
    for it in items:
        want = official_name(table, it.get("name"))
        if not want:
            continue
        for field in ("displayName", "runewordName"):
            if ch.set("runewords", path, field, it.get(field), want, it.get("name")):
                it[field] = want
                changed += 1
    if changed and not ch.check:
        json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"  符文之语 Runewords.json: {changed} 处")


def fix_affixes(table, ch):
    """词缀名对齐（配对规则见 tools/affixes_match.py，校验与修正共用）。

    ⚠️ 不要按 `(group, level)` 取第一个候选：同一键下多行、官方名各不相同
    （组101 lvl1：Stout 坚固之 / Blanched 白化之 / Sturdy 结实之 / Miocene 教化之），
    取第一个会把 736 条词缀塞成同一个名字（实测踩过，468 条名字是错的）。
    """
    path = os.path.join(ROOT, "public", "data", "Affixes.json")
    items = json.load(open(path, encoding="utf-8"))
    assign, guessed = affix_match(table, items)
    changed = 0
    for i, it in enumerate(items):
        if i not in assign:
            continue
        row, cols = assign[i]
        want = official_name(table, cell(row, cols, "Name"))
        if not want:
            continue
        if ch.set("affixes", path, "name", it.get("name"), want, f"g{it.get('group')} lvl{it.get('level')}"):
            it["name"] = want
            changed += 1
    if changed and not ch.check:
        json.dump(items, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"  词缀 Affixes.json: {changed} 处（配对 {len(assign)}/{len(items)}，按顺序推定 {guessed}）")


SAFE_MIN_LEN = 4          # 短名（如「酋长」「霜风」）可能是别的东西（升华名/技能名），不自动改


def fix_renamed_prose(ch, log, safe_min=SAFE_MIN_LEN):
    """改名后同步「正文 / 生成器源码」里的旧名。

    两条必须：
    1. **生成器源码也要改** —— `generate_cube_page.py` 等把旧名硬编码在文案里，
       只改生成物的话，下次 `refresh_data.py` 又会把旧名写回来（实测踩过）。
    2. **只改长度 ≥ safe_min 的名字** —— 「酋长」既是暗金 The Chieftain，也是野蛮人升华名；
       「霜风」既是暗金也是技能名。短名一律不动，列进报告人工判断。
    """
    # 改名映射要**持久化**：本工具是幂等的，第二次跑时 log 为空，
    # 若不读历史映射，「累加残留塌缩」就没机会执行（实测 Builds.json 留在脏状态）。
    map_path = os.path.join(GEN, "client_zh_renames.json")
    pairs = {}
    if os.path.exists(map_path):
        try:
            pairs.update({k: v for k, v in json.load(open(map_path, encoding="utf-8")).items()})
        except (OSError, ValueError):
            pass
    for e in log:
        old, new = e["old"], e["new"]
        # ⚠️ **只同步暗金名**：词缀名是通用词（`冰冷`→`通灵`、`炼狱`→`介质`、`强大`→`强壮`），
        #    套到正文会把内容改烂（实测污染了 SkillsData / Skills / Cube 等 30 个文件）。
        #    符文之语同理偏短（`荣誉`→`荣耀`），一律不动正文。
        if e["section"] != "uniques":
            continue
        if old and new and old != new and len(str(old)) >= safe_min:
            pairs[str(old)] = new
    if not pairs:
        return
    os.makedirs(GEN, exist_ok=True)
    json.dump(pairs, open(map_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    targets = [os.path.join(ROOT, "public", "data", f) for f in os.listdir(os.path.join(ROOT, "public", "data"))
               if f.endswith(".json")]
    targets += [os.path.join(ROOT, "public", "data", "damnation", f)
                for f in os.listdir(os.path.join(ROOT, "public", "data", "damnation")) if f.endswith(".json")]
    targets += sorted(__import__("glob").glob(os.path.join(HERE, "*.py")))
    # 这些文件的「名字」由本工具前两步或 rebuild_unique_refs 负责，
    # prose 替换再插一脚会把词缀名等改成暗金旧名（实测误伤 Affixes.json 14 条）。
    skip = {"official_zh.json", "SiteUpdates.json", "Uniques.json",
            "Weapons.json", "Armors.json", "Runewords.json", "Affixes.json"}
    changed = 0
    for path in targets:
        base = os.path.basename(path)
        if base in skip or base == "apply_client_zh.py":
            continue
        text = open(path, encoding="utf-8").read()
        original = text
        # 先塌缩历史累加残留（旧名是新名子串时，早期多遍替换会写成「大大自然的和平」）
        for old, new in pairs.items():
            if old in new:
                expansion = new.replace(old, "", 1)
                if expansion:
                    text = re.sub(r"(?:" + re.escape(expansion) + r"){2,}" + re.escape(old),
                                  expansion + old, text)
        hits = {old: text.count(old) for old in pairs if old in text}
        if not hits and text == original:
            continue
        # ⚠️ 必须**单遍**替换：多遍 `str.replace` 会累加 ——
        #    新名里含旧名时（`自然的和平` ⊂ `大自然的和平`），跑多次就变成
        #    「大大大大大大自然的和平」（实测踩过）。
        if hits:
            pat = re.compile("|".join(re.escape(k) for k in sorted(hits, key=len, reverse=True)))
            text = pat.sub(lambda m: pairs[m.group(0)], text)
        open(path, "w", encoding="utf-8").write(text)
        n = sum(hits.values())
        changed += n
        ch.set("prose", path, "(text)", f"{len(hits)} 个旧名", "已同步", ", ".join(list(hits)[:3]))
        print(f"  正文/源码改名 {os.path.relpath(path, ROOT)}: {n} 处 {list(hits)[:3]}")
    if not changed:
        print("  正文/源码：无旧名残留")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只看差异，不写文件")
    ap.add_argument("--only", default="uniques,runewords,affixes")
    ap.add_argument("--client", default=None)
    ap.add_argument("--no-prose", action="store_true", help="不同步正文/生成器里的旧名")
    args = ap.parse_args()

    table, per_file, _ = load_client_table(args.client)
    print(f"客户端串表: {sum(per_file.values())} 条（{', '.join(per_file)}）")
    only = {x.strip() for x in args.only.split(",") if x.strip()}

    ch = Changer(args.check)
    if "uniques" in only:
        fix_uniques(table, ch)
    if "runewords" in only:
        fix_runewords(table, ch)
    if "affixes" in only:
        fix_affixes(table, ch)

    if not args.check and not args.no_prose:
        fix_renamed_prose(ch, ch.log)

    sections = {}
    for e in ch.log:
        sections.setdefault(e["section"], []).append(e)
    print()
    for sec, entries in sections.items():
        print(f"  {sec}: {len(entries)} 处")
    print(f"  合计 {len(ch.log)} 处" + ("（--check，未写文件）" if args.check else ""))

    os.makedirs(GEN, exist_ok=True)
    out = os.path.join(GEN, "client_zh_applied.json")
    json.dump(ch.log, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  变更清单: {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
