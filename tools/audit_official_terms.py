# -*- coding: utf-8 -*-
"""官方术语一致性审计。

权威来源：`docs/reference/soe.txt`（国服客户端中文串表，UTF-16 导出）
→ 清洗颜色码后落为 `public/data/official_zh.json`（key → 中文，3854 条）。

审计三件事：
  1. **旧译残留**：早期人工翻译的术语（表格里列出的）是否还出现在站点输出里；
  2. **生成器硬编码对照**：`tools/*.py`、`src/*.jsx` 里手写的「英文名 → 中文名」映射，
     如果该英文名能对应到游戏数据里的物品 code，就与官方中文逐个比对；
  3. **物品名一致性**：物品 JSON 中出现的 code，其显示名必须等于官方中文（若官方有）。

用法:
    python3 tools/audit_official_terms.py            # 报告
    python3 tools/audit_official_terms.py --strict   # 有差异时退出码 1
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 旧译 → 官方（2026-08-29 全站对齐 + apply_zh_terms 的词表）
LEGACY = {
    "神圣宝珠": "神授宝珠",
    "机会宝珠": "机遇宝珠",
    "结晶余烬之魂": "晶化烬魂",
    "永恒硬币": "永恒币",
    "雕文": "铭文",
    "恶魔方块": "恶魔宝盒",
    "飞升": "升华",
    "筑防宝珠": "强化法珠",
    "混沌庇护所护符": "群魔殿护符",
    "魔血腰带": "法师之血",
    "增强伤害": "强化伤害",
    "致命攻击": "致命一击",
    "冰冷伤害": "冰霜伤害",
    "更好的机会获得魔法物品": "寻获魔法物品几率提高",
    "受到的伤害转换为法力": "受到伤害转换为法力",
    "炼狱窑炉": "炼狱熔炉",
}

# 这些文件里的旧词是「历史叙述」或「旧译词典本身」，不算残留
SKIP_FILES = {
    "official_zh.json",     # 术语源本体
    "SiteUpdates.json",     # 更新日志记录「旧词→新词」
    "s1-patch-notes.md",    # 官方说明原文存档
    "s1-verification.md",
    "apply_zh_terms.py",    # 替换词表本身
    "zh_dict.py",           # 旧词典（已标注，仅参考）
    "TRANSLATION_GUIDE.md",
    "audit_official_terms.py",
    "item_names.py",        # 早期人工词典，已标 DEPRECATED 且无任何工具引用
}
# 这些文件已标 DEPRECATED，不参与扫描
SKIP_PREFIXES = ("translate_",)

SCAN_DIRS = ["public/data", "src"]
CJK = re.compile(r"[\u4e00-\u9fff]")


def clean(text):
    return re.sub(r"\\[a-z]+;", "", text).strip()


def load_official():
    data = json.load(open(os.path.join(ROOT, "public", "data", "official_zh.json"), encoding="utf-8"))
    return {k: clean(v) for k, v in data["names"].items()}


def load_english_names():
    """code → 英文名（来自游戏数据表）。同时记录 namestr（游戏取名优先用它）。"""
    out = {}
    for t in ["Misc.txt", "Weapons.txt", "Armor.txt", "Gems.txt", "Runes.txt", "Sets.txt"]:
        p = os.path.join(ROOT, "public", "data", "standard", t)
        if not os.path.exists(p):
            continue
        lines = open(p, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
        if not lines:
            continue
        hdr = lines[0].split("\t")
        if "code" not in hdr:
            continue
        ci = hdr.index("code")
        ni = next((hdr.index(c) for c in ("name", "Name", "index", "FileName", "runename") if c in hdr), None)
        if ni is None:
            continue
        for l in lines[2:]:
            f = l.split("\t")
            if len(f) > max(ci, ni) and f[ci] and f[ni] and f[ci] not in out:
                out[f[ci]] = f[ni].strip()
    return out


# 官方的符文/宝石等条目带「类别：」前缀，UI 只显示名字，视为等价
PREFIX_RE = re.compile(r"^(符文|宝石|护符|戒指|项链|武器|护甲|珠宝)：")

# 这些文件只做「硬编码词表」检查，不做物品名比对（暗金 displayName 是暗金自己的名字）
UNIQUE_NAME_FILES = {"Uniques.json"}


def norm_name(s):
    return PREFIX_RE.sub("", str(s).strip()).strip()


def iter_files():
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        for dirpath, _dirnames, filenames in os.walk(base):
            for fn in filenames:
                if fn in SKIP_FILES or fn.startswith(SKIP_PREFIXES):
                    continue
                if fn.rsplit(".", 1)[-1] not in ("json", "jsx", "js", "md", "py", "txt"):
                    continue
                yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    official = load_official()
    en2code = {}
    for code, en in load_english_names().items():
        en2code.setdefault(en.lower(), []).append(code)

    issues = []

    # ---------- 1) 旧译残留 ----------
    print("== 1. 旧译残留扫描 ==")
    for path in iter_files():
        rel = os.path.relpath(path, ROOT)
        try:
            txt = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for old, new in LEGACY.items():
            if old not in txt:
                continue
            for m in re.finditer(re.escape(old), txt):
                ctx = txt[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
                issues.append(f"[旧译] {rel}: 「{old}」应为「{new}」 → …{ctx}…")
    print(f"  命中 {len(issues)} 处")

    # ---------- 2) 生成器硬编码「英文 → 中文」 ----------
    print("\n== 2. 生成器硬编码术语比对（能对应到 code 的） ==")
    pair_re = re.compile(r'"([A-Za-z][A-Za-z\'’ \-]{2,40})"\s*:\s*"([^"]{1,24})"')
    checked = mismatch = 0
    for d in ("tools", "src"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.startswith(SKIP_PREFIXES) or fn in SKIP_FILES or not fn.endswith((".py", ".jsx")):
                continue
            p = os.path.join(ROOT, d, fn)
            short = os.path.relpath(p, ROOT)
            txt = open(p, encoding="utf-8", errors="replace").read()
            for m in pair_re.finditer(txt):
                en, zh = m.group(1), m.group(2)
                if not CJK.search(zh):
                    continue
                for code in en2code.get(en.lower(), []):
                    want = official.get(code)
                    if not want:
                        continue
                    checked += 1
                    if norm_name(want) != norm_name(zh):
                        mismatch += 1
                        issues.append(f"[硬编码] {short}: {en} → 「{zh}」，官方（{code}）应为「{want}」")
    print(f"  可比对 {checked} 条，不一致 {mismatch} 条")

    # ---------- 3) 物品 JSON 显示名（按游戏取名链路：namestr 优先，否则 code） ----------
    print("\n== 3. 物品数据显示名比对（namestr 优先） ==")
    key_map = {}
    for t in ("Weapons.txt", "Armor.txt", "Misc.txt"):
        p = os.path.join(ROOT, "public", "data", "standard", t)
        if not os.path.exists(p):
            continue
        rows = [r.split("\t") for r in open(p, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n") if r.strip()]
        hdr = rows[0]
        if "code" not in hdr:
            continue
        ci = hdr.index("code")
        ni = hdr.index("namestr") if "namestr" in hdr else None
        for r in rows[1:]:
            if len(r) <= ci or not r[ci]:
                continue
            ns = r[ni].strip() if ni is not None and len(r) > ni else ""
            key_map[r[ci].lower()] = (ns or r[ci]).lower()

    def official_for(code):
        c = str(code or "").lower()
        return official.get(key_map.get(c, c))

    checked3 = bad3 = 0
    for fn in ("Weapons.json", "Armors.json"):
        p = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(p):
            continue
        for it in json.load(open(p, encoding="utf-8")):
            want = official_for(it.get("code"))
            if not want:
                continue
            got = str(it.get("name") or "")
            checked3 += 1
            if got and norm_name(got) != norm_name(want):
                bad3 += 1
                issues.append(f"[物品名] {fn}: code={it.get('code')} 显示「{got}」，官方「{want}」")

    # 暗金 / 套装里嵌套的底材名
    for fn in ("Uniques.json",):
        p = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(p):
            continue
        for it in json.load(open(p, encoding="utf-8")):
            for field in ("weaponBase", "armorBase", "jeweleryBase"):
                b = it.get(field)
                if not isinstance(b, dict):
                    continue
                want = official_for(b.get("code"))
                if not want:
                    continue
                got = str(b.get("name") or "")
                checked3 += 1
                if got and norm_name(got) != norm_name(want):
                    bad3 += 1
                    issues.append(f"[底材名] {fn}[{it.get('displayName')}].{field}: 「{got}」官方「{want}」")
    print(f"  可比对 {checked3} 条，不一致 {bad3} 条")

    print("\n== 结论 ==")
    if not issues:
        print("  ✅ 未发现与官方中文串表不一致的地方")
        return 0

    print(f"  ⚠️ 共 {len(issues)} 条：")
    for x in issues[:80]:
        print("   -", x)
    if len(issues) > 80:
        print(f"   … 其余 {len(issues) - 80} 条省略")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
