# -*- coding: utf-8 -*-
"""同步「掉落计算器」使用的游戏数据表到指定 SOECN 提交。

掉落计算器读取 `public/data/<mode>/*.txt`，这些表是上游 SOE 数据表的**中文化副本**
（仅少量列被译为中文，例如 `MonStats.txt` 的 `NameStr`）。本工具：

1. 从上游仓库按提交取出目标版本的表；
2. 对含中文列的表，**保留**本地译文（按首列主键匹配），其余列替换为上游新值；
3. 校验行数 / 列数是否一致，不一致则中止，避免破坏计算器。

用法:
    python3 tools/sync_dropcalc_tables.py \
        --repo /tmp/SOECN_repo --sha 9b24eb72380a724457e8e6d37a169c837f0ad0a0 [--check]

`--check` 只报告差异，不写文件。
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# (模式, 文件名, 上游相对路径模板, 需要保留中文的列)
TABLES = [
    ("damnation", "TreasureClassEx.txt", "damnation-mode/data/global/excel/TreasureClassEx.txt", []),
    ("damnation", "MonStats.txt", "damnation-mode/data/global/excel/MonStats.txt", ["NameStr"]),
    ("standard", "MonStats.txt", "standard-mode/data/global/excel/MonStats.txt", ["NameStr"]),
]


def show(repo, sha, path):
    out = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"],
                         capture_output=True)
    if out.returncode:
        raise SystemExit(f"git show 失败: {sha}:{path}\n{out.stderr.decode('utf-8', 'replace')}")
    return out.stdout.decode("utf-8-sig", "replace")


def to_rows(text):
    lines = text.replace("\r\n", "\n").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    return [l.split("\t") for l in lines]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="SOECN 仓库本地路径")
    ap.add_argument("--sha", required=True, help="目标提交")
    ap.add_argument("--check", action="store_true", help="只报告差异，不写文件")
    args = ap.parse_args()

    total_changed = 0
    for mode, fname, rel, keep_cols in TABLES:
        dst = os.path.join(ROOT, "public", "data", mode, fname)
        if not os.path.exists(dst):
            print(f"跳过（本地不存在）: {mode}/{fname}")
            continue

        src_rows = to_rows(show(args.repo, args.sha, rel))
        dst_rows = to_rows(open(dst, encoding="utf-8").read())

        if len(src_rows) != len(dst_rows):
            raise SystemExit(f"行数不一致，中止: {mode}/{fname} 上游 {len(src_rows)} vs 本地 {len(dst_rows)}")
        if src_rows[0] != dst_rows[0]:
            raise SystemExit(f"表头不一致，中止: {mode}/{fname}")

        hdr = src_rows[0]
        # 主键 → 译文列
        keep_idx = [hdr.index(c) for c in keep_cols if c in hdr]
        trans = {}
        for r in dst_rows[1:]:
            if not r or not r[0]:
                continue
            trans[r[0]] = {i: r[i] for i in keep_idx if i < len(r)}

        changed = 0
        out_rows = [src_rows[0]]
        for r in src_rows[1:]:
            row = list(r)
            t = trans.get(row[0] if row else "")
            if t:
                for i, v in t.items():
                    if v and i < len(row) and row[i] != v:
                        changed += 1
                        row[i] = v
            out_rows.append(row)
        # 与本地逐格比较（统计真实差异）
        real = sum(1 for a, b in zip(out_rows, dst_rows)
                   for x, y in zip(a, b) if x != y)

        print(f"{mode}/{fname}: 保留中文列 {keep_cols or '（无）'} · 还原译文 {changed} 格 · 实际更新 {real} 格")
        total_changed += real

        if not args.check and real:
            with open(dst, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join("\t".join(r) for r in out_rows) + "\n")

    print(f"合计更新 {total_changed} 格" + ("（--check，未写文件）" if args.check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
