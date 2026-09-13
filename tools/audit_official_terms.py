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
    # 旧符文名（官方串表 r01–r33）
    "夏尔": "沙伊", "书尔": "图尔", "特尔": "提尔", "萨德": "佐德",
    "那夫": "奈夫", "爱斯": "艾斯", "爱欧": "艾欧",
    "伊斯特": "伊司特", "瓦克斯": "伐克斯",
    # 钥匙：官方串表 rkey = 骷髅钥匙（可重复使用）；key 无官方条目 → 站内统一叫「普通钥匙」
    "骷髅钥匙（消耗品）": "普通钥匙",
}

# 这些文件里的旧词是「历史叙述」或「旧译词典本身」，不算残留
SKIP_FILES = {
    "official_zh.json",     # 术语源本体
    "SiteUpdates.json",     # 更新日志记录「旧词→新词」
    "s1-patch-notes.md",    # 官方说明原文存档
    "s1-verification.md",
    "apply_zh_terms.py",    # 替换词表本身
    "",
    "audit_official_terms.py",
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

    # ---------- 4) {{icon:CODE}} 与紧随其后的名称是否匹配 ----------
    # 基础类型兜底：统一走 tools/official_names.py（唯一实现，别在这里再写一遍）
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from official_names import OfficialNames  # noqa: E402

    _on = OfficialNames()
    _eternal_raw = {}
    for _c in _on.rows:
        _zh, _src = _on.resolve(_c)
        if _zh and _src == "StrEternal":
            _eternal_raw[_c] = _zh

    eternal = _eternal_raw
    # 与 apply_official_item_names 的口径一致：namestr/code 键**有**官方条目时以它为准，
    # 基础类型名只在没有条目时兜底 —— 否则会把正确的名字报成错误
    _keys = {}
    for tbl in ("Weapons.txt", "Armor.txt", "Misc.txt"):
        pth = os.path.join(ROOT, "public", "data", "standard", tbl)
        if not os.path.exists(pth):
            continue
        rows = open(pth, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
        hdr = rows[0].split("\t")
        if "code" not in hdr:
            continue
        ci = hdr.index("code")
        ni = hdr.index("namestr") if "namestr" in hdr else None
        for r in rows[1:]:
            f = r.split("\t")
            if len(f) <= ci or not f[ci].strip():
                continue
            ns = f[ni].strip() if ni is not None and len(f) > ni else ""
            _keys[f[ci].strip().lower()] = (ns or f[ci].strip()).lower()
    eternal = {c: w for c, w in eternal.items() if _keys.get(c, c) not in official}
    print("\n== 3b. 底材名 ↔ 官方「基础类型」名 ==")
    bad3b = 0
    # 嵌套基底名：标准版 + 炼狱版（默认视图用的是后者）都要查
    for rel in ("Uniques.json", os.path.join("damnation", "Uniques.json")):
        pth_u = os.path.join(ROOT, "public", "data", rel)
        if not os.path.exists(pth_u):
            continue
        for u in json.load(open(pth_u, encoding="utf-8")):
            for field in ("weaponBase", "armorBase", "jeweleryBase"):
                b = u.get(field)
                if not isinstance(b, dict) or not b.get("code"):
                    continue
                w = _on.resolve(str(b["code"]).lower())[0]
                checks = [("name", b.get("code")), ("displayName", b.get("code"))]
                for tf, tc in (("normalItemDisplayName", "normalTierCode"),
                               ("exceptionalItemDisplayName", "exceptionalTierCode"),
                               ("eliteItemDisplayName", "eliteTierCode")):
                    checks.append((tf, b.get(tc)))

                for sub, src_code in checks:
                    got = b.get(sub)
                    w2 = _on.resolve(str(src_code or "").lower())[0]
                    if w2 and got and norm_name(got) != norm_name(w2):
                        bad3b += 1
                        issues.append(
                            f"[底材名不符] {rel}[{u.get('displayName')}].{field}.{sub}: 「{got}」应为「{w2}」")

    for fn in ("Weapons.json", "Armors.json"):
        pth = os.path.join(ROOT, "public", "data", fn)
        if not os.path.exists(pth):
            continue
        for it in json.load(open(pth, encoding="utf-8")):
            code = str(it.get("code", "")).lower()

            # 物品自身：**所有**名字字段都要一致 —— 前端渲染用的是 displayName，
            # 只校验 name 会漏掉（巧工弩第二次翻车就是栽在这里）
            for field in ("name", "displayName"):
                w = _on.resolve(code)[0]
                if w and it.get(field) and norm_name(it[field]) != norm_name(w):
                    bad3b += 1
                    issues.append(f"[底材名不符] {fn} {it.get('code')}.{field}: 「{it[field]}」应为「{w}」")

            # 三个阶位的显示名（按各自 tier code 取名）
            for field, tier_code in (("normalItemDisplayName", "normalTierCode"),
                                     ("exceptionalItemDisplayName", "exceptionalTierCode"),
                                     ("eliteItemDisplayName", "eliteTierCode")):
                got = it.get(field)
                w2 = _on.resolve(str(it.get(tier_code) or "").lower())[0]
                if got and w2 and norm_name(got) != norm_name(w2):
                    bad3b += 1
                    issues.append(f"[底材名不符] {fn} {it.get('code')}.{field}: 「{got}」应为「{w2}」")

    print(f"  比对 {len(eternal)} 个基础类型的全部名字字段，不一致 {bad3b} 条")

    # ---------- 5) 官方中文名覆盖率 ----------
    print("\n== 5. 官方中文名覆盖率 ==")
    stat, unregistered = _on.coverage()
    print("  取名来源: " + " · ".join(f"{k} {v}" for k, v in sorted(stat.items())))

    # 站点**真正展示**的装备必须能追溯到官方名；追溯不到的必须显式登记
    shown = set()
    for fn in ("Weapons.json", "Armors.json"):
        pth = os.path.join(ROOT, "public", "data", fn)
        if os.path.exists(pth):
            for it in json.load(open(pth, encoding="utf-8")):
                shown.add(str(it.get("code", "")).lower())
    pth = os.path.join(ROOT, "public", "data", "Uniques.json")
    if os.path.exists(pth):
        for u in json.load(open(pth, encoding="utf-8")):
            for field in ("weaponBase", "armorBase", "jeweleryBase"):
                b = u.get(field)
                if isinstance(b, dict) and b.get("code"):
                    shown.add(str(b["code"]).lower())

    naked = sorted(c for c in shown if _on.classify(c)[1] == "未登记")
    print(f"  展示中的装备无官方来源且未登记: {len(naked)} 件")
    if naked:
        for c in naked[:20]:
            issues.append(f"[名字来源未登记] {c}: {_on.rows.get(c, ('', ''))[1]!r} "
                          f"—— 请补进 tools/official_names.py 的 BASE_GAME_NAME 或 NO_OFFICIAL_NAME")

    # ---------- 6) 纯文本字段里不能出现标记 ----------
    print("\n== 6. 标记只能出现在 markdown 渲染的字段里 ==")
    PLAIN_FIELDS = {"displayName", "title", "caption", "name", "displayType", "itemType"}
    MARK_RE = re.compile(r"\{\{icon:|（\d+号）")
    dirty = 0

    def _scan(node, rel, hits=None):
        nonlocal dirty
        if hits is None:
            hits = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k in PLAIN_FIELDS and isinstance(v, str) and MARK_RE.search(v):
                    hits.append(f"{rel} [{k}] {v[:60]}")
                elif not (k in PLAIN_FIELDS):
                    _scan(v, rel, hits)
        elif isinstance(node, list):
            for v in node:
                _scan(v, rel, hits)
        return hits

    scan_files = []
    for f in sorted(os.listdir(os.path.join(ROOT, "public", "data"))):
        if f.endswith(".json") and f not in ("official_zh.json", "SiteUpdates.json", "ItemImages.json"):
            scan_files.append(os.path.join(ROOT, "public", "data", f))
    # 子目录也要扫：炼狱模式（默认）加载的是 data/damnation/Uniques.json
    for sub in ("damnation", "standard"):
        d = os.path.join(ROOT, "public", "data", sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                scan_files.append(os.path.join(d, f))

    for pth in scan_files:
        f = os.path.relpath(pth, os.path.join(ROOT, "public", "data"))
        try:
            data = json.load(open(pth, encoding="utf-8"))
        except Exception:
            continue
        for h in _scan(data, f):
            dirty += 1
            issues.append(f"[标记落到纯文本字段] {h}")
    print(f"  纯文本字段中的标记: {dirty} 处")

    # ---------- 3c) 各基底上的暗金引用是否与 Uniques.json 一致 ----------
    print("\n== 3c. 基底 ↔ 暗金引用一致性 ==")
    try:
        _uni = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"), encoding="utf-8"))
        _want = {}
        for _u in _uni:
            _b = _u.get("weaponBase") or _u.get("armorBase") or _u.get("jeweleryBase") or {}
            _c = str(_b.get("code") or "").lower()
            if _c:
                _want.setdefault(_c, []).append(_u.get("displayName") or _u.get("index"))

        bad3c = 0
        for fn in ("Weapons.json", "Armors.json"):
            pth = os.path.join(ROOT, "public", "data", fn)
            if not os.path.exists(pth):
                continue
            for it in json.load(open(pth, encoding="utf-8")):
                got = [x.get("uniqueName") for x in (it.get("uniques") or [])]
                exp = _want.get(str(it.get("code", "")).lower(), [])
                if got != exp:
                    bad3c += 1
                    issues.append(f"[暗金引用过时] {fn} {it.get('code')}: 表里 {got}，应为 {exp}")
        print(f"  可比对 {len(_want)} 个基底，不一致 {bad3c} 件")
    except Exception as _e:  # noqa: BLE001
        print(f"  跳过（{_e}）")

    # ---------- 3d) 暗金结构与源码表一致性（缺项 / 关键字段） ----------
    print("\n== 3d. 暗金 ↔ UniqueItems.txt 一致性 ==")
    # 已知且**有意**不收录的条目：说明写清楚，避免被当成漏网
    # 以下条目在 UniqueItems.txt 里 enabled=1，但**有意**不放进「暗金装备」列表。
    # 每条都要写清理由 —— 登记成例外是为了让「真·漏项」无处可藏，不是把问题藏起来。
    KNOWN_MISSING_UNIQUES = {
        "彩虹刻面": "本站以「彩虹刻面·闪电 / 冰冷 / 火焰 / 毒素」四条收录，源码 4 行同名",
        "克林姆连枷": "任务物品（源码 quest 列非空）",
        "超级克林姆连枷": "任务物品",
        "国王之杖": "任务物品",
        "地狱熔炉之锤": "任务物品",
        "蝮蛇项链": "任务物品",
        "赫拉迪克法杖": "任务物品",
    }
    # 前缀后缀类：升华灵魂石系列（已在「升华」页收录）
    KNOWN_MISSING_PREFIX = [
        ("力量灵魂石", "升华物品，已在「升华」页收录"),
        ("升华灵魂石", "升华物品，已在「升华」页收录"),
        ("统御灵魂石", "升华物品，已在「升华」页收录"),
        ("神性灵魂石", "升华物品，已在「升华」页收录"),
        ("升华石冢", "升华物品，已在「升华」页收录"),
    ]
    try:
        _p = os.path.join(ROOT, "public", "data", "standard", "UniqueItems.txt")
        _rows = [l.split("\t") for l in
                 open(_p, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n").split("\n")
                 if l.strip()]
        _h = _rows[0]
        _ci, _en = _h.index("index"), _h.index("enabled")
        _li, _ri, _coi = _h.index("lvl"), _h.index("lvl req"), _h.index("code")

        _uni = json.load(open(os.path.join(ROOT, "public", "data", "Uniques.json"), encoding="utf-8"))
        _have = {}
        for _x in _uni:
            _have.setdefault(_x.get("index"), []).append(str(_x.get("code", "")).lower())

        _missing, _fieldbad, _documented = [], 0, []
        for _r in _rows[1:]:
            if len(_r) <= max(_ci, _en, _li, _ri, _coi) or _r[_en].strip() != "1":
                continue
            _nm, _code = _r[_ci].strip(), _r[_coi].strip().lower()
            reason = KNOWN_MISSING_UNIQUES.get(_nm)
            if not reason:
                for pre, why in KNOWN_MISSING_PREFIX:
                    if _nm.startswith(pre):
                        reason = why
                        break
            if reason:
                _documented.append(f"{_nm}（{reason}）")
                continue
            if _nm not in _have:
                _missing.append(_nm)
                continue
            if _code not in _have[_nm]:
                _missing.append(f"{_nm}({_code})")
        for _m in _missing:
            issues.append(f"[暗金缺项] {_m} —— UniqueItems.txt 里 enabled=1 但本站没有")
        print(f"  源码启用暗金 {sum(1 for _r in _rows[1:] if len(_r) > _en and _r[_en].strip() == '1')} 条，"
              f"本站缺失 {len(_missing)} 条")
        print(f"  已登记的有意例外 {len(_documented)} 条: "
              + "; ".join(sorted({d.split('（')[1].rstrip('）') for d in _documented})))
    except Exception as _e:  # noqa: BLE001
        print(f"  跳过（{_e}）")

    # ---------- 3e) 基础游戏物品名 ↔ PD2 汉化 wiki ----------
    print("\n== 3e. 基础游戏物品名 ↔ PD2 汉化 wiki ==")
    _wp = os.path.join(ROOT, "docs", "reference", "pd2_zh_item_names.json")
    if os.path.exists(_wp):
        import importlib
        _m = importlib.import_module("official_names")
        _w = json.load(open(_wp, encoding="utf-8"))["names"]
        # 有意偏离 wiki 的例外（写清理由）
        _deviations = {"key": "wiki「钥匙」；本站作「普通钥匙」以区别于 rkey「骷髅钥匙」"}
        _bad = 0
        _checked = 0
        for _c, _name in _m.BASE_GAME_NAME.items():
            _ww = _w.get(_c)
            if not _ww or not _ww.get("fix"):
                continue
            _checked += 1
            if _c in _deviations:
                continue
            if _name != _ww["fix"]:
                _bad += 1
                issues.append(f"[基础游戏名不符] {_c}: 登记为「{_name}」，wiki 修正简为「{_ww['fix']}」")
        print(f"  可比对 {_checked} 条，不一致 {_bad} 条"
              f"（另有 {len(_deviations)} 条登记的有意偏离）")
    else:
        print("  跳过（缺 docs/reference/pd2_zh_item_names.json）")

    # ---------- 3f) 狱铸前缀 ----------
    print("\n== 3f. 狱铸装备名前缀 ==")
    _wrong = 0
    for _rel in ("Uniques.json", os.path.join("damnation", "Uniques.json")):
        _pth = os.path.join(ROOT, "public", "data", _rel)
        if not os.path.exists(_pth):
            continue
        for _u in json.load(open(_pth, encoding="utf-8")):
            _n = str(_u.get("displayName") or "")
            # 官方写法是「地狱锻铸·××」；「地狱锻造××」是社区旧写法
            if _n.startswith("地狱锻造"):
                _wrong += 1
                issues.append(f"[狱铸前缀错] {_rel}: 「{_n}」应为「地狱锻铸·…」")
    print(f"  错误前缀 {_wrong} 处（官方为「地狱锻铸·」）")

    # ---------- 3g) 标准版 / 炼狱版暗金表条目集合一致性 ----------
    print("\n== 3g. 标准版 ↔ 炼狱版暗金表 ==")
    _ps = os.path.join(ROOT, "public", "data", "Uniques.json")
    _pd = os.path.join(ROOT, "public", "data", "damnation", "Uniques.json")
    if os.path.exists(_ps) and os.path.exists(_pd):
        def _sig(path):
            out = []
            for _x in json.load(open(path, encoding="utf-8")):
                _b = _x.get("weaponBase") or _x.get("armorBase") or _x.get("jeweleryBase") or {}
                out.append((str(_x.get("displayName")), str(_b.get("code") or _x.get("code")),
                            str(_x.get("level"))))
            return out

        _a, _b = _sig(_ps), _sig(_pd)
        _only_a = [x for x in _a if x not in _b]
        _only_b = [x for x in _b if x not in _a]
        if _only_a or _only_b:
            issues.append(f"[暗金表不一致] 仅标准版有 {len(_only_a)} 条、仅炼狱版有 {len(_only_b)} 条"
                          f"（两份应当是同一套条目，只差模式字段）")
        print(f"  标准版 {len(_a)} 条 / 炼狱版 {len(_b)} 条；仅标准有 {len(_only_a)}，仅炼狱有 {len(_only_b)}")
    else:
        print("  跳过（缺文件）")

    print("\n== 4. 图标标记 ↔ 名称一致性 ==")
    official_norm = {k: norm_name(v) for k, v in official.items()}
    # 站内为区分重名而自定的别名（官方串表未收录）
    ALIAS_NAME = {"key": "普通钥匙"}

    known_names = sorted(
        set(official_norm.values()) | set(ALIAS_NAME.values()),
        key=len, reverse=True,
    )
    # 只匹配「紧跟标记的、已知的物品名」，避免把后面的短语一起吃进来
    name_alt = re.compile("|".join(re.escape(x) for x in known_names if x))
    icon_re = re.compile(r"\{\{icon:([A-Za-z0-9_]+)\}\}")

    checked4 = bad4 = 0
    for path in iter_files():
        rel = os.path.relpath(path, ROOT)
        if not rel.startswith("public" + os.sep + "data"):
            continue
        try:
            txt = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue

        for m in icon_re.finditer(txt):
            code = m.group(1).lower()
            want = official_norm.get(code) or ALIAS_NAME.get(code)
            if not want:
                continue

            tail = txt[m.end():m.end() + 16]
            hit = name_alt.match(tail)
            if not hit:
                continue          # 标记后面不是已知物品名（可能是列表/表格），跳过

            checked4 += 1
            if norm_name(want) != norm_name(hit.group(0)):
                bad4 += 1
                issues.append(
                    f"[图标名不符] {rel}: {{{{icon:{m.group(1)}}}}}{hit.group(0)}，"
                    f"但 {m.group(1)} 的名称应为「{want}」"
                )
    print(f"  可比对 {checked4} 条，不一致 {bad4} 条")

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
