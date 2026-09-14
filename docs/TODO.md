# 待办与注意事项

> **最后更新**：2026-09-14
> **当前状态**：14 项审计全绿 · **45 条**断言通过 · `npm run lint` **0 error / 4 warning** · 本地已提交，**未推送**（push 后 Actions 自动发布）
> 源码仓库已恢复到 `<工作区>/.sources/SOECN`（不再放 `/tmp`），自检：`python3 tools/source_repo.py`
> 本文是「下次继续」的入口；具体规则细节在 [`../README.md`](../README.md)，本文只做索引与待办。

---

## 一、待办事项（按优先级）

### P0 · 值得做

**1. 给 `Uniques.json` 的属性串做校验（推荐先只做校验，不改数据）**

- **为什么**：582 条暗金的 `displayProperties`（如「+40-50% 强化伤害」）是早期翻译脚本的产物，**从未被任何审计校验过**。
  今天已经证实同类遗留数据里藏着成批错误（名字 4500 处、炼狱版暗金表整份损坏）。
- **可行性高**：这批数据有结构化字段 `{displayString, property, min, max}`，
  可以从现有条目**反推「属性码 → 中文模板」**（例：`ac%` 20-30 → `+20-30% 增强防御`）。
- **建议分两步**：
  1. **只做校验**：用模板回算每条属性串，与 `displayString` 比对，报出不一致 → **不改任何数据**，先看错多少；
  2. 校验干净后，再考虑用它生成缺失条目。
- ⚠️ **别把同样的思路用在 `Affixes.json` 上** —— 词缀那条路已试过并证明走不通
  （源码有 141 行是同一条词缀按物品类型重复登记；两组数据 key 对不齐，既缺 273 又多 226）。详见 README「4.3.2 已知缺口」。
- **起点不是零**：`tools/unique_prop_parser.py`（中文属性串解析器）+ `tools/unique_prop_diff.py`（桥接 221 件暗金做数值 diff）
  早在 2026-08-30 就写过，README §4.5 有登记。但 `tools/generated/` 是 gitignored → **当时那份报告已丢，要重跑一次**。

**2. 国服「神授宝珠」问题简报 —— 已写好，是否发出由你定**

- 文件：[`docs/reference/issue-divine-orb-damnation.md`](reference/issue-divine-orb-damnation.md)
- **结论已更正过**：不是「狱铸装备拿不到」，而是「**定向**路线不可用 + 32 条启用配方成为死配方」
  （狱铸暗金本身在炼狱模式 `enabled=1`、`rarity` 1~5，照常掉落）。
- 含可运行的复现命令（实测输出 32 行、行号一致）。

### P1 · 质量

| # | 事项 | 说明 |
|---|---|---|
| 3 | 剩 4 条 lint warning | 都是 React Hook 依赖提示，历史遗留、无功能影响。**不要再抬高这个数字** |
| 4 | S1 中文文案无法验证 | 技能描述、狼人变化中文名等只存在于客户端文案，仓库只有英文。需要国服客户端文案或截图 |
| 5 | 47 个代码没有中文名 | 任务物品 / 内部占位（如 `tpfs`、`decoy dagger`），PD2 汉化 wiki 也没收录 —— 不影响展示 |

### P2 · 结构性（不急）

**6. 还有 3 个数据文件没有生成器**：`Uniques.json` · `Affixes.json` · `Runewords.json`
（`Weapons.json` / `Armors.json` 已由 `tools/build_item_tables.py` 从游戏表生成；
`SkillsData.json` 已由 `tools/gen_skills_data.py` 生成 —— **2026-09-14 订正，原文写「4 个」有误**）

今天 5 个数据 bug 全部出自这类「手改产物」，所以长期看值得逐个收编 —— 但只有 Uniques 的性价比最高（见 P0-1）；
Affixes 那条路已证走不通（§4.3.2），Runewords 目前无已知问题。

---

## 二、注意事项（每次改数据前先看）

**先读 README 的「更新注意事项」**，其中与本仓库最相关的几节：

