# -*- coding: utf-8 -*-
"""官方物品中文名的**唯一**解析入口。

为什么要有这个模块
------------------
2026-09 出过一次重大事故：505 件底材里有 298 件用了社区旧译（诸葛弩 / 重弩 / 谐角之冠…），
和游戏里显示的名字不一致。根因是**取值链路不完整**：

    官方串表里，物品中文名有**两条**来源
      1. 物品自己的键：`namestr`（为空则用 `code`）        e.g. `mfo` → 神话宝珠
      2. 基础类型族：`StrEternal<英文名去空格/连字符>`      e.g. `StrEternalChuKoNu` → 巧工弩

    而当时「生成工具」和「审计工具」各自只实现了第 1 条 —— 于是**校验器与被校验对象
    犯了同一个错**，298 件错名既没被发现、也永远不会被报出来。

现在的规矩：**所有需要物品官方中文名的地方，都必须经过本模块**，
不要再在各自的脚本里手写一遍取值逻辑（那样迟早又会分叉）。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TABLES = ["Weapons.txt", "Armor.txt", "Misc.txt"]

# 串表里确实没有官方名的物品，**必须在这里显式登记** —— 将来真有装备混进来才能被看见。
#
# 分两类，含义不同：
#   NO_OFFICIAL_NAME —— 不展示 / 展示的是内部占位名或任务名，无所谓
#   BASE_GAME_NAME   —— **正文里天天出现**（珠宝、护身符、钥匙、宝石…），
#                       游戏里显示的是「基础游戏」的中文串（不在 SOE 串表内），
#                       所以**无法用串表验证**。改动这些名字前必须另找依据，
#                       也不要对外声称「已与官方对齐」。
NO_OFFICIAL_NAME = {
    "hst": "赫拉迪克法杖（任务物品）",
    "7cr2": "双手幻化之刃（SOE 自定义基底）",
}

BASE_GAME_NAME = {
    "jew": "珠宝", "cm1": "小护身符", "cm2": "中护身符", "cm3": "大护符",
    "key": "普通钥匙", "toa": "赦免徽章", "ice": "冰封之球",
    "tbk": "回城之书", "ibk": "鉴定之书", "elx": "药剂",
}


def clean(v):
    """去掉 `\\red;` 之类的颜色控制码。"""
    return re.sub(r"\\[a-z]+;", "", str(v)).strip()


def load_official():
    p = os.path.join(ROOT, "public", "data", "official_zh.json")
    return {k: clean(v) for k, v in json.load(open(p, encoding="utf-8"))["names"].items()}


def load_rows(name):
    p = os.path.join(ROOT, "public", "data", "standard", name)
    rows = open(p, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
    while rows and not rows[-1].strip():
        rows.pop()
    return [r.split("\t") for r in rows]


def name_candidates(english_name):
    """英文名 → 可能对应的 `StrEternal` 键（去后缀、去斜杠、去符号、小写）。

    游戏表里的英文名不一定干净：`Gloves(L)` / `Boneweave [S]` / `Cap/hat`
    / `Hunter's Bow`（对应键写成了 `StrEternalHunterSBow`）等都要照顾到。
    """
    base = re.sub(r"[\(\[][^\)\]]*[\)\]]", "", english_name or "")   # 去 (L)/(M)/[S]
    out = []
    for part in base.split("/"):
        k = re.sub(r"[^A-Za-z0-9]", "", part).lower()
        if k:
            out.append(k)
    return out


class OfficialNames:
    """一次装载，反复查询；三条链路按优先级串起来。"""

    def __init__(self):
        self.official = load_official()

        # StrEternal 族：小写英文名 → 基础类型名
        self.eternal = {}
        for k, v in self.official.items():
            if k.startswith("StrEternal") and v.startswith("基础类型："):
                self.eternal[k[len("StrEternal"):].lower()] = v[len("基础类型："):]

        # code → (namestr 键, 英文名)
        self.rows = {}
        for t in TABLES:
            rows = load_rows(t)
            hdr = rows[0]
            if "code" not in hdr:
                continue
            ci = hdr.index("code")
            ni = hdr.index("name") if "name" in hdr else None
            si = hdr.index("namestr") if "namestr" in hdr else None
            for r in rows[1:]:
                if len(r) <= ci or not r[ci].strip():
                    continue
                code = r[ci].strip().lower()
                ns = r[si].strip() if si is not None and len(r) > si else ""
                en = r[ni].strip() if ni is not None and len(r) > ni else ""
                self.rows[code] = (ns or code, en)

    def resolve(self, code, english_name=None):
        """返回 (官方中文名, 来源)；查不到返回 (None, None)。"""
        if not code:
            return None, None
        code = str(code).lower()

        if english_name is None:
            english_name = self.rows.get(code, ("", ""))[1]

        key = self.rows.get(code, (code, ""))[0].lower()
        hit = self.official.get(key)
        if hit:
            return hit, "namestr/code"

        for cand in name_candidates(english_name):
            hit = self.eternal.get(cand)
            if hit:
                return hit, "StrEternal"

        return None, None

    def classify(self, code):
        """resolve 的语义化版本：official / base-game / placeholder。"""
        zh, src = self.resolve(code)
        if src:
            return zh, src
        if code in BASE_GAME_NAME:
            return BASE_GAME_NAME[code], "基础游戏（串表未覆盖）"
        if code in NO_OFFICIAL_NAME:
            return None, "占位/任务物品"
        return None, "未登记"

    def coverage(self, english_name_override=None):
        """统计所有游戏表物品的取名来源，返回 (统计, 未覆盖 [code...])。"""
        from collections import Counter

        stat = Counter()
        missing = []
        for code in self.rows:
            zh, src = self.classify(code)
            stat[src] += 1
            if src == "未登记":
                missing.append(code)
        return stat, missing


if __name__ == "__main__":
    on = OfficialNames()
    stat, missing = on.coverage()
    print("取名来源统计:", dict(stat))
    print("无官方来源:", missing)
