# -*- coding: utf-8 -*-
"""用**国服客户端中文串表**校验全站翻译（权威来源：游戏里真正加载的文本）。

数据源
------
从国服客户端 `PD2-SOE-战网.zip` 的 `Diablo II/SoE/Data/local/Lng/Chi/` 解出，
放到 `<工作区>/.sources/client-zh/`：

| 文件 | 条数 | 说明 |
|---|---|---|
| `string.tbl` | 5391 | 基础游戏（D2 classic）|
| `expansionstring.tbl` | 2818 | 资料片 |
| `PatchString.tbl` | 4616 | 补丁（**PD2 新增串最多，`mfo`/`exo`/`ncoi` 等都在这**）|

**以 `.tbl` 为准**：它是 UTF-8 的 `key\\0value\\0` 序列（文件头 word@2 = 条数），
是游戏实际加载的文件；同目录的 `.txt` 是旧导出（08-16，比 tbl 的 09-02 旧），
会用做过期值（例：`Blank` 旧 txt 写「空无」，tbl 是「虚无」）→ 仅作 `.tbl` 解析的定位引导与兜底。
查找优先级 **PatchString > ExpansionString > String**（与游戏一致），键名大小写不敏感。

各数据集的 key 约定（均已实测确认，非猜测）
------------------------------------------
| 数据集 | key | 例 |
|---|---|---|
| `official_zh.json` | 就是 key 本身 | `Gust` → 风遁 |
| `Uniques.json` | 英文暗金名，**需经源表 `UniqueItems.txt` 用 (code, lvl) 关联**（582/582 命中）| `Templar's Might` → 圣堂武士的力量 Templar's Might |
| `Weapons/Armors.json` | `code`（= 源表 `namestr` 列）| `hax` → 手斧、`uap` → 军帽 Shako |
| `Runewords.json` | `name`（`Runeword1`…）| `Runeword1` → 古代人的契约 Ancients' Pledge |
| `SkillsData.json` | `id` → `skillname<id>` / `skillan<id>` / `skillsd<id>` / `skillld<id>` | `skillname80` → 复苏骷髅法师 |
| `Affixes.json` | 源表 `MagicPrefix/Suffix.txt` 的 `Name` 列 → 官方词缀名全集 | 集合校验 |

用法::

    python3 tools/verify_client_zh.py [--client <目录>]

输出::

    tools/generated/client_zh_diff.md    # 人读报告
    tools/generated/client_zh_diff.json  # 机器读全量差异（供后续修正）
"""
import argparse
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from source_repo import excel_dir  # noqa: E402

GEN = os.path.join(HERE, "generated")
TBL_FILES = [("string", "String.txt"), ("expansionstring", "expansionstring.txt"),
             ("PatchString", "PatchString.txt")]   # 后者覆盖前者（优先级由低到高）


# ---------------------------------------------------------------- 客户端串表

# 客户端串表加载与归一化统一走 client_zh（唯一入口，别再在这里手写一遍）
from uniques_match import cell, match  # noqa: E402
from client_zh import (  # noqa: E402
    client_candidates,
    client_value,
    load_client_table,
    norm,
    official_name,
)


def client_any_value(table, text):
    """该中文串是否出现在客户端**任意**值里（用于判定「我方名字是否属官方体系」）。"""
    return norm(text) in _VALUE_INDEX.setdefault("v", set())


def _build_value_index(table):
    _VALUE_INDEX["v"] = {norm(v) for (_, v) in table.values() if v}


_VALUE_INDEX = {}


# ---------------------------------------------------------------- 校验框架

