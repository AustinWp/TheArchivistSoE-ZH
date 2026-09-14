# -*- coding: utf-8 -*-
"""官方属性术语全站替换（语义完全一致的明确对应）。

只替换官方串表明确给出、且与本站旧词语义相等的最小集合；
其余保留（避免误伤）。输出替换计数。

用法: python3 tools/apply_zh_terms.py
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK = re.compile(r"[\u4e00-\u9fff]")

# (旧词, 官方式新词)
PAIRS = [
    ("增强伤害", "强化伤害"),                      # strModEnhancedDamage
    ("致命攻击", "致命一击"),                      # ModStr5q
    ("命中致盲目标", "击中使目标失明"),            # ModStr6d
    ("冰冷伤害", "冰霜伤害"),                      # strModColdDamage
    ("更好的机会获得魔法物品", "寻获魔法物品几率提高"),  # ModStr1x
    ("魔法伤害受到的减少", "魔法伤害降低"),          # ModStr2t_PD2
    ("物理伤害受到的减少", "物理伤害降低"),          # ModStr2u_PD2
    ("受到的物理伤害减免", "物理伤害降低"),          # ModStrMapPlayerPDR
    ("受到的伤害转换为法力", "受到伤害转换为法力"),  # ModStr3w_PD2
    # 旧符文名 → 官方（RUNE_ZH 表已对齐，这里兜住正文里的手写残留）
    ("夏尔", "沙伊"), ("书尔", "图尔"), ("特尔", "提尔"), ("萨德", "佐德"),
    ("那夫", "奈夫"), ("爱斯", "艾斯"), ("爱欧", "艾欧"),
    ("伊斯特", "伊司特"), ("瓦克斯", "伐克斯"),
    ("莉莉丝之镜", "莉莉丝的镜子"),
    # 页面正文里出现过的旧译 / 错字（审计第 1 项会盯住）
    ("诸葛弩", "巧工弩"), ("巧攻弩", "巧工弩"),
    ("地狱锻造", "地狱锻铸"),
    ("中护身符", "大型护身符"),
    ("回城之书", "城镇传送之书"),
    ("冰封之球", "马拉之药"),                  # llmr（物品名；命运卡描述里官方仍写作「莉莉丝之镜」）
]


# 这些文件是「术语来源」或原始存档，必须与游戏串表逐字一致，禁止被本脚本改写。
SKIP = {
    "official_zh.json",  # 由 tools/extract_official_zh.py 从 soe.txt 生成，是术语唯一标准
    "SiteUpdates.json",  # 更新日志是历史叙述（含「旧词→新词」的说明），改写会破坏语义
}


def protected_terms():
    """需要保护的「更长官方术语」集合：官方串表 + 站点各类名字字段。

    ⚠️ 背景：裸串替换会把「**爱斯**特龙之铁的保护区」里的「爱斯」当旧符文名吃掉
    （2026-09-14 实测，`("爱斯","艾斯")` 把官方暗金名改错）。命中位置若落在更长术语内就跳过。
    """
    out = set()
    try:
        names = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"),
                               encoding="utf-8"))["names"]
        out.update(str(v) for v in names.values() if v and CJK.search(str(v)))
    except OSError:
        pass
    for rel, fields in [("Uniques.json", ("index", "displayName")),
                        ("damnation/Uniques.json", ("index", "displayName")),
                        ("Weapons.json", ("displayName", "normalItemDisplayName",
                                          "exceptionalItemDisplayName", "eliteItemDisplayName")),
                        ("Armors.json", ("displayName", "normalItemDisplayName",
                                         "exceptionalItemDisplayName", "eliteItemDisplayName")),
                        ("Runewords.json", ("displayName", "runewordName")),
                        ("Affixes.json", ("name",))]:
        p = os.path.join(ROOT, "public", "data", rel)
        if not os.path.exists(p):
            continue
        for it in json.load(open(p, encoding="utf-8")):
            for f in fields:
                v = it.get(f)
                if v and CJK.search(str(v)):
                    out.add(str(v).strip())
    return out


def replace_guarded(text, old, new, protected):
    """替换 ``old``→``new``，跳过落在更长官方术语内部的匹配。返回 (文本, 替换数, 跳过数)。"""
    out, i, done, skipped = [], 0, 0, 0
    while True:
        j = text.find(old, i)
        if j < 0:
            out.append(text[i:])
            break
        a, b = j, j + len(old)
        while a > 0 and CJK.match(text[a - 1]):        # 向两侧扩到最长中文串
            a -= 1
        while b < len(text) and CJK.match(text[b]):
            b += 1
        run = text[a:b]
        if run != old and run in protected:
            skipped += 1
        else:
            out.append(text[i:j])
            out.append(new)
            done += 1
        i = j + len(old)
    return "".join(out), done, skipped


def main():
    protected = protected_terms()
    counts, skips = {}, {}
    for pattern in (os.path.join(ROOT, "public", "data", "*.json"),
                    os.path.join(ROOT, "public", "data", "damnation", "*.json"),
                    os.path.join(ROOT, "src", "*.jsx")):
        for f in glob.glob(pattern):
            if os.path.basename(f) in SKIP:
                continue
            s = open(f, encoding="utf-8").read()
            n = k = 0
            for old, new in PAIRS:
                if old not in s:
                    continue
                s, d, sk = replace_guarded(s, old, new, protected)
                n += d
                k += sk
            if n:
                open(f, "w", encoding="utf-8").write(s)
                counts[f] = n
            if k:
                skips[f] = k
    print(f"替换总数: {sum(counts.values())}")
    for f, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:5d}  {f}")
    if skips:
        print(f"跳过（落在更长官方术语内）: {sum(skips.values())}")
        for f, n in sorted(skips.items(), key=lambda x: -x[1]):
            print(f"  {n:5d}  {f}")


if __name__ == "__main__":
    main()
