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
    # 来源：PD2 汉化 wiki（`docs/reference/pd2_zh_item_names.json`，2026-09-13 抓取）的「修正简」列。
    # 这些是**基础游戏**物品，SOE 串表未覆盖，客户端回落到基础游戏中文串 —— 无法从 SOECN 仓库验证，
    # 故以 PD2（SOE 的底座）中文 wiki 为准。
    #
    # 有意偏离 wiki 的例外：
    #   key —— wiki 作「钥匙」，本站作「普通钥匙」：用于与 rkey「骷髅钥匙」区分，
    #          且国服 S1 更新说明原文即写「普通钥匙」。
    "ass": "技能之书",
    "bbb": "蓝.依森之书",
    "bkd": "石冢之钥",
    "bks": "艾尼弗斯卷轴",
    "box": "赫拉迪克方块",
    "cm1": "小护身符",
    "cm2": "大型护身符",
    "cm3": "超大型护身符",
    "ear": "耳",
    "elx": "靈葯",
    "g34": "黄金鸟",
    "gcb": "碎裂的蓝宝石",
    "gcg": "碎裂的绿宝石",
    "gcr": "碎裂的红宝石",
    "gcv": "碎裂的紫宝石",
    "gcw": "碎裂的钻石",
    "gcy": "碎裂的黄宝石",
    "gfb": "裂开的蓝宝石",
    "gfg": "裂开的绿宝石",
    "gfr": "裂开的红宝石",
    "gfv": "裂开的紫宝石",
    "gfw": "裂开的钻石",
    "gfy": "裂开的黄宝石",
    "glb": "无瑕疵的蓝宝石",
    "gld": "金币",
    "glg": "无瑕疵的绿宝石",
    "glr": "无瑕疵的红宝石",
    "glw": "无瑕疵的钻石",
    "gly": "无瑕疵的黄宝石",
    "gpb": "完美的蓝宝石",
    "gpg": "完美的绿宝石",
    "gpl": "勒頸瓦斯葯劑",
    "gpm": "窒息瓦斯葯劑",
    "gpr": "完美的红宝石",
    "gps": "惡臭瓦斯葯劑",
    "gpv": "完美的紫宝石",
    "gpw": "完美的钻石",
    "gpy": "完美的黄宝石",
    "gsb": "蓝宝石",
    "gsg": "绿宝石",
    "gsr": "红宝石",
    "gsv": "紫宝石",
    "gsw": "钻石",
    "gsy": "黄宝石",
    "gzv": "无瑕疵的紫宝石",
    "hp1": "轻微治疗药剂",
    "hp2": "轻型治疗药剂",
    "hp3": "治疗药剂",
    "hp4": "强力药剂",
    "hp5": "超级治疗药剂",
    "hrb": "葯草",
    "ibk": "辨视之书",
    "ice": "马拉之药",
    "isc": "辨视卷轴",
    "j34": "玉制小人",
    "jaw": "顎骨",
    "jew": "珠宝",
    "key": "钥匙",
    "leg": "維特的腿",
    "luv": "黑塔之鑰",
    "mp1": "轻微法力药剂",
    "mp2": "轻型法力药剂",
    "mp3": "法力药剂",
    "mp4": "强力法力药剂",
    "mp5": "超级法力药剂",
    "mss": "墨菲斯托的灵魂之石",
    "opl": "猛爆性葯劑",
    "opm": "爆炸葯劑",
    "ops": "油",
    "qbr": "克林姆的大脑",
    "qey": "克林姆的眼球",
    "qhr": "克林姆的心脏",
    "qll": "硬毛",
    "rvl": "全面回复活力药剂",
    "rvs": "回复活力药剂",
    "skc": "碎裂的骷髅",
    "skf": "裂开的骷髅",
    "skl": "无瑕疵的骷髅",
    "sku": "骷髅",
    "skz": "完美的骷髅",
    "sol": "靈魂",
    "spe": "脾臟",
    "tal": "尾巴",
    "tbk": "城镇传送之书",
    "toa": "赦免徽章",
    "tr1": "赫拉迪克卷轴",
    "tr2": "抵抗卷轴",
    "tsc": "城镇传送卷轴",
    "vps": "体力药剂",
    "wms": "融解药剂",
    "xyz": "生命药剂",
    "yps": "解毒药剂",
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
