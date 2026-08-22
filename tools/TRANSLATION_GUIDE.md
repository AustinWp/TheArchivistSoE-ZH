# PD2 流放圣域中文资料库 · 静态页翻译规范

## 任务
把指定 JSON 文件中每个条目的 `text` 数组（英文 markdown 行）翻译为简体中文，直接写回文件。
`id` 和 `title` **不要改动**（title 已翻译）。

## 文件格式
- UTF-8 JSON，数组形式
- 写回格式：`json.dump(data, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)`
- 每行是一条 markdown，翻译后保持**行数一一对应**（数组元素数量不变）

## Markdown 语法（必须保留，只翻译文本内容）
- `` `反引号` ``：代码/物品名/数值高亮 —— 翻译内容（如 `Mythic Orb` → `神话宝珠`）
- `**粗体**`：翻译内容
- `[显示文本](链接)`：链接 URL 保持不变；显示文本翻译
  - 外部链接如 `[Vanilla PD2 Wiki](https://...)`：显示文本翻译
  - 内部跳转链接 `[action speed](app:changes:action speed)`：**前缀 `app:` 和 tab 名保持英文**（如 `app:changes:`），但最后的 name 参数翻译为中文（如 `app:changes:动作速度`），使其与翻译后的页面内容匹配
- `- ` 列表项、`  - ` 子列表、缩进全部保留原样

