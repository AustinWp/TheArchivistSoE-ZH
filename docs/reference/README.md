# 参考文件（Reference Sources）

本站全部「配方/术语/物品」数据的**唯一事实来源**，均来自流放圣域（Sanctuary of Exile，
SOE）游戏模组仓库 [`wdjwxh/PD2-Sanctuary-of-Exile`](https://github.com/wdjwxh/PD2-Sanctuary-of-Exile)
的 `SOECN` 分支。

| 文件 | 说明 | 来源 |
|---|---|---|
| `soe.txt` | 游戏内置**官方中文字符串表**（UTF-16 导出，Tab 分隔：键 → 中文文本）。全站术语唯一标准（颜色控制码已由 `tools/extract_official_zh.py` 清除后存入 `public/data/official_zh.json`） | 模组自带本地化（服务端导出） |
| `CubeMain.standard.txt` | 标准模式魔方配方表（6,801 条启用行） | `standard-mode/data/global/excel/CubeMain.txt` |
| `CubeMain.damnation.txt` | 炼狱（毁灭）模式魔方配方表（6,874 条启用行） | `damnation-mode/data/global/excel/CubeMain.txt` |

**基准版本**：`SOECN` 分支，commit `9b24eb72`（2026-09-11，国服 SOL **第一赛季（S1）正式服版本**；上一基准 `374d8971`，2026-08-24）。
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
- 游戏当前版本不存在（未上线/占位）的条目，本站一律**不收录、不提示**；验证记录与处置结论见
  [`verification-notes.md`](verification-notes.md)（含日后恢复指引）。

## 已知限制

- 官方串表未覆盖全部物品（暗金 606 件中仅 221 件、符文之语 209 个中仅 32 个有官方中文名），
  未覆盖的保留本站现有译名。
- 标准模式 `Misc.txt` 等物品表滞后于实际游戏（部分条目只有串表条目并无物品定义）；
  交叉核验以两模式 `misc.bin`（游戏实际加载的物品表）为准，结论见 `verification-notes.md`。


---

## 国服客户端中文串表（2026-09-14 起纳入基准）

除 `soe.txt`（服务端导出）外，**国服客户端**自带一份中文串表，这才是游戏真正加载、玩家看到的东西：

| 文件 | 条数 | 说明 |
|---|---|---|
| `string.tbl` | 5391 | 基础游戏（D2 classic）|
| `expansionstring.tbl` | 2818 | 资料片 |
| `PatchString.tbl` | 4616 | 补丁（**PD2 新增串最多**：`mfo`/`exo`/`ncoi` 等只在这里）|

来源：客户端包（如 `PD2-SOE-战网.zip`）里的 `Diablo II/SoE/Data/local/Lng/Chi/`。
解出后放 `<工作区>/.sources/client-zh/`（不入库，路径可用 `$CLIENT_ZH` 覆盖）。

**格式与坑（都实测踩过，别再重新发现）**：

1. `.tbl` 是 **UTF-8 的 `key\0value\0` 序列**，文件头 `word@2` = 条数；同目录的 `.txt` 是**旧导出**
   （08-16 vs `.tbl` 09-02），会给出过期值（`Blank` 旧 txt 写「空无」，实为「虚无」）→ **以 `.tbl` 为准**。
2. 查找优先级 **PatchString > ExpansionString > String**，键名大小写不敏感。
3. **`<key>_pd2` 覆盖键**（126 个）：PD2 用它顶替基础串，游戏显示 `_pd2` 的值
   （`skillname17_pd2` = 迟缓，而 `skillname17` 是旧名「慢速箭」）。比对/合并都必须先查它。
4. 值里带颜色码（`ÿc1`）与英文名（`军帽 Shako`）→ 清洗时**只剥「空白 + 字母开头、长度 ≥2」的尾巴**，
   否则会把格式符剥掉（`所有抗性 +%d` 曾被剥成 `所有抗性 +%`）。
5. `.tbl` 用**真换行**，本站数据历来用字面 `\n` → 入库时转换。

工具：`tools/verify_client_zh.py`（校验）、`tools/apply_client_zh.py`（对齐）、`tools/client_zh.py`（唯一加载入口）。