class Report:
    def __init__(self):
        self.sections = []

    def add(self, title, note, stats, rows):
        self.sections.append((title, note, stats, rows))

    def to_markdown(self):
        out = ["# 客户端中文串表校验报告", "",
               "> 来源：国服客户端 `Diablo II/SoE/Data/local/Lng/Chi/*.tbl`（UTF-8，游戏实际加载）。",
               "> 本报告是**诊断产物**（`tools/generated/` 不入库）。差异需人工判断三类："
               "**真错** / **我方译法（可接受）** / **版本或来源差异**。", ""]
        for title, note, stats, rows in self.sections:
            out.append(f"## {title}")
            if note:
                out.append(note)
            out.append("")
            out.append("统计：" + " · ".join(f"{k} **{v}**" for k, v in stats.items()))
            out.append("")
            if rows:
                out.append("| # | key | 我们的写法 | 客户端官方 |")
                out.append("|---|---|---|---|")
                for i, (k, ours, theirs) in enumerate(rows[:100], 1):
                    out.append(f"| {i} | `{k}` | {ours} | {theirs} |")
                if len(rows) > 100:
                    out.append(f"| … | 其余 {len(rows) - 100} 条见 JSON | | |")
            out.append("")
        return "\n".join(out)


def _excel(fname):
    path = os.path.join(excel_dir(), fname)
    if not os.path.exists(path):
        return [], []
    lines = open(path, encoding="utf-8-sig", errors="replace").read().splitlines()
    return lines[0].split("\t"), [l.split("\t") for l in lines[1:] if l.strip()]


# ---------------------------------------------------------------- 各项校验

def check_official_zh(table, rep):
    names = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"),
                           encoding="utf-8"))["names"]
    bad, missing = [], []
    for key, ours in names.items():
        ckey, theirs = client_value(table, key)
        if ckey is None:
            missing.append((key, ours, "*(客户端无此 key)*"))
            continue
        if norm(ours) and norm(ours) != norm(theirs):
            bad.append((key, ours, theirs))
    rep.add("一、官方术语表 `official_zh.json`",
            f"模组官方串表（soe.txt 导出，{len(names)} 条）逐条比对客户端。",
            {"checked": len(names), "mismatch": len(bad), "missing": len(missing)}, bad)
    rep.add("一之二、`official_zh.json` 中客户端没有的 key",
            "客户端串表里查不到 → 可能是本站自造 / 已废弃 / 属于服务端专用文案。",
            {"checked": len(names), "mismatch": 0, "missing": len(missing)}, missing)


def check_uniques(table, rep):
    items = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"), encoding="utf-8"))
    assign, guessed, cols = match(table, items)          # 配对与修正共用同一实现
    bad, missing = [], []
    for i, it in enumerate(items):
        row = assign.get(i)
        if row is None:
            missing.append((f"{it.get('code')}/{it.get('level')}", it.get("displayName"), "*(未配到源表行)*"))
            continue
        en_name = cell(row, cols, "index")
        want = official_name(table, en_name)
        if not want:
            missing.append((en_name, it.get("displayName"), "*(客户端无此 key)*"))
            continue
        if norm(it.get("displayName")) != norm(want):
            bad.append((en_name, it.get("displayName"), want))
    rep.add("二、暗金名 `Uniques.json`",
            f"配对走 tools/uniques_match.py（(code,lvl) 分组打分，组内撞车 130 行；"
            f"本次配对 {len(assign)}/{len(items)}，按顺序推定 {guessed} 条）。",
            {"checked": len(items), "mismatch": len(bad), "missing": len(missing)}, bad)


def _namestr_map():
    """code → 游戏实际使用的字符串键（namestr 非空则用它，否则用 code）。

    必须走这条链路：`rar` / `rbe` 这些是**镶孔变体**行，它们的 `code` 键在串表里
    指向「镶孔骸骨链甲」，而游戏显示的是 `namestr`（`uhn` → 骸骨链甲）。
    直接用 `code` 查会把正确的名字报成错的（实测 3 条假阳）。
    """
    out = {}
    for fname in ("Weapons.txt", "Armor.txt", "Misc.txt"):
        hdr, rows = _excel(fname)
        if not hdr or "code" not in hdr:
            continue
        ci = hdr.index("code")
        si = hdr.index("namestr") if "namestr" in hdr else None
        for r in rows:
            if len(r) <= ci or not r[ci].strip():
                continue
            ns = r[si].strip() if si is not None and len(r) > si else ""
            out[r[ci].strip().lower()] = ns or r[ci].strip()
    return out


