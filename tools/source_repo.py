# -*- coding: utf-8 -*-
"""SOECN 源码仓库路径解析 —— 全站唯一入口。

**为什么有这个文件**：以前每个工具各自硬编码源码路径，还是两个互不一致的位置
（`/tmp/SOECN` 与 `/tmp/SOECN_repo`）。2026-09-14 机器重启后系统清空了 `/tmp`，
8 个工具同时失效，`refresh_data.py` 第 1 步就挂 —— 源码不在仓库里，丢了只能重新 clone。

**现在**：源码 clone 到**持久目录**（不放 /tmp），所有工具从这里取路径。

    git clone --single-branch --branch SOECN \\
      https://github.com/wdjwxh/PD2-Sanctuary-of-Exile.git \\
      "<工作区>/.sources/SOECN"

解析顺序（先命中先用）：

1. 环境变量 ``SOECN_REPO``
2. ``<项目>/../.sources/SOECN``  ← 推荐位置（工作区级，跨项目复用）
3. ``<项目>/.sources/SOECN``
4. ``/tmp/SOECN_repo`` · ``/tmp/SOECN``（旧位置，仅兼容，重启即失效）

用法::

    from source_repo import repo_root, excel_dir, BASELINE_SHA

    ge = excel_dir()                 # …/SOECN/standard-mode/data/global/excel
    ge = excel_dir("damnation")      # …/SOECN/damnation-mode/data/global/excel
    root = repo_root()               # …/SOECN（找不到时抛出可执行的报错）

自检::

    python3 tools/source_repo.py     # 打印解析结果 + HEAD 是否等于基准 commit
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)

# S1 基准版本（国服正式服）——见 docs/reference/README.md
BASELINE_SHA = "9b24eb72380a724457e8e6d37a169c837f0ad0a0"
BASELINE_LABEL = "9b24eb72"
UPSTREAM_URL = "https://github.com/wdjwxh/PD2-Sanctuary-of-Exile.git"
BRANCH = "SOECN"

MODES = ("standard", "damnation")

CLONE_HINT = (
    "找不到 SOECN 源码仓库。恢复命令（/tmp 会被系统清理，请放持久目录）：\n"
    f'  git clone --single-branch --branch {BRANCH} {UPSTREAM_URL} \\\n'
    f'    "{os.path.join(os.path.dirname(PROJECT_ROOT), ".sources", "SOECN")}"\n'
    "克隆后自检： python3 tools/source_repo.py"
)


def candidates():
    """按优先级返回候选仓库路径。"""
    out = []
    env = os.environ.get("SOECN_REPO")
    if env:
        out.append(os.path.abspath(os.path.expanduser(env)))
    out.append(os.path.join(os.path.dirname(PROJECT_ROOT), ".sources", "SOECN"))
    out.append(os.path.join(PROJECT_ROOT, ".sources", "SOECN"))
    out.append("/tmp/SOECN_repo")
    out.append("/tmp/SOECN")
    return out


def _looks_like_repo(path):
    return any(os.path.isdir(os.path.join(path, f"{m}-mode")) for m in MODES)


def repo_root(required=True):
    """解析 SOECN 仓库根目录。

    ``required=False`` 时找不到返回 None（给可选步骤用），不抛异常。
    """
    for path in candidates():
        if _looks_like_repo(path):
            return path
    if required:
        raise RuntimeError(CLONE_HINT)
    return None


def excel_dir(mode="standard", required=True):
    """返回某模式的 Excel 数据目录（游戏表 .txt 所在处）。"""
    if mode not in MODES:
        raise ValueError(f"mode 只能是 {MODES}，收到 {mode!r}")
    path = os.path.join(repo_root(required=required) or "", f"{mode}-mode",
                        "data", "global", "excel")
    if required and not os.path.isdir(path):
        raise RuntimeError(f"{mode} 模式数据目录不存在：{path}\n{CLONE_HINT}")
    return path


def head_sha(root=None):
    """仓库当前 HEAD commit（读不到返回 None）。"""
    root = root or repo_root(required=False)
    if not root:
        return None
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                           capture_output=True, text=True)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except OSError:
        return None


def main():
    root = repo_root(required=False)
    print(f"基准版本        : {BASELINE_LABEL}（{BASELINE_SHA[:12]}…）")
    print(f"上游            : {UPSTREAM_URL} [{BRANCH}]")
    if not root:
        print("\n❌ 未找到源码仓库（候选路径都为空）")
        for p in candidates():
            print(f"   - {p}")
        print(f"\n{CLONE_HINT}")
        return 1

    print(f"解析到仓库      : {root}")
    if root.startswith("/tmp/"):
        print("⚠️  位置在 /tmp —— 系统重启会被清空，建议挪到 <工作区>/.sources/SOECN")

    sha = head_sha(root)
    if sha is None:
        print("HEAD            : 读不到（不是 git 仓库？）")
    elif sha == BASELINE_SHA:
        print(f"HEAD            : {sha[:7]} ✅ 等于基准 commit")
    else:
        print(f"HEAD            : {sha[:7]} ⚠️  与基准 {BASELINE_LABEL} 不同"
              f"（若是有意升级基准，请同步 README / docs/reference/README.md / "
              f"tools/source_repo.py 的 BASELINE_SHA）")

    ok = True
    for m in MODES:
        p = excel_dir(m, required=False)
        if p and os.path.isdir(p):
            n = len([f for f in os.listdir(p) if f.endswith(".txt")])
            print(f"{m:<15} : {p}（{n} 个 .txt）")
        else:
            ok = False
            print(f"{m:<15} : ❌ 缺失 {p}")

    print("\n✅ 源码仓库可用" if ok else "\n❌ 源码仓库不完整")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
