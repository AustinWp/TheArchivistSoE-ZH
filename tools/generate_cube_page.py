# -*- coding: utf-8 -*-
"""魔方配方页数据生成器（唯一来源：SOECN CubeMain 结构化数据 + 官方串表）。

生成 public/data/Cube.json：{id, title, modes?, text} 结构（Markdown 文本块，
GFM 表格由站点渲染）。modes 字段支持按「标准/炼狱」切换过滤。

用法: python3 tools/generate_cube_page.py
"""
import json
import os
import re
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

RECS = json.load(open(os.path.join(HERE, "generated", "cube_recipes.json"), encoding="utf-8"))["recipes"]
ST, DM = RECS["standard"], RECS["damnation"]
ZH = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
CARDS = json.load(open(os.path.join(ROOT, "public", "data", "FateCards.json"), encoding="utf-8"))

RUNE_ZH = {"El": "艾尔", "Eld": "艾德", "Tir": "提尔", "Nef": "奈夫", "Eth": "艾斯", "Ith": "伊斯",
           "Tal": "塔尔", "Ral": "拉尔", "Ort": "欧特", "Thul": "书尔", "Amn": "安姆", "Sol": "索尔",
           "Shael": "夏尔", "Dol": "多尔", "Hel": "海尔", "Io": "爱欧", "Lum": "卢姆", "Ko": "科",
           "Fal": "法尔", "Lem": "莱姆", "Pul": "普尔", "Um": "乌姆", "Mal": "马尔", "Ist": "伊斯特",
           "Gul": "古尔", "Vex": "瓦克斯", "Ohm": "欧姆", "Lo": "罗", "Sur": "瑟", "Ber": "贝",
           "Jah": "乔", "Cham": "查姆", "Zod": "佐德"}


def zh(code):
    if not code:
        return ""
    return ZH.get(code, "")


def disp(code, fallback=""):
    """优先官方中文名，其次 fallback/英文名（去除 Stack/基类后缀）。"""
    z = zh(code)
    if z:
        return z
    return fallback


def rune_name(name):
    return RUNE_ZH.get(name, name)


def fn(recs, section=None, desc=None):
    return [r for r in recs
            if (section is None or r["section"] == section)
            and (desc is None or desc.lower() in r["description"].lower())]


def md_table(head, rows, escape=True):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for row in rows:
        cells = []
        for c in row:
            c = str(c).replace("\n", " ").replace("|", "\\|")
            cells.append(f"`{c}`" if escape and False else c)
        out.append("| " + " | ".join(cells) + " |")
    return out


RUNE_BY_NUM = {"r%d" % i: RUNE_ZH[name] for i, name in enumerate(
    ["El","Eld","Tir","Nef","Eth","Ith","Tal","Ral","Ort","Thul","Amn","Sol","Shael","Dol","Hel","Io",
     "Lum","Ko","Fal","Lem","Pul","Um","Mal","Ist","Gul","Vex","Ohm","Lo","Sur","Ber","Jah","Cham","Zod"], 1)}


ENG2ZH = {
    "Skeleton Key": "骷髅钥匙", "Eld Rune": "艾德", "Tir Rune": "提尔", "Nef Rune": "奈夫",
    "Eth Rune": "艾斯", "Ith Rune": "伊斯", "Tal Rune": "塔尔", "Ral Rune": "拉尔",
    "Ort Rune": "欧特", "Thul Rune": "书尔", "Amn Rune": "安姆", "Sol Rune": "索尔",
    "Shael Rune": "夏尔", "Dol Rune": "多尔", "Hel Rune": "海尔", "Io Rune": "爱欧",
    "Lum Rune": "卢姆", "Ko Rune": "科", "Fal Rune": "法尔", "Lem Rune": "莱姆",
    "Pul Rune": "普尔", "Um Rune": "乌姆", "Mal Rune": "马尔", "Ist Rune": "伊斯特",
    "Gul Rune": "古尔", "Vex Rune": "瓦克斯", "Ohm Rune": "欧姆", "Lo Rune": "罗",
    "Sur Rune": "瑟", "Ber Rune": "贝", "Jah Rune": "乔", "Cham Rune": "查姆", "Zod Rune": "佐德",
    "Perfect Ruby": "完美红宝石", "Perfect Saphire": "完美蓝宝石", "Perfect Topaz": "完美黄宝石",
    "Perfect Emerald": "完美绿宝石", "Perfect Diamond": "完美钻石", "Perfect Skull": "完美骷髅",
    "Perfect Amethyst": "完美紫宝石",
    "Exalted Orb": "崇高宝珠", "Chisel of Avarice": "制图师凿子·贪婪",
    "Chisel of Procurement": "制图师凿子·采购", "Glyph of Corruption": "腐化铭文",
    "Glyph of Adversaries": "强敌铭文", "Glyph of Nemeses": "宿敌铭文",
    "Catalyst Shard": "催化剂碎片", "Orb of Alchemy": "炼金宝珠", "Chaos Orb": "混沌宝珠",
    "Mythic Orb": "神话宝珠", "Demonic Cube": "恶魔宝盒", "Larzuk's Puzzlebox": "拉苏克谜盒",
    "Orb of Extraction": "提取宝珠", "Divine Orb": "神授宝珠", "Eternal Orb": "永恒宝珠",
    "Worldstone Shard": "世界之石碎片", "Crystallised Cindersoul": "晶化烬魂",
    "Infernal Kiln": "炼狱熔炉", "Eternal Coin": "永恒币", "Jeweller's Prism": "珠宝匠棱镜",
    "Lilith Mirror": "莉莉丝之镜", "Orb of Horizons": "地平线宝珠", "Puzzlepiece": "拉苏克谜盒碎片",
    "Puzzlebox": "拉苏克谜盒", "Larzuks Malus": "拉苏克的铁锤", "Larzuk's Mallus": "拉苏克的铁锤",
    "Blood": "血腥系模组", "Caster": "施法系模组", "Hitpower": "打击系模组", "Safety": "安全系模组",
    "Vampiric": "妖蝠系模组", "Bountiful": "丰饶系模组", "Brilliant": "闪耀系模组",
    "Prismatic": "闪耀系模组",
}

