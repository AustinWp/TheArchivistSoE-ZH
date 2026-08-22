# -*- coding: utf-8 -*-
"""PD2 The Archivist 中文数据翻译引擎。
用法: python3 tools/translate_data.py
将 public/data 下的 JSON 数据与 .txt 数据原地翻译为中文（保留结构）。"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "public", "data")
OUT_DIR = os.path.join("/tmp", "names_out")

sys.path.insert(0, HERE)
from zh_dict import PROP_PHRASES, WORD_DICT, ITEM_TYPE_DICT, TIER_DICT, CLASS_DICT  # noqa

# ---------------------------------------------------------------- helpers

def load_names(name):
    p = os.path.join(OUT_DIR, name)
    if not os.path.exists(p):
        return {}
    return json.load(open(p, encoding="utf-8"))

NAMES = {}
if os.path.isdir(OUT_DIR):
    for f in sorted(os.listdir(OUT_DIR)):
        if f.endswith(".json"):
            NAMES[f[:-5]] = load_names(f)

def name_zh(en):
    """名称查表: 专项词典优先, 其次全局名称池, 最后原样。"""
    if not en:
        return en
    if isinstance(en, (int, float)):
        return en
    s = str(en)
    for key in ["uniques_a", "uniques_b", "weapons", "armors", "runewords", "fatecards",
                "sacreds", "corruptions", "affixes", "monsters_a", "monsters_b", "levels"]:
        d = NAMES.get(key, {})
        if s in d:
            return d[s]
    return s

# ---------------------------------------------------------------- prop translation

# 排序: 短语按长度降序
PHRASES = sorted(PROP_PHRASES, key=lambda kv: len(kv[0]), reverse=True)

ON_ACTION = {
    "Casting": "施法时",
    "Attack": "攻击时",
    "Striking": "击中时",
    "Kill": "击杀时",
    "Death": "死亡时",
    "Level-Up": "升级时",
    "Being Hit": "受击时",
    "Hit": "受击时",
    "Cast": "施法时",
    "Equip": "装备时",
}

def _link_repl(m):
    label, tab, name = m.group(1), m.group(2), m.group(3)
    zh_label = name_zh(label) or label
    zh_name = name_zh(name) or name
    return f"[{zh_label}](app:{tab}:{zh_name})"

_translate_prop = None  # filled below



def _restore_tokens(text, protected):
    def _res(tok_m):
        return "[" + protected[int(tok_m.group(1))] + "]"
    return re.sub(r"\x00(\d+)\x00", _res, text)

def _cast_repl(m, chance, spell_raw, action_raw, protected):
    action = ON_ACTION.get(action_raw.strip(), action_raw.strip())

    chance_plain = _restore_tokens(chance, protected)
    spell_plain = _restore_tokens(spell_raw.strip(), protected)
    mm = re.match(r"^(\d+(?:-\d+)?|\[[^\]]+\])\s+(.+)$", spell_plain)
    if mm:
        spell = f"{mm.group(1)} 级 {_translate_prop(mm.group(2).strip())}"
    else:
        spell = _translate_prop(spell_plain)
    return f"{chance_plain}% 几率在{action}施展 {spell}"

def translate_prop(s):
    if not s:
        return s
    out = str(s)
    is_literal_nl = "\\n" in out
    if is_literal_nl:
        # 按字面 \n 拆行逐行翻译，最后还原
        parts = out.split("\\n")
        return "\\n".join(translate_prop(p) for p in parts)

    # 1) markdown 链接
    out = re.sub(r"\[([^\]]+)\]\(app:([a-z]+):([^)]+)\)", _link_repl, out)

    # 2) 随机占位括号 [a/b] [a-null] [Random X] -> \x00N\x00 (内部 Random 先翻译)
    protected = []

    def _bracket_protect(m):
        inner = m.group(1)
        if re.search(r"Random|random", inner):
            inner = translate_prop(inner)
        protected.append(inner)
        return f"\x00{len(protected) - 1}\x00"

    out = re.sub(r"\[([^\]]+)\]", _bracket_protect, out)

    # 3) 结构化正则
    # 3a) (N Per Character Level) -> （每级 N）
    out = re.sub(r"\(([\d.]+(?:-[\d.]+)?)%?\s*Per Character Level\)",
                 lambda m: f"（每级 {m.group(1)}%）" if m.group(0).count("%") else f"（每级 {m.group(1)}）", out)
    # 3b) Level X-Y Spell (N Charges) -> X-Y 级 法术（N 次充能）
    out = re.sub(r"Level (\d+(?:-\d+)?) ([^(]+?) \((\d+) Charges\)",
                 lambda m: f"{m.group(1)} 级 {translate_prop(_restore_tokens(m.group(2).strip(), protected))}（{m.group(3)} 次充能）", out)
    # 3c) Level X-Y Aura When Equipped -> 装备时赋予 X-Y 级 灵气
    out = re.sub(r"Level (\d+(?:-\d+)?) (.+?) Aura When Equipped",
                 lambda m: f"装备时赋予 {m.group(1)} 级 {translate_prop(_restore_tokens(m.group(2).strip(), protected))} 灵气", out)
    # 3d) X% Chance to Cast Level Y Spell on Z -> X% 几率在Z时施展 Y 级 法术
    #     chance/level 可能为占位 token 或数字
    out = re.sub(r"((?:\x00\d+\x00)|\d+(?:\.\d+)?(?:-[\d.]+)?)% Chance to Cast Level ((?:\x00\d+\x00)|\d+(?:-\d+)?) (.+?) on ([A-Za-z -]+)",
                 lambda m: _cast_repl(m, m.group(1), m.group(2) + " " + m.group(3), m.group(4), protected), out)
    # 3e) Socketed (N) -> 有 N 个凹槽
    out = re.sub(r"Socketed \((\d+)\)", lambda m: f"有 {m.group(1)} 个凹槽", out)
    # 3f) (Limited to +N on class that this skill belongs to) -> （限于该类技能 +N）
    out = re.sub(r"\(Limited to \+(\d+) on class that this skill belongs to\)",
                 lambda m: f"（限于该类技能 +{m.group(1)}）", out)
    # 3g) (N Only) -> （职业专用）
    out = re.sub(r"\(([A-Za-z ]+?) Only\)",
                 lambda m: "（" + CLASS_DICT.get(m.group(1).strip(), translate_prop(_restore_tokens(m.group(1).strip(), protected))) + "专用）", out)
    # 3h) (X Per Energy/Strength/...) -> （每 X 点精力/力量...）
    out = re.sub(r"\(([\d.]+(?:-[\d.]+)?)%?\s*Per ([A-Za-z ]+)\)",
                 lambda m: f"（每 {m.group(1)}%{translate_prop(_restore_tokens(m.group(2).strip(), protected))}）" if m.group(0).count("%") else f"（每 {m.group(1)} 点{translate_prop(_restore_tokens(m.group(2).strip(), protected))}）", out)
    # 3i) Repairs X Durability in Y Seconds -> Y 秒内修复 X 点耐久度
    out = re.sub(r"Repairs (\d+(?:-\d+)?) Durability in (\d+) Seconds",
                 lambda m: f"{m.group(2)} 秒内修复 {m.group(1)} 点耐久度", out)

    # 3j) 占位 bracket 之间的 " to " (如 [1-null] to [2-5])
    out = re.sub(r"(\x00\d+\x00)\s+to\s+(\x00\d+\x00)", r"\1 至 \2", out)

    # 4) 数值区间 " to " 清理 (短语替换之前, 避免 "to" 空短语先删)
    # 4a) -N to -M -> -N 至 -M
    out = re.sub(r"(?<![A-Za-z0-9])(-\d+(?:-\d+)?(?:\.\d+)?%?)\s+to\s+", r"\1 至 ", out)
    # 4b) +N to ... -> +N ...
    out = re.sub(r"(\+\d+(?:-\d+)?(?:\.\d+)?%?)\s+to\s+", r"\1 ", out)
    # 4c) N to ... -> N ...
    out = re.sub(r"(?<![A-Za-z])(\d+(?:-\d+)?(?:\.\d+)?%?)\s+to\s+", r"\1 ", out)

    # 5) 短语词典 (最长优先, 词边界)
    for en, zh in PHRASES:
        if zh == "":
            out = re.sub(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", "", out)
        else:
            out = re.sub(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", zh, out)

    # 6) 还原占位 bracket
    def _restore(m):
        return "[" + protected[int(m.group(1))] + "]"
    out = re.sub(r"\x00(\d+)\x00", _restore, out)

    # 7) bracket 之间 " to " (如 [1-null] to [2-5])
    out = re.sub(r"(\[[^\]]+\])\s+to\s+(\[[^\]]+\])", r"\1 至 \2", out)

    # 8) 词级兜底 (再次保护 bracket)
    protected2 = []

    def _protect2(m):
        protected2.append(m.group(0))
        return f"\x00{len(protected2) - 1}\x00"

    out = re.sub(r"\[[^\]]*\]", _protect2, out)
    out = re.sub(r"[A-Za-z][A-Za-z'\-]*",
                 lambda m: WORD_DICT.get(m.group(0).lower(), WORD_DICT.get(m.group(0), m.group(0))), out)

    def _restore2(m):
        return protected2[int(m.group(1))]
    out = re.sub(r"\x00(\d+)\x00", _restore2, out)

    # 9) 清理空格与标点
    out = re.sub(r"\s+", " ", out)
    # 半角括号内含中文 -> 全角
    out = re.sub(r"\(([^()]*[\u4e00-\u9fff][^()]*)\)", r"（\1）", out)
    out = re.sub(r"\+ （", "+（", out)
    out = re.sub(r" （", "（", out)
    out = re.sub(r"） (\d)", r"）\1", out)
    out = out.replace("） ", "）")
    out = re.sub(r" ([，。：；、）】%）])", r"\1", out)
    out = re.sub(r"([（【]) ", r"\1", out)
    out = re.sub(r" ([,.;:!?%)\]}])", r"\1", out)
    out = re.sub(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])", r"\1\2", out)
    out = out.replace(": ", "：").replace(" ,", "，")
    return out.strip()

_translate_prop = translate_prop

# ---------------------------------------------------------------- type / tier / names

def translate_type(s):
    if not s:
        return s
    v = ITEM_TYPE_DICT.get(str(s))
    return v if v else name_zh(s)

def translate_name(s, kind="name"):
    if not s:
        return s
    v = name_zh(str(s))
    return v if v != str(s) else s

def translate_tier(s):
    if not s:
        return s
    return TIER_DICT.get(str(s), str(s))

# ---------------------------------------------------------------- file processors

def proc_list(fn):
    """通用列表处理器: 翻译常见字段。"""
    p = os.path.join(DATA_DIR, fn)
    if not os.path.exists(p):
        print(f"  skip (missing): {fn}")
        return
    data = json.load(open(p, encoding="utf-8"))
    for it in data:
        for k in ("name", "displayName", "uniqueName", "runewordName", "title"):
            if isinstance(it.get(k), str):
                it[k] = translate_name(it[k])
        if isinstance(it.get("index"), str):
            it["index"] = translate_name(it["index"])
        if isinstance(it.get("itemTier"), str):
            it["itemTier"] = translate_tier(it["itemTier"])
        if isinstance(it.get("displayProperties"), list):
            out_p = []
            for x in it["displayProperties"]:
                if isinstance(x, str):
                    out_p.append(translate_prop(x))
                elif isinstance(x, dict) and isinstance(x.get("displayString"), str):
                    x = dict(x)
                    x["displayString"] = translate_prop(x["displayString"])
                    out_p.append(x)
                else:
                    out_p.append(x)
            it["displayProperties"] = out_p
        if isinstance(it.get("displayItemTypes"), list):
            it["displayItemTypes"] = [translate_type(x) for x in it["displayItemTypes"]]
        if isinstance(it.get("displayItemTypeNames"), list):
            it["displayItemTypeNames"] = [translate_type(x) for x in it["displayItemTypeNames"]]
        if isinstance(it.get("displayExcludedItemTypeNames"), list):
            it["displayExcludedItemTypeNames"] = [translate_type(x) for x in it["displayExcludedItemTypeNames"]]
        if isinstance(it.get("itemTypesDisplayNames"), list):
            it["itemTypesDisplayNames"] = [translate_type(x) for x in it["itemTypesDisplayNames"]]
        if isinstance(it.get("corruptionProperties"), list):
            it["corruptionProperties"] = [translate_prop(x) if isinstance(x, str) else x for x in it["corruptionProperties"]]
        if isinstance(it.get("classDisplayName"), str) and it["classDisplayName"]:
            it["classDisplayName"] = CLASS_DICT.get(it["classDisplayName"], it["classDisplayName"])
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  ok: {fn} ({len(data)} entries)")

def proc_articles(fn):
    p = os.path.join(DATA_DIR, fn)
    if not os.path.exists(p):
        print(f"  skip (missing): {fn}")
        return
    data = json.load(open(p, encoding="utf-8"))
    for it in data:
        if isinstance(it.get("title"), str):
            it["title"] = translate_name(it["title"])
        t = it.get("text")
        if isinstance(t, list):
            it["text"] = [translate_article_line(x) for x in t]
        elif isinstance(t, str):
            it["text"] = translate_article_line(t)
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  ok: {fn} ({len(data)} articles)")

def translate_article_line(s):
    # 文章行: 保持 markdown, 统一 app: 链接的中文一致性
    s = re.sub(r"\[([^\]]+)\]\(app:([a-z]+):([^)]+)\)", _link_repl, s)
    return s

def main():
    print("== JSON 数据翻译 ==")
    # 武器/护甲 (带嵌套结构)
    for fn in ("Weapons.json", "Armors.json"):
        p = os.path.join(DATA_DIR, fn)
        data = json.load(open(p, encoding="utf-8"))
        for it in data:
            for k in ("displayName", "normalItemDisplayName", "exceptionalItemDisplayName", "eliteItemDisplayName"):
                if isinstance(it.get(k), str):
                    it[k] = translate_name(it[k])
            if isinstance(it.get("itemTier"), str):
                it["itemTier"] = translate_tier(it["itemTier"])
            for tk in ("itemType", "secondItemType"):
                t = it.get(tk)
                if isinstance(t, dict) and isinstance(t.get("displayName"), str):
                    t["displayName"] = translate_type(t["displayName"])
            for u in (it.get("uniques") or []):
                if isinstance(u.get("uniqueName"), str):
                    u["uniqueName"] = translate_name(u["uniqueName"])
        json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  ok: {fn} ({len(data)} entries)")

    for fn in ["Uniques.json", "Runewords.json", "Sacreds.json", "Affixes.json", "Corruptions.json"]:
        proc_list(fn)

    # 圣物 propertiesByItemType 键(物品类型)与值(属性)
    p = os.path.join(DATA_DIR, "Sacreds.json")
    data = json.load(open(p, encoding="utf-8"))
    RUNES = ("El","Eld","Tir","Nef","Eth","Ith","Tal","Ral","Ort","Thul","Amn","Sol","Shael","Dol","Hel","Io","Lum","Ko","Fal","Lem","Pul","Um","Mal","Ist","Gul","Vex","Ohm","Lo","Sur","Ber","Jah","Cham","Zod")
    for s in data:
        m = s.get("propertiesByItemType")
        if isinstance(m, dict):
            nm = {}
            for k, v in m.items():
                nm[translate_type(k)] = [translate_prop(x) for x in v]
            s["propertiesByItemType"] = nm
        for k in ("firstInputDisplayName", "secondInputDisplayName", "thirdInputDisplayName",
                  "fourthInputDisplayName", "fifthInputDisplayName", "sixthInputDisplayName"):
            v = s.get(k)
            if isinstance(v, str) and v and v not in RUNES:
                s[k] = translate_name(v)
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  ok: Sacreds.json (propertiesByItemType)")

    # 文章类
    for fn in ["Skills.json", "Cube.json", "Ascendancies.json", "Mapping.json", "Standard.json",
               "Changelog.json", "Damnation.json", "Kiln.json"]:
        proc_articles(fn)

    # 命运卡牌
    p = os.path.join(DATA_DIR, "FateCards.json")
    data = json.load(open(p, encoding="utf-8"))
    for c in data:
        if isinstance(c.get("name"), str):
            c["name"] = translate_name(c["name"])
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  ok: FateCards.json ({len(data)} cards)")

    print("== 掉落计算器 .txt ==")
    for folder in ("standard", "damnation"):
        fd = os.path.join(DATA_DIR, folder)
        if not os.path.isdir(fd):
            continue
        for fn in ("UniqueItems.txt", "SetItems.txt"):
            fp = os.path.join(fd, fn)
            if not os.path.exists(fp):
                continue
            lines = open(fp, encoding="utf-8", errors="replace").read().split("\n")
            hdr = [h.strip() for h in lines[0].split("\t")]
            idx = {h: i for i, h in enumerate(hdr)}
            if "index" not in idx:
                continue
            out = [lines[0]]
            for ln in lines[1:]:
                cols = ln.split("\t")
                if len(cols) > idx["index"] and cols[idx["index"]].strip():
                    cols[idx["index"]] = translate_name(cols[idx["index"]])
                out.append("\t".join(cols))
            open(fp, "w", encoding="utf-8").write("\n".join(out))
            print(f"  ok: {folder}/{fn}")
        # MonStats.txt NameStr 列
        fp = os.path.join(fd, "MonStats.txt")
        if os.path.exists(fp):
            lines = open(fp, encoding="utf-8", errors="replace").read().split("\n")
            hdr = [h.strip() for h in lines[0].split("\t")]
            idx = {h: i for i, h in enumerate(hdr)}
            out = [lines[0]]
            for ln in lines[1:]:
                cols = ln.split("\t")
                if "NameStr" in idx and len(cols) > idx["NameStr"] and cols[idx["NameStr"]].strip():
                    cols[idx["NameStr"]] = translate_name(cols[idx["NameStr"]])
                out.append("\t".join(cols))
            open(fp, "w", encoding="utf-8").write("\n".join(out))
            print(f"  ok: {folder}/MonStats.txt")
        # Levels.txt Name 列
        fp = os.path.join(fd, "Levels.txt")
        if os.path.exists(fp):
            lines = open(fp, encoding="utf-8", errors="replace").read().split("\n")
            hdr = [h.strip() for h in lines[0].split("\t")]
            idx = {h: i for i, h in enumerate(hdr)}
            out = [lines[0]]
            for ln in lines[1:]:
                cols = ln.split("\t")
                if "Name" in idx and len(cols) > idx["Name"] and cols[idx["Name"]].strip():
                    cols[idx["Name"]] = translate_name(cols[idx["Name"]])
                out.append("\t".join(cols))
            open(fp, "w", encoding="utf-8").write("\n".join(out))
            print(f"  ok: {folder}/Levels.txt")

    print("== 完成 ==")

if __name__ == "__main__":
    main()
