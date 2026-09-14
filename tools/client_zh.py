# -*- coding: utf-8 -*-
"""国服客户端中文串表：**唯一**加载与归一化入口。

为什么单独一个模块
------------------
客户端的键值约定有几个坑，任何一个写错都会得出完全相反的结论（曾据此误判 191 条术语）：

1. **以 `.tbl` 为准，`.txt` 是旧导出**。`SoE/Data/local/Lng/Chi/` 下同时有 `.tbl`（09-02）
   与 `.txt`（08-16）；`.tbl` 是游戏实际加载的文件，`PatchString.tbl` 比旧 txt 多 1636 条
   （PD2 新增串 `mfo`/`exo`/`ncoi` 都在里面）。旧 txt 还会给出过期值（`Blank` 写「空无」，实为「虚无」）。
   `.tbl` 的格式是 UTF-8 的 `key\\0value\\0` 序列，文件头 `word@2` = 条数。
2. **查找优先级 PatchString > ExpansionString > String**（与游戏一致），键名大小写不敏感
   （`Skillname224` 与 `skillname80` 并存）。
3. **`<key>_pd2` 覆盖键**：PD2 用 126 个 `_pd2` 键顶替基础串（例：`skillname17_pd2` = 迟缓，
   而 `skillname17` 是旧名「慢速箭」）。**游戏优先用 `_pd2`**，比对时必须先查它，否则会误报。
4. **值里带颜色码与英文名**：`ÿc1神话宝珠`、`军帽 Shako`。比对与落库前都要清洗。

用法::

    from client_zh import load_client_table, client_value, norm, strip_english

    table, per_file, source = load_client_table()      # 目录自动解析
    key, value = client_value(table, "hax")            # ('hax', '手斧')，自动优先 _pd2
"""
import os
import re
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TBL_FILES = [("string", "String.txt"),
             ("expansionstring", "expansionstring.txt"),
             ("PatchString", "PatchString.txt")]          # 优先级由低到高

_ICON = re.compile(r"\{\{icon:[^}]+\}\}")
_COLOR = re.compile(r"[\ufffd\u00ff]c[0-9a-zA-Z;:/]")     # ÿc1 / ÿc/ / ÿc;
_ESCAPE = re.compile(r"\\[a-zA-Z]+;")                     # \purple; \gold;
# 尾部英文名：**必须**前面有空白，且英文以字母开头、总长 ≥2 ——
# 否则会把格式符剥掉（`所有抗性 +%d` 曾被剥成 `所有抗性 +%`，真事故）。
_ASCII_TAIL = re.compile(r"[\s\u3000]+\(?[A-Za-z][A-Za-z0-9'’\-.,()/&! ]{1,}\)?$")


def norm(text, strip_en=True):
    """归一化：去图标标记 / 颜色码 / 转义 / 空白 / 全角差异；可选去掉尾部英文名。"""
    if text is None:
        return ""
    s = str(text)
    s = _ICON.sub("", s)
    s = s.replace("\\n", " ").replace("\n", " ").replace("\t", " ")
    s = _COLOR.sub("", s)
    s = _ESCAPE.sub("", s)
    s = s.replace("－", "-").replace("—", "-").replace("：", ":").replace("＋", "+")
    s = re.sub(r"^[\d\s]+", "", s)                        # 对话串开头的行数
    s = re.sub(r"[\s\u3000]+", " ", s).strip()
    if strip_en:
        prev = None
        while prev != s:
            prev = s
            s = _ASCII_TAIL.sub("", s).strip()
    return re.sub(r"[\s\u3000]+", "", s)


def strip_english(text):
    """去掉尾部英文名（`军帽 Shako` → `军帽`、`召唤灰熊 (Summon Grizzly)` → `召唤灰熊`）。

    ⚠️ 只剥「空白 + 字母开头、长度 ≥2」的尾巴 —— 早期版本会把 `所有抗性 +%d` 剥成
    `所有抗性 +%`（格式符被当英文名），务必保持这条约束。
    """
    if text is None:
        return ""
    s = _COLOR.sub("", str(text)).strip()
    prev = None
    while prev != s:
        prev = s
        s = _ASCII_TAIL.sub("", s).strip()
    return s.strip()


