# -*- coding: utf-8 -*-
"""官方术语对照表生成器。

产出三份 Markdown 对照表（工具目录 tools/generated/），供全站术语替换执行：
  1. official_terms.md        —— 重点物品官方中文名（按 code 聚类）
  2. sacred_orbs.md           —— 86 条圣化宝珠：官方名 vs 本站 Sacreds.json
  3. fate_cards.md            —— 63 张命运卡：游戏数量/奖励 vs 本站 FateCards.json

用法: python3 tools/generate_terms_md.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def official_name(code, zh):
    return zh.get(code, "")


def main():
    zh = load(os.path.join(ROOT, "public", "data", "official_zh.json"))["names"]

    # ---------- 1) 重点术语 ----------
    KEY = [
        # 基准货币/宝珠
        ("dvo", "神授宝珠"), ("exo", "崇高宝珠"), ("mfo", "神话宝珠"), ("sror", "圣化宝珠"),
        ("ooal", "炼金宝珠"), ("csor", "混沌宝珠"), ("etor", "永恒宝珠"), ("etri", "永恒宝珠印记"),
        ("oroh", "地平线宝珠"), ("ooe", "提取宝珠"), ("dsno", "亵渎宝珠"), ("ncoi", "永恒币"),
        ("imrn", "恶魔方块→恶魔宝盒"), ("lpp", "拉苏克拼图→拉苏克谜盒碎片"),
        ("lbox", "拉苏克谜盒"), ("lmal", "拉苏克铁锤→拉苏克的铁锤"),
        # 法珠系
        ("upma", "天使宝珠→天使法珠"), ("urma", "天使法珠(已充能)"),
        ("imma", "奥术宝珠→奥术法珠"), ("irma", "奥术法珠(已充能)"),
        ("imra", "萨卡兰姆宝珠→萨卡兰姆法珠"), ("irra", "萨卡兰姆法珠(已充能)"),
        ("rera", "赫拉迪姆宝珠→赫拉迪姆法珠"), ("rrra", "赫拉迪姆法珠(已充能)"),
        ("scou", "毁灭宝珠→毁灭法珠"), ("upmp", "制图师宝珠→制图师法珠"), ("fort", "筑防宝珠→强化法珠"),
        # 物品
        ("hfcr", "晶化烬魂"), ("hfmx", "烬魂簇"), ("hffd", "炼狱窑炉→炼狱熔炉"),
        ("wss", "世界之石碎片"), ("cwss", "暗之世界石碎片"), ("std", "英雄旗帜"),
        ("ccbx", "恰西的制作箱→恰西的工艺箱"), ("gcbx", "基德的箱子→基德的珍奇箱"),
        ("asb1", "升华灵魂石之箱"), ("ubtm", "混沌庇护所护符→群魔殿护符"),
        ("uba", "先祖遗物→古代人的遗物"), ("rtma", "虚空石"), ("luca", "憎恨之影"),
        ("dcma", "恐惧幻象→恐怖异象"),
        # 凿子/铭文/恐惧
        ("ccsl", "制图师凿子"), ("ccsa", "贪婪凿子→制图师凿子·贪婪"),
        ("ccpr", "采办凿子→制图师凿子·采购"), ("ccpl", "制图师凿子·增殖(无配方,占位)"),
        ("scnm", "宿敌雕文→宿敌铭文"), ("scas", "敌手雕文→强敌铭文"), ("sccn", "腐化雕文→腐化铭文"),
        ("troo", "富裕恐惧→富饶恐惧"), ("troe", "虚幻恐惧→虚灵恐惧"),
        ("tror", "璀璨恐惧→辉煌恐惧"), ("troa", "绝对恐惧"),
        # 灌注物（官方为「系模组」）
        ("crfb", "血腥灌注物→血腥系模组"), ("crfc", "施法灌注物→施法系模组"),
        ("crfs", "安全灌注物→安全系模组"), ("crfh", "强力灌注物→打击系模组"),
        ("crfv", "吸血鬼灌注物→妖蝠系模组"), ("crfu", "丰饶灌注物→丰饶系模组"),
        ("crfp", "辉煌灌注物→闪耀系模组"),
        # 系统
        ("reso", "重塑宝珠（官方有描述/无物品无配方，勿写）"),
        ("ooin", "意志宝珠→意念宝珠（官方有描述/无物品无配方，勿写）"),
        ("ipk", "恐惧/憎恨/毁灭之钥(pk1 pk2 pk3)"),
    ]
    lines = ["# 官方重点术语对照（来源：SOECN 官方串表）\n",
             "| 物品/系统 | 官方中文名（唯一标准） | 备注 |", "|---|---|---|"]
    for code, note in KEY:
        name = official_name(code, zh)
        # 若 note 里已含「A→B」格式，保留为备注
        rem = note if ("→" in note and code not in ("hfcr", "hfmx", "hffd")) else ""
        lines.append(f"| {code} | {name or '（官方无）'} | {note if not rem else note.split('→')[0] + ' → ' + note.split('→')[1]} |")
    # 修正：表格第二列用官方名
    lines2 = ["# 官方重点术语对照（来源：SOECN 官方串表）\n",
              "| code | 官方中文名（唯一标准） | 本站/文档现行说法（需替换） |", "|---|---|---|"]
    for code, note in KEY:
        name = official_name(code, zh)
        if "→" in note:
            old, new = note.split("→", 1)
            lines2.append(f"| {code} | {name or '（官方无）'} | {old} |")
        else:
            lines2.append(f"| {code} | {name or '（官方无）'} | （一致） |")
    with open(os.path.join(HERE, "generated", "official_terms.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines2) + "\n")

    # ---------- 2) 圣化宝珠对照 ----------
    sacs = load(os.path.join(ROOT, "public", "data", "Sacreds.json"))
    sr_names = {}
    for i in range(1, 91):
        n = official_name(f"sr{i:02d}", zh)
        if n:
            sr_names[f"sr{i:02d}"] = n.replace("圣化宝珠·", "")
    out = ["# 圣化宝珠：官方名 vs 本站 Sacreds.json\n",
           "| 本站名 | 官方名 | 是否一致 |", "|---|---|---|"]
    diff = 0
    for s in sacs:
        cur = s["displayName"].replace("圣化宝珠", "").replace("的", "").strip()
        # 官方名唯一匹配：按名称含关键字
        official = next((v for k, v in sr_names.items() if v and (v in s["displayName"] or s["displayName"] in v)), None)
        ok = bool(official)
        if not ok:
            diff += 1
        out.append(f"| {s['displayName']} | {official or '见下备注'} | {'✓' if ok else '✗ 需改'} |")
    # 精确做法：直接给官方 86 条名单
    out2 = ["# 圣化宝珠官方名单（86 条，按 sr 编号）\n", "| 编号 | 官方名 |", "|---|---|"]
    for i in sorted(sr_names):
        out2.append(f"| {i} | 圣化宝珠·{sr_names[i]} |")
    with open(os.path.join(HERE, "generated", "sacred_orbs.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n\n---\n\n" + "\n".join(out2) + "\n")

    # ---------- 3) 命运卡对照 ----------
    cards = load(os.path.join(ROOT, "public", "data", "FateCards.json"))
    recs = load(os.path.join(HERE, "generated", "cube_recipes.json"))["recipes"]["standard"]
    tiers = {"TIER 0", "TIER 1", "TIER 2", "TIER 3", "TIER 4", "TIER 5"}
    facts = {}
    for r in recs:
        if r["section"] not in tiers:
            continue
        if not r["description"].strip() or r["description"] in tiers:
            continue
        c = r["inputs"][0]
        facts[c["code"]] = (c["qty"], r["output"]["name"] if r["output"] else "")
    out3 = ["# 命运卡 63 张：游戏事实 vs 本站 FateCards.json\n",
            "| 卡 | 张数(游戏) | 奖励(游戏) | 本站张数 | 状态 |", "|---|---|---|---|---|"]
    for c in sorted(facts, key=lambda x: int(x[2:])):
        qty, reward = facts[c]
        w = next((x for x in cards if x["code"] == c), None)
        wq = w["requiredAmount"] if w else "-"
        status = "✓" if w and wq == qty else ("✗ 缺卡" if not w else f"✗ 张数 {wq}→{qty}")
        out3.append(f"| {c} | {qty} | {reward} | {wq} | {status} |")
    with open(os.path.join(HERE, "generated", "fate_cards.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out3) + "\n")

    print("生成的对照表：")
    for fn in ("official_terms.md", "sacred_orbs.md", "fate_cards.md"):
        print("  tools/generated/" + fn)


if __name__ == "__main__":
    main()