| 章节 | 内容 |
|---|---|
| §0 | 物品数据来自生成器，**不要手改** Weapons/Armors |
| §0.1 | 国服实际运行**炼狱（毁灭）模式**，站点默认也是它 |
| §1 | 口径规则：代码有改动的以代码为准，代码没有的以说明为准 |
| §2 | **术语源不能批量替换**（`official_zh.json` 是唯一权威） |
| §4.2 / §4.2.1 | 物品名有 **5 个字段**，`displayName` 才是前端渲染用的 |
| §4.4 | 加标记只能加在 **markdown 渲染**的字段 |
| §4.5 | 按需运行的诊断工具清单 |

### 三条铁律

1. **不要手改生成物** —— `Weapons.json` / `Armors.json` / `Cube.json` / `Sacreds.json` / `SeasonS1.json`
   会在下次 `refresh_data.py` 时被覆盖，而且手改正是过去反复出错的根源。
2. **「对不上」时先把它变成可见的例外（写清理由），不要编一个值填上** ——
   例：`驯服` 曾被登记为「无法重建」的例外，后来查明是方块合成产物并补录；
   词缀缺口至今仍是「无法可靠枚举 → 不做」。
3. **改完必须自检**：
   ```bash
   python3 tools/refresh_data.py     # 14 项审计 + 45 条断言，必须全绿
   npm run lint                      # 不得高于 4 problems（0 error / 4 warning）
   ```

---

## 三、环境与常用命令

```bash
# 仓库（站点）
cd "/Users/austin/Desktop/日常AI目录/PD2-SOL-WIKI/TheArchivistSoE-ZH"

python3 tools/refresh_data.py      # 一键流程：解析→校验→生成→术语→审计→构建
python3 tools/audit_official_terms.py   # 14 项审计（单独跑）
npm run lint && npm run build

# 国服源码仓库（核对用；不入库）—— 位置由 tools/source_repo.py 统一解析，别再硬编码
../.sources/SOECN                  # 工作区级持久目录（⚠️ 不要放 /tmp：系统清理后 8 个工具会集体失效）
python3 tools/source_repo.py       # 自检：解析到的路径 + HEAD 是否等于基准 commit 9b24eb72
python3 tools/verify_dropcalc_tables.py   # --repo / --sha 可省，默认自动解析

# 部署：push main 后 GitHub Actions 自动发布
git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push origin main
# 网络需要本地代理 127.0.0.1:7897（git 与 curl 都要带）
```

**部署校验**：轮询 `https://api.github.com/repos/AustinWp/TheArchivistSoE-ZH/actions/runs?per_page=1`
直到 `conclusion == success`，再抽查线上数据文件。

---

## 四、2026-09-13 已完成（简要）

| 类别 | 内容 |
|---|---|
| **赛季发布** | 国服 S1 赛季页、说明 ↔ 代码交叉验证、数据基准升到 `9b24eb72` |
| **数据正确性** | 底材名对齐官方 **~4500 处**（含 `StrEternal` 机制、炼狱版漏改、嵌套阶位名）；钥匙命名；旧符文名；狱铸前缀；**重建损坏的炼狱版暗金表**（缺 57 / 重复 59） |
| **根治手改** | 新增 `build_item_tables.py`：武器/护甲从游戏表生成（顺带修出盾牌伤害 0→1~3 等） |
| **功能修复** | 掉落计算器卡死 100s→1s + 引导；图标全站 ~1200 处；符文编号全站；「驯服」补录 |
| **口径呈现** | 默认炼狱模式；不支持内容标红置底；合成次数只写结果；魔方页把机遇宝珠/炼狱专属提到最前 |
| **机制加固** | 审计 3 → **14 项**；唯一解析入口 `official_names.py`；`textwalk.py`；两篇事故复盘 |
| **清理** | 废弃翻译脚本/旧词典/过期研究文档/样式 mockup/6.4 MB 死文件；lint 11 errors → 0 |

### 2026-09-14 补充