def check_base_items(table, rep):
    for json_name, label in [("Weapons.json", "武器"), ("Armors.json", "护甲")]:
        items = json.load(open(os.path.join(ROOT, "public", "data", json_name), encoding="utf-8"))
        bad, missing = [], []
        checked = 0
        ns_map = _namestr_map()
        for it in items:
            for code, ours in [(it.get("normalTierCode"), it.get("normalItemDisplayName")),
                               (it.get("exceptionalTierCode"), it.get("exceptionalItemDisplayName")),
                               (it.get("eliteTierCode"), it.get("eliteItemDisplayName"))]:
                if not code:
                    continue
                checked += 1
                ckey, theirs = client_value(table, ns_map.get(str(code).lower(), code))
                if ckey is None:
                    missing.append((code, ours, "*(客户端无此 key)*"))
                    continue
                if norm(theirs) and norm(ours) != norm(theirs):
                    bad.append((code, ours, theirs))
        rep.add(f"三、{label}底材名 `{json_name}`",
                "key = 物品 `code`（源表 `namestr` 列即 code）；普通/扩展/精英三阶分别比对。",
                {"checked": checked, "mismatch": len(bad), "missing": len(missing)}, bad)


def check_runewords(table, rep):
    items = json.load(open(os.path.join(ROOT, "public", "data", "Runewords.json"), encoding="utf-8"))
    bad, missing, alt = [], [], []
    for it in items:
        ckey, theirs = client_value(table, it.get("name"))
        if ckey is None:
            missing.append((it.get("name"), it.get("displayName"), "*(客户端无此 key)*"))
            continue
        if norm(it.get("displayName")) != norm(theirs):
            bad.append((it.get("name"), it.get("displayName"), theirs))
        if it.get("runewordName") and norm(it["runewordName"]) != norm(theirs):
            alt.append((it.get("name"), it["runewordName"], theirs))
    rep.add("四、符文之语名 `Runewords.json`",
            "key = `name`（`Runeword1`…）；`displayName` 是前端渲染字段。",
            {"checked": len(items), "mismatch": len(bad), "missing": len(missing)}, bad)
    rep.add("四之二、`runewordName` 字段（备用名，若前端不渲染可只改 displayName）",
            "同一批条目的另一个中文字段。",
            {"checked": len(items), "mismatch": len(alt), "missing": 0}, alt)


def check_skills(table, rep):
    data = json.load(open(os.path.join(ROOT, "public", "data", "SkillsData.json"), encoding="utf-8"))
    skills = data["skills"] if isinstance(data, dict) else data
    name_bad, brief_bad, missing = [], [], []
    for sk in skills:
        sid = str(sk.get("id", "")).strip()
        cname = client_value(table, f"skillname{sid}")[1] or client_value(table, f"skillan{sid}")[1]
        cbrief = client_value(table, f"skillsd{sid}")[1]
        ours_name, ours_brief = sk.get("name"), sk.get("brief")
        # 技能名：PD2 给部分技能用了任意 key（tornadoshot / frostgalesoe），
        # 所以按「是否属客户端官方命名体系」判定，而不是按 id 硬对。
        if ours_name and any("\u4e00" <= c <= "\u9fff" for c in str(ours_name)):
            if not client_any_value(table, ours_name):
                name_bad.append((f"{sid}", ours_name, "*(客户端所有串里都找不到此名)*"))
        if cbrief and norm(ours_brief) and norm(ours_brief) != norm(cbrief):
            # 错位探测：客户端 id±1 能对上 → 标为「疑似错位」而不是措辞差异
            off = None
            for delta in (-1, 1, -2, 2):
                alt = client_value(table, f"skillsd{int(sid) + delta}")[1] if sid.isdigit() else None
                if alt and norm(alt) == norm(ours_brief):
                    off = delta
                    break
            if off is not None:
                name_bad.append((f"{sid} {ours_name}", ours_brief, f"*疑似错位：客户端 skillsd{int(sid)+off} = {alt}*"))
            else:
                brief_bad.append((f"{sid} {ours_name}", ours_brief, cbrief))
    rep.add("五、技能名（`skillname<id>` / `skillan<id>`）",
            "仅比对**我方为中文**的条目（我方存英文内部名的属另一类问题）。",
            {"checked": len(skills), "mismatch": len(name_bad), "missing": len(missing)}, name_bad)
    rep.add("五之二、技能短说明（`skillsd<id>`）",
            "技能面板上那句一句话说明；我方 brief 多来自 soe.txt，可能与客户端有版本差。",
            {"checked": len(skills), "mismatch": len(brief_bad), "missing": 0}, brief_bad)


