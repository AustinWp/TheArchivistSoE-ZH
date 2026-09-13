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

> `tools/zh_dict.py`、`tools/TRANSLATION_GUIDE.md` 是早期人工翻译字典，**不在刷新流程里**；
> `translate_*.py` 三个一次性脚本已标 `DEPRECATED`，**不要再运行**（它们的术语是官方对齐之前的旧译）。


术语替换必须挂在 `refresh_data.py` 里（**生成之后、构建之前**），否则重新生成的数据会退回旧词。

### 3. 生成物不要手改

`Cube.json` / `Sacreds.json` / `SeasonS1.json` / `ItemImages.json` 都是**生成物**。
要改内容就改生成器（`tools/*.py`）或源文件，然后重跑；手改会在下一次刷新时被覆盖。

### 4. 模式差异必须分开写

很多改动**只在炼狱（毁灭）模式生效**：烬魂消耗（标准 25/15/25 ↔ 炼狱 50/25/50）、取消低级精华、分解分档、酋长第四阶概率（标准 25% / 炼狱 15%）、烬魂印钞概率表（两张不同的表）。数据表本来就是两份，改一份不影响另一份。

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
│   ├── refresh_data.py            一键刷新（解析/校验/生成/构建）
│   └── generated/             生成物（gitignore；含报告与对照表）
└── src/                      站点源码
```

## 部署

推送到 GitHub 仓库的 `main` 分支后，`.github/workflows/deploy.yml` 会自动构建并发布到 GitHub Pages。

线上地址：`https://<用户名>.github.io/TheArchivistSoE-ZH/`
