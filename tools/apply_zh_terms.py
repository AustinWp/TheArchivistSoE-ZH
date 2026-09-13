# -*- coding: utf-8 -*-
"""官方属性术语全站替换（语义完全一致的明确对应）。

只替换官方串表明确给出、且与本站旧词语义相等的最小集合；
其余保留（避免误伤）。输出替换计数。

用法: python3 tools/apply_zh_terms.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    ("莉莉丝之镜", "莉莉丝的镜子"),                  # llmr（物品名；命运卡描述里官方仍写作「莉莉丝之镜」）
]


# 这些文件是「术语来源」或原始存档，必须与游戏串表逐字一致，禁止被本脚本改写。
SKIP = {
    "official_zh.json",  # 由 tools/extract_official_zh.py 从 soe.txt 生成，是术语唯一标准
    "SiteUpdates.json",  # 更新日志是历史叙述（含「旧词→新词」的说明），改写会破坏语义
}


def main():
    counts = {}
    for pattern in (os.path.join(ROOT, "public", "data", "*.json"),
                    os.path.join(ROOT, "public", "data", "damnation", "*.json"),
                    os.path.join(ROOT, "src", "*.jsx")):
        for f in glob.glob(pattern):
            if os.path.basename(f) in SKIP:
                continue
            s = open(f, encoding="utf-8").read()
            n = 0
            for old, new in PAIRS:
                c = s.count(old)
                if c:
                    n += c
                    s = s.replace(old, new)
            if n:
                open(f, "w", encoding="utf-8").write(s)
                counts[f] = n
    total = sum(counts.values())
    print(f"替换总数: {total}")
    for f, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:5d}  {f}")


if __name__ == "__main__":
    main()
