# -*- coding: utf-8 -*-
"""递归改写 JSON 里的散文字段。

为什么要单独有这个东西
----------------------
标注工具最初只处理「顶层是 list、元素里有 `text`」的结构，于是
`Builds.json`（顶层是 dict：`{updatedAt, classes:[...]}`，散文埋在 6 层深）
被**整个跳过**了 —— 构筑页从来没有图标、也没有符文编号，却没人发现。

所以：**只要输入是一份页面 JSON，就用这里遍历，不要假设它的外形。**
"""
import json
import os

# 这些键下的内容**不是散文**（标识符 / 资源路径 / 枚举），一律跳过。
# 其余**任意层级的字符串**都会处理 —— 页面数据的散文外形五花八门：
# 有的在 `text` 里，有的是 `sections[].items[]` 这种**裸字符串数组**，
# 还有表格 `rows[][]`。只认 `text` 会漏掉一整页（Builds.json 就是这么被漏掉的）。
SKIP_KEYS = {
    # 标识符 / 资源路径 / 枚举
    "id", "name", "enName", "code", "src", "author", "version", "type",
    "slug", "key", "url", "href", "icon", "updatedAt", "modes",
    # 以下字段前端是**纯文本**渲染（不进 markdown），插了标记会露出 `{{icon:xxx}}` 原文，
    # 有的还参与名称匹配（displayName 用于跳转 / 高亮），标了会直接破坏功能
    "displayName", "title", "caption", "displayType", "itemType",
}

# 构筑页（BuildsPanel）按 block.type 决定渲染方式，单独处理：
#   p / hl   → <InlineMd>      ✅ 可以标
#   ul       → items 走 InlineMd ✅ 可以标
#   h2/h3/note/warn/table/imgs/caption → 纯文本 ❌ 不能标
BUILDS_MD_BLOCK_TYPES = {"p", "hl"}
BUILDS_LIST_BLOCK_TYPES = {"ul"}

DEFAULT_KEYS = None  # None = 处理所有非 SKIP_KEYS 下的字符串


def is_skip_key(k):
    """标识性字段判断 —— 前端纯文本渲染、或参与名称匹配的字段一律跳过。

    除了固定黑名单，**所有以 Name 结尾的键**都算（displayName / fourthInputDisplayName /
    itemTypesDisplayNames / uniqueName / baseName …）—— 漏掉一个就会在页面上露出
    `{{icon:xxx}}` 原文（圣化页就是这么漏的）。
    """
    return k in SKIP_KEYS or k.endswith("Name") or k.endswith("Names")


def rewrite_prose(node, fn, keys=DEFAULT_KEYS):
    """递归处理 node 里的散文，返回改动次数。

    keys=None → 处理所有字符串，但跳过 SKIP_KEYS 指定的键。
    keys=(...) → 只处理这些键下的内容。
    """
    changed = 0

    if isinstance(node, dict):
        for k, v in node.items():
            if keys is None and is_skip_key(k):
                continue
            if keys is not None and k not in keys:
                changed += rewrite_prose(v, fn, keys)
                continue

            if isinstance(v, str):
                nv = fn(v)
                if nv != v:
                    node[k] = nv
                    changed += 1
            elif isinstance(v, list):
                for i, line in enumerate(v):
                    if isinstance(line, str):
                        nv = fn(line)
                        if nv != line:
                            v[i] = nv
                            changed += 1
                    else:
                        changed += rewrite_prose(line, fn, keys)
            else:
                changed += rewrite_prose(v, fn, keys)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, str):
                nv = fn(v)
                if nv != v:
                    node[i] = nv
                    changed += 1
            else:
                changed += rewrite_prose(v, fn, keys)

    return changed


def _rewrite_builds(node, fn):
    """Builds.json 专用：只处理真正走 markdown 的 block。"""
    changed = 0

    if isinstance(node, dict):
        t = node.get("type")
        if t in BUILDS_MD_BLOCK_TYPES and isinstance(node.get("text"), str):
            nv = fn(node["text"])
            if nv != node["text"]:
                node["text"] = nv
                changed += 1
            return changed
        if t in BUILDS_LIST_BLOCK_TYPES and isinstance(node.get("items"), list):
            for i, it in enumerate(node["items"]):
                if isinstance(it, str):
                    nv = fn(it)
                    if nv != it:
                        node["items"][i] = nv
                        changed += 1
            return changed
        for k, v in node.items():
            if is_skip_key(k):
                continue
            changed += _rewrite_builds(v, fn)
    elif isinstance(node, list):
        for v in node:
            changed += _rewrite_builds(v, fn)

    return changed


def strip_everywhere(node, pattern):
    """把**所有**字符串里的 pattern 去掉（含被排除的纯文本字段）。

    必须做这一步：字段规则收紧后，之前插进 `displayName`/`caption` 的标记若不清掉，
    就会永久留在数据里，前端会直接把 `{{icon:xxx}}` 显示出来。
    """
    changed = 0

    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                nv = pattern.sub("", v)
                if nv != v:
                    node[k] = nv
                    changed += 1
            else:
                changed += strip_everywhere(v, pattern)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, str):
                nv = pattern.sub("", v)
                if nv != v:
                    node[i] = nv
                    changed += 1
            else:
                changed += strip_everywhere(v, pattern)

    return changed


def process_file(path, fn, keys=DEFAULT_KEYS, check=False, strip_pattern=None):
    """读文件 → 递归改写 → 有变化才写回。返回改动次数。"""
    data = json.load(open(path, encoding="utf-8"))

    n = 0

    # 清理也算改动 —— 否则「只清不标」的文件不会被写回，旧标记会永久残留
    if strip_pattern is not None:
        n += strip_everywhere(data, strip_pattern)

    if os.path.basename(path) == "Builds.json":
        n += _rewrite_builds(data, fn)
    else:
        n += rewrite_prose(data, fn, keys)

    if n and not check:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    return n