## 游戏机制术语（必须使用，符合暗黑 2 机制与官方译名）
- PDR/Physical Damage Reduction → 物理伤害减少；MDR/Magic Damage Reduction → 魔法伤害减少
- %PDR → 百分比物理伤害减少；flat PDR → 固定物理伤害减少
- Faster Cast Rate → 施法速度；Faster Hit Recovery → 快速打击恢复；Faster Block Rate → 快速格挡率
- Increased Attack Speed → 攻击速度；Cast speed → 施法速度；Run/Walk speed → 跑动/行走速度
- Attack Rating → 攻击准确率；Defense → 防御；Base defense → 基础防御
- Enhanced Damage → 增强伤害；Physical Damage → 物理伤害；Magic Damage → 魔法伤害；Elemental Damage → 元素伤害
- Crushing Blow → 压碎性打击；Deadly Strike → 致命攻击；Open Wounds → 撕裂伤口
- Life stolen per hit → 每次命中偷取生命；Mana stolen per hit → 每次命中偷取法力
- Life leech → 生命偷取；Mana leech → 法力偷取
- Resistance → 抗性（Fire → 火焰、Cold → 冰冷、Lightning → 闪电、Poison → 毒素）
- Physical Resist → 物理抗性；Magic Resist → 魔法抗性
- Maximum Resistance → 抗性上限
- Break immunities → 破除免疫
- Hard points / base level → 基础技能等级（hard points 指投入的技能点）
- Synergy → 协同加成
- Projectile → 投射物；pierce → 穿透
- DoT / damage over time → 持续伤害
- Splash damage → 溅射伤害
- Aura → 灵气；Curse → 诅咒
- 技能系名：Poison and Bone Skills → 毒素与白骨技能；Summoning → 召唤；Shape Shifting → 变形；Elemental → 元素；Offensive Auras → 攻击灵气；Defensive Auras → 防御灵气；Shadow Disciplines → 影子训练；Passive and Magic → 被动与魔法；Martial Arts → 武学；Warcries → 战吼；Combat Masteries → 战斗专家；Cold Spells → 冰冷法术；Fire Spells → 火焰法术；Lightning Spells → 闪电法术；Trap → 陷阱
- 职业：Amazon → 亚马逊；Assassin → 刺客；Barbarian → 野蛮人；Druid → 德鲁伊；Necromancer → 死灵法师；Paladin → 圣骑士；Sorceress → 法师
- 难度：Normal → 普通；Nightmare → 噩梦；Hell → 地狱
- Act → 幕（Act 1 → 第一幕）
- 货币/材料：Mythic Orb → 神话宝珠；Divine Orb → 神圣宝珠；Exalted Orb → 崇高宝珠；Sacred Orb → 圣化宝珠；Chaos Orb → 混沌宝珠；Orb of Alchemy → 点金石；World Stone Shard → 世界之石碎片；Ornate Charm → 华丽护符；Mythical Jewel → 神话珠宝；Glyph → 雕文；Terror → 恐怖；Chisel → 雕刻刀；Essence → 精华；Rune → 符文（符文名 El/Zod 等保持英文大写）
- 品质：Normal → 普通；Exceptional → 扩展；Elite → 精英；Superior → 超强；Magic → 魔法；Rare → 稀有；Set → 套装；Unique → 暗金；Crafted → 手工；Ethereal → 无形
- 物品部位：Weapon → 武器；Armor → 护甲；Helm/Helmet → 头盔；Shield → 盾牌；Gloves → 手套；Boots → 靴子；Belt → 腰带；Ring → 戒指；Amulet → 项链；Charm → 护符；Jewel → 珠宝；Grand Charm → 大型护符
- 暗金名（D2 经典译名）：Nagelring → 拿各的戒指；Manald Heal → 马纳德的治疗；Raven Frost → 乌鸦之霜；Dwarf Star → 矮人之星；Carrion Wind → 腐肉之风；Nokozan Relic → 诺科赞遗物；The Cat's Eye → 猫眼；The Mahim Oak Curio → 马希姆橡树古玩；Saracen's Chance → 撒拉森的机会；Crescent Moon → 新月；The Eye of Etlich → 艾利屈之眼；Atma's Scarab → 阿特玛的圣甲虫；Gheed's Fortune → 基德的运气；The Stone of Jordan → 乔丹之石；Tyrael's Might → 泰瑞尔的力量；Goldwrap → 金包袱；Gore Rider → 血脚；String of Ears → 长串之耳；Verdungo's Hearty Cord → 维尔登戈的心结；Arachnid Mesh → 蛛网腰带；Spirit Shroud → 灵魂帷幕；Skin of the Vipermagi → 蛇魔法师之皮；Que-Hegan's Wisdom → 魁黑刚的智慧；Shaftstop → 谢夫特斯坦布；Guardian Angel → 守护天使；Bonehew → 白骨阴影；Lidless Wall → 无睑墙；Stormshield → 暴风之盾；Mara's Kaleidoscope → 马拉的万花筒；Highlord's Wrath → 大君之怒
- 怪物名：Andariel → 安达利尔；Duriel → 督瑞尔；Mephisto → 墨菲斯托；Diablo → 暗黑破坏神；Baal → 巴尔；Hephasto → 赫法斯托；Blood Raven → 血乌；Radament → 罗达门特；The Summoner → 召唤者；Nihlathak → 尼拉塞克；Uber boss → 超级首领；Uber Tristram → 超级崔斯特瑞姆；Pindleskin → 粉碎者
- NPC：Cain → 凯恩；Charsi → 恰西；Gheed → 基德；Warriv → 瓦瑞夫；Larzuk → 拉苏克；Tyrael → 泰瑞尔；Izual → 衣卒尔；Malah → 马拉；Anya → 安亚
- 场景/机制：Moo Moo Farm → 哞哞农场；Cow Level → 奶牛关；Horadric Cube → 赫拉迪克方块；Hellforge → 地狱熔炉；Infernal Kiln → 炼狱熔炉；Sacred → 圣化；Corruption → 腐化；Damnation Mode → 毁灭模式；Standard Mode → 标准模式；Ascendancy → 飞升；Sanctuary of Exile → 流放圣域（SoE 保持缩写）；Drop Rate → 掉落率；Treasure Class → 财宝等级；Magic Find → 寻宝率（MF）；Item Level → 物品等级；Quality Level → 品质等级；Socket → 孔/孔数；Durability → 耐久度；Required Level → 需求等级

## 风格
- 简体中文、游戏术语风格（参考暗黑 2 官方中文版）
- 保留数字、百分比、公式（如 `1000 - 34 * base skill level` 中英文单词翻译、公式结构不变）
- 不确定的专有名词可音译+注释，但尽量使用上述标准译名
- 完成后报告：翻译了多少行、是否遇到无法处理的行（列出原文）
