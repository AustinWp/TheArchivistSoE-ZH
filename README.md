# PD2 流放圣域（Sanctuary of Exile）中文资料库

[The Archivist](https://lukaszpg.github.io/TheArchivistSoE/) 的简体中文复刻版 —— Project Diablo 2《流放圣域（Sanctuary of Exile）》物品资料库。

## 特性

- 完全复刻原站样式（Diablo 风格暗色主题、ExocetBlizzard 字体、物品图标、悬浮提示）
- 全部界面与数据中文化：国服SOL第一赛季 / 武器 / 护甲 / 暗金装备 / 符文之语 / 词缀 / 圣化 / 腐化 / 命运卡牌 / 技能 / 魔方配方 / 飞升 / 地图 / 标准模式 / 毁灭模式 / 炼狱熔炉 / 更新日志
- **国服 S1 赛季页**：收录《PD2-SOE S1 Patch Notes Final》全文，并逐条与国服代码交叉验证（见 `docs/reference/s1-verification.md`）
- **⛔ 国服不支持标记**：国服代码中不存在或未接入的功能 / 公式（如随机狱铸配方、范围公式对狂犬病与火魔圣火不生效等）在页面上以红色徽标标出
- **国服优先**：默认炼狱（毁灭）模式；模式专属内容会标注并收到页面底部的「⛔ 本服务器不支持」分组
- 物品库存贴图：武器 / 护甲 / 暗金列表与提示框显示游戏内贴图（暗金用专属贴图）
- 暗金详情含**制作底材**：列出可用的普通 / 扩展 / 精英基底与对应通货宝珠，基底名可点击跳转
- 配方 / 熔炉 / 地图等页面正文里的材料与成品**带物品小图标**（由物品名自动标注）
- 掉落计算器（含怪物、财宝等级、区域名中文显示）、技能计算器
- 符文筛选、物品类型 / 孔数 / 阶位筛选、搜索（含属性内容搜索）
- GitHub Actions 自动构建并部署到 GitHub Pages

## 本地开发

```bash
npm install
npm run dev      # 开发
npm run build    # 构建到 dist/
npm run preview  # 预览构建产物
```

## 数据来源（重要）

**本站配方 / 术语 / 物品数据以游戏模组官方数据为唯一标准，不再直接录入网络文档。**

| 来源 | 说明 | 仓库位置 |
|---|---|---|
| 官方中文字符串表（soe.txt） | 全站**术语唯一标准**；清洗后生成 `public/data/official_zh.json` | `docs/reference/soe.txt` |
| 标准模式魔方配方表 | 6,801 条启用配方 | `docs/reference/CubeMain.standard.txt` |
| 炼狱（毁灭）模式魔方配方表 | 6,874 条启用配方 | `docs/reference/CubeMain.damnation.txt` |
| 物品库存贴图 | 644 张 PNG（游戏客户端 DC6 库存贴图转换） | `public/item-images/`（映射见 `public/data/ItemImages.json`） |

- 原始来源：游戏模组仓库 [`wdjwxh/PD2-Sanctuary-of-Exile`](https://github.com/wdjwxh/PD2-Sanctuary-of-Exile) 的 `SOECN` 分支（commit `9b24eb72`，2026-09-11，国服 S1 正式服版本；上一基准 `374d8971`）
- 数据流与重生成方法见 [`docs/reference/README.md`](docs/reference/README.md)
- 校验：`python3 tools/verify_cube_claims.py`（41 条事实断言 + 页面表格自检，含国服 S1 拆解分档 / 随机狱铸配方已删除）
- 重生成全部数据：`python3 tools/refresh_data.py`（解析 → 校验 → 生成页面数据 → 构建）
- 待游戏内验证的疑点：`tools/generated/pending_verification.md`（生成物，运行 `python3 tools/parse_cubemain.py` 后生成）
- 国服 S1 更新说明全文：`docs/reference/s1-patch-notes.md`；交叉验证结论：`docs/reference/s1-verification.md`

## 更新注意事项（每次改数据前先看）

> 这一节记录的是**实际踩过的坑**，不是通用建议。照着走能避开 90% 的返工。

### 0. 标准流程

```bash
# 1) 拉取上游 SOECN（GitHub 直连不稳时走本地代理）
git -c http.proxy=http://127.0.0.1:7897 clone --filter=blob:none \
    https://github.com/wdjwxh/PD2-Sanctuary-of-Exile.git /tmp/SOECN_repo

# 2) 看区间内到底改了哪些文件（不要靠猜）
#    https://api.github.com/repos/wdjwxh/PD2-Sanctuary-of-Exile/compare/<旧>...<新>

# 3) 替换参考文件 → 跑一键流程 → 校验 → 构建
cp <新>/standard-mode/.../CubeMain.txt docs/reference/CubeMain.standard.txt
cp <新>/damnation-mode/.../CubeMain.txt docs/reference/CubeMain.damnation.txt
python3 tools/refresh_data.py     # 解析 → 校验 → 生成 → 术语替换 → 构建
```

同步更新 **基准提交号 / 配方条数**：根 `README.md`、`docs/reference/README.md`、`public/data/Cube.json` 顶部说明。

### 0.1 国服实际运行的模式

**国服（SOECN 战网）运行的是「炼狱（毁灭）模式」，不是标准模式。** 依据：S1 说明中的经济改动
（烬魂消耗 25→50、取消完美级以下精华、分解档位等）**全部只落在 `damnation-mode` 数据**；
`docs/SOE战网经济平衡TODO.md` 也写明「Damnation 当前继承 standard 的 MonStats」。

因此本站的原则是 **国服优先**：

- 页面**默认打开炼狱模式**（`localStorage.damnation !== "false"`）；
- 模式专属内容用 `modes: ["standard"]` / `["damnation"]` 标注，**不匹配当前模式的不隐藏**，
  统一收到页面底部的「⛔ 本服务器不支持 / 当前模式不可用」分组；
- 切到标准模式时页面顶部显示横幅，提示该视图下哪些内容在国服不适用；
- 新增/修改页面数据时，**别忘标注 `modes`**，并确认对应面板传入了 `damnation` 属性。

### 1. 口径规则（更新说明 ↔ 游戏代码 冲突时）

1. **代码里有改动 → 以代码为准**（数值、公式、清单按代码收录；说明的约数与漏项按代码修正）；
2. **代码里没有改动 → 以说明为准**（说明宣布的功能照常收录为已上线，不因数据表里查不到就否定）；
3. 代码改动**只落在某一模式**时，**按模式分别标注**，不要合并成一句话。

### 2. 术语源绝对不能被批量替换

`public/data/official_zh.json` 由 `tools/extract_official_zh.py` 从 `soe.txt` 生成，是**全站术语唯一标准**。
`tools/apply_zh_terms.py` 的 `SKIP` 里必须保留它，原因是一个真实案例：

```
soe.txt: strModEnhancedDamage   → 强化伤害      ← 官方
soe.txt: ModStrEnhancedDamage   → 增强伤害(ED)  ← 官方，是另一个键
```

两者是**不同的字符串键**。整表替换会把术语源改成错的，等于自己污染标准。

同理 `SiteUpdates.json`（更新日志是历史叙述，含「旧词→新词」的说明）也要 `SKIP`。
**易混术语对照**（左列一律以官方串表为准，别按语感改）：

| 官方键 | 官方中文 | 是什么 | 常见错误写法 |
|---|---|---|---|
| `mfo` | **神话宝珠** | Mythic Orb，普通/扩展基底合暗金 | — |
| `divo` / `dvo` | **神授宝珠** | Divine Orb，精英基底合暗金 | ❌ 神圣宝珠（旧译，2026-08-29 已改） |
| `mjw` | **神话珠宝** | Mythic Jewel，地图掉落的高级**珠宝** | ❌ 神话宝珠（是另一件东西） |
| `oroc` | **机遇宝珠** | 炼狱模式专属 | ❌ 机会宝珠 |
| `jewf` / `jewp` | 珠宝碎片 / 珠宝匠棱镜 | 珠宝系材料 | — |

> 早期人工翻译字典（`zh_dict.py` / `item_names.py` / `TRANSLATION_GUIDE.md` / 三个 `translate_*.py`）已于 2026-09 清理删除 ——
> 它们的译名已过时（诸葛弩 / 重弩 / 谐角之冠…），留着只会误导。需要时看 git 历史。
> `translate_*.py` 三个一次性脚本已标 `DEPRECATED`，**不要再运行**（它们的术语是官方对齐之前的旧译）。


术语替换必须挂在 `refresh_data.py` 里（**生成之后、构建之前**），否则重新生成的数据会退回旧词。

### 3. 生成物不要手改

`Cube.json` / `Sacreds.json` / `SeasonS1.json` / `ItemImages.json` 都是**生成物**。
要改内容就改生成器（`tools/*.py`）或源文件，然后重跑；手改会在下一次刷新时被覆盖。

### 4. 模式差异必须分开写

很多改动**只在炼狱（毁灭）模式生效**：烬魂消耗（标准 25/15/25 ↔ 炼狱 50/25/50）、取消低级精华、分解分档、酋长第四阶概率（标准 25% / 炼狱 15%）、烬魂印钞概率表（两张不同的表）。数据表本来就是两份，改一份不影响另一份。

### 4.0 物品数据来自生成器，不要手改

`Weapons.json` / `Armors.json` 现在由 **`tools/build_item_tables.py` 从游戏表重新生成**（已接入 `refresh_data.py`）：

- **结构数值**（伤害/防御/等级/需求/孔数/阶位码）一律以 `Weapons.txt` / `Armor.txt` 为准；
- **中文名**走 `official_names.py`（唯一解析入口），查不到官方中文名的物品**不收录**（页面上不出现英文名）；
- 排除投掷药水与 TPot 内部占位；任务物品照收；
- `itemType` 等表里没有中文的字段从旧数据**收割**，不丢翻译。

**所以别再手改这两个文件** —— 手改会在下次 `refresh_data.py` 时被覆盖，而且正是过去反复出错的根源
（名字改一半、阶位码写错、整行缺失、属性被写成单个字符）。

### 4.1 不要写「合成几次」，只写结果

`CubeMain` 里带 `ROLL`(op18) 行的机制（机遇宝珠、崇高宝珠、烬魂簇、仇恨宝珠重洗、
命运卡增殖、地狱火炬亵渎、炼狱熔炉印钞）在数据上是「掷骰 → 结算」两段，
官方串表里 `hfmx`/`dsno`/`umbx`/`cabx`/`ccbx`/`gcbx` 的描述也写着「合成两次」。

**但玩家在游戏里的体感并不统一**（第一次点下去物品原样退回，容易被当成"没反应"），
而**官方串表本身不是我们该照抄的文案口径**。因此站点的写法是：

> **只描述结果，不声称合成次数。** 例如「机遇宝珠 + 物品放入方块判定：
> 成功 = 同底材暗金；失败 = 物品被摧毁并获得 1×普通钥匙」。

这样无论实际是一次还是两次都不会写错。**不要**再往正文里加「合成两次 / 合成一次 /
第一次登记、第二次判定」这类说法。

### 4.2 底材名的官方来源：`StrEternal<英文名>`

**几百个基础物品的 `namestr`/`code` 在官方串表里根本没有条目**（例如 `8rx` 的 namestr 就是 `8rx`，
串表里没有这个键）。它们的官方中文名只存在于另一处：

```
StrEternalChuKoNu  =  基础类型：巧工弩        ← 键 = StrEternal + 英文名去掉空格/连字符
StrEternalBalista  =  基础类型：弩炮
StrEternalShako    =  基础类型：军帽
```

取名优先级（`apply_official_item_names.py` 与审计工具都按这个口径）：

1. `namestr` 键（为空则用 `code`）能在串表里查到 → **以它为准**
2. 查不到 → 用 `StrEternal<英文名>` 的「基础类型」名兜底
3. 都查不到 → 保留原值

历史上没有第 2 层，导致 505 件底材里有 **298 件用的是社区旧译**（诸葛弩 / 重弩 / 谐角之冠…），
与游戏里显示的名字不一致。审计第 3b 项专门盯这类问题。

### 4.3 事故复盘：298 件底材名全错（2026-09-13）

**现象**：玩家指出「游戏里有**巧工弩**，wiki 搜不到」。查证后不是缺物品 ——
是我们把它叫成了「诸葛弩」，而且同类错误共 **298 件**（505 件底材的 59%）。

**根因（按重要性排序）**

1. **取值链路不完整（直接原因）**
   官方串表里物品中文名有**两条**来源：
   - 物品自己的键：`namestr`（为空则用 `code`），如 `mfo` → 神话宝珠
   - 基础类型族：`StrEternal<英文名去空格/连字符>`，如 `StrEternalChuKoNu` → 巧工弩

   而**几百个基础物品的第一条链路是空的**：`8rx` 的 `namestr` 就是 `8rx`，串表里没有这个键。
   我们只实现了第一条 → 查不到就**默默沿用早期的社区旧译**，没有任何提示。

2. **校验器与被校验对象犯了同一个错（为什么长期没被发现）**
   审计工具的「物品显示名比对」用的也是 `namestr/code` 这一条链路 ——
   **它只能验证自己知道的那部分**，298 件错名正好落在它的盲区里，永远不会报出来。
   > 教训：**审计不能和被审计对象共用同一个假设**，否则盲区等于没有审计。

3. **没有覆盖率指标（为什么能漏这么久）**
   从来没人统计「多少件物品能追溯到官方名、多少件在裸奔」。加一行统计，
   `298 / 505` 这个数字第一天就会跳出来。

4. **历史包袱**
   早期那套翻译脚本（**已删除**，见 git 历史）用社区译名批量生成数据；后来补了「对齐官方串表」的步骤，
   但只覆盖能查到的那部分，剩下的静静留着 —— 表面看「已经对齐过了」。

**已做的机制性修复**

| 修复 | 说明 |
|---|---|
| **唯一解析入口** | 新增 `tools/official_names.py`，取值链路只实现一次，`apply_official_item_names` / `annotate_item_icons` / `audit_official_terms` 全部 import 它 —— 杜绝再次分叉 |
| **补齐链路** | `namestr/code` → `StrEternal<英文名>` 两级兜底；英文名先剥 `(L)/(M)/[S]` 后缀、按 `/` 拆分、**忽略大小写**（`Hunter's Bow` 的键被写成 `HunterSBow`）、允许符号差异（`Chu-Ko-Nu` → `ChuKoNu`） |
| **覆盖率审计** | 审计第 5 项统计取名来源；**站点真正展示的装备若追溯不到官方名且未登记就直接报错** |
| **显式登记** | 串表确实没有的物品（珠宝 / 护身符 / 钥匙 / 宝石 / 药水…）必须登记进 `BASE_GAME_NAME`。它们显示的是**基础游戏**的中文串，**无法用 SOE 串表验证** —— 改动前必须另找依据，且不要对外声称「已与官方对齐」 |
| **图标同步** | 图标标注走同一解析器，可标注物品名 424 → **893** |
| **修数据** | 底材名（含暗金嵌套基底、制作底材区块）共修正 **817 + 32 处** |

**下次的检查清单**

1. 判断「某个名字对不对」时，**先跑 `python3 tools/official_names.py`** 看覆盖率与未登记清单，不要凭印象；
2. 游戏表里的英文名**不一定干净**（`Gloves(L)` / `Cap/hat` / `Hunter's Bow`），
   用 `name_candidates()` 生成候选键，不要手写字符串拼接；
3. 新增/修改物品数据后，**必须**让审计第 2、3、3b、4、5 项全部通过；
4. **串表查不到 ≠ 名字是对的** —— 基础游戏物品只能另找依据，并在 `BASE_GAME_NAME` 登记；
5. 玩家报「游戏里有、wiki 没有」时，**先怀疑名字不一致，再怀疑缺数据**。

### 4.3.1 掉落计算器的数据表要与国服源码核对

计算器读取 `public/data/<mode>/*.txt` 共 **10 张表**，注意两条规则：

1. **炼狱模式只覆盖 6 张**（CubeMain / Misc / MonStats / SuperUniques / TreasureClassEx / UniqueItems），
   其余表在客户端里是编译好的 `.bin` → 本地副本**应当等于标准模式的那张**；
2. 若干列是**中文化副本**（`UniqueItems.index`、`SetItems.index`、`Levels.LevelName`/`Name`、
   `MonStats.NameStr`），比对时跳过。

核对方法（需要 SOECN 仓库）：

```bash
python3 tools/verify_dropcalc_tables.py --repo /tmp/SOECN_repo \
    --sha 9b24eb72380a724457e8e6d37a169c837f0ad0a0
```

同步新版本用 `tools/sync_dropcalc_tables.py`（保留中文列，只换其它列）。

**2026-09 实测**：10 张表 × 2 模式全部一致；期间修掉 3 处漂移 ——
`standard/Armor.txt` 的 `smer` 行阶位码写错（`smer/rxx/rxx` → `smn/smx/smer`）、
`damnation/Armor.txt` 缺 2 行、`damnation/Levels.txt` 缺 9 行炼狱地图。

### 4.3.2 已知缺口（复查过、有理由、**不要靠猜去补**）

| 缺口 | 数字 | 原因 / 处置 |
|---|---|---|
| 词缀 | 前缀缺 85 / 后缀缺 111 | 早期翻译脚本（**已删除**）**只收录它有中文译文的条目**（缺失项 version/mod 分布杂乱，不是模式过滤）。补齐需要「属性码 → 中文模板」映射，靠推断有风险 → **暂不补**，保持可见 |
| 暗金「驯服」 | 1 条 | `rarity=0`（掉率 0）且一半属性是隐藏项（`aura-hidden` / `static-modifier-display`），`occurrenceChance` 无法忠实重建 → 登记在审计第 3d 项的例外里 |
| 任务物品 | 6 条 | 国王之杖 / 赫拉迪克法杖 等，`quest` 列非空，不进暗金列表 |
| 升华灵魂石系列 | 19 条 | 源码 `UniqueItems.txt` 里有，但属**升华**内容，已在「升华」页收录 |
| 139 件物品中文名 | — | 珠宝 / 护身符 / 钥匙 / 宝石 / 药水走**基础游戏**中文串，SOE 串表（3854 条，仅为模组覆盖表）里没有，**无法验证** |

> 原则：**「对不上」时先把它变成可见的例外（写清理由），而不是编一个值填上。**

### 4.4 加标记（图标 / 符文编号）只能加在「markdown 渲染」的字段

`{{icon:CODE}}` 和「（N号）」这类标记，**只有经过 markdown 渲染器**才会变成图标/富文本；
加在纯文本字段上会**把标记原文显示给用户**，有的字段还参与名称匹配（加进去直接破坏跳转）。

踩过的三个坑：

1. **页面 JSON 的外形不能假设**
   `Builds.json` 顶层是 **dict**（`{updatedAt, classes:[...]}`），散文埋在 6 层深，
   还有 `sections[].items[]` 这种**裸字符串数组**。早期工具只认「顶层 list + `text` 字段」，
   于是**整个构筑页从来没被标注过**，而且没有任何报错。
   → 统一走 `tools/textwalk.py`：递归遍历，**不要假设外形**。

2. **哪些字段是纯文本**
   凡是「名字类」字段（`displayName` / `fourthInputDisplayName` / `itemTypesDisplayNames[]` /
   `title` / `caption` / 以及**所有以 `Name` 结尾的键**）都是纯文本或参与匹配 →
   一律跳过（`textwalk.is_skip_key`）。
   圣化页就是因为漏了 `itemTypesDisplayNames` 而露出 20 处 `{{icon:...}}`。

3. **渲染器不止一个**
   全局 markdown（`renderInlineMarkdown`）之外，构筑面板还有自己的 `InlineMd`
   —— 它最初不认图标标记。**新增渲染器时要同步支持标记**，否则该面板的内容会露原文。
   另外：**加粗 / 斜体里也会夹标记**（`**{{icon:rin}}戒指**`），
   所以渲染器遇到加粗要**递归**再解析一次。

**两道自动防护**：
- 审计第 6 项：扫描所有页面数据，**纯文本字段里出现标记就报错**（当前 0 处）；
- 标注工具采用「先全量清理、再按安全字段标注」两段式，
  这样即使字段规则收紧，旧标记也会被清掉，不会永久留在数据里。

### 4.2.1 一个物品有**多个**名字字段，改名字要全改

`Weapons.json` / `Armors.json` 里每个物品有 5 个名字相关字段：

| 字段 | 用途 |
|---|---|
| `name` | 数据层名字 |
| **`displayName`** | **前端实际渲染用的就是这个**（`displayName \|\| name`） |
| `normalItemDisplayName` / `exceptionalItemDisplayName` / `eliteItemDisplayName` | 普通/扩展/精英三个阶位的显示名（按各自的 `normalTierCode` / `exceptionalTierCode` / `eliteTierCode` 取官方名） |

**只改 `name` 不改 `displayName`，页面上就还是旧名字** —— 巧工弩第一次修复后又"没生效"，
就是栽在这里（`name` 已是「巧工弩」，`displayName` 还是「诸葛弩」）。
`apply_official_item_names.py` 现在会把这 5 个字段一起对齐，审计第 3b 项也逐字段校验。

### 4.5 按需运行的分析工具（不在刷新流程里）

这些是排查用的**诊断脚本**，平时不用跑，但别删 —— 它们是复查数据的依据：

| 工具 | 用途 |
|---|---|
| `verify_dropcalc_tables.py` | 掉落计算器 10 张表 vs 国服源码（需 `--repo` / `--sha`） |
| `affix_deep_align.py` / `affix_depth_diff.py` | 词缀与游戏表的三层比对（缺 196 条的结论就出自这里） |
| `unique_prop_parser.py` / `unique_prop_diff.py` | 暗金属性串 → (property, min, max) 解析与数值 diff |
| `diff_game_tables.py` | 全表差异报告（游戏仓库 vs 站点数据） |
| `sync_dropcalc_tables.py` | 同步游戏数据表到新提交（保留中文列） |
| `build_item_images.py` / `fetch_item_images.py` | 物品贴图映射表与下载 |
| `gen_skills_data.py` | `SkillsData.json` 生成 |

### 5. 中文文案不在代码仓库

`SOECN` 仓库只有 `data/local/LNG/ENG/patchstring.tbl`（英文，纯 ASCII），**没有中文串表**。
所以「技能中文说明 / 中文名修正」这类改动**无法用仓库核对**，需要国服客户端的中文串表另行比对 —— 遇到这类条目直接标「无法从代码验证」，不要硬凑结论。

### 6. 掉落计算器数据表是「中文化副本」，不能直接覆盖

`public/data/{standard,damnation}/*.txt` 里 `MonStats.txt` 的 `NameStr`、`Levels.txt` 的 `Name`/`LevelName` 是中文。
用 `tools/sync_dropcalc_tables.py` 同步：按首列主键匹配、保留中文列、行数或表头不一致就中止。

⚠️ 这些表**可能落后于基准提交**（S1 时 `damnation/TreasureClassEx.txt` 还停在更早的测试期经济快照）。升级基准时顺手核对一次。

### 7. 物品贴图

- 映射从 `Weapons/Armor/Misc.txt` 的 `invfile` / `uniqueinvfile` / `setinvfile` 生成，**不依赖外部站点**；
- 下载时源站文件名**大小写不统一**（游戏表 `invrEl` ↔ 站上 `invrel`），`fetch_item_images.py` 已做小写回退，落盘一律用游戏表原名；
- 新增或改名物品后：`build_item_images.py` → `fetch_item_images.py --check` → 补下载。

### 8. 前端两个固定坑

- **`useJson` 只接受数组**（非数组会被丢成 `[]`）。对象型数据文件用 `useJsonObject`。
- **模块级缓存要在渲染期写入，不能放 `useEffect`**：effect 在本次渲染提交后才执行，而写缓存不会触发重渲染，界面会一直停在旧状态（物品贴图就这么白排查了一轮）。
- 所有贴图都带 `onError` 回落到 SVG 图标，缺图不会出现裂图。

### 9. 提交与部署

- **push 前先 fetch**：远端可能已有另一个工作副本推的提交（历史上出现过），推送被拒时先合并再推，**不要强推**；
- push 到 `main` → `.github/workflows/deploy.yml` 自动构建发布；**等 Actions run 变成 success** 再验证线上；
- 线上验证记得**硬刷新**（Cmd+Shift+R），否则看到的还是旧缓存。

### 10. 交付前的自检

```bash
python3 tools/verify_cube_claims.py       # 断言应全绿（当前 41 条；数据变了就同步改断言）
python3 tools/audit_official_terms.py --strict   # 术语必须与官方串表完全一致（应输出「未发现不一致」）
npm run lint                          # 与基线比较，不要新增问题
npm run build
```

## 目录结构

```
├── docs/reference/           官方参考文件（soe.txt + 两模式 CubeMain.txt + 说明）
├── public/data/              页面数据（中文；official_zh.json 为术语源）
│   ├── standard/ damnation/  掉落计算器使用的游戏数据表（.txt）
├── tools/                    数据生成/校验方案（Python）
│   ├── extract_official_zh.py    soe.txt → official_zh.json
│   ├── parse_cubemain.py         CubeMain → 结构化配方 JSON
│   ├── verify_cube_claims.py     41 条断言校验
│   ├── generate_cube_page.py     CubeMain → 魔方配方页 Cube.json
│   ├── rebuild_sacreds.py        CubeMain → 圣化宝珠页 Sacreds.json
│   ├── generate_terms_md.py      术语/圣化宝珠/命运卡对照表
│   ├── generate_season_page.py    S1 更新说明 → 赛季页 SeasonS1.json
│   ├── sync_dropcalc_tables.py    同步掉落计算器数据表（保留中文列）
│   ├── build_item_images.py       游戏数据表 → 物品贴图映射 ItemImages.json
│   ├── fetch_item_images.py       下载物品贴图到 public/item-images/
│   ├── apply_official_item_names.py 底材名对齐官方中文串表
│   ├── audit_official_terms.py     术语一致性审计（旧译残留/硬编码/物品名）
│   ├── annotate_item_icons.py     页面正文物品名加图标标记 {{icon:CODE}}
│   ├── annotate_rune_numbers.py   正文符文名补编号（提尔 → 提尔（3号））
│   ├── official_names.py          ★ 官方物品名的唯一解析入口（改了名字链路只改这里）
│   ├── build_item_tables.py       ★ 从游戏表重建武器/护甲（保留中文名）
│   ├── verify_dropcalc_tables.py  核对掉落计算器 10 张表与国服源码
│   ├── textwalk.py                ★ 页面 JSON 的散文遍历（递归，别假设外形）
│   ├── refresh_data.py            一键刷新（解析/校验/生成/构建）
│   └── generated/             生成物（gitignore；含报告与对照表）
└── src/                      站点源码
```

## 部署

推送到 GitHub 仓库的 `main` 分支后，`.github/workflows/deploy.yml` 会自动构建并发布到 GitHub Pages。

线上地址：`https://<用户名>.github.io/TheArchivistSoE-ZH/`