PUZZLE_ZH = {
    "Puzzlebox 2h weapon": "拉苏克谜盒·双手武器", "Puzzlebox Bow": "拉苏克谜盒·弓",
    "Puzzlebox XBow": "拉苏克谜盒·弩", "Puzzlebox 1h weapon": "拉苏克谜盒·单手武器",
    "Puzzlebox 1h throw weapon": "拉苏克谜盒·单手投掷武器", "Puzzlebox helm": "拉苏克谜盒·头盔",
    "Puzzlebox chest": "拉苏克谜盒·胸甲", "Puzzlebox shield": "拉苏克谜盒·盾牌",
    "Puzzlebox quiver": "拉苏克谜盒·箭袋", "Puzzlebox normal boots": "拉苏克谜盒·普通靴子",
    "Puzzlebox exceptional boots": "拉苏克谜盒·扩展靴子", "Puzzlebox elite boots": "拉苏克谜盒·精英靴子",
    "Larzuks Malus + weap = 1 socket": "拉苏克的铁锤·武器",
    "Larzuks Malus + helm = 1 socket": "拉苏克的铁锤·头盔",
    "Larzuks Malus + shield = 1 socket": "拉苏克的铁锤·盾牌",
    "Larzuks Malus + chest = 1 socket": "拉苏克的铁锤·胸甲",
    "Larzuks Malus + quiver = 1 socket": "拉苏克的铁锤·箭袋",
    "Larzuk's Mallus all boots": "拉苏克的铁锤·全部靴子",
}

MOD_ZH = {
    "map-glob-density": "地图密度", "map-play-mag-gold%": "魔法/金币掉落", "map-play-addxp": "额外经验",
    "map-mon-hp%": "怪物生命 %", "chiseled-hidden": "（已凿标记）", "chiseled": "（已凿标记）",
}

AFFIX_ZH = {
    "+1 to All Skills": "+1 所有技能", "+1 Spell Projectiles": "+1 法术投射物",
    "+1 Attack Strikes": "+1 攻击打击", "+10% Curse Resistance": "+10% 诅咒抗性",
    "+[30-40]% Enhanced Damage": "+[30-40]% 增强伤害", "Cannot Be Frozen": "无法冰冻",
    "+2% to ALL Maximum Resistances": "+2% 所有抗性上限", "+1 Attack Projectiles": "+1 攻击投射物",
    "Poison Length Reduced by 50%": "毒素持续时间降低 50%", "Poof to ashes!": "火炬被摧毁（得到地狱火灰烬）",
}


def mat_str(i):
    """input dict -> 材料字符串（`名字 ×数量`）。"""
    if not i:
        return ""
    code = i.get("code") or ""
    name = i.get("name") or code
    if name.endswith(" Stack"):
        name = name[:-6]
    m = re.match(r"^r(\d\d?)[ts]?$", code)
    if m:
        name = RUNE_BY_NUM.get("r" + str(int(m.group(1))), name)
    else:
        name = zh(code) or ENG2ZH.get(name) or name
    if name.endswith(" Stack"):
        name = name[:-6]
    q = i.get("qty")
    return f"**{name}**" + (f"×{q}" if isinstance(q, int) and q > 1 else "")


def fmt_in(row):
    return " + ".join(mat_str(i) for i in row["inputs"])


def fmt_out(row, suffix=""):
    o = row["output"] or {}
    if not o.get("code") or o["code"] in ("useitem", "usetype"):
        return suffix or "（保持物品/见说明）"
    name = o["name"] or o["code"]
    name = zh(o["code"]) or name
    q = o["qty"] if isinstance(o["qty"], int) and o["qty"] > 1 else ""
    s = f"**{name}**" + (f"×{q}" if q else "")
    if o.get("quality") and o["quality"] not in ("", "nor"):
        s += f"（{o['quality']}）"
    return s + suffix


def section_rows(recs, sec):
    """节内按 description 去重返回（供逐条渲染）。"""
    rows = fn(recs, section=sec)
    seen, out = set(), []
    for r in rows:
        d = r["description"]
        if d in seen:
            continue
        seen.add(d)
        out.append(r)
    return out


