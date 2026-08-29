# 参考文件（Reference Sources）

本站全部「配方/术语/物品」数据的**唯一事实来源**，均来自流放圣域（Sanctuary of Exile，
SOE）游戏模组仓库 [`wdjwxh/PD2-Sanctuary-of-Exile`](https://github.com/wdjwxh/PD2-Sanctuary-of-Exile)
的 `SOECN` 分支。

| 文件 | 说明 | 来源 |
|---|---|---|
| `soe.txt` | 游戏内置**官方中文字符串表**（UTF-16 导出，Tab 分隔：键 → 中文文本）。全站术语唯一标准（颜色控制码已由 `tools/extract_official_zh.py` 清除后存入 `public/data/official_zh.json`） | 模组自带本地化（服务端导出） |
| `CubeMain.standard.txt` | 标准模式魔方配方表（6,801 条启用行） | `standard-mode/data/global/excel/CubeMain.txt` |
| `CubeMain.damnation.txt` | 炼狱（毁灭）模式魔方配方表（6,918 条启用行） | `damnation-mode/data/global/excel/CubeMain.txt` |

**基准版本**：`SOECN` 分支，commit `374d8971`（2026-08-24，`修复时间膨胀护符一秒后失效`）。
更新任一文件时，请同步更新本节以及 `public/data/Cube.json` 顶部的「数据基准」说明。

## 数据流（参考文件 → 页面数据）

```
docs/reference/soe.txt
      │  tools/extract_official_zh.py        清洗颜色码、UTF-16 → UTF-8
      ▼
public/data/official_zh.json                （术语唯一标准，页面可用）

docs/reference/CubeMain.{standard,damnation}.txt
      │  tools/parse_cubemain.py            解析 → 结构化（含来源行号）
      ▼
tools/generated/cube_recipes.json           （gitignore，不入库；随时可重生成）

      ├─ tools/verify_cube_claims.py        → 32 条事实断言（每次改数据后必跑）
      ├─ tools/generate_cube_page.py        → public/data/Cube.json（魔方配方页）
      └─ tools/rebuild_sacreds.py           → public/data/Sacreds.json（圣化宝珠页）
```

一键执行（解析 → 校验 → 生成 → 构建）：`python3 tools/refresh_data.py`

**注意**：
- `tools/generated/` 为生成物目录（已 gitignore），内含每次运行生成的报告与对照表；
  历史对照表（`official_terms.md`、`sacred_orbs.md`、`fate_cards.md`、
  `pending_verification.md`）可直接人工查阅。
- 官方串表与配方数据矛盾时（如圣者宝藏卡片说明 3→2× vs 配方 2→3×），**以 CubeMain 配方为准**。

## 已知限制

- 官方串表未覆盖全部物品（暗金 606 件中仅 221 件、符文之语 209 个中仅 32 个有官方中文名），
  未覆盖的保留本站现有译名。
- 标准模式 `Misc.txt` 等物品表滞后于实际游戏（如恰西的工艺箱/基德的珍奇箱只有串表条目）；
  以 `soe.txt` + 配方表交叉核验为准，不一致项见 `tools/generated/pending_verification.md`。
