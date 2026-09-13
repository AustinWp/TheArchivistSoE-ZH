# -*- coding: utf-8 -*-
"""一键刷新：解析官方数据 → 校验 → 重新生成页面数据与对照表。

用法: python3 tools/refresh_data.py
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("解析 CubeMain（生成结构化配方）", ["python3", "parse_cubemain.py"]),
    ("事实断言校验（含表格自检）", ["python3", "verify_cube_claims.py"]),
    ("生成魔方配方页 Cube.json", ["python3", "generate_cube_page.py"]),
    ("重建圣化宝珠页 Sacreds.json", ["python3", "rebuild_sacreds.py"]),
    ("生成术语/宝珠/命运卡对照表", ["python3", "generate_terms_md.py"]),
    ("生成国服S1赛季页数据", ["python3", "generate_season_page.py"]),
    ("从游戏表重建武器/护甲（保留中文）", ["python3", "build_item_tables.py"]),
    ("官方属性术语全站替换", ["python3", "apply_zh_terms.py"]),
    ("底材名对齐官方串表", ["python3", "apply_official_item_names.py"]),
    ("重建暗金引用（各基底上的暗金）", ["python3", "rebuild_unique_refs.py"]),
    ("配方页物品图标标注", ["python3", "annotate_item_icons.py"]),
    ("符文名补编号", ["python3", "annotate_rune_numbers.py"]),
    ("官方术语一致性审计", ["python3", "audit_official_terms.py"]),
    ("构建站点", ["npm", "run", "build"]),
]

def main():
    failures = []
    for label, cmd in STEPS:
        print(f"\n>>> {label}: {' '.join(cmd)}")
        r = subprocess.run(cmd, cwd=(HERE if cmd[0] == "python3" else os.path.dirname(HERE)))
        if r.returncode:
            failures.append(label)
            print(f"!! 失败: {label}")
            break
    if failures:
        sys.exit(1)
    print("\n全部步骤通过。")


if __name__ == "__main__":
    main()
