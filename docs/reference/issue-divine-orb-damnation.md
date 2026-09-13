# 问题报告：炼狱（毁灭）模式下「神授宝珠」无任何获取途径

**报告日期**：2026-09-13
**核对基准**：`SOECN` 仓库（`SOECN` 分支）commit **`9b24eb72`**（国服 SOL 第一赛季正式服，2026-09-11）
**相关文件**：`damnation-mode/data/global/excel/{CubeMain.txt, TreasureClassEx.txt, Misc.txt}`

---

## 结论

炼狱（毁灭）模式下，**有 32 条启用配方需要「神授宝珠」（`dvo`），但该模式下神授宝珠没有任何可获得来源** ——
不掉落、印钞不产出、也没有产出它的配方，这 32 条配方因此无法执行。

**严重性说明**：狱铸暗金本身在炼狱模式仍可正常掉落（`enabled=1`、`rarity` 1~5），
受影响的是「**定向**指定狱铸」这条便利路线，不是内容可达性。

---

## 证据

### 1. 需要神授宝珠的配方：32 条，全部 `enabled=1`

`damnation-mode/data/global/excel/CubeMain.txt`（行号按文件物理行）：

| 行号 | 说明 | 产出 |
|---|---|---|
| **L3762** | Create Armageddon Blade | Arma Blade Replica |
| **L4480 – L4510** | Hellforged ×××（**31 条**，指定地狱锻铸暗金） | 各自的 Hellforged 版本 |

配方材料构成：`炼狱熔炉 + 神授宝珠（dvo）×1 + 结晶烬魂 + 目标暗金`。

### 2. 掉落表里没有神授宝珠

`damnation-mode/data/global/excel/TreasureClassEx.txt`：**`dvo` 出现 0 次**。

炼狱模式的宝珠掉落池 `New orbs` 只剩：

```
New orbs      = csor(2) ooal(3)          ← 混沌宝珠 / 点金石
New orbs T1   = etor(1) csor(39) ooal(60)
New orbs T2   = etor(1) csor(43) ooal(50)
New orbs T3   = etor(1) csor(47) ooal(52)
```

对比标准模式（`standard-mode`）同一个池子：`mfo(15) exo(35) csor(20) ooal(30)`；
`dvo` 在标准模式掉落表里出现 **10 次**（`New orbs T1/T2/T3`、`New orbs fallen`、`Dungeon Orbs` 等）。

### 3. 炼狱熔炉「烬魂印钞」不产出神授宝珠

`CubeMain.txt` 中 `OUTCOME`（印钞）的 12 个产出为：
`Chisel of Avarice / Chisel of Procurement / Glyph of Corruption / Glyph of Adversaries /
Glyph of Nemeses / Catalyst Shard / Orb of Alchemy / Chaos Orb / Demonic Cube /
Larzuk's Puzzlebox / Orb of Extraction / Eternal Orb` —— **不含 `dvo`**。

### 4. 唯一产出配方是空转的

炼狱模式下产出 `dvo` 的配方只有 1 条：

```
[Divine Orb CONVERSION - TECHNICAL] Convert old divine orb to new divine orb
  输入: 旧神授宝珠（divo）×1  →  输出: 神授宝珠（dvo）×1
```

但 **`divo` 在标准模式与炼狱模式下同样是「掉落 0 处、产出 0 条」**（两模式的 CubeMain 里都没有任何产出 `divo` 的行）——
即这条转换配方的输入也无从获得。

### 5. 物品本身是启用状态

`Misc.txt`：`dvo` = `Divine Orb`，`spawnable=1`，`level=85`，`namestr=dvo`。
官方串表（国服客户端）中 `dvo = 神授宝珠`（另有旧版 `divo` 同名）。

---

## 影响

- 炼狱模式下这 32 条配方**无法执行**（材料拿不到）。
- **但这不是「内容不可达」**（2026-09-13 复核更正）：31 件狱铸暗金在**两种模式下都 `enabled=1`、
  `rarity` 为 1~5**，也就是说**它们本身照常掉落**，不依赖这条配方；这条配方只是「**定向**获得」的便利路线。
- 因此本问题的严重性限于：**便利路线不可用 + 32 条启用配方成为死配方**。
- 若服务端另有发放方式（管理发放 / 活动奖励 / 或某张表不在本仓库内），请忽略本报告。

---

## 建议（供选择）

1. **若属有意设计**（炼狱模式不做地狱锻铸）→ 建议把这 32 条配方的 `enabled` 置 0，避免玩家在方块前反复尝试；
2. **若属疏漏** → 恢复一个来源即可，最小改动是：
   - 在 `New orbs T1/T2/T3` 池里按标准模式的比例加入 `dvo`（标准模式为 17/20/22），或
   - 在炼狱熔炉 `OUTCOME`（印钞）里加入 `dvo`（标准模式为 3.5%），或
   - 给 `divo → dvo` 这条转换配方补一个 `divo` 的来源。

---

## 复现方法

```bash
git -C <SOECN 仓库> show 9b24eb72:damnation-mode/data/global/excel/CubeMain.txt | \
  awk -F'\t' 'NR==1{for(i=1;i<=NF;i++){if($i=="description")d=i; if($i=="input 2")i2=i; if($i=="output")o=i}} NR>1 && $i2 ~ /^dvo/ {print NR": "$d" -> "$o}'
```
（等价于本报告第 1 节的行号列表。）
