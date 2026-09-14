# -*- coding: utf-8 -*-
"""官方中文字符串表提取器 —— **全站术语唯一标准** `public/data/official_zh.json`。

两个来源，**客户端优先**（客户端才是游戏真正加载、玩家看到的东西）：

| 来源 | 说明 |
|---|---|
| `docs/reference/soe.txt` | 服务端导出的模组串表（UTF-16，Tab 分隔）|
| 国服客户端 `SoE/Data/local/Lng/Chi/*.tbl` | 游戏实际加载的串表（UTF-8 `key\\0value\\0`）。比旧 `.txt` 导出新且全（`PatchString` 多 1636 条）|

合并规则（三个坑，都实测踩过）：

1. **客户端优先**，客户端没有的键保留 soe.txt 的值（模组自定义文案）；
2. **`<key>_pd2` 覆盖键优先** —— PD2 用 `_pd2` 变体顶替基础串，游戏显示的是 `_pd2` 的值；
3. **键名大小写不敏感合并** —— 否则会留下 `StrEternalDemonHead` 与 `StrEternalDemonhead`
   两份键，取值时命中旧的那份。

值会清掉颜色控制码（`\\red;` / `ÿc1`）与尾部英文名（`军帽 Shako` → `军帽`），
并把真换行转成本站约定的字面 `\\n`。

用法::

    python3 tools/extract_official_zh.py                       # soe.txt + 客户端
    python3 tools/extract_official_zh.py --no-client           # 只用 soe.txt
    python3 tools/extract_official_zh.py --src xxx.txt --client <目录>
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from client_zh import load_client_table, resolve_dir, strip_english  # noqa: E402

COLOR_RE = re.compile(r"\\[a-z]+;")
HEXCOLOR_RE = re.compile(r"[\ufffd\u00ff]c[0-9a-zA-Z;:/]")   # ÿc1 / ÿc/ / ÿc;
HAS_ZH = re.compile(r"[\u4e00-\u9fff]")


def clean(text):
    """去颜色控制码 + 尾部英文名；真换行转成本站约定的字面 `\\n`。

    客户端 .tbl 里存的是真换行（0x0A），而 soe.txt / 本站数据历来用字面 `\\n`
    两字符表示换行 —— 不转的话会把新格式混进下游渲染。
    """
    t = COLOR_RE.sub("", str(text))
    t = HEXCOLOR_RE.sub("", t)
    t = t.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")
    return strip_english(t)


def extract_soe(src):
    """soe.txt（UTF-16 或 UTF-8）→ {key: 中文}，仅含含中文的非空条目。"""
    data = open(src, "rb").read()
    try:
        text = data.decode("utf-16")
    except UnicodeDecodeError:
        text = data.decode("utf-8-sig", errors="replace")
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        key, val = line.split("\t", 1)
        key = key.strip()
        if not key or not val.strip() or not HAS_ZH.search(val):
            continue
        out[key] = clean(val)
    return out


def extract_client(directory):
    """客户端三张串表 → {key: 中文}（`_pd2` 覆盖键优先；大小写不敏感合并）。"""
    table, _, _ = load_client_table(directory)

    def has_zh(v):
        return bool(v) and bool(HAS_ZH.search(v))

    out, lower_index = {}, {}

    def put(key, value):
        low = key.lower()
        target = lower_index.get(low, key)      # 已有同形键就覆盖它，不产生大小写重复键
        out[target] = value
        lower_index[low] = target

    for _lower, (key, value) in table.items():              # 先铺基础值
        if not key.lower().endswith("_pd2") and has_zh(value):
            put(key, clean(value))
    for _lower, (key, value) in table.items():              # 再用 _pd2 覆盖
        if key.lower().endswith("_pd2") and has_zh(value):
            put(key[: -len("_pd2")], clean(value))
    return out


def default_soe():
    for c in [os.path.join(ROOT, "docs", "reference", "soe.txt"),
              os.path.expanduser("~/Downloads/soe.txt")]:
        if os.path.exists(c):
            return c
    return os.path.join(ROOT, "docs", "reference", "soe.txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=default_soe(), help="soe.txt 路径")
    ap.add_argument("--client", default=None, help="客户端 Chi 串表目录（默认自动解析）")
    ap.add_argument("--no-client", action="store_true", help="不合并客户端串表")
    ap.add_argument("--out", default=os.path.join(ROOT, "public", "data", "official_zh.json"))
    args = ap.parse_args()

    if not os.path.exists(args.src):
        print(f"找不到 soe.txt: {args.src}")
        return 1

    names = extract_soe(args.src)
    # soe.txt 内部也可能有只差大小写的重复键（StrEternalDemonHead / StrEternalDemonhead），
    # 先按小写去重，否则合并后仍是两份、取值会命中旧的那份。
    dedup, seen = {}, set()
    for k, v in names.items():
        if k.lower() in seen:
            continue
        seen.add(k.lower())
        dedup[k] = v
    names = dedup
    sources = [f"soe.txt（{len(names)} 条含中文）"]

    client_dir = None if args.no_client else resolve_dir(args.client)
    if client_dir:
        cn = extract_client(client_dir)
        lower_index = {k.lower(): k for k in names}
        overridden = added = 0
        for k, v in cn.items():
            tgt = lower_index.get(k.lower())
            if tgt is not None:
                if names[tgt] != v:
                    overridden += 1
                names[tgt] = v
            else:
                names[k] = v
                lower_index[k.lower()] = k
                added += 1
        sources.append(f"国服客户端串表（{len(cn)} 条含中文：覆盖 {overridden}、新增 {added}）")
        print(f"客户端串表: {client_dir}")
    else:
        sources.append("国服客户端串表：**未合并**")

    meta = {
        "source": " + ".join(sources),
        "description": "键 -> 官方中文名（客户端优先）。已清除颜色控制码与尾部英文名；仅含含中文的条目。",
        "count": len(names),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "names": names}, f, ensure_ascii=False, indent=1)
    print(f"OK  {len(names)} 条 -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
