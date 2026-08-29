# -*- coding: utf-8 -*-
"""配方数据断言校验器：对 SOECN CubeMain 结构化数据执行事实断言。

从 tools/parse_cubemain.py 生成的 data/cube_recipes.json 读取，逐条校验
「文档/页面」声称的关键事实，输出 JSON 报告（tools/generated/verify_report.json）。

用法:
    python3 tools/verify_cube_claims.py
    python3 tools/verify_cube_claims.py --data public/data/cube_recipes.json
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(data_path):
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)["recipes"]


def find(recs, desc_sub, sec_sub=None):
    return [r for r in recs
            if desc_sub.lower() in r["description"].lower()
            and (sec_sub is None or sec_sub.lower() in r["section"].lower())]


def inputs_code(r, code):
    return [i for i in r["inputs"] if i and i["code"] == code]


def inputs_name(r, name):
    return [i for i in r["inputs"] if i and name.lower() in (i["name"] or "").lower()]


class Checker:
    def __init__(self):
        self.results = []

    def check(self, name, ok, detail=""):
        self.results.append({"name": name, "ok": bool(ok), "detail": detail})
        print(("  \u2713 " if ok else "  \u2717 ") + name + (f"  [{detail}]" if detail else ""))

    def group(self, name):
        print(f"\n== {name} ==")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "generated", "cube_recipes.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "tools", "generated", "verify_report.json"))
    args = ap.parse_args()

    data = load(args.data)
    ST, DM = data["standard"], data["damnation"]
    ck = Checker()

    # ---------- 1) 凯恩的智慧 + 毁灭小护符：禁用 ----------
    ck.group("A. 凯恩的智慧")
    ann = [r for r in ST if "annihilus" in r["description"].lower() and "cain" in r["description"].lower()]
    ck.check("标准：无启用中的 `凯恩的智慧+毁灭小护符` 行", len(ann) == 0,
             f"命中 {len(ann)} 行" if ann else "")

    # ---------- 2) 腐化精华：世界之石碎片，非烬魂、无熔炉 ----------
    ck.group("B. 疯狂/歇斯底里精华")
    ins = [r for r in ST if r["description"] == "Perfect Essence of Abrasion to Essence of Insanity"][0]
    ck.check("疯狂精华材料不含炼狱熔炉/晶化烬魂",
             not inputs_code(ins, "hffd") and not inputs_code(ins, "hfcr"))
    ck.check("疯狂精华使用世界之石碎片", bool(inputs_code(ins, "wss")))
    hys = [r for r in ST if r["description"] == "Perfect Essence of Abrasion to Essence of Hysteria"][0]
    ck.check("歇斯底里精华：世界之石碎片 + 钥匙",
             bool(inputs_code(hys, "wss")) and bool(inputs_name(hys, "Skeleton Key")))

    # ---------- 3) 圣者宝藏 ----------
    ck.group("C. 命运卡·圣者宝藏")
    st5 = [r for r in ST if r["section"] == "TIER 5" and "Saint's" in r["description"]]
    ok = len(st5) == 1 and st5[0]["inputs"][0]["qty"] == 2 and st5[0]["output"]["code"] == "exo" and st5[0]["output"]["qty"] == 3
    ck.check("标准：2 张 → 3×崇高宝珠", ok,
             "（注：游戏内卡片说明串 faca62Desc 仍写 3→2×，属串表滞后）" if ok else str([ (r['inputs'][0].get('qty'), r['output']) for r in st5 ]))

    # ---------- 4) 重塑/意念宝珠：物品与配方均不存在 ----------
    ck.group("D. 占位道具（不可写为正式配方）")
    def anywhere(recs, code):
        hit = []
        for r in recs:
            if (r["output"] and r["output"]["code"] == code) or inputs_code(r, code):
                hit.append(r["description"][:40])
        return hit
    ck.check("标准+炼狱：无任何 reso(重塑宝珠) 配方行", not (anywhere(ST, "reso") or anywhere(DM, "reso")))
    ck.check("标准+炼狱：无任何 ooin(意念宝珠) 配方行", not (anywhere(ST, "ooin") or anywhere(DM, "ooin")))
    ck.check("标准+炼狱：无任何 gcbx(基德珍奇箱) 配方行", not (anywhere(ST, "gcbx") or anywhere(DM, "gcbx")))

    # ---------- 5) 烬魂簇 ----------
    ck.group("E. 烬魂簇结果池")
    cl = [r for r in ST if r["section"] == "CINDERSOUL CLUSTER - OUTCOME"]
    q = sorted(set(r["output"]["qty"] for r in cl if r["output"]))
    ck.check("标准：结果池 = 15/25/50/125/250", q == [15, 25, 50, 125, 250], str(q))

    # ---------- 6) 无畏者 ----------
    ck.group("F. 命运卡·无畏者")
    un = [r for r in ST if r["section"] == "TIER 3" and "Undaunted" in r["description"]]
    ck.check("标准：4 张 → 仅暗金腰带（无稀有分支）",
             len(un) == 1 and un[0]["output"]["quality"] == "uni" and un[0]["lvl"] == "87",
             str([(u['output'].get('quality'), u['lvl']) for u in un]))

    # ---------- 7) 魔卡数量 ----------
    ck.group("G. 命运卡总表")
    def cards(recs, tier):
        return {r["inputs"][0]["code"]: r for r in recs
                if r["section"] in tier and r["description"].strip() and r["inputs"] and r["inputs"][0]["code"].startswith("fa")}
    tier_all = {"TIER 0", "TIER 1", "TIER 2", "TIER 3", "TIER 4", "TIER 5"}
    gs, gd = cards(ST, tier_all), cards(DM, tier_all)
    ck.check("标准 63 张 / 炼狱 60 张", len(gs) == 63 and len(gd) == 60, f"{len(gs)}/{len(gd)}")
    ck.check("标准含 fa35 Bowyer's Dream（2 张）", gs.get("fa35") and gs["fa35"]["inputs"][0]["qty"] == 2)
    ck.check("炼狱移除 3 张：fa04/fa57/fa62", set(gs) - set(gd) == {"fa04", "fa57", "fa62"},
             str(sorted(set(gs) - set(gd))))
    ck.check("fa58 斥候 = 4 张", gs["fa58"]["inputs"][0]["qty"] == 4)
    ck.check("fa62 圣者宝藏 = 2 张", gs["fa62"]["inputs"][0]["qty"] == 2)

    # ---------- 8) 神话/神授/崇高宝珠 ----------
    ck.group("H. 转化宝珠")
    dvo_orn = [r for r in ST if "ornate charm" in r["description"] and "Divine Orb" in r["description"]]
    ck.check("华丽护符：1×神授宝珠（非 3×）",
             len(dvo_orn) == 1 and len(inputs_code(dvo_orn[0], "dvo")) == 1 and inputs_code(dvo_orn[0], "dvo")[0]["qty"] == 1)
    ring_out = set(r["description"] for r in ST if r["section"] == "MYTHIC ORB RINGS OUTCOME - PHASE 2" and "x" not in r["description"])
    ck.check("神话宝珠戒指池 = 5 件", len(ring_out) == 5, str(sorted(ring_out)))
    amu_out = set(r["description"] for r in ST if r["section"] == "MYTHIC ORB AMULETS OUTCOME - PHASE 2" and "x" not in r["description"])
    ck.check("神话宝珠项链池 = 7 件", len(amu_out) == 7, str(sorted(amu_out)))
    rod = set(r["description"] for r in ST if r["section"] == "DIVINE ORB RINGS OUTCOME - PHASE 2" and "x" not in r["description"])
    ck.check("神授宝珠戒指池 = 10 件", len(rod) == 10, str(sorted(rod)))
    arma = find(ST, "armageddon")
    ck.check("末日之刃：幻化之刃 + 5×神授宝珠 + 1×永恒币",
             bool(arma) and len(inputs_code(arma[0], "dvo")) == 1 and inputs_code(arma[0], "dvo")[0].get("qty") == 5
             and len(inputs_code(arma[0], "ncoi")) == 1 and inputs_code(arma[0], "ncoi")[0].get("qty") == 1)

    # ---------- 9) 圣化宝珠 ----------
    ck.group("I. 圣化宝珠")
    def sec_count(secname):
        return len([r for r in ST if r["section"] == secname])
    helms = [r for r in ST if r["section"] == "SACRED ORBS - HELMS"]
    ck.check("头盔类 6 条 / 盾 8 / 胸甲 17 / 武器 48 / 投射物 4 / 靴 3",
             sec_count("SACRED ORBS - HELMS") == 6
             and sec_count("SACRED ORBS - SHIELDS") == 8
             and sec_count("SACRED ORBS - CHESTS") == 17
             and sec_count("SACRED ORBS - WEAPONS") == 48
             and sec_count("SACRED ORB - QUIVERS") == 4
             and sec_count("SACRED ORB - BOOTS") == 3)
    rare = [r for r in ST if "Delirium" in r["description"] and "Rare - mods" in r["description"]]
    ck.check("稀有物品同样可圣化（存在 rar 词缀行）", len(rare) == 1)
    ck.check("圣化宝珠创建配方共 86 条", sum(
        len([r for r in ST if r["section"] in s])
        for s in ["SACRED ORBS - HELMS", "SACRED ORB - BOOTS", "SACRED ORBS - CHESTS",
                  "SACRED ORBS - SHIELDS", "SACRED ORBS - WEAPONS", "SACRED ORB - QUIVERS"]) == 86)

    # ---------- 10) 精华 ----------
    ck.group("J. 精华")
    e = [r for r in ST if r["description"] == "Essence of Abrasion -> Greater Essence of Abrasion" and r["inputs"][0]["qty"] == 48]
    ck.check("精华升级 3:1（48 → 16）", len(e) == 1 and e[0]["output"]["qty"] == 16)
    ck.check("无瑕珠宝切割 = 50×完美宝石",
             len(find(ST, "Fire", "UNCUT")) == 1 and inputs_name(find(ST, "Fire", "UNCUT")[0], "Perfect Ruby")[0]["qty"] == 50)

    # ---------- 11) 炼狱模式差异 ----------
    ck.group("K. 炼狱模式差异")
    ck.check("炼狱：无 MYTHIC ORB / DIVINE ORB 节",
             not any(r["section"].startswith("MYTHIC ORB") for r in DM)
             and not any(r["section"].startswith("DIVINE ORB") for r in DM))
    ck.check("炼狱：存在 ORB OF CHANCE（ROLL/POOF/SUCCESS）",
             len([r for r in DM if r["section"] == "ORB OF CHANCE - ROLL"]) == 52
             and len([r for r in DM if r["section"] == "ORB OF CHANCE - OUTCOME - POOF"]) == 52)
    hi = [r for r in DM if "downgrade" in r["description"] and any(k in r["description"] for k in ("gul", "zod", "jah", "ber", "vex", "ohm", "lo", "sur", "cham"))]
    ck.check("炼狱：无 Gul+ 高符文降级", not hi)
    exch = [r for r in DM if inputs_code(r, "ncoi") and any(i["code"] == "lpp" for i in r["inputs"])]
    ck.check("炼狱：无 2×拼图+币 → 谜盒（EXCHANGES）", not exch,
             "（炼狱仍保留拼图/谜盒/铁锤的打孔配方）")
    ck.check("炼狱：无 珠宝/华丽护符 类型重掷（币+5×恶魔宝盒）",
             not any("Reroll type" in r["description"] for r in DM))
    ck.check("炼狱：存在 暗金/套装→碎片 拆解（DAMNATION MODE ONLY CHANGES 30 行）",
             len([r for r in DM if r["section"] == "DAMNATION MODE ONLY CHANGES"]) == 30)
    ck.check("机遇宝珠：炼狱 52 组 ROLL/POOF/SUCCESS，标准模式无此系统",
             len([r for r in DM if r["section"] == "ORB OF CHANCE - ROLL"]) == 52
             and len([r for r in DM if r["section"] == "ORB OF CHANCE - OUTCOME - POOF"]) == 52
             and len([r for r in DM if r["section"] == "ORB OF CHANCE - OUTCOME - SUCCESS"]) == 52
             and not any(r["section"].startswith("ORB OF CHANCE") for r in ST))

    # ---------- 12) 文档已证错误行（应当删除/改写） ----------
    ck.group("L. 文档硬错误复核（改写后应为空/修正）")
    ck.check("无「炼狱熔炉+完美精华+晶化烬魂」格式的疯狂精华配方",
             not any(inputs_code(r, "hffd") and inputs_code(r, "hfcr")
                     for r in ST if "Insanity" in r["description"]))

    # ---------- 13) 新补章节 ----------
    ck.group("M. 光颂之瓶 / 白袍")
    ls = find(ST, "Lightsong")
    ck.check("光颂之瓶：有形武器/护甲 → 无形（mods ethereal）",
             len(ls) >= 2 and any(m["code"] == "ethereal" for r in ls for m in r["mods"]))
    tb = find(ST, "Tabula special removal")
    ck.check("白袍：Tabula Rasa + 骷髅钥匙 移除镶孔（特殊属性）",
             len(tb) == 1 and bool(inputs_name(tb[0], "Skeleton Key")))

    # ---------- 14) 页面内容自检：Cube.json 表格语法 ----------
    ck.group("N. Cube.json 表格自检")
    cube_path = os.path.join(ROOT, "public", "data", "Cube.json")
    cube = json.load(open(cube_path, encoding="utf-8"))
    issues = []
    tables = 0
    for sec in cube:
        lines = [l for l in sec.get("text", []) if l.strip().startswith("|")]
        block = []
        def flush():
            nonlocal tables
            if not block:
                return
            tables += 1
            cells = [l.strip().strip("|").split("|") for l in block]
            widths = [len(c) for c in cells]
            if len(set(widths)) != 1:
                issues.append(f"{sec['id']}: 表格列数不一致 {widths}")
            block.clear()
        for l in lines:
            if l.startswith("|") and l.endswith("|"):
                block.append(l)
            else:
                flush()
        flush()
    ck.check("Cube.json 表格列数一致", not issues, "; ".join(issues[:5]))
    ck.check("Cube.json 含表格", tables >= 20, f"{tables} 个表格")

    report = {"passed": sum(1 for x in ck.results if x["ok"]),
              "failed": sum(1 for x in ck.results if not x["ok"]),
              "results": ck.results}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"\n{report['passed']} 通过 / {report['failed']} 失败 -> {args.out}")
    sys.exit(1 if report["failed"] else 0)


if __name__ == "__main__":
    main()
