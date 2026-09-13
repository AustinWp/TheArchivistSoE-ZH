# -*- coding: utf-8 -*-
"""核对「掉落计算器」用到的游戏数据表是否与国服源码一致。

计算器读取 `public/data/<mode>/*.txt` 共 10 张表。其中：
- **炼狱模式只覆盖 6 张**（CubeMain / Misc / MonStats / SuperUniques / TreasureClassEx / UniqueItems），
  其余表在客户端里是编译好的 `.bin`，源码仓库不提供 → 本地副本应当与**标准模式**的那张一致；
- 若干列是**中文化副本**（物品名 `index`、地名 `LevelName`/`Name`、`MonStats.NameStr`），
  这些列的差异属预期，比对时跳过。

用法:
    python3 tools/verify_dropcalc_tables.py --repo /tmp/SOECN_repo \
        --sha 9b24eb72380a724457e8e6d37a169c837f0ad0a0
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TABLES = ["MonStats.txt", "TreasureClassEx.txt", "Weapons.txt", "Armor.txt", "Misc.txt",
          "UniqueItems.txt", "SetItems.txt", "ItemRatio.txt", "ItemTypes.txt", "Levels.txt"]

# 炼狱模式在源码里覆盖了哪些表；其余回落标准模式（源码中为 .bin）
DAMNATION_OVERRIDES = {"CubeMain.txt", "Misc.txt", "MonStats.txt", "SuperUniques.txt",
                       "TreasureClassEx.txt", "UniqueItems.txt"}

# 中文化列（差异属预期）
TRANSLATED = {
    "MonStats.txt": {"NameStr"},
    "UniqueItems.txt": {"index"},
    "SetItems.txt": {"index"},
    "Levels.txt": {"LevelName", "Name"},
}


def show(repo, sha, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True)
    if r.returncode:
        return None
    return r.stdout.decode("utf-8-sig", "replace")


def rows(text):
    return [l for l in text.replace("\r\n", "\n").split("\n") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--sha", required=True)
    args = ap.parse_args()

    problems = 0
    print(f"基准: {args.repo} @ {args.sha[:7]}\n")

    for mode in ("standard", "damnation"):
        print(f"===== {mode} 模式 =====")
        for t in TABLES:
            if mode == "damnation" and t not in DAMNATION_OVERRIDES:
                src_mode, note = "standard", "（炼狱未覆盖 → 应等于标准版）"
            else:
                src_mode, note = mode, ""

            repo_txt = show(args.repo, args.sha,
                            f"{src_mode}-mode/data/global/excel/{t}")
            if repo_txt is None:
                print(f"  {t:20} 源码里没有 ❓")
                continue

            local_path = os.path.join(ROOT, "public", "data", mode, t)
            if not os.path.exists(local_path):
                print(f"  {t:20} 本地缺失 ❌ {note}")
                problems += 1
                continue

            remote = rows(repo_txt)
            local = rows(open(local_path, encoding="utf-8-sig", errors="replace").read())

            if len(remote) != len(local):
                print(f"  {t:20} 行数不同 源码 {len(remote)} vs 本地 {len(local)} ❌ {note}")
                problems += 1
                continue

            header = local[0].split("\t")
            skip = TRANSLATED.get(t, set())
            diff = {}
            for a, b in zip(remote[1:], local[1:]):
                fa, fb = a.split("\t"), b.split("\t")
                for j in range(max(len(fa), len(fb))):
                    va = fa[j] if j < len(fa) else ""
                    vb = fb[j] if j < len(fb) else ""
                    if va != vb:
                        col = header[j] if j < len(header) else f"col{j}"
                        if col in skip:
                            continue
                        diff[col] = diff.get(col, 0) + 1

            if diff:
                print(f"  {t:20} 有差异 ❌ {note}: {dict(list(diff.items())[:6])}")
                problems += 1
            else:
                print(f"  {t:20} ✅ 一致 {note}")
        print()

    print("结论:", "✅ 全部与国服源码一致（仅中文化列存在预期差异）"
          if not problems else f"⚠️ {problems} 处不一致")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
