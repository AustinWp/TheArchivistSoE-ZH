# -*- coding: utf-8 -*-
"""暗金属性中文串解析器（规则表版）。

把 Uniques.json / 通用中文属性串解析为 (property, min, max)。
规则优先级：特殊短语（顺序敏感）> 标准「数值+短语」。未命中返回 None。

用法（模块）：
    from unique_prop_parser import parse_props
    parse_props(["14% 几率在命中时施展 31 级 伤害加深", "无法破坏"])
"""
import re

# (regex, property, 数值取值方式)
#  v=数值1, w=数值2, s=技能名；min/max 顺序 = 游戏 UniqueItems 列顺序（min/max 或 min=几率 max=等级）
RULES = [
    # 技能触发类（min=几率%, max=技能等级）
    (re.compile(r"^(?P<v>\d+(?:\.\d+)?)%? 几率在命中时施展 (?P<l>\d+) 级"), "hit-skill"),
    (re.compile(r"^(?P<v>\d+(?:\.\d+)?)%? 几率在受击时施展 (?P<l>\d+) 级"), "gethit-skill"),
    (re.compile(r"^(?P<v>\d+(?:\.\d+)?)%? 几率在施法时施展 (?P<l>\d+) 级"), "cast-skill"),
    (re.compile(r"^(?P<v>\d+(?:\.\d+)?)%? 几率施展等级 (?P<l>\d+) .*?时 你死亡"), "death-skill"),
    (re.compile(r"^装备时赋予 ?(?P<v>\d+)-(?P<w>\d+) ?级 ?[\u4e00-\u9fff]+灵气"), "aura"),
    (re.compile(r"^等级 (?P<v>\d+) [\u4e00-\u9fff]+装备时"), "equipped-skill"),
    (re.compile(r"^几率命中使怪物逃跑 (?P<v>\d+(?:\.\d+)?)"), "howl"),
    (re.compile(r"^射出魔法箭矢"), "magicarrow"),
    (re.compile(r"^\+?(?P<v>\d+) 所有技能$"), "allskills"),
    (re.compile(r"^\+?(?P<v>\d+)（随机职业）技能等级$"), "randclassskill2"),
    (re.compile(r"^\+?(?P<v>\d+)-(?P<w>\d+)?%?(?:武器)? 攻击次数$"), "attack-strikes"),
    # 元素伤害/抗性
    (re.compile(r"^增加 (?P<v>\d+)-(?P<w>\d+) 火焰伤害"), "dmg-fire"),
    (re.compile(r"^增加 (?P<v>\d+)-(?P<w>\d+) 冰[霜冷]伤害"), "dmg-cold"),
    (re.compile(r"^增加 (?P<v>\d+)-(?P<w>\d+) 闪电伤害"), "dmg-ltng"),
    (re.compile(r"^增加 (?P<v>\d+)-(?P<w>\d+) 毒素伤害"), "dmg-pois"),
    (re.compile(r"^增加 (?P<v>\d+)-(?P<w>\d+) 魔法伤害"), "dmg-mag"),
    (re.compile(r"^增加 (?P<v>\d+) 至 (?P<w>\d+) 至敌人(火焰|冰冷|闪电|毒素|魔法)抗性"), None),  # 特殊：pierce 系，见下
    (re.compile(r"^(?P<v>\d+)-(?P<w>\d+)%?\s?至敌人(火焰|冰冷|闪电|毒素|魔法)抗性"), None),
    (re.compile(r"^(?P<v>\d+) 至 (?P<w>\d+) 至敌人(火焰|冰冷|闪电|毒素|魔法)抗性"), None),
    # 抗性与属性
    (re.compile(r"^(?:所有抗性|全抗) [+%]?(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%?$"), "res-all"),
    (re.compile(r"^(?:冰冷抗性|冰抗) [+%]?(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%?$"), "res-cold"),
    (re.compile(r"^(?:火焰抗性|火抗) [+%]?(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%?$"), "res-fire"),
    (re.compile(r"^(?:闪电抗性|电抗) [+%]?(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%?$"), "res-ltng"),
    (re.compile(r"^(?:毒素抗性|毒抗) [+%]?(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%?$"), "res-pois"),
    (re.compile(r"^(?:魔法抗性|魔抗) [+%]?(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%?$"), "res-mag"),
    (re.compile(r"^[+%]?(?P<v>-?\d+)(?:-| 至 )(?P<w>-?\d+)?%? (?:生命|体力)$"), "vit"),
    # 击杀/恢复
    (re.compile(r"^(?P<v>\d+)-(?P<w>\d+)?%? 每次命中偷取生命$"), "lifesteal"),
    (re.compile(r"^(?P<v>\d+)-(?P<w>\d+)?%? 每次命中偷取法力$"), "manasteal"),
    (re.compile(r"^每击杀一个敌人后获得(?P<v>\d+)-(?P<w>\d+) 生命$"), "heal-kill"),
    (re.compile(r"^每击杀一个敌人后获得(?P<v>\d+)-(?P<w>\d+) 法力$"), "mana-kill"),
    (re.compile(r"^消耗生命 (?P<v>\d+)"), None),  # regen 负值，见下
    # 等级决定
    (re.compile(r"^（每级 (?P<v>[\d.]+)%?）(?P<w>[-\d]+)-(?P<x>\d+)?[^（]*（以角色等级决定）$"), None),
    # 凹槽
    (re.compile(r"^有 (?P<v>\d+) 个凹槽$"), "sock"),
    (re.compile(r"^(?P<v>\d+) 孔$"), "sock"),
    (re.compile(r"^凹槽 \((?:\d+-)?(?P<v>\d+)-(?P<w>\d+)\)$"), "sock"),
    # 特殊标记
    (re.compile(r"^无法破坏$"), "indestruct"),
    (re.compile(r"^忽略目标防御$"), "ignore-ac"),
    (re.compile(r"^增加格挡几率(?:[+%]?(?P<v>\d+))?$"), "block"),
    (re.compile(r"^受到的物理伤害减免 (?P<v>\d+)%"), "red-dmg%"),
    (re.compile(r"^受到的魔法伤害(?:\s?降低)? (?P<v>\d+)%"), "red-mag"),
    (re.compile(r"^(?P<v>\d+)% 更[好高]的机会获得魔法物品$"), "mag%"),
    (re.compile(r"^攻击次数 ?[+%]?(?P<v>\d+)$"), "attack-strikes"),
    (re.compile(r"^\+?(?P<v>\d+) 法术投射物$"), "spell-projectiles"),
]

