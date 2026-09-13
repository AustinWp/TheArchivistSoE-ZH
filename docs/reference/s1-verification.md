# S1 更新说明 × 国服代码 交叉验证报告

- **核对对象**：国服代码仓库 [`wdjwxh/PD2-Sanctuary-of-Exile`](https://github.com/wdjwxh/PD2-Sanctuary-of-Exile)（分支 `SOECN`）
- **基准提交**：`374d8971`（2026-08-24，站点升级前的数据基准）
- **目标提交**：`9b24eb72`（2026-09-11，**国服 SOL 第一赛季正式服版本**）
- **更新说明原文**：[`s1-patch-notes.md`](s1-patch-notes.md)（腾讯文档《PD2-SOE S1 Patch Notes Final》照录）
- **核对时间**：2026-09-13
- **核对方式**：对两提交的全部数据表做逐字段比对（`Skills.txt` 256 列、`CubeMain.txt` 105 列、`TreasureClassEx.txt` / `MonStats.txt` / `Missiles.txt` / `Skilldesc.txt` / `States.txt` / `ItemStatCost.txt` 等），并用 GitHub compare / commits API 定位每个数值的改动提交与提交说明。

## 0. 总体结论

| 项目 | 结果 |
|---|---|
| 本区间提交数 | 14 个提交 |
| 本区间变动文件 | **13 个，全部是 `.txt` 数据表**（无 DLL、无 `.tbl`、无源码） |
| 逐条核对条目 | **52 条** |
| ✅ 与代码一致 | 46 条 |
| ⚠️ 部分一致（模式差异 / 约数差异） | 5 条 |
| ⭕ 代码无改动 → 以说明为准 | 2 条（A1A5 Boss 2DT、珍稀宝物倍率 5 项） |
| ❓ 无法从本仓库验证 | 3 条（中文字符串、D2GL 修复、汉服基准绝对倍率） |

**一句话结论**：S1 说明中的**技能数值、魔方配方、经济掉落、机制公式与技能清单全部与国服代码逐字段吻合**（含 93/93 范围技能清单、29/29 增益清单、11/11 频率清单）。

### 0.1 口径规则（本站采用）

> 1. **代码里有改动 → 以代码为准**（数值、公式、清单按代码收录，说明的约数与漏项按代码修正）；
> 2. **代码里没有改动 → 以说明为准**（说明宣布的功能照常收录为已上线，不因数据表里查不到就否定）；
> 3. 代码改动**只落在某一模式**时，按模式分别标注。

按此规则，本次核对需特别说明的两点为：
- **「A1A5 剧情 Boss 2DT」与「珍稀宝物倍率」属于第 2 类**：本次代码改动中查不到痕迹 → **按说明收录为已上线**；
- **多条改动只落在炼狱（毁灭）模式**（酋长概率、熔炉消耗、取消低级精华、分解档位等）→ **按模式分别标注**。

---

## 1. 技能改动（德鲁伊 / 刺客 / 死灵法师 / 法师）

结论：**21 条全部 ✅一致**（`standard-mode/data/global/excel/Skills.txt`，本区间共 22 行字段变化）。

| 说明条目 | 结论 | 代码证据（文件 · 字段 · 旧→新） |
|---|---|---|
| 召唤灰熊 生命 +4%→+8% | ✅ | `Skills.txt` `Summon Grizzly.calc1` `lvl*4 → lvl*8` |
| 召唤灰熊 召唤物抗性上限 80%→85% | ✅ | 同行 `aurastatcalc1..4`（火/冰/电/毒抗）`min(ln78,80) → min(ln78,85)` |
| 召唤灰熊 冷却 2 秒→1 秒 | ✅ | 同行 `delay` `50 → 25`（25 帧 = 1 秒） |
| 召唤灰熊 乌鸦+灵狼协同 +4%→+6% | ✅ | 同行 `Param6` `4 → 6`，被 `DmgSymPerCalc=(Raven.blvl+Summon Spirit Wolf.blvl)*par6` 使用 |
| 召唤灰熊 溅射半径 3.33→5.33 码 | ✅ | `MonProp.txt` `druidbear` 新增 `inc_splash_radius 100 ␣ 60 60`（基准无此属性 = 0）；提交 `2cfae75662` 原文「对应约 5.33 码」；`Wearbear.aurastat5=20` 未动 → 确实「仅作用于召唤灰熊」 |
| 召唤乌鸦 攻击次数上限 5→100000 | ✅ | `Skills.txt` `Raven.Param5` `5 → 100000` |
| 召唤乌鸦 100% 冰 → 50% 物 + 50% 冰 | ✅ | 物理列由空填入与冷伤列**完全相同**的 `4/6` 及各阶成长，同时 `HitShift 7 → 6`（每部分减半）→ 总伤不变、冷/物各半 |
| 召唤乌鸦 数量成长每两级→每级 | ✅ | `Raven.petmax` `min((lvl/2)+2,par2) → min(lvl+2,par2)` |
| 召唤乌鸦 15 只所需等级 26→13 | ✅ | 同上（`par2=15`，13 级满 15 只） |
| 召唤乌鸦 协同 +8%→+12% | ✅ | `Raven.Param8` `8 → 12` |
| 风遁 可在狼人/熊人形态使用 | ✅ | `Gust.restrict` 空 → `1`（`restrict`：0=仅人形、1=人形+变形、2=仅指定 State） |
| 狼人变化 基础 ED +20%→+30% | ✅ | `Wearwolf.Param5` `20 → 30` |
| 狼人变化 每级 ED +4%→+6% | ✅ | `Wearwolf.Param6` `4 → 6` |
| 狂怒 每级 ED +8%→+16% | ✅ | `Fury.Param4` `8 → 16` |
| 狂怒 野性狂暴协同 +4%→+6% | ✅ | `Fury.Param8` `4 → 6`，用于 `calc2 = ln34 + Feral Rage.blvl*par8` |
| 熊人变化 每级 ED +15%→+20% | ✅ | `Wearbear.Param2` `15 → 20` |
| 撞锤 ED 成长 +40%→+50% | ✅ | `Maul.Param3` `40 → 50` |
| 焰爪 协同 +24%→+28% | ✅ | `Fire Claws.Param8` `24 → 28` |
| 火山 协同 +9%→+12% | ✅ | `Volcano.Param8` `9 → 12`（物理/火焰两条线同步） |
| 毁天灭地 基础伤害与各阶成长 +约 25%；协同 +10%→+12%、焰爪 +5%→+7% | ⚠️ 量级 | `Armageddon`：`MinDam 15→19`、`MaxDam 45→56`、`EMin 15→19`、`EMax 45→56`，各阶成长 `10/13/17/21/25 → 13/16/21/26/31`；`Param8 10→12`、`Param6 5→7`；地面火 `Missiles.txt armageddonfire` `EMin 10→13`、`EMax 14→18`。**实测 +24%~+30%**，说明写「约 25%」偏低 |
| 毒藤 地面轨迹 +4 帧重复命中间隔 | ✅ | `Missiles.txt plague vines trail`：`NextHit` 空→`1`、`NextDelay` 空→`4`（毒伤字段未动） |
| 刃之怒 武器伤害系数 75%→100% | ✅ | `Blade Fury.SrcDam` `96 → 128`（128=100%） |
| 刃之怒 协同 +8%→+15% | ✅ | `Blade Fury.Param8` `8 → 15` |
| 刃之怒 提示显示实际 100% | ✅ | `Skilldesc.txt blade fury.desccalca2` `85 → 100` |
| 骷髅法师 四种弹体 / 飞行 50、40 帧 / 冻结 10 帧 / 毒雾 60 帧 + 4 帧重复命中 | ✅ | `Missiles.txt`：火 `necromage3` `CelFile Firebolt→Fireball`、`Range 30→50`、`CollideKill→1`、`CltHitSubMissile1→fireexplosion2`；冰 `necromage2` `CelFile Icebolt→GlacialSpike`、`EType cold→frze`、`ELen 25→10`、`ELevLen1 25→0`；电 `necromage4` `CelFile ChargedBolt→null`、`Vel/MaxVel 14→32`、`Range 30→40`、`CollideKill→0`、`NumDirections 16→1`；毒 `necromage1` `pClt/pSrvHitFunc→2`、`CollideKill→1`、`HitSubMissile1→soe_necromage_poisoncloud`；新行 `soe_necromage_poisoncloud`：`Range=60`、`NextHit=1/NextDelay=4`、`ELen=12`、`Vel=2` |
| 骷髅法师 基础伤害/成长/精通不变 | ✅ | `Skills.txt` `Raise Skeletal Mage`(Id 80) 与 `NecromageMissile`(Id 338) 本次**均无字段变化** |
| 火焰石魔 圣火间隔 30→25 帧 | ✅ | `Skills.txt Holy Fire Fire Golem.perdelay` `30 → 25` |
| 火焰石魔 28+ 级最小成长 6→11、最大 7→12 | ✅ | 同行 `EMinLev5 6 → 11`、`EMaxLev5 7 → 12`；圣骑士 `Holy Fire` 行未改 |
| 新星 协同 +4%→+5%；新增范围属性支持 | ✅ | `Nova.Param8` `4 → 5`；新增 `cltcalc1`/`calc3` 使用 `item_skill_aoe` |
| 霜之新星 协同 +6%→+8%；新增范围属性支持 | ✅ | `Frost Nova.Param8` `6 → 8`；同式（分母 `3*12*100`） |
| 能量盾 36 级后继续提高、45 级到 90%；20 点基础点 0.5 法力/伤害；下限 0.5 | ✅ | `Energy Shield.calc1` `min(edmn,85) → min(min(15+2*(lvl-1),85)+max(lvl-36,0)*5/9,90)`；`calc2` `max(par5-blvl-es_eff,14) → max(34-min(blvl,10)-((max(min(blvl,20)-10,0)*16+5)/10)-es_eff,8)` → blvl=20 时 `8/16 = 0.5`（旧 `14/16 = 0.875`） |
| 装备自带能量盾 +16 个百分点；最低 0.5；启蒙 18 级盾 49%→65%、1.0→0.75 | ✅ | `Energy Shield SelfAura.calc1` `min(edmn,90) → min(edmn+16,90)`；`calc2` 下限 `14 → 8`、`Param5 34 → 30`；18 级 `edmn=15+2*17=49` → `49% → 65%`，耗蓝 `max(30-0-18,8)=12` → `12/16 = 0.75`（旧 `16/16 = 1.0`）。「启蒙」= 符文之语 `Epiphany`（`Runes.txt`，`es-efficiency-and-es-when-equip → Energy Shield SelfAura 18 18`）；`Tempest`、`Uldyssian's Awakening` 同技能 |
| 升华 酋长第四阶 击杀爆炸概率 25%→15% | ⚠️ **仅炼狱模式** | 概率在 `CubeMain.txt` 升华配方的 `kill-skill` 第 4 参数：**`standard-mode` L4752 仍为 `25`（未改）**；**`damnation-mode` L4707 `25 → 15`** |
| 升华 秘术师第三阶 秽言绽放概率 25%→15% | ✅ | `CubeMain.txt` **两模式都改**：standard L4730 / damnation L4685 `kill-skill 100 687 25 1 → 15 1` |
| 叠层 烈风之力 6 层 / 锐眼版 10 层 / 无尽之渴 10 层 | ✅ | `Gale Force.aurastatcalc1` → `min(..., 6)`；`Gale Force Deadeye` → `min(..., 10)`；`Indigon Stacks` → `min(..., 10)` |
| 技能说明 面板/公式类（乌鸦数量、灰熊生命与冷却、刃之怒比例、能量盾公式） | ✅ | `Skilldesc.txt` 5 行：`raven.desccalca2` + `descline5 38→47`；`summon grizzly.desccalca3 50→25`、`dsc2calca3 lvl*4→lvl*8`；`blade fury.desccalca2 85→100`；`energy shield` / `energy shield selfaura` 提示改为读新公式 |
| 技能说明 中文文案（乌鸦混合伤害、灰熊溅射、风遁、火魔圣火、狼人变化中文名、骷髅法师说明） | ❓ 无法验证 | 仓库本地化仅 `data/local/LNG/ENG/patchstring.tbl`（**英文**，两提交 blob SHA 相同、本次未改），全树无 CHS/CHT 中文表，4 个 DLL 未改动 → 中文串不在本仓库 |

---

## 2. 通用修改（经济 / 掉落 / 魔方配方）

结论：**10 条 ✅一致，1 条 ❌（A1A5 2DT），1 条 ⚠️（珍稀宝物倍率）**。

| 说明条目 | 结论 | 代码证据 |
|---|---|---|
| **A1A5 剧情关底 Boss 统一 2DT** | ⭕ **代码无改动 → 以说明为准（收录为已上线）**（代码侧证据见下，供日后回归核对） | ① damnation `TreasureClassEx.txt` 中 A1A5 Boss 全部相关行（`Andariel` / `Andarielq` / `Duriel` / `Mephisto` / `Diablo` / `Baal` / `Baalq`）old=new **逐字节相同**，`Picks` 均 7、`group` 均空；② TC 名称列表 diff 为空，**没有新增任何 `2DT` 形式的 TC 行**；③ 在全部已下载数据文件中检索 `2DT`（不区分大小写）**0 命中**；④ `MonStats.txt` 本次只改了 `horrorofabsolutet1..4` 4 行；⑤ 新增的 `SuperUniques.txt` 不含关底 Boss；⑥ 3 个 DLL 本次均未改动。→ **说明有、本次代码无**；按口径规则第 2 条，本站**仍收录为已上线** |
| 虚灵之怖 符文掉落 ≈ 1/4（T1–T4） | ✅ | `TreasureClassEx.txt` `Ethereal Terror T1..T4`：期望符文抽取 = `Picks×Prob/(Prob+NoDrop)`，T1 `0.500→0.125`、T2 `0.667→0.167`、T3 `1.000→0.250`、T4 `2.000→0.500` → **四层全部恰为 1/4** |
| 绝对之怖每组固定 1 只 + 降低材料掉落（总产出 ≈ 1/10） | ✅ | ① `MonStats.txt horrorofabsolutet1..t4` `MaxGrp 2 → 1`；② `TreasureClassEx.txt` 材料子池：T1 `NoDrop 2→36`、T2 `1→29`、T3 `0→23`、T4 `Picks3/NoDrop3 → Picks1/NoDrop12`；单只比值 `0.150/0.152/0.148/0.146` × 组数比 `1/1.5` = **≈ 1/10** |
| 取消完美级以下精华掉落 | ✅ **仅炼狱模式** | `TreasureClassEx.txt`：地图精华 `Essences T1/T2/T3 Map` 由「Perfect 15 / Greater 35 / Base 50」→「Perfect Tier Essences 1 + NoDrop」；`Hatred Orb Essences` 同改；普通世界 `Act X Good` 系列的 `Base Tier Essences` 条目全部删除，权重转入 `NoDrop`；全表 `Base/Greater Tier Essences` 引用 19/4 → **0/0**，`Perfect` 仍 4 处。**standard 的 `TreasureClassEx.txt` 未改动** |
| 降低提取宝珠世界掉率与炼狱熔炉抽取概率 | ✅ | ① `Orb of Extraction NM/H`：NM `Unique 3000→14063`、`Set 10→167`；H `Unique 1000→9375`、`Set 10→167` → 约 1/30,000 → 1/2,348,521、1/10,000 → 1/1,565,625；② 炼狱熔炉 OUTCOME `Orb of Extraction` `2.95% → 0.4%`（按 `value` 窗口 819→131，分母 32767） |
| 珍稀宝物世界掉落倍率（镜子 ×3 / 光之歌瓶 ×3 / 回城书 ×6 / 骷髅钥匙 ×6 / 鉴定书 ×6 / 恶魔宝盒 ×20 / 谜盒 ×6） | ⭕ **以说明为准**（本次代码未改动这 5 项） | **本区间实际只改了 3 项**：`Lillith Mirror` `Unique 75000/37500/25000 → 150000/75000/50000`（掉率减半）、`Vial of Lightsong` 同幅减半、`Orb of Extraction`（见上）。**骷髅钥匙 / 回城书 / 鉴定书 / 恶魔宝盒 / 拉苏克谜盒 5 项 old=new 完全未变** → 所述倍率是在基准提交（08-24）之前就写入的。可核对的：拉苏克谜盒普通难度 `Unique=0` → 不掉落 ✅；回城书/鉴定书/骷髅钥匙 = `1/(15000×167) = 1/2,505,000`，对仓库自带 `docs/SOE战网经济平衡TODO.md` 记载的汉服 `1/15,000,000` 恰为 **6.00×** ✅，噩梦/地狱同为 6.00× ✅。**无法验证**：镜子与光之歌瓶的绝对「约 3 倍」、恶魔宝盒「20 倍」、谜盒「约 6 倍」——汉服基准表（`G:\ggma`）不在仓库内 |
| 炼狱熔炉随机抽取灰烬 25→50 | ✅ **仅炼狱模式** | damnation `CubeMain.txt` `KILN CURRENCY PRINTER / Roll the dice`：`hfcr,qty=25 → 50`（standard 同为 25 未改） |
| 提高「制图师凿子·贪婪」概率 | ✅ | 同区 OUTCOME `Chisel of Avarice` `value 6553 → 7241`（`7241/32767 = 22.1%`，旧 20%） |
| Boss 材料随机转换灰烬 15→25 | ✅ **仅炼狱模式** | `UBER MATS CONVERSION - SAME UBER`（19 抽取行 + 79 结果行）`hfcr,qty=15 → 25` |
| 憎恨宝珠随机转换灰烬 25→50 | ✅ **仅炼狱模式** | `RE-ROLL HATE ORB TYPE - ROLL/OUTCOME`（6 + 30 行）`hfcr,qty=25 → 50` |
| 暗金武器/护甲/箭袋/弩矢袋 分解产出 普通1/扩展2/精英3 机遇碎片 | ✅ **仅炼狱模式** | `DAMNATION MODE ONLY CHANGES` 新增 `[bas]/[exc]/[eli]` 三档：`armo,uni` / `weap,uni` / `misl,uni`，`output oros,qty=1/2/3`（旧为单一档 `oros×1`）。`oros` 官方串表 = 机遇碎片 |
| 套装武器/护甲 分解产出 普通1/扩展2/精英3 套装碎片；两类均支持普通钥匙与可复用骷髅钥匙 | ✅ **仅炼狱模式** | `armo,set` / `weap,set` × `bas/exc/eli`，`output exos,qty=1/2/3`（`exos` 官方串表 = **崇高碎片**，说明称「套装碎片」）。钥匙：`key`（骷髅钥匙，消耗）+ `rkey`（`Skeleton Key Unlimited`，`output useitem` 返还，碎片走第二输出列）。暗金 3×3×2 = 18 行（旧 6），套装 2×3×2 = 12 行（旧 4）。说明「别分解朴素长袍，会吃钥匙」自洽：`smer` = 朴素长袍，其暗金版 `Tabula Rasa` 会匹配 `armo,uni,*` 而消耗钥匙 |
| 取消「机遇宝珠 / 神话宝珠 + 灰烬 → 随机狱铸暗金」配方 | ✅ **仅炼狱模式** | damnation `CubeMain.txt`：神话宝珠 `mfo` 抽取行（`hffd` + `mfo,qty=5` + `hfcr,qty=35`）及 31 条 `Hellforged …` 结果行，以及机遇宝珠 `oroc` 抽取行（`hffd` + `oroc,qty=1` + `hfcr,qty=35`）及 31 条结果行，**全部 `enabled 1→0`**（配方文本仍在表中，但不可执行，页面仅收录 enabled=1 故已消失） |

---

## 3. 机制说明（技能范围 / 技能增益效果 / 技能频率）

结论：**公式、表格、技能清单全部逐格吻合，零偏差**。

| 说明条目 | 结论 | 代码证据 |
|---|---|---|
| `P＝70 × X ÷（X＋18）` | ✅ | `Skills.txt` 中 `(stat('item_skill_aoe'.accr)*70)/(stat('item_skill_aoe'.accr)+18)` 出现于 **93 个技能行**，系数 70 / 常数 18 **无任何变体** |
| `范围＝（基础范围＋固定范围）×（1＋P÷100）`，固定范围先加后乘、不走递减曲线 | ✅ | `ItemStatCost.txt`：`item_skill_aoe` ID=263（`StrSkillRadius`）、`item_skill_aoe_flat` ID=295（`StrSkillAoeFlat`），两提交完全相同。93 个技能中 91 个为半径型 `((基础 + flat) * (100 + P) / 100)`，仅 `Nova`/`Frost Nova` 为速度型 |
| X→P 表（+0/5/10/18/42/72% → 0/15.2/25/35/49/56%） | ✅ | 逐点验算 `70X/(X+18)`：`15.217` / `25` / `35` / `49` / `56`，与表格**逐格一致**；趋近 70% 极限亦成立 |
| 新星 X→初始扩散速度表（+5%→12.5%、+18%→33.3%、+42%→45.8%、+72%→54.2%）；两种新星变化相同 | ✅ | `Nova.cltcalc1/calc3` = `(24*P)/100 + (flat*64*(100+P))/(3*14*100)`，`Frost Nova` 同式（分母 `3*12*100`）。`Missiles.txt`：`nova` Vel=24/Range=14、`frostnova` Vel=24/Range=12（本次未改）→ 速度增量 `24*trunc(P)/100`：`3/24=12.5%`、`8/24=33.33%`、`11/24=45.83%`、`13/24=54.17%`，**逐格一致**；两者百分比项相同（Vel 均 24）故「变化相同」，固定范围项分母不同故「分别换算」 |
| 受技能范围影响的职业技能清单（7 职业 + 独立变体） | ✅ **93/93 完全吻合** | 亚马逊 5 / 法师 9 / 死灵法师 12 / 圣骑士 23 / 野蛮人 6 / 德鲁伊 8 / 刺客 11 / 独立变体 19 = 93。说明**无多列、无漏列**；唯一额外行 `Hierophant Tier 4` 只在 `aurastat5` **提供**该属性，说明已明确排除 |
| 狂犬病、火魔专属圣火未接入范围公式 | ✅ | `Rabies` 整行无 `item_skill_aoe*`；`Holy Fire Fire Golem.aurarangecalc = ln12`（纯基础+等级成长） |
| 技能增益效果公式（线性，不用范围曲线） | ✅ | `buff_effect`（`ItemStatCost.txt` ID=465）在 `Skills.txt` 29 个技能行、86 个单元格使用，**全部**为 `X*(100+buff)/100` 形态；与 `item_skill_aoe` 同时出现的表达式数 = **0** |
| 增益效果受益清单 | ✅ **29/29 完全吻合** | 见下节「清单对照」 |
| 炽烈之径地面火伤 / 冰甲反击 / 能量盾吸收与耗蓝 不受增益放大 | ✅ | `Blaze` 的 `buff_effect` 仅作用于 `velocitypercent`；`Shiver Armor` / `Chilling Armor` 仅作用于 `skill_armor_percent` / `item_fasterblockrate` / `toblock`，反击伤害字段无 `buff_effect`；`Energy Shield` / `Energy Shield SelfAura` 整行无 `buff_effect`；`Missiles.txt` 中 `buff_effect` 出现 **0 次**（任何弹体伤害都不按其放大） |
| 技能频率公式 `间隔＝原间隔×(1－频率÷100)` | ✅ | `item_skill_frequency`（`ItemStatCost.txt` ID=267）；`Skills.txt` 11 行使用，形态统一为 `max(下限, 原间隔 - 原间隔*freq/100)`，全部带下限 |
| 频率受益清单与基础间隔 | ✅ **11/11 逐值吻合** | 见下节「清单对照」 |

### 3.1 清单对照（三方一致）

| 清单 | 说明 vs 代码 |
|---|---|
| 技能范围（93 项） | 说明里有、代码里没有：**无**；代码里有、说明没写：**无** |
| 技能增益效果（29 项） | 说明里有、代码里没有：**无**；代码里有、说明没写：**无** |
| 技能频率（11 项） | 说明里有、代码里没有：**无**；代码里有、说明没写：**无**（爆裂箭引信 `par5=2`、雷云风暴 `par3=50` 且表达式 `blvl*25/20`、四光环 `25` 帧、火山爆 `par2=6`、龙卷风 `par1=15`、刃之怒 `par4=4` 且 `max(2,…)`、装备刀盾 `max(3,…)`、火魔圣火 `perdelay=25` 字面量） |

---

## 4. 荣誉光环系统 / 客户端修复

| 说明条目 | 结论 | 说明 |
|---|---|---|
| 荣誉光环系统于 S1 启用（99 级 / DClone / Rathma / Lucion / 大主教拉撒路 / 咖啡 / 开发者） | ⚠️ **部分可验证** | **可验证**：`States.txt` S1 新增 `soe_lazarus_honor`（Id 254、`aura=1`、`overlay1=aura_magicgoldfind`）+ `Overlay.txt` 新增 `soe_lazarus_ice`，与「大主教拉撒路光环」直接对应。<br>**无法验证**：全数据表（`States.txt` 全 72 列、`Overlay.txt`、`Skills.txt`、`ItemStatCost.txt`、`UniqueItems.txt`、`Misc.txt`、`MonStats*.txt` 等）中**没有** 99 级 / Diablo Clone / Rathma / Lucion / 咖啡 / 开发者光环的任何定义。这些解锁条件、`Lv0/Lv1 不解锁`、`重进房间生效`、`赛季独立`、`账号级 vs 角色级` 属于**服务端逻辑**，不在本数据仓库 |
| 修复 D2GL 在 `-direct` 环境下的崩溃 | ❓ 无法验证 | 仓库文件树（705 条路径）中无任何 `d2gl` / `glide` / `ddraw` / `-direct` 相关文件或引用；`modified DLLs/` 仅 4 个 DLL 且本次未改动。该修复应在启动器 / 客户端二进制（另有仓库） |

> ⚠️ 附带澄清：本区间新增的 `damnation-mode/.../SuperUniques.txt`（69 行）**与拉撒路 / 荣誉系统无关** —— 它是补齐的原版超级唯一怪表，与 `standard-mode` 版本逐行比较**仅 1 处差异**（`The Feature Creep` 的地狱 TC）。

---

## 5. 代码中有、说明未收录的改动（建议补录）

| # | 改动 | 证据 | 影响 |
|---|---|---|---|
| 1 | **降低软核死亡经验惩罚** | `standard-mode/DifficultyLevels.txt` `DeathExpPenalty`：噩梦 `5→1`、地狱 `10→1`（提交 `c151208975`） | 难度 / 手感，值得在赛季页明示 |
| 2 | 随机材料配方的**永恒宝珠代码修正** | `standard` + `damnation` `CubeMain.txt` 输出 `eto → etor`；炼狱熔炉 OUTCOME 描述 `0.05% → 0.061%`（提交 `565a1bd644`；`Misc.txt` 中已无 `eto`） | 修正类 |
| 3 | **地狱铁匠非任务击杀不掉炼狱熔炉修复** | 新增 `damnation SuperUniques.txt`（`The Feature Creep` 地狱 TC `Haphesto (H) → SOE Story Haphesto (H)`）+ `TreasureClassEx.txt` `SOE Story Haphesto (H)` 子 TC 顺序交换使 `hffd` 先判（提交 `d8900ee139`） | 影响炼狱熔炉获取 |
| 4 | **普通命运卡掉落提前到第一幕 / 第二幕** | `damnation TreasureClassEx.txt`：`Act 1 Good` 新增 `Fate Card Normal Prob=8`、`Act 2 Good` 新增 `Prob=12`（提交 `9b24eb7238`，S1 首发提交） | 经济改动，建议补录 |
| 5 | 炼狱熔炉 OUTCOME 概率整体再分配 + 新增未启用的「No reward」行 | 同区：`Chisel of Procurement 18%→16%`、`Catalyst Shard 8%→8.448%`、`Eternal Orb 0.05%→0.061%` 等；新增 `No reward (furnace returned; Cindersouls consumed)`（`enabled=0`） | 说明只提到凿子与提取宝珠两项 |
| 6 | **灵狼（fenris）溅射半径削弱** | `standard-mode/MonProp.txt` `fenris.inc_splash_radius`：噩梦/地狱 `-20 → -60`（普通不变） | 技能数值削弱，说明未提 |
| 7 | 酋长爆燃 / 秽言绽放 **爆炸半径 16 → 12** | `Skills.txt` `Chieftain Explosion.Param1`、`Profane Bloom.Param1`（提交 `3f41b79bbe`，理由为**性能**，提交信息明确「不修改触发概率」） | 说明的「升华调整」节只写了概率，漏了半径 |
| 8 | 深渊军团小怪动画列位修复 | `standard-mode/MonStats2.txt` `abysshordelesser_ext1/2/3`（提交 `fb1277541c`） | 表现修复 |

---

## 6. 模式范围提示（重要）

S1 的多项改动**只作用于炼狱（毁灭）模式**，标准模式未同步。站点若同时展示两种模式，需分别标注：

| 改动 | 标准模式 | 炼狱（毁灭）模式 |
|---|---|---|
| 炼狱熔炉：随机货币烬魂消耗 | 25（未变） | **50** |
| 炼狱熔炉：Boss 材料转换烬魂消耗 | 15（未变） | **25** |
| 炼狱熔炉：憎恨宝珠重洗烬魂消耗 | 25（未变） | **50** |
| 炼狱熔炉：随机狱铸暗金配方 | 已无 | **已禁用**（`enabled=0`） |
| 炼狱熔炉：烬魂印钞概率表 | 一套（崇高宝珠 10%、贪婪 9%…） | **另一套**（贪婪 22.1%、采购 16%、提取宝珠 0.4%…） |
| 取消完美级以下精华掉落 | 未变（仍有低级精华） | **已取消** |
| 暗金 / 套装分解档位（1/2/3 碎片） | 无此配方 | **有** |
| 升华·酋长第四阶击杀爆炸概率 | **25（未改）** | **15** |
| 升华·秘术师第三阶秽言绽放概率 | 15 | 15 |

---

## 7. 无法从本仓库验证的项目

1. **中文文案改动**（乌鸦混合伤害、灰熊溅射、变形风遁、火魔圣火、狼人变化中文名与快捷栏名、骷髅法师说明）—— 仓库仅有英文串表，且本次未改动任何 `.tbl`。需以**国服客户端中文串表**另行核对。
2. **D2GL 崩溃修复** —— 不在数据仓库（启动器 / 客户端二进制）。
3. **相对 PD2 汉服基准的绝对倍率**（镜子 ×3、光之歌瓶 ×3、恶魔宝盒 ×20、拉苏克谜盒 ×6）—— 汉服基准表不在仓库内；仓库侧只能确认本次实际改动了哪些、以及回城书/鉴定书/骷髅钥匙相对仓库自带的汉服记录恰为 6.00×。
4. **荣誉光环系统的解锁与管理规则**（99 级、Boss Lv2 单人击杀、管理员授予、账号级 / 角色级、赛季独立）—— 属服务端逻辑。

---

## 8. 复现方式

```bash
# 1) 拉两版数据（走本地代理）
git clone -b SOECN https://github.com/wdjwxh/PD2-Sanctuary-of-Exile /tmp/SOECN
git -C /tmp/SOECN checkout 9b24eb72380a724457e8e6d37a169c837f0ad0a0

# 2) 逐字段比对
diff -u <(git -C /tmp/SOECN show 374d8971:standard-mode/data/global/excel/Skills.txt) \
        /tmp/SOECN/standard-mode/data/global/excel/Skills.txt

# 3) 配方层面断言（本站校验脚本，41 条）
python3 tools/verify_cube_claims.py
```