| 类别 | 内容 |
|---|---|
| **环境加固** | 源码仓库从 `/tmp` 迁到 `<工作区>/.sources/SOECN`。起因：`/tmp` 被系统清理后 **8 个工具集体失效**，`refresh_data.py` 第 1 步就挂（源码不在仓库里，丢了只能重下）。新增 `tools/source_repo.py` 作**路径唯一入口**，8 个工具改为向它取路径，顺手消掉 `/tmp/SOECN` 与 `/tmp/SOECN_repo` 两套不一致的硬编码；`verify_dropcalc_tables.py` / `sync_dropcalc_tables.py` 的 `--repo` / `--sha` 变成可省 |
| **文档订正** | ① TODO 里失效的简报链接（真实位置 `docs/reference/`）；② P2-6「4 个数据文件没有生成器」→ 实为 **3 个**（`SkillsData.json` 早有 `gen_skills_data.py`）；③ README §4.5 里**已作废的「词缀缺 196 条」**数字清掉；④ 标注 `docs/SOE战网经济平衡TODO.md` 并不在本仓库 |

---

## 五、今天踩过的坑（下次别再踩）

1. **物品名有 5 个字段**（`name` / `displayName` / 普通·扩展·精英三个阶位名）——
   只改 `name` 页面**不会变**（前端渲染用 `displayName`）；暗金里还有一层嵌套基底要一起改。
2. **两份模式数据必须同步** —— `damnation/Uniques.json` 曾整份损坏而无人察觉（默认视图加载的就是它）。
   现在审计 **3g** 盯住「两份表条目集合一致」。
3. **标记只能加在 markdown 渲染的字段**（名字类字段都是纯文本，加了会露出 `{{icon:xxx}}` 原文）；
   渲染器遇到**加粗里夹标记**要递归解析。审计 **6** 盯住这一点。
4. **页面 JSON 的外形不能假设** —— `Builds.json` 顶层是 dict、散文埋在多层里，
   早期工具只认「顶层 list + `text`」，导致**整页从未被标注**且不报错。统一走 `textwalk.py`。
5. **官方术语**：`地狱锻铸·`（不是「地狱锻造」）· `巧工弩`（不是「诸葛弩」）·
   `钥匙`(key) 与 `骷髅钥匙`(rkey) 是两个物品 · 官方品名一律以 `official_zh.json` 为准。
6. **掉落计算器用到的 10 张表要与国服源码核对**（`verify_dropcalc_tables.py`）——
   曾查出 3 处漂移，其中炼狱版 `Levels.txt` 少了 9 行炼狱地图。
7. **别急着下结论** —— 今天有 4 次自我更正（合成次数、词缀数字、`displayName`、简报严重性），
   每次都是先写了个看起来精确的错数字。**不确定就写「无法可靠枚举」**。
8. **同一件暗金的中文名有 3 个来源，动手前先分清**（2026-09-14 补）：
   源码表里是**英文名**（`Templar's Might`）→ 中文化副本的 `index` 列（可被早期翻译脚本污染）→
   **客户端实际显示**（国服实测为「圣堂武士的力量」）。只看其中一处都会得出相反结论；
   本次还顺手发现「底材能在商店买到」这类**游戏内事实本站数据无法复核**（参考文件只有串表 + 两张 `CubeMain`），
   写进页面时必须标明是社区经验。

---

## 六、2026-09-14 已完成（简要）

| 类别 | 内容 |
|---|---|
| **魔方页** | 「机遇宝珠系统」补**低成本路线**（商店底材 → 炼金宝珠点金 → 稀有升阶两次 → 机遇宝珠）+ 两条前提：**只有稀有/制作可升阶**、配方行 `ilvl` 空 / 输出 `lvl=99`（不设底材等级门槛）；并标明「商店可买」为社区经验 |
| **断言** | 43 → **45 条**（新增「升阶公式无白色/魔法底材」「机遇宝珠 52 行 lvl=99 且 ilvl 空」） |
| **数据修正** | 暗金 `Templar's Might` 旧译「圣骑士的力量」→ **「圣堂武士的力量」**（`Uniques.json` / `damnation/Uniques.json` / 两张 `UniqueItems.txt` 中文 `index` 列，共 4 处） |
