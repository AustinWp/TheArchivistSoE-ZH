# -*- coding: utf-8 -*-
"""「国服SOL第一赛季」页面数据生成器。

唯一来源：docs/reference/s1-patch-notes.md（赛季更新说明原文，照录腾讯文档）。
本脚本把该 Markdown 切分为页面区块，并追加两节由**代码核对**得出的内容：
  - 国服不支持 / 不适用的功能与公式
  - 与国服代码（SOECN）的交叉验证结论
输出：public/data/SeasonS1.json（{id,title,text} 列表，供 StaticDataPanel 渲染）。

用法: python3 tools/generate_season_page.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "docs", "reference", "s1-patch-notes.md")
OUT = os.path.join(ROOT, "public", "data", "SeasonS1.json")
VERIFY = os.path.join(ROOT, "docs", "reference", "s1-verification.md")

# 页面区块标题映射（Markdown 二级标题 → 页面标题）
TITLE_MAP = {
    "S1 更新内容（正式服 9/11 上线）": None,  # 按三级标题（职业）再切分
    "荣誉光环系统": "荣誉光环系统（S1 启用）",
    "升华调整": "升华调整 / 叠层上限",
    "客户端修复": "客户端修复",
    "技能说明": "技能说明（中文本地化）",
    "机制说明（非本次平衡改动）": None,  # 按三级标题再切分
}


def split_sections(md):
    """把正文按 `## ` / `### ` 切成 (标题, 正文行) 列表。

    只有 TITLE_MAP 中值为 None 的二级标题（如「S1 更新内容」「机制说明」）
    才继续按三级标题切分，其余二级标题整体保留。
    """
    lines = md.split("\n")
    # 去掉开头的引用块（原文档链接、用途说明）与一级标题
    body = []
    for ln in lines:
        if ln.startswith(">") or ln.startswith("# "):
            continue
        body.append(ln)

    sections = []
    cur = None
    split_h3 = False
    for ln in body:
        if ln.startswith("## "):
            if cur:
                sections.append(cur)
            cur = {"title": ln[3:].strip(), "lines": []}
            split_h3 = TITLE_MAP.get(cur["title"], "keep") is None
        elif ln.startswith("### ") and split_h3:
            if cur:
                sections.append(cur)
            cur = {"title": ln[4:].strip(), "lines": []}
        else:
            if cur is None:
                cur = {"title": "赛季前言", "lines": []}
            cur["lines"].append(ln)
    if cur:
        sections.append(cur)
    return sections


def slug(title, idx):
    keep = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", title).strip("-")
    return f"s1-{idx:02d}-{keep}".lower()


def trim(lines):
    """去掉区块首尾空行，并把 `---` 分隔线去掉。"""
    out = [l for l in lines]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return [l for l in out if l.strip() != "---"]


# ---------------------------------------------------------------- 由代码核对得出
# 说明：以下两节内容均有 tools/verify_cube_claims.py 与 docs/reference/s1-verification.md
# 中的代码证据支撑；改动时请同步更新核对文件。
UNSUPPORTED = [
    "- 本节汇总**国服（SOECN 分支）代码核对后确认「不支持 / 不适用」**的功能与公式，"
    "避免把上游或通用说明直接套用到国服。",
    "",
    "## 已删除 / 已禁用的功能",
    "",
    "| 功能 | 状态 | 依据 |",
    "|---|---|---|",
    "| 炼狱熔炉「神话宝珠 + 灰烬 → **随机**狱铸暗金」 | ⛔ **国服已禁用**（抽取行 + 31 条 `Hellforged` 结果行 `enabled 1→0`） | 炼狱模式 `CubeMain.txt` |",
    "| 炼狱熔炉「机遇宝珠 + 灰烬 → **随机**狱铸暗金」 | ⛔ **国服已禁用**（同上） | 炼狱模式 `CubeMain.txt` |",
    "| 完美级以下（基础 / 高等）精华掉落 | ⛔ **炼狱模式已取消**（完美级保留；**标准模式未变**） | `TreasureClassEx.txt`：`Base/Greater Tier Essences` 引用 19/4 → 0/0 |",
    "| 神话宝珠 / 神授宝珠（炼狱模式） | ⛔ 炼狱模式本就**不可用**，配方禁用 | `Damnation.json`「禁用内容」 |",
    "",
    "## 公式明确不适用的技能",
    "",
    "**技能范围（`item_skill_aoe` / `item_skill_aoe_flat`）不接入**：",
    "",
    "- 狂犬病（Rabies）",
    "- 火焰石魔专属圣火（`Holy Fire Fire Golem`）",
    "- 「近战溅射范围」是另一类属性，**不套用** `P＝70×X÷(X＋18)` 曲线",
    "",
    "**技能增益效果（`buff_effect`）不放大**：",
    "",
    "- 炽烈之径的地面火伤",
    "- 两种冰甲（碎冰甲 / 寒冰装甲）的反击伤害",
    "- 能量盾的吸收比例与耗蓝效率",
    "",
    "**技能频率（`item_skill_frequency`）不适用**：",
    "",
    "- 火魔专属圣火（固定每 25 帧一次，不走圣骑士圣火的光环频率公式）",
    "- 未列入「技能频率」表的技能一律不会因堆叠技能频率而加快",
    "",
    "## 使用时请注意",
    "",
    "- 上表技能清单表示**该技能支持该属性**，**不表示**召唤物 / 雇佣兵自动继承主人的范围装备。",
    "- 仅提供「范围属性」的升华，不作为一个范围技能重复计入清单。",
    "- 国服 S1 的烬魂消耗上调**只作用于炼狱（毁灭）模式**，标准模式数值不变（详见「魔方配方 → 炼狱熔炉」）。",
    "",
    "## 口径规则（说明 ↔ 代码 冲突时的取舍）",
    "",
    "本站对「更新说明」与「国服代码」的取舍规则：",
    "",
    "1. **代码里有改动 → 以代码为准**（数值、公式、清单全部按代码收录，说明的约数与漏项按代码修正）；",
    "2. **代码里没有改动 → 以说明为准**（说明宣布的功能照常收录为已上线，不因代码表里查不到就否定）；",
    "3. 代码改动**只落在某一模式**时，按模式分别标注（见下一节）。",
    "",
    "| 条目 | 代码情况 | 本站口径 |",
    "|---|---|---|",
    "| A1A5 剧情关底 Boss（安达利尔 / 督瑞尔 / 墨菲斯托 / 迪亚波罗 / 巴尔）统一 **2DT** | 本次代码改动中查不到痕迹（两模式 `TreasureClassEx.txt` 对应行逐字节相同、无 `2DT` 形式 TC 行、检索 0 命中） | ✅ **按说明收录为已上线**（代码无改动 → 以说明为准）。若实测不符，请以游戏内为准并在群内反馈 |",
    "| 珍稀宝物世界掉落倍率（镜子 ×3 / 光之歌瓶 ×3 / 恶魔宝盒 ×20 等） | 这 5 项在本次区间**数值未变**（倍率是更早版本写入的） | ✅ **按说明收录**（代码无改动 → 以说明为准） |",
    "| 升华·酋长第四阶 击杀触发爆炸概率 25%→15% | 代码有改动，但**只在炼狱模式**（标准仍 `25`） | 按代码：**炼狱 15% / 标准 25%** |",
    "| 升华·秘术师第三阶 秽言绽放概率 25%→15% | 两模式都改 | 按代码：两模式均为 **15%** |",
    "| 毁天灭地 伤害「提高约 25%」 | 代码实测 **+24%~+30%** | 按代码：**+24%~+30%** |",
    "| 升华调整只提到「概率」 | 代码同时把酋长爆燃 / 秽言绽放**爆炸半径 16→12**（性能原因） | 按代码：**半径同时缩小到 12** |",
    "| 暗金 / 套装**分解碎片**的名称 | 代码产物 `exos` 的官方串表名为「**崇高碎片**」 | 按代码 / 官方串表：**崇高碎片**（说明所称「套装碎片」即此物） |",
    "",
    "## 模式差异（标准 vs 炼狱）",
    "",
    "以下 S1 改动**只作用于炼狱（毁灭）模式**，标准模式数值未变：",
    "",
    "| 条目 | 标准模式 | 炼狱（毁灭）模式 |",
    "|---|---|---|",
    "| 炼狱熔炉：随机货币烬魂消耗 | 25 | **50** |",
    "| 炼狱熔炉：Boss 材料转换烬魂消耗 | 15 | **25** |",
    "| 炼狱熔炉：憎恨宝珠重洗烬魂消耗 | 25 | **50** |",
    "| 炼狱熔炉：烬魂印钞概率表 | 一套（崇高宝珠 10%、贪婪 9%…） | **另一套**（贪婪 22.1%、采购 16%、提取宝珠 0.4%…） |",
    "| 取消完美级以下精华掉落 | 未变 | **已取消** |",
    "| 暗金 / 套装分解档位（1/2/3 碎片） | 无此配方 | **有** |",
    "| 升华·酋长第四阶击杀爆炸概率 | 25 | **15** |",
    "",
    "## 代码里有、说明未收录的改动",
    "",
    "- **降低软核死亡经验惩罚**：`DifficultyLevels.txt` 噩梦 `5→1`、地狱 `10→1`",
    "- **普通命运卡掉落提前到第一幕 / 第二幕**：`Act 1 Good` / `Act 2 Good` 新增 `Fate Card Normal`",
    "- **地狱铁匠（赫法斯托）非任务击杀不掉炼狱熔炉**：已修复（`SuperUniques.txt` + `SOE Story Haphesto (H)` 子 TC 顺序）",
    "- **灵狼（狂狼）溅射半径削弱**：`fenris.inc_splash_radius` 噩梦 / 地狱 `-20 → -60`",
    "- **永恒宝珠代码修正**：输出 `eto → etor`，炼狱熔炉描述 `0.05% → 0.061%`",
    "- 炼狱熔炉印钞概率整体再分配 + 新增未启用的「No reward」行",
]


def build():
    md = open(SRC, encoding="utf-8").read()
    out = []

    out.append({
        "id": "about",
        "title": "关于本页 / 数据基准",
        "text": [
            "- 本页整理**国服 SOL 第一赛季（S1）**的官方更新说明，正式服上线时间 **2026-09-11**。",
            "- 更新说明原文：腾讯文档《PD2-SOE S1 Patch Notes Final》；仓库存档：[`docs/reference/s1-patch-notes.md`](https://github.com/AustinWp/TheArchivistSoE-ZH/blob/main/docs/reference/s1-patch-notes.md)",
            "- 代码基准：`SOECN` 仓库（`SOECN` 分支）commit `9b24eb72`（2026-09-11），上一基准为 `374d8971`（2026-08-24）。",
            "- 全站术语以游戏官方中文串表为准（例如「强化伤害」= 说明原文的「增强伤害」）；配方 / 掉落 / 技能数值以国服代码为唯一标准。",
            "- 更新说明的**逐字原文**存档在 `docs/reference/s1-patch-notes.md`，本页文案按全站术语做了统一。",
            "- 页面中的「⛔ 国服不支持」标记表示该功能或公式在**国服代码中不存在或未接入**，请勿按通用/上游资料套用。",
            "- **口径规则**：说明与代码冲突时 —— **代码里有改动的以代码为准**；**代码里没有的以说明为准**；只在单一模式落地的按模式分别标注。",
        ],
    })

    for idx, sec in enumerate(split_sections(md)):
        title = TITLE_MAP.get(sec["title"], sec["title"])
        title = sec["title"] if title is None else title
        text = trim(sec["lines"])
        if not text:
            continue
        out.append({"id": slug(title, idx), "title": title, "text": text})

    out.append({
        "id": "cn-unsupported",
        "title": "⛔ 国服不支持 / 不适用的功能与公式",
        "cnUnsupported": True,
        "text": UNSUPPORTED,
    })

    if os.path.exists(VERIFY):
        vtext = trim(open(VERIFY, encoding="utf-8").read().split("\n"))
        if vtext:
            out.append({"id": "cross-verification", "title": "交叉验证：更新说明 ↔ 国服代码", "text": vtext})

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"OK -> {OUT}  ({len(out)} 节)")
    for s in out:
        print(f"   - {s['id']}  {s['title']}  ({len(s['text'])} 行)")


if __name__ == "__main__":
    build()
