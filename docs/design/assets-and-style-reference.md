# 素材与风格参考调研：bd.wdjwxh.com

> 调研时间 2026-09-13。目标站点：<https://bd.wdjwxh.com>（国服 SOL 官方「天梯与角色档案」）。
> 结论：**物品贴图可以直接复用，且 sprite 名的映射在我们自己的数据里就有**；装备说明的**数据层我们比它更全**，差距只在呈现分组与视觉风格。

## 1. 目标站拆解

Vite + React SPA（nginx 托管），无服务端模板。页面顶部 5 张图片、其余全部来自运行时接口。

| 素材 | 位置 | 说明 |
|---|---|---|
| 游戏数据 JSON | `/game-data/soe-13.0.2-battle-net.json`（1.27 MB） | `meta.source = private-client:pd2data.mpq/ItemStatCost.bin;sha256=…` —— **从国服客户端 MPQ 抽出的**。含 `items`(1114) / `stats`(511) / `skills`(695) / `sanctifications`(513) / `corruptions`(1024) / `magicPrefixes`(958) / `magicSuffixes`(1067) / `uniqueItems`(670) / `setItems`(128) / `runewords`(197) / `monsterNames`(1995) 等 |
| 战网角色 API | `/api/battle-net/characters`、`/api/battle-net/characters/<id>` | 313 个角色摘要；单角色详情是该角色**完整存档**（装备 33 格 + 随身 + 佣兵 + 技能 + 属性），每个词缀带现成中文 `description`，例如 `{"name":"item_addexperience","values":[29],"description":"+29% 额外经验值获得"}` |
| **物品贴图** | `/item-images/<sprite>.png` | 28–56 px 透明 PNG，1–3 KB/张。sprite 名如 `invhax`(手斧)、`invhaxu`(暗金手斧)、`invcap`(帽子)。**本质是客户端 DC6 库存贴图转 PNG** |
| 职业头像 | `/class-portraits/<class>.png` | 7 个职业，46×41 |
| 品牌与插画 | `/brand/pd2-soe-logo.webp`、`s1-druid-{desktop,mobile,oil-desktop,oil-mobile}-*.webp` | logo + 2 张 AI 生成的德鲁伊赛季插画（桌面/移动各一版） |

## 2. 可行性核验（已实测）

**关键结论：不需要依赖他们的 JSON —— sprite 名映射在我们自己的游戏数据表里。**

`public/data/standard/{Weapons,Armor,Misc}.txt` 已含 `invfile` / `uniqueinvfile` / `setinvfile` 三列：

```
Weapons.txt  invfile=invhax  uniqueinvfile=invhaxu  setinvfile=invhaxu
Armor.txt    invfile=invcap  uniqueinvfile=invcapu  setinvfile=invcapu
Misc.txt     invfile=invpot  uniqueinvfile=invvip
```

统计与抽样结果：

| 项目 | 结果 |
|---|---|
| 我们需要的唯一贴图名 | **644** 个（武器/护甲/杂项的全部 `invfile` + 暗金/套装变体） |
| 在他们的服务器上存在 | **643 / 644** |
| 抽样下载（40 张） | 全部 HTTP 200，1–3 KB，RGBA 透明 PNG |
| 全量体积估算 | 约 **1.5–2 MB** |

## 3. 装备说明：我们的数据比它更全

| | bd.wdjwxh.com | 本站 |
|---|---|---|
| 暗金词缀 | `uniqueItems` **只是名字列表**（670 条），无词缀数据；真实属性来自**在线角色存档** | `Uniques.json` **581 件全部**有 `displayProperties`（中文词缀） |
| 额外字段 | — | `dropRate` / `occurrenceChance` / `hellforged` / `dropSource` / `itemTier` / `showCanBeCreatedWith` |
| 符文之语 | `runewords` 列表为 `null` 占位 | `Runewords.json` 126 条含 `displayProperties`、`sacreds` |
| 圣化 / 腐化 | 有原始 requirements | `Sacreds.json`（86 条）+ `Corruptions.json` |

差距在**呈现**：他们按「基础 / 词缀 / 镶嵌 / 圣化」分区展示，层次更清楚。

## 4. 视觉风格对照

| | bd.wdjwxh.com | 本站现状 |
|---|---|---|
| 底色 | `#100d0b`（暖黑） | `#101012`（中性冷灰） |
| 面板 / 线 | `#121418` / `#292a2c` | 同类深灰 |
| 强调色 | 金 `#c89a4b`、亮金 `#efd28a` | 金（仅点缀） |
| 标题字体 | **衬线中文** `Noto Serif SC` | 无衬线 |
| 正文字体 | `Noto Sans SC` | 无衬线 |
| 顶部 | 大幅插画 banner（赛季主题） | 无 |
| 列表 | 卡片 + 职业头像 + 库存格 56/72px | 紧凑行 + 通用 SVG 类型图标 |
| 品质配色 | 暗金=金、套装=绿、荣誉分档色 | 部分使用 |

## 5. 建议方案（可拆分独立实施）

### P0 · 物品图 —— ✅ 已于 2026-09-13 实施
1. ✅ `tools/build_item_images.py`：解析 `Weapons/Armor/Misc.txt` 的 `invfile`/`uniqueinvfile`/`setinvfile` → `public/data/ItemImages.json`（1113 个物品代码 / 644 张贴图）。
2. ✅ `tools/fetch_item_images.py`：批量下载 PNG 到 `public/item-images/`（644 张，2.7 MB）。源站文件名大小写不统一（游戏表 `invrEl`，站上 `invrel`），工具已做小写回退、落盘仍用游戏表原名。
3. ✅ 前端：列表行左侧 38px 库存格显示贴图（暗金用专属贴图），提示框顶部放大显示；贴图缺失时 `onError` 自动回落到原有 SVG 类型图标。
4. ⬜ 尚未同步到魔方配方页 / 圣化页的物品引用（P1 一并处理）。
5. ⬜ 尚未加品质描边（暗金金框 / 套装绿框）。

### P1 · 装备说明分组（低风险）
tooltip 改为分区：`基础属性` → `暗金属性 / 符文之语属性` → `镶嵌物` → `圣化`（链到圣化页）→ `腐化` → `掉落来源`。

### P2 · 视觉换风格 —— ⛔ 已决定**不做**（2026-09-13 确认：维持现有风格）
~~衬线中文标题、暖黑底 + 金色卡片、卡片化列表、顶栏品牌区。~~ 结论：**维持原有风格**，本节仅作为资料留存；`docs/design/style-mockup/` 保留作参考，不再推进。

### P3 · 职业头像 —— 暂不推进（P2 不做，头像单独上会与现有风格不搭）
职业头像（7 张）用于「核心BD构筑」页，按职业给构筑卡片配头像。

## 6. 结论

- ~~素材用法~~ → 已确认：**下载进仓**，并在页脚注明来源（物品贴图取自游戏客户端，经国服档案站 bd.wdjwxh.com 转换）。
- ~~**插画 banner**~~ → 不需要（P2 不做）。
- **图片版权**：物品贴图源自游戏客户端 `pd2data.mpq`，与本站记录的是同一款游戏；已在页脚写明来源。

## 7. 本地预览

`docs/design/style-mockup/index.html` 是按上述方向做的样式 mockup（含 20 张示例贴图与 7 张职业头像），可直接用浏览器打开查看：

```bash
open docs/design/style-mockup/index.html
```