def client_candidates():
    out = []
    env = os.environ.get("CLIENT_ZH")
    if env:
        out.append(os.path.abspath(os.path.expanduser(env)))
    out.append(os.path.join(os.path.dirname(ROOT), ".sources", "client-zh"))
    out.append(os.path.join(ROOT, ".sources", "client-zh"))
    return out


def resolve_dir(directory=None):
    if directory:
        return directory if os.path.isdir(directory) else None
    for c in client_candidates():
        if os.path.isdir(c) and (os.path.exists(os.path.join(c, "PatchString.tbl"))
                                 or os.path.exists(os.path.join(c, "PatchString.txt"))):
            return c
    return None


def _find_data_start(raw, txt_path):
    """定位 .tbl 数据区起点（优先用同目录 .txt 的首个 key；否则向后扫描）。"""
    if txt_path and os.path.exists(txt_path):
        for line in open(txt_path, encoding="utf-16").read().splitlines():
            if "\t" in line:
                k = line.split("\t", 1)[0].strip()
                if k and k != "String Index":
                    off = raw.find(k.encode("utf-8"))
                    if off >= 0:
                        return off
    for i in range(len(raw) - 8):
        if i and raw[i - 1] != 0:
            continue
        j = raw.find(b"\x00", i, i + 80)
        if j < 0 or not (2 <= j - i <= 64) or not all(32 <= c < 127 for c in raw[i:j]):
            continue
        k2 = raw.find(b"\x00", j + 1, j + 1 + 2000)
        if k2 < 0:
            continue
        try:
            raw[j + 1:k2].decode("utf-8")
        except UnicodeDecodeError:
            continue
        return i
    return None


def load_client_table(directory=None):
    """返回 (table, per_file, source)。

    ``table`` 的键是 **小写 key**，值是 ``(原始 key, 值)``。
    """
    directory = resolve_dir(directory)
    if not directory:
        raise RuntimeError(
            "找不到客户端串表目录。把 Chi 串表放到 <工作区>/.sources/client-zh"
            "（从 PD2-SOE-战网.zip 的 Diablo II/SoE/Data/local/Lng/Chi/ 解出），"
            "或用 $CLIENT_ZH / 参数指定。")
    table, per_file, source = {}, {}, {}
    for stem, txt_name in TBL_FILES:
        tbl = os.path.join(directory, stem + ".tbl")
        txt = os.path.join(directory, txt_name)
        pairs = None
        if os.path.exists(tbl):
            raw = open(tbl, "rb").read()
            count = struct.unpack_from("<H", raw, 2)[0]
            start = _find_data_start(raw, txt)
            if start is not None:
                parts = raw[start:].split(b"\x00")
                pairs = {}
                for i in range(min(count, len(parts) // 2)):
                    k = parts[2 * i].decode("utf-8", "replace").strip()
                    if k:
                        pairs[k] = parts[2 * i + 1].decode("utf-8", "replace")
                source[stem] = "tbl"
        if pairs is None and os.path.exists(txt):
            pairs = {}
            for line in open(txt, encoding="utf-16").read().splitlines():
                if "\t" in line:
                    k, v = line.split("\t", 1)
                    if k.strip() and k.strip() != "String Index":
                        pairs[k.strip()] = v
            source[stem] = "txt（旧导出）"
        if not pairs:
            continue
        per_file[stem] = len(pairs)
        for k, v in pairs.items():
            table[k.lower()] = (k, v)
    return table, per_file, source


def client_value(table, key, prefer_pd2=True):
    """查客户端值：**优先 `<key>_pd2`**（PD2 覆盖约定）；返回 (原始 key, 值)。"""
    if key is None:
        return None, None
    k = str(key).strip().lower()
    if prefer_pd2:
        hit = table.get(k + "_pd2")
        if hit:
            return hit
    return table.get(k, (None, None))


CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def official_name(table, key, prefer_pd2=True):
    """客户端官方中文名（去尾部英文名）。

    **必须含中文**才返回，否则返回 None —— 源表里有大量占位行（`Name=Dummy`、
    以及客户端值本身就是英文的键），把它们当"官方名"写进数据会把名字改成 `Dummy`
    （2026-09-14 实测踩过 12 条词缀）。
    """
    _key, value = client_value(table, key, prefer_pd2=prefer_pd2)
    if not value:
        return None
    name = strip_english(value)
    if not name or not CJK_RE.search(name):
        return None
    return name
