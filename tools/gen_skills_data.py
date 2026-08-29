# -*- coding: utf-8 -*-
"""技能数据生成器：Skills.txt + Skilldesc.txt -> public/data/SkillsData.json。

命名原则：官方串表优先；官方未提供的（技能名官方仅 2 条）保留英文名。

用法: python3 tools/gen_skills_data.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GE = "/tmp/SOECN/standard-mode/data/global/excel"

CLASS_ZH = {"ama": "亚马逊", "bar": "野蛮人", "pal": "圣骑士", "nec": "死灵法师",
            "sor": "法师", "dru": "德鲁伊", "ass": "刺客"}


def read(path):
    return [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8-sig", errors="replace") if l.strip()]


def main():
    zh = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))["names"]
    skills = read(os.path.join(GE, "Skills.txt"))
    sh = skills[0]
    skd = read(os.path.join(GE, "Skilldesc.txt"))
    dh = skd[0]

    # skilldesc -> 技能名 / 简介（官方串表优先）
    name_by_desc = {}
    brief_by_desc = {}
    for r in skd[1:]:
        if len(r) < dh.index("skilldesc") + 1:
            continue
        key = r[dh.index("skilldesc")]
        nm = r[dh.index("str name")] if "str name" in dh and len(r) > dh.index("str name") else ""
        sn = r[dh.index("str short")] if "str short" in dh and len(r) > dh.index("str short") else ""
        # 名称回退链：官方中名(str name 键) -> 官方中名(key) -> skilldesc 英文键
        name_by_desc[key] = zh.get(nm, "") or zh.get(key, "") or key
        brief_by_desc[key] = zh.get(sn, "")

    rows = []
    for r in skills[1:]:
        if len(r) < 5:
            continue
        sid = r[sh.index("Id")]
        desc_key = r[sh.index("skilldesc")]
        cls = r[sh.index("charclass")] if "charclass" in sh else ""
        req = {
            "level": r[sh.index("reqlevel")] if "reqlevel" in sh else "",
            "str": r[sh.index("reqstr")] if "reqstr" in sh else "",
            "dex": r[sh.index("reqdex")] if "reqdex" in sh else "",
        }
        rows.append({
            "id": sid,
            "name": name_by_desc.get(desc_key, desc_key),
            "brief": brief_by_desc.get(desc_key, ""),
            "className": CLASS_ZH.get(cls, ""),
            "reqLevel": req["level"],
            "reqStr": req["str"],
            "reqDex": req["dex"],
            "skilldesc": desc_key,
        })
    payload = {"meta": {"source": "SOECN Skills.txt/Skilldesc.txt", "count": len(rows)},
               "skills": rows}
    with open(os.path.join(ROOT, "public", "data", "SkillsData.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"OK {len(rows)} 技能 -> public/data/SkillsData.json")
    from collections import Counter
    print(Counter(x["className"] or "通用" for x in rows))


if __name__ == "__main__":
    main()