def check_affixes(table, rep):
    items = json.load(open(os.path.join(ROOT, "public", "data", "Affixes.json"), encoding="utf-8"))
    # 逐条 join：我方 (group, level, 前缀/后缀) → 源表行 → Name 键 → 客户端官方名
    idx = {}
    for fname, is_suffix in [("MagicPrefix.txt", False), ("MagicSuffix.txt", True)]:
        hdr, rows = _excel(fname)
        if not hdr or "Name" not in hdr:
            continue
        gi, li, ni = hdr.index("group"), hdr.index("level"), hdr.index("Name")
        for r in rows:
            if len(r) > max(gi, li, ni) and r[ni]:
                idx.setdefault((r[gi], r[li], is_suffix), []).append(r[ni])
    bad, unmatched = [], []
    for it in items:
        keys = idx.get((str(it.get("group")), str(it.get("level")), bool(it.get("suffix"))))
        if not keys:
            unmatched.append((f"g{it.get('group')} lvl{it.get('level')}", it.get("name"), "*(源表未匹配)*"))
            continue
        _, theirs = client_value(table, keys[0])
        want = official_name(table, keys[0])
        if not want:
            # 源表里有未使用的占位行（`Name=Dummy`），客户端值就是英文 "Dummy"，
            # 不属于「翻译错」——单独归类，不混进差异数。
            unmatched.append((keys[0], it.get("name"), "*(占位行 / 客户端无中文名)*"))
            continue
        if norm(it.get("name")) != norm(want):
            bad.append((keys[0], it.get("name"), theirs))
    rep.add("六、词缀名 `Affixes.json`",
            "逐条 join：我方 (group, level, 前缀/后缀) → 源表 `MagicPrefix/Suffix.txt` 行 → `Name` 键 → 客户端官方名。",
            {"checked": len(items), "mismatch": len(bad), "missing": len(unmatched)}, bad)


# ---------------------------------------------------------------- 主流程

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default=None, help="客户端 Chi 串表目录（默认自动解析）")
    args = ap.parse_args()

    directory = args.client
    if not directory:
        for c in client_candidates():
            if os.path.isdir(c) and (os.path.exists(os.path.join(c, "PatchString.tbl"))
                                     or os.path.exists(os.path.join(c, "PatchString.txt"))):
                directory = c
                break
    if not directory:
        print("找不到客户端串表目录。把 client-zh 放到 <工作区>/.sources/client-zh，"
              "或用 --client / $CLIENT_ZH 指定。")
        return 1

    table, per_file, source = load_client_table(directory)
    _build_value_index(table)
    print(f"客户端串表: {directory}")
    for k, v in per_file.items():
        print(f"  {k:18} {v:>6} 条  （来源 {source.get(k)}）")
    print(f"  合并后（小写 key）: {len(table)} 条\n")

    rep = Report()
    check_official_zh(table, rep)
    check_uniques(table, rep)
    check_base_items(table, rep)
    check_runewords(table, rep)
    check_skills(table, rep)
    check_affixes(table, rep)

    os.makedirs(GEN, exist_ok=True)
    md_path = os.path.join(GEN, "client_zh_diff.md")
    json_path = os.path.join(GEN, "client_zh_diff.json")
    open(md_path, "w", encoding="utf-8").write(rep.to_markdown())
    json.dump({"client_dir": directory,
               "sections": [{"title": t, "stats": s,
                             "rows": [{"key": k, "ours": o, "client": c} for k, o, c in rows]}
                            for t, _, s, rows in rep.sections]},
              open(json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"{'章节':<46}{'已查':>7}{'不一致':>8}{'客户端无':>9}")
    for title, _, stats, _ in rep.sections:
        print(f"{title:<46}{stats.get('checked',0):>7}{stats.get('mismatch',0):>8}{stats.get('missing',0):>9}")
    print(f"\n报告：{os.path.relpath(md_path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