# 标准「数值+短语」（来自词缀结构化数据反推）
STANDARD = None  # 延迟加载


def _load_standard():
    global STANDARD
    import json, os
    if STANDARD is not None:
        return STANDARD
    here = os.path.dirname(os.path.abspath(__file__))
    tpl = json.load(open(os.path.join(here, "generated", "prop_zh_templates.json"), encoding="utf-8"))
    STANDARD = []
    for code, phrase in tpl.items():
        if not phrase or phrase in ("pois-min", "pois-max", "pois-len"):
            continue
        # 短语需为纯中文/常见词，防止误匹配
        if not re.fullmatch(r"[\u4e00-\u9fff（）%+\-/.·\s]+", phrase):
            continue
        STANDARD.append((code, phrase))
    return STANDARD


def parse_prop(s):
    s = s.strip()
    for rx, code in RULES:
        m = rx.match(s)
        if not m:
            continue
        g = m.groupdict()
        if "v" not in g:
            # 无数值：直接返回固定值
            return (code, 0, 0)
        v = int(float(g["v"])) if g.get("v") else 0
        if code is None:
            continue  # 特殊规则：交给下方 fallback 处理
        w = int(float(g["w"])) if g.get("w") else (int(float(g["l"])) if g.get("l") else v)
        return (code, v, w)
    # 特殊：pierce / regen / 标准短语
    m = re.match(r"^(?P<v>-?\d+)(?: 至 (?P<w>-?\d+))?%? 至敌人(火焰|冰冷|闪电|毒素|魔法)抗性$", s)
    if m:
        code = {"火焰": "pierce-fire", "冰冷": "pierce-cold", "闪电": "pierce-ltng",
                "毒素": "pierce-pois", "魔法": "res-mag"}[m.group(3)]
        v = int(m.group(1)); w = int(m.group(2)) if m.group(2) else v
        return (code, v, w)
    m = re.match(r"^需求 [+%]?(?P<v>-?\d+)%?$", s)
    if m:
        return ("ease", int(m.group(1)), int(m.group(1)))
    m = re.match(r"^消耗生命 (?P<v>\d+)$", s)
    if m:
        return ("regen", -int(m.group(1)), -int(m.group(1)))
    m = re.match(r"^（每级 (?P<v>[\d.]+)%?）(?P<a>[+-]?\d+)-(?P<b>\d+)[^（]*（以角色等级决定）$", s)
    if m:
        return (f"perlv:{m.group('v')}", int(m.group("a")), int(m.group("b")))
    # 标准短语：+N 短语 / N% 短语 / N-N 短语 / 短语 前后数值
    for code, phrase in _load_standard():
        p = re.escape(phrase if phrase != "增强伤害" else "增强伤害")
        for rx in (
            re.compile(r"^[+\-]?(?P<v>\d+)(?:-(?P<w>\d+))?%?\s*" + p + r"$"),
            re.compile(r"^" + p + r"\s*[+\-]?(?P<v>\d+)(?:-(?P<w>\d+))?%?$"),
        ):
            m = rx.match(s)
            if m:
                v = int(m.group("v")); w = int(m.group("w")) if m.group("w") else v
                return (code, v, w)
    return None


def parse_props(lines):
    out = []
    bad = []
    for s in lines:
        r = parse_prop(s)
        if r is None:
            bad.append(s)
        else:
            out.append(r)
    return out, bad


if __name__ == "__main__":
    tests = [
        "14% 几率在命中时施展 31 级 伤害加深", "无法破坏", "+30-60 体力", "装备时赋予 4-6 级活力灵气",
        "增加 1-74 闪电伤害", "-3 至 -5% 至敌人闪电抗性", "有 6 个凹槽", "100% 几率施展等级 47 连锁闪电时 你死亡",
        "20% 加成攻击命中值", "5-9% 每次命中偷取生命", "50% 耐力消耗", "100% 几率在命中时施展 31 级 伤害加深",
        "（每级 0.5%）0-49 致命攻击（以角色等级决定）", "等级 16 精力盾牌装备时", "8% 几率在受击时施展 12 级 霜之新星",
    ]
    for t in tests:
        print(f"{t[:40]:42s} -> {parse_prop(t)}")