def main():
    cube = []
    def add(sec_id, title, text_lines, modes=None):
        item = {"id": sec_id, "title": title}
        if modes:
            item["modes"] = modes
        item["text"] = text_lines
        cube.append(item)

    # ------------------------------------------------------------------ 1 about
    add("about", "关于魔方配方", [
        "- 以下配方为流放圣域（Sanctuary of Exile，SOE）专属及较原版发生变化的配方；原版 Project Diablo 2 配方同样有效",
        "- 数据基准：`SOECN` 仓库（SOECN 分支），标准模式 **6,801** 条 / 炼狱模式 **6,918** 条启用配方",
        "- 术语以游戏官方中文为准（官方串表）：例如 `圣化宝珠`、`恶魔宝盒`、`永恒币`、`炼狱熔炉`、`××法珠`、`血腥系模组` 等",
    ])

    # ------------------------------------------------------------------ 2 转化宝珠
    orb_rows = []
    def orb_table(sec, with_quiver, magic_extra):
        rows = []
        for r in section_rows(ST, sec):
            if "rings rolling" in r["description"].lower() or "amulets rolling" in r["description"].lower():
                continue
            rows.append([r["description"], fmt_in(r), fmt_out(r)])
        return rows
    mats = [
        ["神话宝珠 + 普通/超强/魔法/稀有的**普通/扩展**武器或护甲", "同底材暗金物品（结果必为有形）"],
        ["神话宝珠 + 魔法大型护符", "基德的运气（固定物品）"],
        ["神话宝珠 + 魔法/稀有戒指", "随机低阶暗金戒指（拿各的戒指 / 马纳德的治疗 / 乌鸦之霜 / 矮人之星 / 腐肉之风）"],
        ["神话宝珠 + 魔法/稀有项链", "随机低阶暗金项链（诺科兰遗物 / 猫眼 / 玛希姆奥克的橡木古董 / 萨拉森的机会 / 新月 / 艾利屈之眼 / 阿特玛的圣甲虫）"],
        ["神话宝珠 + 普通/超强/魔法/稀有的箭矢或弩矢", "同底材暗金箭矢/弩矢（普通/扩展）"],
    ]
    add("mythic-orb-recipes", "神话宝珠配方", [
        "- 结果物品必定为**有形**，即使输入物品为无形",
        "- 戒指/项链按对应暗金物品稀有度（见`暗金装备`页出现几率）",
        *md_table(["材料", "结果"], mats),
    ])
    add("divine-orb-recipes", "神授宝珠配方", [
        "- 结果物品必定为**有形**，即使输入物品为无形",
        *md_table(["材料", "结果"], [
            ["神授宝珠 + 普通/超强/魔法/稀有的**精英**武器或护甲", "同底材暗金物品"],
            ["神授宝珠 + 5×珠宝碎片", "随机普通暗金珠宝"],
            ["神授宝珠 + 魔法/稀有神话珠宝", "随机暗金神话珠宝"],
            ["神授宝珠 ×1 + 魔法华丽护符", "随机暗金华丽护符（当前正式版 1 枚）"],
            ["神授宝珠 + 普通/超强/魔法/稀有的精英箭矢或弩矢", "同底材暗金箭矢/弩矢"],
            ["神授宝珠 + 魔法/稀有戒指", "随机高阶暗金戒指（乔丹之石 / 布尔凯索的婚戒 / 自然的和平 / 收缩之环 / 鬼火投射者 / 死亡的平衡 / 兄弟会的召唤 / 巴尔的通行证 / 巴尔的喘息 / 巴尔之握）"],
            ["神授宝珠 + 魔法/稀有项链", "随机高阶暗金项链（旭日东升 / 大君之怒 / 马拉的万花筒 / 炽天使之韵 / 金属网格 / 命运的抗争 / 阿斯特拉门蒂斯）"],
        ]),
    ])
    add("exalted-orb-recipes", "崇高宝珠配方", [
        "- 任意阶位底材均可；结果必定为**有形**（即使输入为无形）",
        "- 戒指/项链按对应套装物品稀有度",
        "- 崇高宝珠**不能**用于箭矢/弩矢（神话/神授可以）",
        *md_table(["材料", "结果"], [
            ["崇高宝珠 + 普通/超强/魔法/稀有的武器或护甲", "同底材套装物品"],
            ["崇高宝珠 + 魔法/稀有戒指或项链", "同底材套装戒指/项链"],
        ]),
    ])

    # ------------------------------------------------------------------ 3 符文降级
    low = fn(ST, section="RUNE DOWNGRADING - non-stacked")
    high = fn(ST, section="RUNE DOWNGRADING (High Runes) - non stacked")
    low_dm = fn(DM, section="RUNE DOWNGRADING - non-stacked")
    def dname(x):
        return RUNE_ZH.get(x.capitalize(), x)

    def downgrade_table(rows):
        t = []
        for r in rows:
            m = re.search(r"downgrade (\w+) -> (?:(\d+)(?:x)? )?(\w+)", r["description"])
            if not m:
                continue
            base, out = m.group(1), m.group(3)
            cnt = f"{m.group(2)}×" if m.group(2) else ""
            t.append([dname(base), fmt_in(r), f"{cnt}{dname(out)}"])
        return t
    add("rune-downgrading", "符文降级配方", [
        "- 堆叠与非堆叠的符文均有对应公式",
        "- **炼狱模式**：仅 艾德～普尔 可降级（古尔及以上无降级配方）",
        *md_table(["符文", "附加材料", "结果"], downgrade_table(low)),
        *md_table(["高位符文（标准模式）", "附加材料", "结果"], downgrade_table(high)),
    ])

    # ------------------------------------------------------------------ 4 提取宝珠
    add("unsocketing", "提取宝珠（拆孔）", [
        "- 适用于所有可打孔物品，包括**符文之语**；内容物完整保留",
        "- 物品**不能**处于腐化状态",
        "- 阿穆勒特/腰带/靴子等可打孔部位（含 SOE 新增部位）同样可拆",
        *md_table(["部位", "结果"], [
            ["双手武器 / 弓 / 弩", "取出孔内所有镶嵌物并保留物品"],
            ["单手武器 / 头盔 / 胸甲 / 盾牌", "同上"],
            ["项链 / 腰带 / 靴子 / 箭袋", "同上"],
        ]),
        f"- 提取宝珠掉落：普通 1:20000 全怪 / 噩梦 1:10000 / 地狱 1:4000（游戏内为准）",
    ])

    # ------------------------------------------------------------------ 5 莉莉丝之镜
    add("liliths-mirror", "莉莉丝之镜（复制）", [
        "- 被复制的物品**不能再次复制**；复制品保留孔、镶嵌物与无形状态",
        "- 物品不能腐化",
        *md_table(["材料", "结果"], [
            ["莉莉丝之镜 + 未腐化的暗金武器/护甲/戒指/项链", "精确复制品"],
            ["莉莉丝之镜 + 未腐化的套装武器/护甲/戒指/项链", "精确复制品"],
            ["莉莉丝之镜 + 魔法/稀有/暗金普通珠宝或神话珠宝", "精确复制品"],
            ["莉莉丝之镜 + 魔法/稀有/制作箭矢或弩矢（含扩展/精英）", "精确复制品"],
        ]),
    ])

    # ------------------------------------------------------------------ 6 恶魔宝盒
    add("demonic-cube", "恶魔宝盒（重洗与重掷）", [
        "- 恶魔宝盒可重洗合格暗金/套装的可变数值（不改变底材、孔数与孔中内容）",
        "- 基德的运气 / 地狱火炬 / 毁灭小护符 均可重洗",
        "- 通常不能用于已腐化、已镜像、符文之语及被规则排除的物品",
        *md_table(["材料", "结果"], [
            ["恶魔宝盒 + 暗金/套装物品（基德/地狱火炬/毁灭小护符包含在内）", "重洗可变数值"],
            ["恶魔宝盒 + 暗金神话珠宝（广域毁灭 / 阿卡拉特之怒）", "重洗该神话珠宝（1 枚宝盒）"],
            ["恶魔宝盒 + 血肉熔合（暗金华丽护符）", "重洗该护符"],
            ["普通暗金珠宝 + 永恒币 ×1 + 恶魔宝盒 ×1", "重掷为另一枚普通暗金珠宝（标准模式）"],
            ["暗金神话珠宝 + 永恒币 ×1 + 恶魔宝盒 ×5", "重掷为另一枚暗金神话珠宝（标准模式）"],
            ["暗金华丽护符 + 永恒币 ×1 + 恶魔宝盒 ×5", "重掷为另一枚暗金华丽护符（标准模式）"],
        ]),
        "- **炼狱模式**：以上珠宝/护符「类型重掷」配方不存在（由碎片体系取代，见「炼狱模式专属」）",
    ])

    # ------------------------------------------------------------------ 7 珠宝
    add("jewels", "珠宝配方", [
        *md_table(["材料", "结果"], [
            ["珠宝匠棱镜 + 魔法普通珠宝", "稀有普通珠宝"],
            ["珠宝匠棱镜 + 魔法神话珠宝", "稀有神话珠宝"],
            ["魔法/稀有神话珠宝 + 3×同类完美宝石（**不可用完美骷髅**）", "保持稀有度并重洗属性，保留物品等级"],
            ["钥匙 + 1～10 枚魔法/稀有/暗金神话珠宝", "每枚分解为 5×珠宝碎片（钥匙消耗 1 把；另有可重复使用钥匙变体）"],
            ["1～15×普通珠宝 + 钥匙", "等量珠宝碎片（1～15）"],
            ["未腐化普通/神话/暗金珠宝（依类型）+ 永恒币 + 恶魔宝盒", "重掷类型（见恶魔宝盒节）"],
        ]),
    ])

    # ------------------------------------------------------------------ 8 无瑕珠宝
    add("uncut-pristine-jewel", "未切割无瑕珠宝", [
        *md_table(["材料", "结果"], [
            ["未切割无瑕珠宝 + 50×完美红宝石", "火焰彩虹刻面"],
            ["未切割无瑕珠宝 + 50×完美蓝宝石", "冰冷彩虹刻面"],
            ["未切割无瑕珠宝 + 50×完美黄宝石", "闪电彩虹刻面"],
            ["未切割无瑕珠宝 + 50×完美绿宝石", "毒素彩虹刻面"],
            ["未切割无瑕珠宝 + 50×完美钻石", "魔法彩虹刻面"],
        ]),
    ])

    # ------------------------------------------------------------------ 9 炼金/混沌/永恒
    add("alchemy-chaos-eternal", "炼金宝珠 / 混沌宝珠 / 永恒宝珠", [
        *md_table(["材料", "结果"], [
            ["炼金宝珠 + 未腐化的普通/魔法武器、护甲、戒指、项链或箭袋", "变为稀有物品（无形保留）"],
            ["混沌宝珠 + 未腐化的稀有武器/护甲（含无形）/戒指/项链/珠宝/神话珠宝/箭袋", "重洗稀有属性（无形保留）"],
            ["永恒宝珠 + 未腐化、未圣化、未亵渎的稀有物品", "生成「永恒宝珠印记」"],
            ["永恒宝珠印记 + 完全相同且未腐化的底材物品", "把印记保存的属性恢复到该底材"],
        ]),
        "- 印记只适用于同类底材；被腐化的物品无法使用（对应陷阱行见数据）",
    ])

    # ------------------------------------------------------------------ 10 火炬亵渎
    torch = fn(ST, section="HELLFIRE TORCH DESECRATION - PHASE 2 - OUTCOME")
    torch_names = [AFFIX_ZH.get(r["description"], r["description"]) for r in torch]
    add("hellfire-torch-desecration", "地狱火炬亵渎", [
        "- 亵渎宝珠 + 地狱火炬 → 连续合成两次",
        "- 有 45% 几率火炬被摧毁为地狱火灰烬；其余结果获得以下**等权重**亵渎词缀之一：",
        *md_table(["亵渎词缀"], [[x] for x in torch_names if x != "Poof to ashes!"]),
    ])

    # ------------------------------------------------------------------ 11 灌注物
    inf = OrderedDict()
    for r in section_rows(ST, "CRAFTING INFUSIONS CREATING"):
        if r["description"] in inf:
            continue
        inf[r["description"]] = r
    inf_rows = []
    for name, r in inf.items():
        gem = next((i for i in r["inputs"] if i and "Perfect" in (i["name"] or "")), None)
        rune = next((i for i in r["inputs"] if i and "Rune" in (i["name"] or "")), None)
        inf_rows.append([ENG2ZH.get(name, name), mat_str(rune), mat_str(gem), "珠宝碎片"])
    add("crafting-infusions", "制作灌注物（官方名：×系模组）", [
        "- 支持一次制作 1～10 份：三种材料使用相同数量 N",
        "- 官方术语为「××系模组」（血腥系模组 / 施法系模组 / 安全系模组 / 打击系模组 / 妖蝠系模组 / 丰饶系模组 / 闪耀系模组）",
        *md_table(["灌注物", "符文", "完美宝石", "其他"], inf_rows),
        "- 灌注物与相应底材直接制作（魔法/稀有底材均可，无形保留）",
        "- 已制作物品可再次制作；头环类（头环/宝冠/三重冠/权冠）与箭矢/弩矢同样可用",
    ])

    # ------------------------------------------------------------------ 12 精华
    add("essences", "精华系统", [
        "- 精华 + 对应部位且未腐化的物品 → 重洗为稀有物品，并保证出现该精华专属词缀",
        "- 覆盖部位：胸甲 / 盾牌 / 手套 / 头环 / 野蛮人头盔 / 德鲁伊毛皮 / 头盔 / 靴子 / 腰带 / 箭袋 / 法杖 / 法师法珠 / 魔杖 / 武器（含无形）/ 戒指 / 项链",
        "- 升级：**3× 基础精华 = 1× 高等精华；3× 高等精华 = 1× 完美精华**；支持按 3 的倍数批量（最高一次 48 → 16）",
        *md_table(["腐化精华（数据为准）", "材料", "结果"], [
            ["疯狂精华", "任意完美精华 ×1 + **世界之石碎片** ×1", "精华·疯狂（标准/炼狱均可重洗对应部位稀有物品）"],
            ["歇斯底里精华", "任意完美精华 ×1 + 世界之石碎片 ×1 + 钥匙 ×1", "精华·歇斯底里"],
        ]),
        "- ⚠️ 旧资料曾写「炼狱熔炉 + 完美精华 + 晶化烬魂」——**当前数据为世界之石碎片，且不需要炼狱熔炉**",
    ])

    # ------------------------------------------------------------------ 13 地图
    map_currency = [
        ["赫拉迪姆法珠（已充能：赫拉迪姆法珠(已充能)）", "重洗稀有地图（无需宝石/符文）"],
        ["天使法珠(已充能)", "魔法地图 → 稀有地图（无需材料）"],
        ["奥术法珠(已充能)", "普通地图 → 魔法地图"],
        ["萨卡兰姆法珠(已充能)", "普通地图 → 稀有地图（需珠宝+符文）"],
        ["毁灭法珠", "魔法/稀有地图 → 普通地图"],
        ["制图师法珠", "3×同阶 T1/T2 地图 → 1×更高阶地图"],
        ["强化法珠", "强化（筑防）地图"],
        ["地平线宝珠", "未腐化地图 → 同阶另一张随机地图"],
        ["世界之石碎片", "魔法/稀有地图或地下城 → 腐化"],
        ["英雄旗帜", "地图/地下城 → 添加英雄化奖励与难度"],
        ["催化剂碎片", "地图 → 添加随机地图事件（需先于凿子使用）"],
    ]
    add("maps", "地图与地下城", [
        "**货币（官方名）**：",
        *md_table(["物品", "作用"], map_currency),
        "**品质转换**（普通地图可用珠宝/符文升级）：",
        *md_table(["配方", "结果"], [
            ["赫拉迪姆法珠 + 稀有地图 + 完美宝石 + 符文", "重洗为另一张稀有地图"],
            ["天使法珠 + 魔法地图 + 完美宝石 + 符文", "升为稀有地图"],
            ["萨卡兰姆法珠 + 普通地图 + 珠宝 + 符文", "升为稀有地图"],
            ["奥术法珠 + 普通地图 + 珠宝", "升为魔法地图"],
            ["毁灭法珠 + 魔法/稀有地图", "降为普通地图"],
            ["3×同阶普通地图", "随机同阶地图"],
            ["3×T4 稀有地下城", "随机新 T4 稀有地下城"],
            ["赫拉迪姆法珠(已充能) + 稀有 T4 地下城", "重洗稀有 T4 地下城"],
        ]),
        "**炼狱 T3 地图**同样支持以上货币（普通/已充能两种形态）、英雄旗帜、事件碎片、强化（筑防）、腐化等，规则一致；另可加**职业之耳**产生主题词缀：",
        *md_table(["材料", "效果"], [
            ["任意地图 + 亚马逊/刺客/野蛮人/德鲁伊/死灵法师/圣骑士/法师之耳", "怪群稀有度 +25%、掉落加成 +50%、危险标记（treacherous）+ 职业主题词缀"],
        ]),
    ])

    # ------------------------------------------------------------------ 14 凿子
    chisel = []
    for name, rows in [("制图师凿子", "CARTOGRAPHER'S CHISEL"),
                       ("制图师凿子·贪婪", "CARTOGRAPHER'S CHISEL OF AVARICE"),
                       ("制图师凿子·采购", "CARTOGRAPHER'S CHISEL OF PROCUREMENT")]:
        r = fn(ST, section=rows)
        if not r:
            continue
        mods = {MOD_ZH.get(m["code"], m["code"]): f"{m['min']}~{m['max']}" for m in r[0]["mods"] if m["code"]}
        chisel.append([name, "; ".join(f"{k}={v}" for k, v in mods.items())])
    add("chisels", "制图师凿子", [
        "- 普通/魔法/稀有 T1～T3 地图与稀有 T4 地图均可使用；**每张地图最多 2 把**",
        "- **凿子最后用**：先加催化剂碎片可能使地图无法再用凿子",
        *md_table(["凿子", "效果（数据值）"], chisel),
    ])

    # ------------------------------------------------------------------ 15 铭文与恐惧
    glyphs = [
        ["宿敌铭文", "增加独特怪群（可叠加）"],
        ["强敌铭文", "增加地图首领与额外技能板（不叠加）"],
        ["腐化铭文", "普通怪 25% 几率掉腐化物（可叠加）；首领额外掉落 1～3 件腐化暗金（不叠加）"],
    ]
    fears = [
        ["富饶恐惧", "货币类额外掉落"],
        ["虚灵恐惧", "符文类额外掉落"],
        ["辉煌恐惧", "暗金类额外掉落"],
        ["绝对恐惧", "超级首领材料类额外掉落"],
    ]
    add("glyphs-terrors", "铭文与恐惧宝珠", [
        "- **铭文**只用于稀有 T1～T4 / 炼狱 T3 地图；最大铭文权重等于地图阶位，每枚权重 1",
        "- **恐惧宝珠**每张地图最多 1 枚：",
        *md_table(["铭文", "效果"], glyphs),
        "",
        *md_table(["恐惧宝珠", "效果"], fears),
    ])

    # ------------------------------------------------------------------ 16 仇恨宝珠
    hate = fn(ST, section="T1 MAPS")
    hate_rows = []
    for r in hate:
        code = next((i["code"] for i in r["inputs"] if i and i["code"].startswith("hor")), "")
        hate_rows.append([zh(code) or r["description"], "每图最多 5 枚"])
    add("hatred-orbs", "仇恨宝珠", [
        "- 可用于稀有 T1～T4 / 炼狱 T3 地图，**每张地图最多 5 枚**",
        "- 每枚给怪物 +100% 生命 / +10% 物理伤害 / +10% IAS·FCR / +10% FHR，并增加额外掉落几率（数值以游戏内为准）",
        *md_table(["类型", "限制"], hate_rows),
        "- 炼狱熔炉 + 仇恨宝珠 + 25×晶化烬魂 → 重洗为另一类型（六类型等概率往返）",
    ])

    # ------------------------------------------------------------------ 17 炼狱熔炉
    printer = fn(ST, section="KILN CURRENCY PRINTER")
    pr_rows = []
    for r in fn(ST, section="OUTCOME"):
        if "Hellforged" in r["description"]:
            continue
        m = re.match(r"(.+?) \((\d[.,]?\d*)% chance\)", r["description"])
        if m:
            pr_rows.append([ENG2ZH.get(m.group(1), m.group(1)), m.group(2) + "%"])
    for r in fn(DM, section="OUTCOME"):
        if "Hellforged" in r["description"] or r["description"] in [x[0] for x in pr_rows]:
            continue
        m = re.match(r"(.+?) \((\d[.,]?\d*)% chance\)", r["description"])
        if m:
            pr_rows.append([ENG2ZH.get(m.group(1), m.group(1)), m.group(2) + "%"])
    clust = fn(ST, section="CINDERSOUL CLUSTER - OUTCOME")
    blk = [ [fmt_out(r), "随机"] for r in clust ]
    add("infernal-kiln", "炼狱熔炉", [
        "- 除特别说明外，以下配方都需要把**炼狱熔炉**放入方块",
        *md_table(["配方", "结果"], [
            ["任意 1 颗非堆叠完美宝石 + 10×晶化烬魂", "50×对应完美宝石（堆叠）"],
            ["15×晶化烬魂 + 5×珠宝碎片 + 5×对应完美宝石", "5×对应制作灌注物"],
            ["35×晶化烬魂 + 5×神话宝珠", "加权随机狱铸暗金物品"],
            ["50×晶化烬魂 + 1×神授宝珠 + 拥有狱铸版本的暗金物品", "该物品的狱铸版本"],
            ["50×晶化烬魂 + 任意命运卡", "无变化 / 消失 / 单独复制一张（三者之一，概率以游戏内为准）"],
            ["25×晶化烬魂 + 任意仇恨宝珠", "重洗仇恨宝珠种类（六类型等概率）"],
            ["任意完美精华 + 1×晶化烬魂", "疯狂精华（旧版记录；当前无此配方，见精华节）"],
            ["15×晶化烬魂 + 任一超级首领材料", "重洗为同一首领的另一种材料（90% 换种类 / 10% 原样）"],
            ["25×晶化烬魂", "随机货币（见下表）"],
        ]),
        "**25 烬魂印钞概率**：",
        *md_table(["结果", "权重"], pr_rows),
        "**烬魂簇**（单独连续合成两次）：",
        *md_table(["结果", "说明"], blk),
        "- 四块印记碎片（背教/诅咒/背叛/复生）→ **亵渎印记**（该步不需要炼狱熔炉）",
    ])

    # ------------------------------------------------------------------ 18 升华
    asc = fn(ST, section="ROTATE ASCENDANCY CAIRN")
    asc_names = [r["description"].replace("Ascend to ", "") for r in asc]
    add("ascendancies", "升华系统", [
        "- 一级灵魂石单独合成 → 在 14 条升华路线间循环",
        "- 选定的一级灵魂石 + 升华石冢 → 进入该路线；二/三/四级由石冢晋阶",
        "- 升华石冢 + 洗点徽记 → 重置升华；重置后得到的灵魂石之箱单独合成 → 取回对应一/二/三级灵魂石",
        "- 官方名：力量灵魂石·××（一级）、升华灵魂石（二级）、统御灵魂石（三级）、神性灵魂石（四级）",
        "- 14 条路线：血魔法师 / 时术师 / 勇士 / 圣宗 / 狂战士 / 元素使 / 秘术家 / 守护者 / 巫妖 / 追猎者 / 灵行者 / 锐眼 / 酋长 / 破坏者",
    ])

    # ------------------------------------------------------------------ 19 打孔
    def sock_range(sec):
        r = fn(ST, section=sec)
        return r
    pzz = {}
    for r in ST:
        if r["section"] in ("PUZZLEBOX ADDITIONAL RECIPES",) or r["description"].startswith("Puzzlebox ") and r["section"] not in ("PUZZLEBOX ADDITIONAL RECIPES",):
            pass
    def pzz_rows():
        rows = []
        for r in ST:
            d = r["description"]
            if d.startswith("Puzzlebox") or d.startswith("Larzuks Malus") or "Larzuk's Mallus all boots" == d:
                mod = next((m for m in r["mods"] if m["code"] == "sock"), None)
                if not mod:
                    continue
                rows.append([PUZZLE_ZH.get(d, d), f"{mod['min']} ~ {mod['max']}" if mod["min"] != mod["max"] else mod["min"]])
        return rows
    add("socketing", "打孔 / 重铸", [
        "- 拉苏克谜盒：随机打孔（双手武器/弓/弩 2～6；其余常规装备 1～6，受底材上限约束；摧毁孔内内容物）",
        "- 拉苏克谜盒碎片：较小范围随机打孔（2～4 / 1～2）",
        "- 拉苏克的铁锤：合格未打孔装备固定 +1 孔（SOE 允许靴子）",
        "- 标准模式另有：2×拉苏克谜盒碎片 + 1×永恒币 → 拉苏克谜盒（炼狱模式无此配方）",
        *md_table(["配方", "孔数范围（数据）"], pzz_rows()),
    ])

    # ------------------------------------------------------------------ 20 升级/修理/分解
    add("upgrade-repair", "物品升级 / 修理 / 分解", [
        "**暗金/套装升级**（套装按暗金公式；不再附加原版 +5/+7 需求等级惩罚）：",
        *md_table(["配方", "结果"], [
            ["拉尔 + 索尔 + 完美绿宝石 + 普通级暗金/套装武器", "扩展级"],
            ["塔尔 + 夏尔 + 完美钻石 + 普通级暗金/套装护甲或箭袋", "扩展级"],
            ["卢姆 + 普尔 + 完美绿宝石 + 扩展级暗金/套装武器", "精英级"],
            ["科 + 莱姆 + 完美钻石 + 扩展级暗金/套装护甲或箭袋", "精英级"],
        ]),
        "**稀有/制作物品升级**（无惩罚；制作物品按稀有公式）：",
        *md_table(["配方", "结果"], [
            ["欧特 + 安姆 + 完美蓝宝石 + 普通级稀有/制作武器", "扩展级"],
            ["拉尔 + 书尔 + 完美紫宝石 + 普通级稀有/制作护甲或箭袋", "扩展级"],
            ["法尔 + 乌姆 + 完美蓝宝石 + 扩展级稀有/制作武器", "精英级"],
            ["科 + 普尔 + 完美紫宝石 + 扩展级稀有/制作护甲或箭袋", "精英级"],
        ]),
        "**修理与补充聚气**：",
        *md_table(["配方", "结果"], [
            ["欧特 + 非无形武器", "修理并补充聚气（当前数据另需 1×碎裂宝石；旧资料称无需，以数据为准）"],
            ["拉尔 + 非无形护甲", "修理并补充聚气（当前数据另需 1×裂开的宝石）"],
            ["佐德 + 完美骷髅 + 任意物品", "修理并补充聚气（无形物品也有效）"],
        ]),
        "**分解与宝石批量**：",
        *md_table(["配方", "结果"], [
            ["3×无瑕宝石（可堆叠）+ 钥匙", "完美宝石（支持 3～48 批量）"],
            ["低阶符文 + 钥匙", "符文升级（艾尔～莱姆 3:1；普尔～查姆 2:1）"],
            ["1～15×普通珠宝 + 钥匙", "等量珠宝碎片"],
            ["1～7×地狱火炬 + 钥匙", "等量地狱火灰烬"],
        ]),
    ])

    # ------------------------------------------------------------------ 21 超级首领
    add("uber-mats", "超级首领入口材料", [
        "*以下物品名称为官方中文名：",
        *md_table(["配方", "结果"], [
            ["恐惧之钥 + 憎恨之钥 + 毁灭之钥", "开启群魔殿（3 个传送门）"],
            ["墨菲斯托之脑 + 迪亚波罗之角 + 巴尔之眼", "群魔殿护符"],
            ["原初邪恶之魂 + 黑暗灵魂石 + 纯净恶魔精华", "恐怖异象"],
            ["塔格奥颚骨 + 虚空裂片 + 地狱火灰烬或地狱火炬", "虚空石"],
            ["恶魔徽记 + 罪越护符 + 邪恶血肉", "憎恨之影"],
            ["马道克印记 + 塔力克印记 + 科力克印记", "古代人的遗物"],
            ["古代人钥匙 ×3", "古代人所在地图"],
            ["拉斯玛/卢西恩钥匙各 ×3", "对应地图"],
            ["燃烧的恐惧精华 + 暗黑灵魂石 + 纯净恶魔精华（超级迪亚波罗材料）", "超级迪亚波罗地图"],
        ]),
        "- 虚空石 / 恐怖异象 / 憎恨之影 分别单独合成即可在难度 0/1/2 之间循环",
        "- 以上超级首领材料都可放入炼狱熔炉 + 15×晶化烬魂重洗（90% 换种类）",
        "- 四块印记碎片 → 亵渎印记（无需熔炉）",
    ])

    # ------------------------------------------------------------------ 22a 光颂之瓶
    add("lightsong", "光颂之瓶", [
        "- 光颂之瓶来自命运卡 **财富与权力**（4 张兑换 1 个）",
        "- 把**有形（非无形）武器或护甲**与光颂之瓶合成，物品将变为**无形**：",
        *md_table(["材料", "结果"], [
            ["光颂之瓶 + 未腐化有形武器", "变为无形武器（保留品质与属性）"],
            ["光颂之瓶 + 未腐化有形护甲", "变为无形护甲（保留品质与属性）"],
        ]),
        "- 无形装备无法修理（需要 `佐德 + 完美骷髅` 的例外配方）；请注意选择",
    ])

    # ------------------------------------------------------------------ 22b 白袍
    add("tabula-rasa", "白袍（Tabula Rasa）", [
        "- **白袍 + 骷髅钥匙** → 移除白袍的镶孔",
        "- 官方说明：`未腐化时，可与钥匙一同合成以移除镶孔`（soe.txt `StrTabulaSockets`）",
        "- CubeMain 对应行：`Tabula special removal`；物品需未腐化",
    ])

    # ------------------------------------------------------------------ 22 炼狱差异
    dam_diff = [
        ["神话宝珠 / 神授宝珠", "**移除**；由「机遇宝珠」取代（随机暗金化，可能失败）"],
        ["崇高宝珠", "改为掷点制：普通/超强/魔法/稀有武器或护甲、魔法/稀有戒指项链 → 套装；含失败（消失）分支"],
        ["暗金/套装拆解", "暗金 + 钥匙 → 机遇碎片；套装 + 钥匙 → 崇高碎片（珠宝/神话珠宝/华丽护符需额外 + 永恒币）"],
        ["碎片 → 宝珠", "10/20/30/40/50 碎片 → 1/2/3/4/5 个对应宝珠"],
        ["符文降级", "仅 艾德～普尔（古尔及以上不可降级）"],
        ["拉苏克谜盒碎片×2 + 永恒币 → 拉苏克谜盒", "**无**"],
        ["珠宝/神话珠宝/华丽护符 类型重掷（永恒币+恶魔宝盒）", "**无**"],
        ["命运卡", "少 3 张：萨菲罗斯 / 遗弃之财 / 圣者宝藏（与宝珠移除联动）"],
        ["末日之刃复制品", "幻化之刃 + 5×**机遇宝珠** + 永恒币"],
        ["随机狱铸暗金", "输出池略少（对应神话宝珠条目移除）"],
    ]
    add("damnation-differences", "炼狱模式专属（对照标准模式）", [
        "炼狱模式（毁灭）配方表与标准模式差异巨大，以下条目仅启用 `毁灭` 开关后显示：",
        *md_table(["系统", "炼狱模式实际"], dam_diff),
    ], modes=["damnation"])

    json.dump(cube, open(os.path.join(ROOT, "public", "data", "Cube.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"OK Cube.json {len(cube)} 节")


if __name__ == "__main__":
    main()
