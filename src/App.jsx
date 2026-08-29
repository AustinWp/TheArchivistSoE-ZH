import React, {useEffect, useMemo, useState} from "react";

import BuildsPanel from "./BuildsPanel";

import SwordIcon from "./icons/sword.svg";
import StaffIcon from "./icons/staff.svg";
import BowIcon from "./icons/bow.svg";
import JavelinIcon from "./icons/javelin.svg";
import SpearIcon from "./icons/spear.svg";
import AxeIcon from "./icons/axe.svg";
import MaceIcon from "./icons/mace.svg";
import KnifeIcon from "./icons/knife.svg";
import CrossbowIcon from "./icons/crossbow.svg";
import ClawsIcon from "./icons/claws.svg";
import PolearmIcon from "./icons/polearm.svg";
import ScepterIcon from "./icons/scepter.svg";
import WandIcon from "./icons/wand.svg";
import ThrowingAxeIcon from "./icons/throwing-axe.svg";
import ThrowingKnifeIcon from "./icons/throwing-knife.svg";
import SorceressOrbIcon from "./icons/orb.svg";
import HammerIcon from "./icons/hammer.svg";
import ScytheIcon from "./icons/scythe.svg";
import HelmetIcon from "./icons/helmet.svg";
import BodyArmorIcon from "./icons/armor.svg";
import ShieldIcon from "./icons/shield.svg";
import BootsIcon from "./icons/boots.svg";
import GlovesIcon from "./icons/gloves.svg";
import BeltIcon from "./icons/belt.svg";
import RingIcon from "./icons/ring.svg";
import AmuletIcon from "./icons/amulet.svg";
import QuiverIcon from "./icons/quiver.svg";
import JewelIcon from "./icons/jewel.svg";
import MapIcon from "./icons/map.svg";
import MythicJewelIcon from "./icons/mythic.svg";
import OrnateCharmIcon from "./icons/cm4.svg";
import RuneIcon from "./icons/rune.svg";
import SacredIcon from "./icons/sacred.svg";
import FateCardIcon from "./icons/fatecard.svg";

const APP_VERSION = import.meta.env.VITE_APP_VERSION;
const GAME_VERSION = "13.0.2";
const LATEST_RELEASE = "https://github.com/Lukaszpg/PD2-Sanctuary-of-Exile/releases/tag/v13.0.2";

const HIDDEN_MODIFIERS = [
    "一枚戒指统御万戒，于黑暗中将其束缚",
];

const TABS = {
    weapons: "武器",
    armors: "护甲",
    uniques: "暗金装备",
    runewords: "符文之语",
    affixes: "词缀",
    sacreds: "圣化",
    corruptions: {
        title: "腐化",
        badge: "测试版"
    },
    skills: "技能",
    builds: "核心BD构筑",
    cube: "魔方配方",
    changes: "标准模式",
    help: "帮助",
    changelog: "更新日志",
    calculators: "技能计算器",
    dropcalc: {
        title: "掉落计算器",
        badge: "体验版"
    },
    damnation: {
        title: "毁灭模式",
        badge: "测试版"
    },
    ascendancies: "升华",
    mapping: "地图",
    fatecards: "命运卡牌",
    kiln: "炼狱熔炉",
    essences: "精华"
};

const ALL_RUNES = ["El", "Eld", "Tir", "Nef", "Eth", "Ith", "Tal", "Ral", "Ort", "Thul", "Amn", "Sol", "Shael", "Dol", "Hel", "Io", "Lum", "Ko", "Fal", "Lem", "Pul", "Um", "Mal", "Ist", "Gul", "Vex", "Ohm", "Lo", "Sur", "Ber", "Jah", "Cham", "Zod"];

// 符文中文名 + 编号（暗黑 2 官方译名）
const RUNE_ZH = {
    "El": {zh: "艾尔", num: 1}, "Eld": {zh: "艾德", num: 2}, "Tir": {zh: "特尔", num: 3},
    "Nef": {zh: "那夫", num: 4}, "Eth": {zh: "爱斯", num: 5}, "Ith": {zh: "伊司", num: 6},
    "Tal": {zh: "塔尔", num: 7}, "Ral": {zh: "拉尔", num: 8}, "Ort": {zh: "欧特", num: 9},
    "Thul": {zh: "书尔", num: 10}, "Amn": {zh: "安姆", num: 11}, "Sol": {zh: "索尔", num: 12},
    "Shael": {zh: "夏", num: 13}, "Dol": {zh: "多尔", num: 14}, "Hel": {zh: "海尔", num: 15},
    "Io": {zh: "埃欧", num: 16}, "Lum": {zh: "卢姆", num: 17}, "Ko": {zh: "科", num: 18},
    "Fal": {zh: "法尔", num: 19}, "Lem": {zh: "兰姆", num: 20}, "Pul": {zh: "普尔", num: 21},
    "Um": {zh: "乌姆", num: 22}, "Mal": {zh: "马尔", num: 23}, "Ist": {zh: "伊司特", num: 24},
    "Gul": {zh: "古尔", num: 25}, "Vex": {zh: "伐克斯", num: 26}, "Ohm": {zh: "欧姆", num: 27},
    "Lo": {zh: "罗", num: 28}, "Sur": {zh: "瑟", num: 29}, "Ber": {zh: "贝", num: 30},
    "Jah": {zh: "乔", num: 31}, "Cham": {zh: "查姆", num: 32}, "Zod": {zh: "萨德", num: 33},
};

// 符文显示标签：拉尔（8号）；非符文原样返回
function runeLabel(r) {
    const info = RUNE_ZH[r];
    return info ? `${info.zh}（${info.num}号）` : r;
}

// 符文筛选 chip 紧凑标签：拉尔 8号
function runeChipLabel(r) {
    const info = RUNE_ZH[r];
    return info ? `${info.zh} ${info.num}号` : r;
}

// 圣化宝珠英文名 → 中文名（与 Sacreds.json 的 displayName 对齐，用于显示与跳转匹配）
const SACRED_ORB_ZH = {
    "sacred orb of asylum": "庇护所的圣化宝珠",
    "sacred orb of beast": "野兽的圣化宝珠",
    "sacred orb of bone": "白骨的圣化宝珠",
    "sacred orb of bramble": "荆棘的圣化宝珠",
    "sacred orb of brand": "烙印的圣化宝珠",
    "sacred orb of chaos": "混沌的圣化宝珠",
    "sacred orb of crescent moon": "新月的圣化宝珠",
    "sacred orb of death": "死亡的圣化宝珠",
    "sacred orb of delirium": "狂乱的圣化宝珠",
    "sacred orb of desolation": "荒芜的圣化宝珠",
    "sacred orb of destruction": "毁灭的圣化宝珠",
    "sacred orb of dominion": "主宰的圣化宝珠",
    "sacred orb of doom": "末日的圣化宝珠",
    "sacred orb of dragon": "龙的圣化宝珠",
    "sacred orb of dream": "梦境的圣化宝珠",
    "sacred orb of duress": "强制的圣化宝珠",
    "sacred orb of echo": "回响的圣化宝珠",
    "sacred orb of enigma": "谜团的圣化宝珠",
    "sacred orb of epiphany": "顿悟的圣化宝珠",
    "sacred orb of eternity": "永恒的圣化宝珠",
    "sacred orb of exaltation": "擢升的圣化宝珠",
    "sacred orb of exile": "流亡的圣化宝珠",
    "sacred orb of faith": "信念的圣化宝珠",
    "sacred orb of famine": "饥荒的圣化宝珠",
    "sacred orb of ferocity": "凶残的圣化宝珠",
    "sacred orb of flickering flame": "摇曳之火的圣化宝珠",
    "sacred orb of foresight": "预见的圣化宝珠",
    "sacred orb of fortitude": "刚毅的圣化宝珠",
    "sacred orb of fortress": "要塞的圣化宝珠",
    "sacred orb of fury": "狂怒的圣化宝珠",
    "sacred orb of gloom": "幽暗的圣化宝珠",
    "sacred orb of grief": "悔恨的圣化宝珠",
    "sacred orb of harmony": "和谐的圣化宝珠",
    "sacred orb of honor": "荣誉的圣化宝珠",
    "sacred orb of hustle": "匆忙的圣化宝珠",
    "sacred orb of ice": "冰冻的圣化宝珠",
    "sacred orb of infinity": "无限的圣化宝珠",
    "sacred orb of innocence": "纯真的圣化宝珠",
    "sacred orb of insight": "洞察的圣化宝珠",
    "sacred orb of kingslayer": "弑王者的圣化宝珠",
    "sacred orb of last wish": "最后希望的圣化宝珠",
    "sacred orb of lawbringer": "执法者的圣化宝珠",
    "sacred orb of loyalty": "忠诚的圣化宝珠",
    "sacred orb of memory": "回忆的圣化宝珠",
    "sacred orb of mist": "迷雾的圣化宝珠",
    "sacred orb of oath": "誓约的圣化宝珠",
    "sacred orb of obedience": "服从的圣化宝珠",
    "sacred orb of obsession": "执念的圣化宝珠",
    "sacred orb of penance": "赎罪的圣化宝珠",
    "sacred orb of phoenix": "凤凰的圣化宝珠",
    "sacred orb of plague": "瘟疫的圣化宝珠",
    "sacred orb of pride": "骄傲的圣化宝珠",
    "sacred orb of prudence": "审慎的圣化宝珠",
    "sacred orb of purity": "纯净的圣化宝珠",
    "sacred orb of pursuit": "追猎的圣化宝珠",
    "sacred orb of rain": "雨的圣化宝珠",
    "sacred orb of rapture": "狂喜的圣化宝珠",
    "sacred orb of resonance": "共鸣的圣化宝珠",
    "sacred orb of rift": "裂缝的圣化宝珠",
    "sacred orb of sanctuary": "圣堂的圣化宝珠",
    "sacred orb of scripture": "经文的圣化宝珠",
    "sacred orb of shattered wall": "破碎之墙的圣化宝珠",
    "sacred orb of spirit": "精神的圣化宝珠",
    "sacred orb of stone": "石块的圣化宝珠",
    "sacred orb of tailwind": "顺风的圣化宝珠",
    "sacred orb of tantrum": "盛怒的圣化宝珠",
    "sacred orb of unbending will": "不屈意志的圣化宝珠",
    "sacred orb of venom": "毒牙的圣化宝珠",
    "sacred orb of visions": "幻象的圣化宝珠",
    "sacred orb of white": "白色的圣化宝珠",
    "sacred orb of wind": "风的圣化宝珠",
    "sacred orb of winter": "寒冬的圣化宝珠",
    "sacred orb of wrath": "愤怒的圣化宝珠",
    "sacred orb of zenith": "天顶的圣化宝珠",
    "sacred orb of bastion": "堡垒的圣化宝珠",
};
const sacredNameZh = (v) => SACRED_ORB_ZH[String(v ?? "").trim().toLowerCase()] || v;

const PROP_HIGHLIGHT_RULES = [{test: /corrupted|腐化/i, className: "propRed"},];

const WEAPON_ICON_MAP = {
    sword: SwordIcon,
    staff: StaffIcon,
    bow: BowIcon,
    javelin: JavelinIcon,
    spear: SpearIcon,
    axe: AxeIcon,
    mace: MaceIcon,
    knife: KnifeIcon,
    crossbow: CrossbowIcon,
    claws: ClawsIcon,
    polearm: PolearmIcon,
    scepter: ScepterIcon,
    wand: WandIcon,
    throwingAxe: ThrowingAxeIcon,
    throwingKnife: ThrowingKnifeIcon,
    orb: SorceressOrbIcon,
    hammer: HammerIcon,
    scythe: ScytheIcon,
    quiver: QuiverIcon
};

const ARMOR_ICON_MAP = {
    helm: HelmetIcon,
    pahm: HelmetIcon,
    phlm: HelmetIcon,
    pelt: HelmetIcon,
    circ: HelmetIcon,
    tors: BodyArmorIcon,
    shie: ShieldIcon,
    boot: BootsIcon,
    glov: GlovesIcon,
    belt: BeltIcon,
    bels: BeltIcon,
    ashd: ShieldIcon,
    head: ShieldIcon
};

const JEWELRY_ICON_MAP = {
    rin: RingIcon,
    amu: AmuletIcon,
    ram: AmuletIcon,
    aqv: QuiverIcon,
    aqv2: QuiverIcon,
    aqv3: QuiverIcon,
    cqv: QuiverIcon,
    cqv2: QuiverIcon,
    cqv3: QuiverIcon,
    jew: JewelIcon,
    t51: MapIcon,
    t52: MapIcon,
    t53: MapIcon,
    t54: MapIcon,
    t55: MapIcon,
    t56: MapIcon,
    mjw: MythicJewelIcon,
    cm4: OrnateCharmIcon,
    cm2: OrnateCharmIcon,
    cm3: OrnateCharmIcon,
    cm1: OrnateCharmIcon,
};

const MOD_EXPANSIONS = [{
    whenIncludes: "all resistances",
    implies: ["fire resistance", "cold resistance", "lightning resistance", "poison resistance",],
},

    {
        whenIncludes: "all attributes", implies: ["strength", "dexterity", "vitality", "energy"],
    }];

const ARMOR_TYPE_MAP = {
    helm: "头盔",
    tors: "护甲",
    shie: "盾牌",
    glov: "手套",
    boot: "靴子",
    belt: "腰带",
    bels: "腰带",
    pelt: "德鲁伊毛皮",
    phlm: "野蛮人头盔",
    ashd: "圣骑士盾牌",
    head: "死灵法师头颅",
    circ: "头环",
    pahm: "圣骑士头盔"
};

const TOOLTIPS_TEXT_MAP = {
    "qualityLevel": "品质等级是决定物品归属哪个财宝等级的属性。它对赌博（品质等级越高，物品阶位升级的几率越低）和暗金物品掉落生成都很重要，品质等级越高的物品越不容易掉落。",
    "runes": "这里的符文按照制作符文之语时放入物品的准确顺序显示。",
    "occurrenceChance": "出现几率是指：当游戏在该基底上判定掉落暗金物品、且该基底关联多件暗金物品时，这件物品被选中的几率。",
    "dropRate": "掉落率是指该物品从特定怪物（最可能是超级首领）掉落的几率。",
    "code": "此代码可用于你的掉落过滤器中，以高亮这个特定基底。",
    "uniCode": "此代码可用于你的掉落过滤器中，以高亮这个特定基底 - 记得加上 UNI 修饰符。",
    "sacred": "除了此处提到的物品之外，还需要在魔方中使用圣化宝珠。",
    "mythicDivineOrb": "在流放圣域（Sanctuary of Exile）中，暗金物品可以通过在魔方中使用基底物品和与物品阶位匹配的通货宝珠制作 - 普通与扩展基底使用神话宝珠，精英基底使用神授宝珠。",
    "affixMaxLevel": "当物品等级足够高时，部分词缀将不再有资格出现在该物品上，从而让更好的词缀更有可能出现。",
    "affixFrequency": "频率参数决定该属性在物品上出现的概率。",
    "affixRares": "如果为真，则该属性可以出现在稀有物品上。",
    "affixLevel": "决定该词缀出现所需的最低物品等级。"
};

const INFO_BY_TAB = {
    sacreds: {
        title: "关于圣化",
        text: "圣化系统是流放圣域（Sanctuary of Exile）独有的。它允许你驾驭符文之语的力量，并将其铭刻到 `暗金` 或 `手工` 物品上：\n\n" + "- 制作圣化物品需要找到 `圣化宝珠`，它掉落于 `T4 地下城`，或由 `富饶恐惧` 加入的怪物掉落\n\n" + "- 要圣化一件物品，首先用 `符文`（或其他附加物品 - 请查阅下方列表中的相应配方）与 `圣化宝珠` 合成，制作出 `圣化宝珠（X）`\n\n" + "- 符文必须处于堆叠状态，每种符文的堆叠数量需与本页圣化提示中显示的数量一致\n\n" + "- 将制作好的宝珠与你想圣化的 `暗金` 或 `手工` 物品合成。请注意，附加属性可能因物品类型而异\n\n" + "- 圣化物品可以被 `世界之石碎片` 腐化\n\n" + "- 只要物品**不是** `腐化` 状态，就可以用 `恶魔宝盒` 从 `暗金` 物品上移除圣化属性及其圣化状态（⚠️ 当前数据未见对应配方，待游戏内验证）\n\n" + "- `手工` 物品上的圣化属性及圣化状态**无法**被移除，请谨慎选择！\n\n" + "- 配方中提到的附加装备组件可以是任意品质和阶位"
    },
};

function getTitleByTab(tab) {
    const value = TABS[tab];

    if (value && typeof value === "object") {
        return value.title;
    }

    return value;
}

function visibleProperties(properties) {
    return (properties || []).filter((prop) => {
        const text = String(prop);

        return !HIDDEN_MODIFIERS.some((hidden) =>
            text.includes(hidden)
        );
    });
}

function sacredTypes(it) {
    const a = Array.isArray(it?.itemTypesDisplayNames) ? it.itemTypesDisplayNames : [];
    return a.map((x) => typeZh(n(x))).filter(Boolean);
}

function sacredIngredients(it) {
    const out = [];

    repeatIngredient(it?.firstInputDisplayName, it?.firstInputQuantity).forEach(v => out.push(v));
    repeatIngredient(it?.secondInputDisplayName, it?.secondInputQuantity).forEach(v => out.push(v));
    repeatIngredient(it?.thirdInputDisplayName, it?.thirdInputQuantity).forEach(v => out.push(v));
    repeatIngredient(it?.fourthInputDisplayName, it?.fourthInputQuantity).forEach(v => out.push(v));
    repeatIngredient(it?.fifthInputDisplayName, it?.fifthInputQuantity).forEach(v => out.push(v));
    repeatIngredient(it?.sixthInputDisplayName, it?.sixthInputQuantity).forEach(v => out.push(v));

    return out;
}

// ---- 掉落计算器：财宝等级（TC）名中文化 ----
const TC_DIFFICULTY_ZH = {
    "": "普通",
    "(N)": "噩梦",
    "(H)": "地狱",
};

const TC_ACT_TYPE_ZH = {
    H2H: "近战",
    Miss: "远程",
    Cast: "施法者",
    Champ: "冠军",
    Unique: "暗金",
    Wraith: "幽灵",
};

function translateTcDisplay(tcName, monsterTcMap) {
    const tc = n(tcName);
    if (!tc) return tcName;

    // 1) 精确匹配怪物 TC（如 "Andariel (H)" → "安达利尔（地狱）"）
    if (monsterTcMap && monsterTcMap.has(tc)) {
        return monsterTcMap.get(tc);
    }

    // 2) "Act X (H) TYPE A" → "第 X 幕（地狱）近战 A"
    let m = tc.match(/^Act\s*(\d+)\s*(\([NH]\))?\s*([A-Za-z]+)?\s*([A-C])?$/i);
    if (m) {
        const act = m[1];
        const diff = TC_DIFFICULTY_ZH[m[2] || ""] || "";
        const type = TC_ACT_TYPE_ZH[m[3]] || m[3] || "";
        const suffix = m[4] || "";
        return `第 ${act} 幕${diff ? `（${diff}）` : ""}${type}${suffix ? ` ${suffix}` : ""}`.trim();
    }

    // 3) "MonsterName (H)/(N)" → "怪物名（地狱/噩梦）"
    m = tc.match(/^(.+?)\s*(\([NH]\))$/i);
    if (m && monsterTcMap && monsterTcMap.has(m[1])) {
        const diff = TC_DIFFICULTY_ZH[m[2]] || "";
        return `${monsterTcMap.get(m[1])}（${diff}）`;
    }

    return tc;
}

// ---- tiny helpers ----
const n = (v) => (v === null || v === undefined ? "" : String(v).trim());
const has = (v) => n(v) !== "";
const nz = (v) => has(v) && n(v) !== "0";
const fmtSigned = (v) => {
    if (!has(v)) return "";
    const x = Number(v);
    if (Number.isNaN(x)) return String(v);
    return (x > 0 ? "+" : "") + x;
};

function runewordRuneCount(rw) {
    return [rw?.firstRuneDisplayName, rw?.secondRuneDisplayName, rw?.thirdRuneDisplayName, rw?.fourthRuneDisplayName, rw?.fifthRuneDisplayName, rw?.sixthRuneDisplayName,].filter((x) => n(x)).length;
}

function runewordRunes(rw) {
    return [rw?.firstRuneDisplayName, rw?.secondRuneDisplayName, rw?.thirdRuneDisplayName, rw?.fourthRuneDisplayName, rw?.fifthRuneDisplayName, rw?.sixthRuneDisplayName,]
        .map((x) => n(x))
        .filter(Boolean);
}

// ----- Affix helpers -----

function affixPrimaryPropertyAndMax(affix) {
    const dp = affix?.displayProperties;
    if (!dp) return {property: "", max: 0};

    // Pick the first object from displayProperties
    let first = null;

    if (Array.isArray(dp)) {
        first = dp.find((p) => p && typeof p === "object") || dp[0];
    } else if (typeof dp === "object") {
        first = dp;
    }

    if (first && typeof first === "object") {
        const prop = (first.property != null ? String(first.property) : first.prop != null ? String(first.prop) : "").trim();

        const maxRaw = first.max != null ? Number(first.max) : 0;
        const max = Number.isFinite(maxRaw) ? maxRaw : 0;

        return {property: prop, max};
    }

    return {property: "", max: 0};
}

function affixDisplayString(affix) {
    const dp = affix?.displayProperties;
    if (!dp) return "";

    // If it's an array
    if (Array.isArray(dp)) {
        // Array of objects: use displayString
        if (dp.length && typeof dp[0] === "object") {
            return dp
                .map((p) => p && p.displayString)
                .filter(Boolean)
                .join(" / ");
        }
        // Array of strings (old format) – keep supporting it
        return dp.filter(Boolean).join(" / ");
    }

    // Single object
    if (typeof dp === "object") {
        return dp.displayString || "";
    }

    // Fallback – if someone ever makes it a raw string
    return String(dp);
}

function repeatIngredient(name, qtyRaw) {
    const nameStr = n(name);
    if (!nameStr) return [];

    const qty = Number(qtyRaw);
    // quantity 0 or invalid → show once (for things like "Armor", "Any Shield")
    if (!Number.isFinite(qty) || qty <= 1) {
        return [nameStr];
    }

    return Array.from({length: qty}, () => nameStr);
}

function isHighlightedItem(u) {
    return u?.highlight === true;
}

function isUberUnique(u) {
    const src = u?.dropSource;
    return src !== null && src !== undefined && String(src).trim() !== "";
}

function isHellforged(u) {
    return u?.hellforged;
}

function getItemIconUrl(tab, item) {
    if (tab === "weapons") {
        const key = weaponIconKeyForItem(item);
        return key ? WEAPON_ICON_MAP[key] : null;
    }

    if (tab === "armors") {
        const key = armorIconKeyForItem(item);
        return key ? ARMOR_ICON_MAP[key] : null;
    }

    if (tab === "uniques") {
        return getUniqueBaseIconUrl(item);
    }

    if (tab === "runewords") {
        return RuneIcon;
    }

    if (tab === "sacreds") {
        return SacredIcon;
    }

    if (tab === "fatecards") {
        return FateCardIcon;
    }

    return null;
}

function getUniqueBaseIconUrl(u) {
    if (u?.jeweleryBase?.code) {
        const code = String(u.jeweleryBase.code).toLowerCase();
        if (JEWELRY_ICON_MAP[code]) {
            return JEWELRY_ICON_MAP[code];
        }
    }

    if (u?.armorBase) {
        const armorBase = u.armorBase;
        const key = armorIconKeyForItem(armorBase);
        if (key) {
            return ARMOR_ICON_MAP[key];
        }

        if (armorBase.itemType?.code) {
            const typeCode = String(armorBase.itemType.code).toLowerCase();
        }
    }

    if (u?.weaponBase) {
        const weaponBase = u.weaponBase;
        const key = weaponIconKeyForItem(weaponBase);
        if (key) {
            return WEAPON_ICON_MAP[key];
        }
    }

    return null;
}

function armorIconKeyForItem(a) {
    const t = n(a?.itemType?.code) || n(a?.displayType) || ARMOR_TYPE_MAP[n(a?.type)] || n(a?.type);

    return t.toLowerCase();
}

function weaponIconKeyForItem(it) {
    const type = n(it?.itemType?.itemType || it?.itemType).toLowerCase();

    if (type.includes("scythe")) return "scythe";
    if (type.includes("hammer")) return "hammer";
    if (type.includes("orb")) return "orb";
    if (type.includes("throwing knife")) return "throwingKnife";
    if (type.includes("throwing axe")) return "throwingAxe";
    if (type.includes("sword")) return "sword";
    if (type.includes("staff")) return "staff";
    if (type.includes("bow")) return "bow";
    if (type.includes("javelin")) return "javelin";
    if (type.includes("spear")) return "spear";
    if (type.includes("axe")) return "axe";
    if (type.includes("club") || type.includes("mace") || type.includes("hammer")) return "mace";
    if (type.includes("knife")) return "knife";
    if (type.includes("crossbow")) return "crossbow";
    if (type.includes("claws")) return "claws";
    if (type.includes("scythe") || type.includes("polearm")) return "polearm";
    if (type.includes("scepter")) return "scepter";
    if (type.includes("wand")) return "wand";

    return null;
}

function sacredPropertiesText(s) {
    const map = s?.propertiesByItemType && typeof s.propertiesByItemType === "object" ? s.propertiesByItemType : {};

    const lines = [];
    for (const key of Object.keys(map)) {
        const arr = Array.isArray(map[key]) ? map[key] : [];
        for (const v of arr) {
            if (v != null && String(v).trim() !== "") lines.push(String(v));
        }
    }
    return lines.join("\n");
}


function renderInlineMarkdown(text, onLink) {
    const s = String(text ?? "");

    const parts = s.split(/(`[^`]*`)/g);

    // helper: split a plain string into text + link pieces
    function renderWithLinks(str, keyPrefix) {
        const linkRe = /\[([^\]]+)\]\(([^)]+)\)/g;
        const out = [];
        let last = 0;
        let m;
        let idx = 0;

        while ((m = linkRe.exec(str)) !== null) {
            if (m.index > last) {
                out.push(<React.Fragment key={`${keyPrefix}-t-${idx}`}>
                    {str.slice(last, m.index)}
                </React.Fragment>);
            }

            const label = m[1];
            const href = m[2];

            if (href.startsWith("app:") && typeof onLink === "function") {
                const payload = href.slice(4); // remove "app:"
                const [tabRaw, ...rest] = payload.split(":");
                const tab = (tabRaw || "").toLowerCase();
                const name = decodeURIComponent(rest.join(":")).trim();

                out.push(<button
                    key={`${keyPrefix}-app-${idx}`}
                    type="button"
                    className="mdLink mdLinkInternal"
                    onClick={() => onLink({tab, name})}
                >
                    {label}
                </button>);
            } else {
                out.push(<a
                    key={`${keyPrefix}-ext-${idx}`}
                    href={href}
                    target="_blank"
                    rel="noreferrer"
                    className="mdLink"
                >
                    {label}
                </a>);
            }

            last = linkRe.lastIndex;
            idx += 1;
        }

        if (last < str.length) {
            out.push(<React.Fragment key={`${keyPrefix}-tail`}>
                {str.slice(last)}
            </React.Fragment>);
        }

        return out;
    }

    return parts.map((part, idx) => {
        if (part.startsWith("`") && part.endsWith("`")) {
            return (<code key={idx} className="mdCode">
                {part.slice(1, -1)}
            </code>);
        }

        const boldSplit = part.split(/(\*\*[^*]+\*\*)/g);
        return boldSplit.map((b, j) => {
            if (b.startsWith("**") && b.endsWith("**")) {
                return (<strong key={`${idx}-${j}`} className="mdStrong">
                    {b.slice(2, -2)}
                </strong>);
            }

            const italicSplit = b.split(/(\*[^*]+\*)/g);
            return italicSplit.map((it, k) => {
                if (it.startsWith("*") && it.endsWith("*")) {
                    return (<em key={`${idx}-${j}-${k}`} className="mdEm">
                        {it.slice(1, -1)}
                    </em>);
                }

                // this is the plain text segment: run link parsing here
                return (<React.Fragment key={`${idx}-${j}-${k}`}>
                    {renderWithLinks(it, `${idx}-${j}-${k}`)}
                </React.Fragment>);
            });
        });
    });
}

function Markdown({text, onLink}) {
    const src = Array.isArray(text) ? text.join("\n") : text;
    const raw = String(src ?? "").replace(/\r\n/g, "\n");
    const lines = raw.split("\n");

    const blocks = [];
    let buf = [];

    const flushParagraph = () => {
        if (!buf.length) return;
        const joined = buf.join(" ").trim();
        if (joined) blocks.push({type: "p", text: joined});
        buf = [];
    };

    // listBuf now stores objects: { text, children: [] }
    let listBuf = [];
    const flushList = () => {
        if (!listBuf.length) return;
        blocks.push({type: "ul", items: listBuf});
        listBuf = [];
    };

    // tableBuf: consecutive GFM table lines (| a | b |)
    let tableBuf = [];
    const flushTable = () => {
        if (!tableBuf.length) return;
        const rows = tableBuf
            .map((l) => l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim()))
            .filter((cells) => !(cells.length === 1 && !cells[0]))
            .filter((cells) => !cells.every((c) => /^:?-{2,}:?$/.test(c)));
        const head = rows.shift() || [];
        blocks.push({type: "table", head, rows});
        tableBuf = [];
    };

    for (const line of lines) {
        const t = line.trimEnd();

        if (!t.trim()) {
            flushTable();
            flushList();
            flushParagraph();
            continue;
        }

        // GFM table row
        if (t.trim().startsWith("|")) {
            flushList();
            flushParagraph();
            tableBuf.push(t.trim());
            continue;
        }
        flushTable();

        // capture indent + bullet
        const bullet = t.match(/^(\s*)[-*]\s+(.+)$/);
        if (bullet) {
            const indent = bullet[1].length; // number of leading spaces
            const content = bullet[2].trim();

            flushParagraph();

            // top-level bullet: no indent
            if (indent === 0) {
                listBuf.push({text: content, children: []});
            } else {
                // second-level bullet: attach to last top-level item
                const parent = listBuf[listBuf.length - 1];
                if (parent) {
                    if (!parent.children) parent.children = [];
                    parent.children.push(content);
                } else {
                    // if somehow no parent exists, fall back to top-level
                    listBuf.push({text: content, children: []});
                }
            }
            continue;
        }

        flushList();
        buf.push(t.trim());
    }

    flushList();
    flushTable();
    flushParagraph();

    return (<div className="md">
        {blocks.map((b, i) => {
            if (b.type === "ul") {
                return (<ul key={i} className="mdUl">
                    {b.items.map((item, j) => (<li key={j} className="mdLi">
                        {renderInlineMarkdown(item.text, onLink)}
                        {item.children && item.children.length > 0 && (<ul className="mdUl mdUlNested">
                            {item.children.map((child, k) => (<li key={k} className="mdLi mdLiNested">
                                {renderInlineMarkdown(child, onLink)}
                            </li>))}
                        </ul>)}
                    </li>))}
                </ul>);
            }
            if (b.type === "table") {
                return (<table key={i} className="mdTable">
                    <thead>
                        <tr>{b.head.map((c, j) => (<th key={j}>{renderInlineMarkdown(c, onLink)}</th>))}</tr>
                    </thead>
                    <tbody>
                        {b.rows.map((row, j) => (<tr key={j}>
                            {row.map((c, k) => (<td key={k}>{renderInlineMarkdown(c, onLink)}</td>))}
                        </tr>))}
                    </tbody>
                </table>);
            }
            return (<p key={i} className="mdP">
                {renderInlineMarkdown(b.text, onLink)}
            </p>);
        })}
    </div>);
}


function classForPropertyLine(line) {
    const s = String(line || "");
    for (const rule of PROP_HIGHLIGHT_RULES) {
        if (rule?.test?.test(s)) return rule.className;
    }
    return "";
}

function parseSearchQuery(input) {
    const text = input.trim().toLowerCase();
    if (!text) return {phrases: [], terms: []};

    const phrases = [];
    const phraseRegex = /"([^"]+)"/g;

    let rest = text;
    let m;

    while ((m = phraseRegex.exec(text)) !== null) {
        phrases.push(m[1]);
        rest = rest.replace(m[0], " ");
    }

    const terms = rest
        .split(/\s+/)
        .map((s) => s.trim())
        .filter(Boolean);

    return {phrases, terms};
}

function isDontDisplay(it) {
    const v = it ? it.dontDisplay : false;
    return (v === true || v === 1 || v === "1" || (typeof v === "string" && v.toLowerCase() === "true"));
}

function Tip({text, children}) {
    if (!text) return children;

    const parts = String(text).split("\n");

    return (<span className="tipWrap">
      {children}
        <span className="tipBubble" role="tooltip">
        {parts.map((line, i) => (<React.Fragment key={i}>
            {line}
            {i < parts.length - 1 ? <br/> : null}
        </React.Fragment>))}
      </span>
    </span>);
}

function buildSearchTextForItem(tab, it) {
    const name = (n(it?.displayName) || n(it?.runewordName) || n(it?.name)).toLowerCase();

    if (tab === "uniques" || tab === "runewords") {
        const props = Array.isArray(it?.displayProperties) ? it.displayProperties : [];
        const propsText = props
            .filter((x) => x != null)
            .map((x) => String(x).toLowerCase())
            .join("\n");

        return applyModifierExpansions(`${name}\n${propsText}`);
    }

    if (tab === "sacreds") {
        const ing = sacredIngredients(it).join("\n").toLowerCase();
        const props = sacredPropertiesText(it).toLowerCase();
        return `${name}\n${ing}\n${props}`;
    }

    if (tab === "corruptions") {
        const name = n(it?.displayName);

        const props = Array.isArray(it?.corruptionProperties)
            ? it.corruptionProperties.join(" ")
            : "";

        return `${name} ${props}`.toLowerCase();
    }

    if (tab === "affixes") {
        const dp = it?.displayProperties;
        let attrsText = "";

        if (Array.isArray(dp)) {
            if (dp.length && typeof dp[0] === "object") {
                // Array of { displayString, max, ... }
                attrsText = dp
                    .map((p) => p && p.displayString)
                    .filter(Boolean)
                    .join("\n")
                    .toLowerCase();
            } else {
                // Backwards-compat: array of strings
                attrsText = dp
                    .filter(Boolean)
                    .map((x) => String(x).toLowerCase())
                    .join("\n");
            }
        } else if (dp && typeof dp === "object") {
            attrsText = String(dp.displayString || "").toLowerCase();
        }

        return applyModifierExpansions(`${name}\n${attrsText}`);
    }

    return name;
}

function applyModifierExpansions(searchText) {
    let out = searchText;

    for (const rule of MOD_EXPANSIONS) {
        if (!rule?.whenIncludes || !Array.isArray(rule?.implies)) continue;

        if (out.includes(rule.whenIncludes.toLowerCase())) {
            out += "\n" + rule.implies.map((s) => s.toLowerCase()).join("\n");
        }
    }

    return out;
}

function affixTypes(it) {
    const a = Array.isArray(it?.displayItemTypeNames) ? it.displayItemTypeNames : [];
    return a.map((x) => typeZh(n(x))).filter(Boolean);
}

function runewordAllTypes(rw) {
    const a = Array.isArray(rw?.displayItemTypes) ? rw.displayItemTypes : [];
    const b = Array.isArray(rw?.itemTypes) ? rw.itemTypes : [];
    return (a.length ? a : b).map((x) => typeZh(n(x))).filter(Boolean);
}

function filterVisible(arr) {
    if (!Array.isArray(arr)) return [];
    return arr.filter((it) => !isDontDisplay(it));
}

// ---- 物品类型（筛选下拉/标签）中英映射 ----
const TYPE_CODE_ZH = {
    // 武器
    "Sword": "剑类", "swor": "剑类", "Axe": "斧类", "axe": "斧类", "Bow": "弓类", "bow": "弓类",
    "Claws": "爪类", "Staff": "法杖类", "staf": "法杖类", "Javelin": "标枪类", "jave": "标枪类",
    "Spear": "矛类", "spea": "矛类", "Sorceress Orb": "法师宝珠类", "orb": "法师宝珠类",
    "Wand": "魔杖类", "wand": "魔杖类", "Hammer": "锤类", "hamm": "锤类", "Knife": "匕首类",
    "knif": "匕首类", "Polearm": "长柄武器类", "pole": "长柄武器类", "Crossbow": "弩类", "xbow": "弩类",
    "Mace": "钉头锤类", "mace": "钉头锤类", "h2h2": "拳刃类", "h2h": "拳刃类",
    "Scepter": "权杖类", "scep": "权杖类", "Club": "棍棒类", "club": "棍棒类",
    "Throwing Knife": "投掷刀类", "tkni": "投掷刀类", "Throwing Axe": "投掷斧类", "taxe": "投掷斧类",
    "Scythe": "镰刀类", "sc9": "镰刀类", "Amazon Bow": "亚马逊弓", "abow": "亚马逊弓",
    "Amazon Spear": "亚马逊矛", "aspe": "亚马逊矛", "Amazon Javelin": "亚马逊标枪", "ajav": "亚马逊标枪",
    "2H Crystal Sword": "双手水晶剑", "2hcs": "双手水晶剑", "2H Sword": "双手剑", "2hsw": "双手剑",
    "Melee Weapon": "近战武器", "mele": "近战武器", "Missile": "远程武器", "misl": "远程武器",
    "Thrown Weapon": "投掷武器", "thro": "投掷武器", "Sorceress Item": "法师物品", "sorc": "法师物品",
    "Hand to Hand 2": "拳刃类 2", "Hand to Hand": "拳刃类",
    // 护甲
    "Armor": "护甲", "tors": "护甲", "Helm": "头盔", "helm": "头盔", "Shield": "盾牌", "shie": "盾牌",
    "Belt": "腰带", "belt": "腰带", "Gloves": "手套", "glov": "手套", "Boots": "靴子", "boot": "靴子",
    "Pelt": "德鲁伊毛皮", "pelt": "德鲁伊毛皮", "Primal Helm": "野蛮人头盔", "phlm": "野蛮人头盔",
    "Auric Shields": "圣骑士盾牌", "ashd": "圣骑士盾牌", "Voodoo Heads": "死灵法师头颅", "head": "死灵法师头颅",
    "Circlet": "头环", "circ": "头环", "Paladin Helmet": "圣骑士头盔", "pahm": "圣骑士头盔",
    "Belt [S]": "腰带[S]", "bels": "腰带[S]",
    "Any Shield": "任意盾牌",
    // 通用
    "Mythic Jewel": "神话珠宝", "Weapon": "武器", "weap": "武器",
};

const typeZh = (v) => (v ? (TYPE_CODE_ZH[v] || v) : v);

function weaponTypeLabel(w) {
    const primary = typeZh(n(w?.itemType?.displayName) || n(w?.displayType) || n(w?.type) || n(w?.itemType?.itemType));
    const secondary = typeZh(n(w?.secondItemType?.displayName) || n(w?.secondDisplayType) || n(w?.secondType) || n(w?.secondItemType?.itemType));
    return has(secondary) ? `${primary} / ${secondary}` : primary || "武器";
}

function weaponTypeForFilter(w) {
    return typeZh(n(w?.itemType?.itemType) || n(w?.type));
}

function armorTypeLabel(a) {
    const dt = typeZh(n(a?.displayType));
    const sdt = typeZh(n(a?.secondDisplayType));
    const base = dt || ARMOR_TYPE_MAP[n(a?.type)] || typeZh(n(a?.type)) || "护甲";
    const sec = has(sdt) ? sdt : "";
    return has(sec) ? `${base} / ${sec}` : base;
}

function armorTypeForFilter(a) {
    return typeZh(n(a?.displayType)) || ARMOR_TYPE_MAP[n(a?.type)] || typeZh(n(a?.type));
}

function uniqueBase(u) {
    return u?.weaponBase ?? u?.armorBase ?? u?.jeweleryBase ?? null;
}

function uniqueBaseTypeLabel(u) {
    const base = uniqueBase(u);
    return typeZh(n(base?.itemType?.itemType)) || typeZh(n(base?.displayName)) || typeZh(n(base?.type));
}

function uniqueBaseTypeLabelPretty(u) {
    const base = uniqueBase(u);
    return typeZh(n(base?.itemType?.displayName)) || typeZh(n(base?.displayName)) || typeZh(n(base?.displayType)) || uniqueBaseTypeLabel(u);
}

function weaponDmgLines(w) {
    const out = [];
    const min = n(w?.minDamage), max = n(w?.maxDamage);
    const tmin = n(w?.twoHandedMinDamage), tmax = n(w?.twoHandedMaxDamage);
    const mmin = n(w?.minMissileDamage), mmax = n(w?.maxMissileDamage);

    if (has(min) && has(max)) out.push({k: "单手伤害", v: `${min} 至 ${max}`});
    if (has(tmin) && has(tmax)) out.push({k: "双手伤害", v: `${tmin} 至 ${tmax}`});
    if (has(mmin) && has(mmax)) out.push({k: "投掷伤害", v: `${mmin} 至 ${mmax}`});
    return out;
}

function armorDefenseLine(a) {
    const minD = n(a?.minDefense), maxD = n(a?.maxDefense);
    if (has(minD) && has(maxD)) return `${minD} 至 ${maxD}`;
    if (has(minD)) return `${minD}`;
    return "";
}

function useJson(fileName, damnationMode) {
    const [state, setState] = React.useState({
        loading: true, data: [], error: null,
    });

    React.useEffect(() => {
        let cancelled = false;

        const url =
            damnationMode && fileName === "Uniques.json"
                ? `${import.meta.env.BASE_URL}data/damnation/${fileName}`
                : `${import.meta.env.BASE_URL}data/${fileName}`;

        setState((s) => ({...s, loading: true, error: null}));

        fetch(url, {cache: "no-store"}) // <-- prevents 304 responses
            .then(async (r) => {
                if (!r.ok) {
                    throw new Error(`HTTP ${r.status} ${r.statusText}`);
                }
                return r.json();
            })
            .then((json) => {
                if (cancelled) return;
                const arr = Array.isArray(json) ? json : [];
                setState({loading: false, data: filterVisible(arr), error: null});
            })
            .catch((e) => {
                if (cancelled) return;
                const err = e instanceof Error ? e : new Error(String(e));
                setState({loading: false, data: [], error: err});
            });

        return () => {
            cancelled = true;
        };
    }, [fileName, damnationMode]);

    return state;
}

function lineKV(k, v, extraClass = "", tooltipText = "") {
    var showTooltip = tooltipText !== null && tooltipText !== "";
    return (<div className={("line kv " + (extraClass || "")).trim()}>
        {showTooltip ? <Tip text={String(tooltipText)}><span>{k}</span></Tip> : <span>{k}</span>}
        <span>{String(v)}</span>
    </div>);
}

function getItemTypeForUnique(u) {
    if (has(u?.weaponBase)) {
        return "WEAPON";
    }

    if (has(u?.armorBase)) {
        return "ARMOR";
    }

    if (has(u?.jeweleryBase)) {
        return "JEWELERY";
    }
}

function getRequiredLevelForUnique(u, itemType) {
    if (u?.requiredLevel > 0) {
        return u?.requiredLevel;
    }

    if (itemType === "WEAPON") {
        return u?.weaponBase?.requiredLevel;
    }

    if (itemType === "ARMOR") {
        return u?.armorBase?.requiredLevel;
    }

    if (itemType === "JEWELERY") {
        return u?.jeweleryBase?.requiredLevel;
    }
}

function getRequiredStrengthForUnique(u, itemType) {
    if (itemType === "WEAPON") {
        return u?.weaponBase?.requiredStrength;
    }

    if (itemType === "ARMOR") {
        return u?.armorBase?.requiredStrength;
    }
}

function getRequiredDexterityForUnique(u) {
    return u?.weaponBase?.requiredDexterity;
}

function SearchableSelect({
                              value, onChange, options, placeholder = "选择…", style, className = "",
                          }) {
    const [open, setOpen] = React.useState(false);
    const [query, setQuery] = React.useState("");
    const wrapRef = React.useRef(null);
    const inputRef = React.useRef(null);

    const currentLabel = options.find((o) => String(o.value) === String(value))?.label || "";

    const filteredOptions = React.useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return options;
        return options.filter((opt) => (opt.label || "").toLowerCase().includes(q));
    }, [options, query]);

    // Close on outside click
    React.useEffect(() => {
        if (!open) return;

        function handleClick(e) {
            if (!wrapRef.current) return;
            if (!wrapRef.current.contains(e.target)) {
                setOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, [open]);

    // Auto-focus search input when dropdown opens
    React.useEffect(() => {
        if (open && inputRef.current) {
            inputRef.current.focus();
            inputRef.current.select();
        }
    }, [open]);

    const handleSelect = (val) => {
        onChange(val);
        setOpen(false);
        setQuery("");
    };

    return (<div
        ref={wrapRef}
        className={`selSearchWrap ${className}`}
        style={style}
    >
        <button
            type="button"
            className="selTrigger"
            onClick={() => setOpen((o) => !o)}
        >
        <span className={currentLabel ? "" : "placeholder"}>
          {currentLabel || placeholder}
        </span>
            <span className="selArrow">▾</span>
        </button>

        {open && (<div className="selDropdown">
            <input
                ref={inputRef}
                className="selSearchInput"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="筛选选项…"
            />
            <div className="selOptions">
                {filteredOptions.length === 0 ? (
                    <div className="selOption selEmpty">无匹配结果</div>) : (filteredOptions.map((opt) => (<div
                    key={String(opt.value) || opt.label}
                    className="selOption"
                    onClick={() => handleSelect(opt.value)}
                >
                    {opt.label}
                </div>)))}
            </div>
        </div>)}
    </div>);
}

function FiltersBar({
                        search,
                        setSearch,
                        typeValue,
                        setTypeValue,
                        tierValue,
                        setTierValue,
                        socketsValue,
                        setSocketsValue,
                        uberValue,
                        setUberValue,
                        hellforgedValue,
                        setHellforgedValue,
                        types,
                        tiers,
                        showSockets,
                        showUber,
                        showHellforged,
                        typePlaceholder,
                        searchInputRef,
                        showType = true,
                        showTier = true,
                        showHighlight = false,
                        highlightOnly,
                        setHighlightOnly,
                        showAffixType = false,
                        affixTypeValue = "",
                        setAffixTypeValue = () => {
                        },
                        showRuneCount = false,
                        runeCountValue = "",
                        setRuneCountValue = () => {
                        },
                    }) {
    // Build option lists once per render
    const typeOptions = [{value: "", label: typePlaceholder}, ...types.map((t) => ({value: t, label: t})),];

    const runeCountOptions = [{value: "", label: "全部数量"}, {value: "2", label: "2 个符文"}, {
        value: "3",
        label: "3 个符文"
    }, {value: "4", label: "4 个符文"}, {value: "5", label: "5 个符文"}, {value: "6", label: "6 个符文"},];

    const socketsOptions = [{
        value: "",
        label: "全部孔数"
    }, ...Array.from({length: 7}, (_, i) => String(i)).map((s) => ({
        value: s, label: s,
    })),];

    const tierOptions = [{value: "", label: "全部阶位"}, ...tiers.map((t) => ({value: t, label: t})),];

    const affixTypeOptions = [{value: "", label: "全部词缀类型"}, {
        value: "Prefix",
        label: "前缀"
    }, {value: "Suffix", label: "后缀"},];

    return (<div className="filtersRow">
        <div className="filtersPanel">
            <input
                ref={searchInputRef}
                type="text"
                value={search}
                className="searchBar"
                onChange={(e) => setSearch(e.target.value)}
                placeholder="搜索物品名称…"
            />


            {showType && (
                <SearchableSelect
                    value={typeValue}
                    onChange={setTypeValue}
                    options={typeOptions}
                    placeholder={typePlaceholder}
                    style={{maxWidth: 260}}
                />)}

            {showSockets && (<SearchableSelect
                value={socketsValue}
                onChange={setSocketsValue}
                options={socketsOptions}
                placeholder="全部孔数"
                style={{maxWidth: 180}}
            />)}

            {showRuneCount && (<SearchableSelect
                value={runeCountValue}
                onChange={setRuneCountValue}
                options={runeCountOptions}
                placeholder="全部数量"
                style={{maxWidth: 180}}
            />)}

            {/* Tier (searchable) */}
            {showTier && (<SearchableSelect
                value={tierValue}
                onChange={setTierValue}
                options={tierOptions}
                placeholder="全部阶位"
                style={{maxWidth: 180}}
            />)}

            {/* Affix type (Prefix / Suffix) – affixes tab only */}
            {showAffixType && (<SearchableSelect
                value={affixTypeValue}
                onChange={setAffixTypeValue}
                options={affixTypeOptions}
                placeholder="全部词缀类型"
                style={{maxWidth: 200}}
            />)}

            {/* Uber boss toggle (unchanged) */}
            {showUber && (<label className="toggleWrap">
                <span className="toggleLabel">超级首领暗金</span>
                <div className="toggle">
                    <input
                        type="checkbox"
                        checked={!!uberValue}
                        onChange={(e) => setUberValue(e.target.checked ? "yes" : "")}
                    />
                    <span className="toggleSlider"/>
                </div>
            </label>)}

            {showHellforged && (<label className="toggleWrap">
                <span className="toggleLabel">地狱锻造</span>
                <div className="toggle">
                    <input
                        type="checkbox"
                        checked={!!hellforgedValue}
                        onChange={(e) => setHellforgedValue(e.target.checked ? "yes" : "")}
                    />
                    <span className="toggleSlider"/>
                </div>
            </label>)}

            {/* Highlight toggle (unchanged) */}
            {showHighlight && (<label className="toggleWrap">
                <span className="toggleLabel">流放圣域独占</span>
                <div className="toggle">
                    <input
                        type="checkbox"
                        checked={!!highlightOnly}
                        onChange={(e) => setHighlightOnly(e.target.checked)}
                    />
                    <span className="toggleSlider"/>
                </div>
            </label>)}
        </div>
    </div>);
}

function InfoPanel({title, markdownText, isOpen, onToggle, onLink}) {
    if (!markdownText) return null;

    return (<div className="infoPanel">
        <div className="infoHeader">
            <div className="infoTitle">{title}</div>

            <button type="button" className="infoToggle" onClick={onToggle}>
                {isOpen ? "隐藏" : "显示"}
            </button>
        </div>

        {isOpen ? (<div className="infoBody">
            <Markdown text={markdownText} onLink={onLink}/>
        </div>) : null}
    </div>);
}

function renderTabTitle(tab) {
    const value = TABS[tab];

    if (value && typeof value === "object") {
        return (
            <>
                {value.title}
                {value.badge && <span className="tabBadge">{value.badge}</span>}
            </>
        );
    }

    return value;
}

function ListPanel({title, countLabel, items, activeIndex, setActiveIndex, subLabel, tinyLabel, tab}) {

    const activeRowRef = React.useRef(null);

    React.useEffect(() => {
        activeRowRef.current?.scrollIntoView({block: "nearest"});
    }, [activeIndex]);

    return (<div className="listPanel">
        <div className="listHeader">
            <div className="title">{title}</div>
            <div className="count">{countLabel}</div>
        </div>

        <div className="list" role="list">
            {items.length === 0 ? (
                <div className="emptyState">没有符合筛选条件的物品。</div>) : (items.map((it, i) => {
                const iconUrl = getItemIconUrl(tab, it);

                return (<div
                    key={`${i}::${n(it?.code)}::${n(it?.displayName) || n(it?.name)}`}
                    ref={i === activeIndex ? activeRowRef : null}
                    className={"row" + (i === activeIndex ? " active" : "")}
                    onClick={() => setActiveIndex(i)}
                    role="listitem"
                >
                    <div className="ico">
                        {iconUrl ? (<img src={iconUrl} className="icon" alt=""/>) : null}
                    </div>
                    <div className="meta">
                        <div className={tab === "uniques" ? "uniqueName" : "name"}>
                            {n(it?.displayName) || n(it?.name) || "未知"} {isHighlightedItem(it) && (tab === "uniques" || tab === "armors" || tab === "weapons" || tab === "runewords") ?
                            <span className="uniqueSOEAsterisk">*</span> : null}
                        </div>
                        <div className="sub">{subLabel(it)}</div>
                        <div className="tiny">{tinyLabel(it)}</div>
                    </div>
                </div>);
            }))}
        </div>
    </div>);
}


function TooltipShell({children}) {
    return (<div className="tooltipShell">
        <div className="tooltip">{children}</div>
    </div>);
}

function TierLinks({label = "阶位：", entries, onGo}) {
    const usable = entries.filter((e) => has(e.name) && has(e.code));
    if (!usable.length) return null;

    return (<>
        {usable.map((e) => (<div key={e.tierLabel + "|" + e.code} className="line kv">
            <span>{e.tierLabel} 阶位物品：</span>
            <span>
            <a
                className="d2link"
                href="#"
                onClick={(ev) => {
                    ev.preventDefault();
                    onGo(e.code);
                }}
            >
              {e.name}
            </a>
          </span>
        </div>))}
    </>);
}

function UniquesPanel({uniques, onGoUnique}) {
    const list = Array.isArray(uniques) ? uniques : [];
    if (!list.length) return null;

    return (<>
        <div className="hr"/>
        <div className="uniqueHeader">暗金装备</div>

        {list.map((u, idx) => {
            const name = n(u?.uniqueName);
            const code = n(u?.uniqueCode);
            if (!name) return null;

            return (<div key={`${idx}::${name}::${code}`} className="line goToLink">
                {code ? (<a
                    className="d2link"
                    href="#"
                    onClick={(ev) => {
                        ev.preventDefault();
                        onGoUnique(code);
                    }}
                    title={`跳转到暗金：${code}`}
                >
                    {name}
                </a>) : (<span className="d2linkText">{name}</span>)}
            </div>);
        })}
    </>);
}

function SacredTooltip({s, onLink}) {
    if (!s) return <div className="emptyState">请选择物品。</div>;

    const title = n(s?.displayName) || "圣化";
    const types = sacredTypes(s);
    const ing = sacredIngredients(s);

    const map = s?.propertiesByItemType && typeof s.propertiesByItemType === "object" ? s.propertiesByItemType : {};

    const typeKeys = Object.keys(map);

    return (<>
        <div className="tipTitle">{title}</div>

        {types.length ? (<div className="tipSubtitle">
            <span className="dim"></span>
            {types.join(" / ")}
        </div>) : null}

        <div className="hr"/>

        {ing.length ? (<div className="line runesDisplay">
            <Tip text={String(TOOLTIPS_TEXT_MAP["sacred"])}>
                {ing.map(runeLabel).join(" · ")}
            </Tip>
        </div>) : (<div className="line dim">未列出符文。</div>)}

        <div className="hr"/>

        <div className="sacredModsHeader">按物品类型区分的属性</div>
        {typeKeys.length ? (typeKeys.map((k) => {
            const arr = Array.isArray(map[k]) ? map[k] : [];
            if (!arr.length) return null;

            return (<div key={k} style={{marginBottom: 10}}>
                <div className="sacredModsItemType">{k}</div>
                {arr.flatMap((p, i) => {
                    const raw = String(p ?? "");
                    const normalized = raw.replace(/\\n/g, "\n");
                    const lines = normalized
                        .split("\n")
                        .map((l) => l.trim())
                        .filter(Boolean);

                    return lines.map((line, j) => (<div
                        key={`${k}-${i}-${j}`}
                        className="runeModLine"
                    >
                        {renderInlineMarkdown(line, onLink)}
                    </div>));
                })}
            </div>);
        })) : (<div className="line dim">暂无词缀信息。</div>)}
    </>);
}

function CurseEffectCalculator() {
    const [baseValue, setBaseValue] = React.useState("");
    const [bonusValue, setBonusValue] = React.useState("");

    const num = (v) => {
        const x = Number(String(v).replace(",", "."));
        return Number.isFinite(x) ? x : 0;
    };

    const result = React.useMemo(() => {
        const base = num(baseValue);
        const bonus = num(bonusValue);

        const raw = base * (100 + ((bonus * 70) / (bonus + 22))) / 100;

        return Number.isFinite(raw) ? Math.floor(raw) : 0;
    }, [baseValue, bonusValue]);

    const fmt = (x) => {
        const r = Math.round(x * 100) / 100;
        return String(r);
    };

    const reset = () => {
        setBaseValue("");
        setBonusValue("");
    };

    return (<div className="infoPanel">
        <div className="infoHeader">
            <div className="infoTitle">诅咒效果计算器</div>

            <div className="filtersResetPanel">
                <button
                    type="button"
                    className="btn secondary"
                    onClick={reset}
                >
                    重置
                </button>
            </div>
        </div>

        <div className="meta">
            计算考虑递减收益后的最终诅咒效果。
        </div>

        <div className="hr"/>

        <div className="calcGrid">

            <div className="calcRow">
                <div className="calcLabel">基础数值</div>
                <input
                    className="calcInput"
                    type="number"
                    value={baseValue}
                    onChange={(e) => setBaseValue(e.target.value)}
                    placeholder="例如：100"
                />
            </div>

            <div className="calcRow">
                <div className="calcLabel">诅咒效果加成</div>
                <input
                    className="calcInput"
                    type="number"
                    value={bonusValue}
                    onChange={(e) => setBonusValue(e.target.value)}
                    placeholder="例如：50"
                />
            </div>

            <div className="calcOut">
                <div className="calcOutLabel">最终效果</div>
                <div className="calcOutValue">{fmt(result)}</div>
            </div>

            <div className="calcFormula dim">
                X = base × (100 + (bonus × 70)/(bonus + 22)) / 100
            </div>

        </div>
    </div>);
}

function DropCalculatorPanel({request, clearRequest, damnationMode}) {
    const [dropMode, setDropMode] = React.useState("unique");
    const [query, setQuery] = React.useState("");
    const [rows, setRows] = React.useState([]);
    const [page, setPage] = React.useState(1);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState("");
    const [difficulty, setDifficulty] = React.useState("");
    const [players, setPlayers] = React.useState("1");
    const [mf, setMf] = React.useState("");

    useEffect(() => {
        if (!request) return;

        setDropMode("unique");
        setDifficulty("H");
        setQuery(request.item);

        clearRequest?.();

    }, [request]);

    React.useEffect(() => {
        const id = window.setTimeout(() => {
            calculateAll();
        }, 300);

        return () => window.clearTimeout(id);
    }, [dropMode, query, difficulty, players, mf, damnationMode]);

    const n = (v) => (v === null || v === undefined ? "" : String(v).trim());
    const num = (v) => {
        const x = Number(String(v ?? "").replace(",", "."));
        return Number.isFinite(x) ? x : 0;
    };

    async function loadTxt(fileName) {
        const modeFolder = damnationMode ? "damnation" : "standard";

        const url = `${import.meta.env.BASE_URL}data/${modeFolder}/${fileName}`;
        const res = await fetch(url, {cache: "no-store"});

        if (!res.ok) {
            throw new Error(`${fileName}: HTTP ${res.status}`);
        }

        return res.text();
    }

    function parseTxt(text) {
        const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.trim() !== "");
        const headers = lines[0].split("\t").map((h) => h.trim());

        return lines.slice(1).map((line) => {
            const cols = line.split("\t");
            const row = {};
            headers.forEach((h, i) => {
                row[h] = cols[i] ?? "";
            });
            return row;
        });
    }

    function byLower(rows, column, value) {
        const needle = n(value).toLowerCase();
        return rows.find((r) => n(r[column]).toLowerCase() === needle);
    }

    function applyPicks(probability, picks) {
        if (picks === 1) return probability;

        const cappedPicks = picks > 6 ? 6 : picks;
        return 1 - Math.pow(1 - probability, cappedPicks);
    }

    function getRootTc(tcRows, tcName, monsterLevel) {
        const start = byLower(tcRows, "Treasure Class", tcName);
        if (!start) return tcName;

        const group = n(start.group);
        if (!group) return tcName;

        const candidates = tcRows
            .filter((r) => n(r.group) === group)
            .filter((r) => num(r.level) <= monsterLevel)
            .sort((a, b) => num(b.level) - num(a.level));

        return n(candidates[0]?.["Treasure Class"] || tcName);
    }

    function buildTypeRarityMap(itemTypes) {
        const map = new Map();

        for (const r of itemTypes) {
            const code = n(r.Code || r.code);
            if (!code) continue;

            const rarity = num(r.Rarity || r.rarity);
            map.set(code, rarity > 0 ? rarity : 1);
        }

        return map;
    }

    function isBowLike(w) {
        const type = n(w.type).toLowerCase();
        const type2 = n(w.type2).toLowerCase();

        return (
            type.includes("bow") ||
            type2.includes("bow") ||
            type.includes("xbow") ||
            type2.includes("xbow") ||
            type.includes("crossbow") ||
            type2.includes("crossbow")
        );
    }

    function buildAutoTcs(weapons, armors, itemTypes) {
        const buckets = new Map();
        const typeRarity = buildTypeRarityMap(itemTypes);

        function add(bucket, code, weight) {
            if (!buckets.has(bucket)) buckets.set(bucket, []);
            buckets.get(bucket).push({code, weight});
        }

        function itemWeight(row) {
            const type = n(row.type);
            const fromType = typeRarity.get(type);

            if (fromType > 0) return fromType;

            const fromItem = num(row.rarity);
            return fromItem > 0 ? fromItem : 1;
        }

        function addRows(rows, prefixes) {
            for (const r of rows) {
                if (n(r.spawnable) !== "1") continue;

                const code = n(r.code);
                if (!code) continue;

                const level = num(r.level);
                if (level <= 0) continue;

                const bucketLevel = Math.ceil(level / 3) * 3;
                const weight = itemWeight(r);

                for (const prefix of prefixes) {
                    add(`${prefix}${bucketLevel}`, code, weight);
                }
            }
        }

        addRows(weapons, ["weap"]);
        addRows(weapons.filter((w) => !isBowLike(w)), ["mele"]);
        addRows(weapons.filter((w) => isBowLike(w)), ["bow"]);
        addRows(armors, ["armo"]);

        return buckets;
    }

    function isExpansionItem(baseItem) {
        const v = n(baseItem.version);
        return v === "1" || v === "100";
    }

    function isExceptionalOrElite(baseItem, exceptionalOrEliteCodes) {
        const code = n(baseItem.code);

        if (exceptionalOrEliteCodes?.has(code)) {
            return true;
        }

        const norm = n(baseItem.normcode);
        const uber = n(baseItem.ubercode);
        const ultra = n(baseItem.ultracode);

        return (
            (norm && code !== norm) ||
            (uber && code === uber) ||
            (ultra && code === ultra)
        );
    }

    function getItemRatioRow(itemRatioRows, baseItem, exceptionalOrEliteCodes) {
        const version = "1";
        const uber = isExceptionalOrElite(baseItem, exceptionalOrEliteCodes) ? "1" : "0";

        return itemRatioRows.find((r) =>
            n(r.Version) === version &&
            n(r.Uber) === uber &&
            n(r["Class Specific"]) === "0"
        ) || itemRatioRows[0];
    }

    function adjustedNoDrop(noDrop, itemProbTotal, playersValue, partyValue) {
        const players = Math.max(1, Math.min(8, Math.floor(num(playersValue) || 1)));
        const party = Math.max(1, Math.min(8, Math.floor(num(partyValue) || 1)));

        if (noDrop <= 0 || itemProbTotal <= 0) return 0;
        if (players <= 1 && party <= 1) return noDrop;

        const exponent = Math.floor(
            1 + ((players - 1) / 2) + ((party - 1) / 2)
        );

        const base = noDrop / (noDrop + itemProbTotal);
        const powered = Math.pow(base, exponent);

        return Math.floor(itemProbTotal * powered / (1 - powered));
    }

    function tcEntries(tc) {
        const out = [];

        for (let i = 1; i <= 10; i++) {
            const item = n(tc[`Item${i}`]);
            const prob = num(tc[`Prob${i}`]);

            if (item && prob > 0) {
                out.push({item, prob});
            }
        }

        return out;
    }

    function probabilityForPicks(p, picks) {
        if (picks <= 1) return p;
        const capped = Math.min(6, picks);
        return 1 - Math.pow(1 - p, capped);
    }

    function mergeRatios(a, b) {
        return {
            unique: Math.max(a?.unique || 0, b?.unique || 0),
            set: Math.max(a?.set || 0, b?.set || 0),
            rare: Math.max(a?.rare || 0, b?.rare || 0),
            magic: Math.max(a?.magic || 0, b?.magic || 0),
        };
    }

    function tcQualityRatios(tc) {
        return {
            unique: num(tc.Unique),
            set: num(tc.Set),
            rare: num(tc.Rare),
            magic: num(tc.Magic),
        };
    }

    function qualityOccurrenceChance(items, targetItem, code, monsterLevel) {
        const eligible = items.filter((u) =>
            rowItemCode(u) === code &&
            num(u.lvl) <= monsterLevel &&
            (n(u.enabled) === "" || n(u.enabled) === "1")
        );

        if (!eligible.length) return 0;

        const total = eligible.reduce((sum, u) => sum + Math.max(1, num(u.rarity) || 1), 0);
        const own = Math.max(1, num(targetItem.rarity) || 1);

        return own / total;
    }

    function qualityChance(itemRatioRows, baseItem, targetItem, exceptionalOrEliteCodes, monsterLevel, mfValue, tcBonus, qualityName) {
        const ratio = getItemRatioRow(itemRatioRows, baseItem, exceptionalOrEliteCodes);

        const q =
            qualityName === "set"
                ? "Set"
                : qualityName === "rare"
                    ? "Rare"
                    : qualityName === "magic"
                        ? "Magic"
                        : "Unique";

        const base = num(ratio[q]);
        const divisor = Math.max(1, num(ratio[`${q}Divisor`]));
        const min = num(ratio[`${q}Min`]);
        const qlvl = num(baseItem.level);

        let chance = base - Math.floor((monsterLevel - qlvl) / divisor);
        chance *= 128;

        let mfCap = 0;
        if (qualityName === "unique") mfCap = 250;
        if (qualityName === "set") mfCap = 500;
        if (qualityName === "rare") mfCap = 600;

        if (mfCap > 0) {
            const rawMf = Math.max(0, num(mfValue));
            const effectiveMf = rawMf <= 10
                ? rawMf
                : Math.floor((rawMf * mfCap) / (rawMf + mfCap));

            chance = Math.floor((chance * 100) / (100 + effectiveMf));
        }

        if (chance < min) {
            chance = min;
        }

        const bonus = Math.max(0, Math.min(1024, num(tcBonus)));
        if (bonus > 0) {
            chance = chance - Math.floor((chance * bonus) / 1024);
        }

        return chance <= 0 ? 1 : 128 / chance;
    }

    function rowItemCode(row) {
        return n(row.code) || n(row.item);
    }

    function makeAccumulator() {
        return {
            groups: [new Map()]
        };
    }

    function accumulatorCurrent(acc) {
        return acc.groups[acc.groups.length - 1];
    }

    function forkAccumulator(acc) {
        const current = accumulatorCurrent(acc);
        if (current.size > 0) {
            acc.groups.push(new Map());
        }
    }

    function accumulateOutcome(acc, probability, ratios, picks) {
        const current = accumulatorCurrent(acc);
        const key = `${picks}|${ratios.unique}|${ratios.set}|${ratios.rare}|${ratios.magic}`;

        const old = current.get(key);

        if (old) {
            old.probability += probability;
            old.ratios = mergeRatios(old.ratios, ratios);
        } else {
            current.set(key, {
                probability,
                ratios,
                picks
            });
        }
    }

    function collectPaths(
        ctx,
        outcomeName,
        selectionNumerator,
        selectionDenominator,
        parentPicks,
        pathProbability,
        ratiosAccumulator,
        acc,
        accumulatedPicks,
        visited = new Set()
    ) {
        const name = n(outcomeName);
        if (!name) return;

        const tc = byLower(ctx.treasure, "Treasure Class", name);
        const autoRows = ctx.autoTcs.get(name);

        const isRegularTc = !!tc;
        const isAutoTc = !!autoRows;
        const isTargetBase = name === ctx.targetCode;

        const configuredPicks = isRegularTc ? Math.trunc(num(tc.Picks) || 1) : 1;
        const parentPicksNegative = parentPicks < 0;

        const adjustedPicks = configuredPicks < 0
            ? accumulatedPicks
            : configuredPicks;

        const updatedAccumulatedPicks = parentPicksNegative
            ? selectionNumerator * accumulatedPicks * adjustedPicks
            : accumulatedPicks * adjustedPicks;

        const selectionProbability = parentPicksNegative
            ? pathProbability
            : pathProbability * (selectionNumerator / selectionDenominator);

        if (parentPicksNegative) {
            forkAccumulator(acc);
        }

        const nextRatios = isRegularTc
            ? mergeRatios(ratiosAccumulator, tcQualityRatios(tc))
            : ratiosAccumulator;

        if (isTargetBase) {
            accumulateOutcome(acc, selectionProbability, nextRatios, updatedAccumulatedPicks);
            return;
        }

        if (isAutoTc) {
            const total = autoRows.reduce((sum, r) => sum + r.weight, 0);
            if (total <= 0) return;

            for (const r of autoRows) {
                if (r.code !== ctx.targetCode) continue;

                collectPaths(
                    ctx,
                    r.code,
                    r.weight,
                    total,
                    configuredPicks,
                    selectionProbability,
                    nextRatios,
                    acc,
                    updatedAccumulatedPicks,
                    visited
                );
            }

            return;
        }

        if (!isRegularTc) return;

        if (visited.has(name)) return;
        const nextVisited = new Set(visited);
        nextVisited.add(name);

        const entries = tcEntries(tc);
        if (!entries.length) return;

        const probabilityDenominator = entries.reduce((sum, e) => sum + e.prob, 0);
        const noDrop = adjustedNoDrop(num(tc.NoDrop), probabilityDenominator, ctx.players, ctx.party);
        const denominatorWithNoDrop = probabilityDenominator + noDrop;

        for (const e of entries) {
            collectPaths(
                ctx,
                e.item,
                e.prob,
                denominatorWithNoDrop,
                configuredPicks,
                selectionProbability,
                nextRatios,
                acc,
                updatedAccumulatedPicks,
                nextVisited
            );
        }
    }

    function finalQualityFactor(ctx, ratios) {
        if (ctx.dropMode === "misc") {
            return 1;
        }

        const sourceItems = ctx.dropMode === "set" ? ctx.setItems : ctx.uniqueItems;

        const occurrence = qualityOccurrenceChance(
            sourceItems,
            ctx.targetItem,
            ctx.targetCode,
            ctx.monsterLevel
        );

        if (occurrence <= 0) return 0;

        if (ctx.dropMode === "unique") {
            return qualityChance(
                ctx.itemRatio,
                ctx.baseItem,
                ctx.targetItem,
                ctx.exceptionalOrEliteCodes,
                ctx.monsterLevel,
                ctx.mf,
                ratios.unique,
                "unique"
            ) * occurrence;
        }

        if (ctx.dropMode === "set") {
            const uniqueRoll = qualityChance(
                ctx.itemRatio,
                ctx.baseItem,
                ctx.targetItem,
                ctx.exceptionalOrEliteCodes,
                ctx.monsterLevel,
                ctx.mf,
                ratios.unique,
                "unique"
            );

            const setRoll = qualityChance(
                ctx.itemRatio,
                ctx.baseItem,
                ctx.targetItem,
                ctx.exceptionalOrEliteCodes,
                ctx.monsterLevel,
                ctx.mf,
                ratios.set,
                "set"
            );

            return (1 - uniqueRoll) * setRoll * occurrence;
        }

        return 0;
    }

    function calculateDropChanceFromRoot(ctx, rootTc) {
        const acc = makeAccumulator();

        collectPaths(
            ctx,
            rootTc,
            1,
            1,
            1,
            1,
            {unique: 0, set: 0, rare: 0, magic: 0},
            acc,
            1
        );

        let none = 1;

        for (const group of acc.groups) {
            for (const outcome of group.values()) {
                const factor = finalQualityFactor(ctx, outcome.ratios);
                if (factor <= 0) continue;

                const perPick = outcome.probability * factor;
                const chance = probabilityForPicks(perPick, outcome.picks);

                none *= (1 - chance);
            }
        }

        return 1 - none;
    }

    function monsterLevelName(levels, monsterId) {
        const id = n(monsterId);

        const row = levels.find((lvl) =>
            Array.from({length: 10}, (_, i) => n(lvl[`mon${i + 1}`]))
                .includes(id)
        );

        return n(row?.LevelName);
    }

    async function calculateAll() {
        const q = n(query).toLowerCase();

        if (!q) {
            setRows([]);
            setError("");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const [
                monStatsTxt,
                treasureTxt,
                weaponsTxt,
                armorTxt,
                miscTxt,
                uniqueItemsTxt,
                setItemsTxt,
                itemRatioTxt,
                itemTypesTxt,
                levelsTxt,
            ] = await Promise.all([
                loadTxt("MonStats.txt"),
                loadTxt("TreasureClassEx.txt"),
                loadTxt("Weapons.txt"),
                loadTxt("Armor.txt"),
                loadTxt("Misc.txt"),
                loadTxt("UniqueItems.txt"),
                loadTxt("SetItems.txt"),
                loadTxt("ItemRatio.txt"),
                loadTxt("ItemTypes.txt"),
                loadTxt("Levels.txt"),
            ]);

            const monStats = parseTxt(monStatsTxt);
            const treasure = parseTxt(treasureTxt);
            const weapons = parseTxt(weaponsTxt);
            const armors = parseTxt(armorTxt);
            const misc = parseTxt(miscTxt);
            const uniqueItems = parseTxt(uniqueItemsTxt);
            const setItems = parseTxt(setItemsTxt);
            const itemRatio = parseTxt(itemRatioTxt);
            const itemTypes = parseTxt(itemTypesTxt);
            const levels = parseTxt(levelsTxt);

            // 构建 怪物TC名 → 中文怪物名 映射（仅唯一映射，区域 TC 会被多个怪物共享，跳过）
            const monsterTcMap = new Map();
            {
                const tcToNames = new Map();
                for (const mon of monStats) {
                    const nameZh = n(mon.NameStr);
                    if (!nameZh) continue;
                    for (const col of ["TreasureClass1", "TreasureClass1(N)", "TreasureClass1(H)"]) {
                        const tcName = n(mon[col]);
                        if (!tcName) continue;
                        if (!tcToNames.has(tcName)) tcToNames.set(tcName, new Set());
                        tcToNames.get(tcName).add(nameZh);
                    }
                }
                for (const [tcName, names] of tcToNames) {
                    if (names.size === 1) {
                        monsterTcMap.set(tcName, [...names][0]);
                    }
                }
            }

            const autoTcs = buildAutoTcs(weapons, armors, itemTypes);
            const baseItems = [...weapons, ...armors, ...misc];

            const exceptionalOrEliteCodes = new Set();

            for (const item of baseItems) {
                const uber = n(item.ubercode);
                const ultra = n(item.ultracode);

                if (uber) exceptionalOrEliteCodes.add(uber);
                if (ultra) exceptionalOrEliteCodes.add(ultra);
            }

            let targetItem = null;
            let targetCode = "";

            if (dropMode === "unique") {
                targetItem =
                    uniqueItems.find((u) => n(u.index).toLowerCase() === q) ||
                    uniqueItems.find((u) => n(u.index).toLowerCase().includes(q));

                if (!targetItem) throw new Error(`未找到暗金物品：${query}`);

                targetCode = n(targetItem.code);
            }

            if (dropMode === "set") {
                targetItem =
                    setItems.find((u) => n(u.index).toLowerCase() === q) ||
                    setItems.find((u) => n(u.index).toLowerCase().includes(q));

                if (!targetItem) throw new Error(`未找到套装物品：${query}`);

                targetCode = rowItemCode(targetItem);
            }

            if (dropMode === "misc") {
                const miscItem = misc.find((m) => n(m.code).toLowerCase() === q);

                if (!miscItem) throw new Error(`未找到杂项代码：${query}`);

                targetItem = miscItem;
                targetCode = n(miscItem.code);
            }

            const baseItem = baseItems.find((i) => n(i.code) === targetCode);

            if (!baseItem) {
                throw new Error(`未找到对应代码的基底物品：${targetCode}`);
            }

            if (targetItem && n(targetItem.index).toLowerCase().includes("aldur")) {
                console.log("BASE DEBUG", {
                    target: n(targetItem.index),
                    targetCode,

                    baseCode: n(baseItem.code),
                    baseName: n(baseItem.name),

                    // these are critical
                    baseLevel: n(baseItem.level),
                    baseType: n(baseItem.type),
                    baseRarity: n(baseItem.rarity),

                    normcode: n(baseItem.normcode),
                    ubercode: n(baseItem.ubercode),
                    ultracode: n(baseItem.ultracode),

                    isExceptionalElite: isExceptionalOrElite(
                        baseItem,
                        exceptionalOrEliteCodes
                    ),

                    itemRatioRow: getItemRatioRow(
                        itemRatio,
                        baseItem,
                        exceptionalOrEliteCodes
                    ),
                });
            }

            const out = [];

            for (const mon of monStats) {
                const monsterId = n(mon.Id);
                if (!monsterId) continue;

                const tcColumn =
                    difficulty === "H"
                        ? "TreasureClass1(H)"
                        : difficulty === "N"
                            ? "TreasureClass1(N)"
                            : "TreasureClass1";

                const tcName = n(mon[tcColumn]);
                if (!tcName) continue;

                const monsterLevel =
                    difficulty === "H"
                        ? num(mon["Level(H)"])
                        : difficulty === "N"
                            ? num(mon["Level(N)"])
                            : num(mon.Level);
                if (monsterLevel <= 0) continue;

                if (dropMode !== "misc" && monsterLevel < num(targetItem.lvl)) {
                    continue;
                }

                const rootTc = getRootTc(treasure, tcName, monsterLevel);

                const ctx = {
                    treasure,
                    autoTcs,
                    itemRatio,
                    uniqueItems,
                    setItems,
                    targetItem,
                    targetCode,
                    baseItem,
                    monsterLevel,
                    mf,
                    players,
                    party: players,
                    dropMode,
                    exceptionalOrEliteCodes,
                };

                const chance = calculateDropChanceFromRoot(ctx, rootTc);
                const levelName = monsterLevelName(levels, monsterId);

                if (chance > 0) {
                    out.push({
                        monsterId,
                        monsterName: n(mon.NameStr) || monsterId,
                        levelName,
                        treasureClass: translateTcDisplay(rootTc, monsterTcMap),
                        chance,
                        oneIn: Math.round(1 / chance),
                        percent: chance * 100,
                    });
                }
            }

            out.sort((a, b) => b.chance - a.chance);

            setRows(out);
            setPage(1);
        } catch (e) {
            setRows([]);
            setError(e instanceof Error ? e.message : String(e));
        } finally {
            setLoading(false);
        }
    }

    const PAGE_SIZE = 50;
    const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
    const safePage = Math.min(page, totalPages);
    const pageRows = rows.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

    return (
        <>
            <div className="filtersStack">
                <div className="filtersRow">
                    <div className="filtersPanel">
                        <div style={{display: "flex", gap: 12, width: "100%"}}>
                            <SearchableSelect
                                value={dropMode}
                                onChange={setDropMode}
                                options={[
                                    {value: "unique", label: "暗金物品"},
                                    {value: "set", label: "套装物品"},
                                    {value: "misc", label: "按名称查找杂项物品"},
                                ]}
                                style={{flex: "0 0 260px"}}
                            />

                            <SearchableSelect
                                value={difficulty}
                                onChange={setDifficulty}
                                options={[
                                    {value: "", label: "普通"},
                                    {value: "N", label: "噩梦"},
                                    {value: "H", label: "地狱"},
                                ]}
                                style={{flex: "0 0 220px"}}
                            />

                            <SearchableSelect
                                value={players}
                                onChange={setPlayers}
                                options={Array.from({length: 8}, (_, i) => ({
                                    value: String(i + 1),
                                    label: `玩家 ${i + 1}`,
                                }))}
                                style={{flex: "0 0 180px"}}
                            />

                            <input
                                type="text"
                                inputMode="numeric"
                                className="searchBar"
                                value={mf}
                                onChange={(e) => {
                                    const value = e.target.value.replace(/\D/g, "");
                                    setMf(value);
                                }}
                                placeholder="寻宝率（MF）"
                                style={{
                                    flex: "0 0 160px",
                                    maxWidth: 160,
                                    height: 31
                                }}
                            />
                        </div>

                        <input
                            type="text"
                            className="searchBar"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder={dropMode === "misc" ? "输入物品代码…" : "输入物品名称…"}
                        />
                    </div>
                </div>
            </div>

            <div className="affixPanel">
                <div className="affixTableWrapper">
                    <div className="affixPager">
                        <div>
                            <div className="helpTitle">掉落计算器</div>
                            <div>
                                显示第 {rows.length ? (safePage - 1) * PAGE_SIZE + 1 : 0}
                                 - {Math.min(safePage * PAGE_SIZE, rows.length)} 条，共 {rows.length} 条
                            </div>
                        </div>

                        <div className="affixPagerRight">
                            <button
                                type="button"
                                className="btn affixPagerBtn"
                                disabled={safePage <= 1}
                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                            >
                                ‹ 上一页
                            </button>

                            <span className="affixPagerInfo">
                    第 {safePage} / {totalPages} 页
                </span>

                            <button
                                type="button"
                                className="btn affixPagerBtn"
                                disabled={safePage >= totalPages}
                                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                            >
                                下一页 ›
                            </button>
                        </div>
                    </div>

                    <div className="affixTableScroll">
                        <table className="affixTable">
                            <thead>
                            <tr>
                                <th>怪物</th>
                                <th>财宝等级</th>
                                <th>等级</th>
                                <th>掉落几率</th>
                                <th>掉落几率 %</th>
                            </tr>
                            </thead>

                            <tbody>
                            {loading && (
                                <tr>
                                    <td colSpan="5" className="table-message">
                                        计算中…
                                    </td>
                                </tr>
                            )}

                            {!loading && error && (
                                <tr>
                                    <td colSpan="5" className="table-message">
                                        {error}
                                    </td>
                                </tr>
                            )}

                            {!loading && !error && pageRows.map((r, i) => (
                                <tr key={`${r.monsterId || r.monsterName}-${i}`}>
                                    <td>{r.monsterName}</td>
                                    <td>{r.treasureClass}</td>
                                    <td>{r.levelName}</td>
                                    <td>1:{r.oneIn}</td>
                                    <td>{r.percent.toFixed(6)}%</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </>
    );
}

function AuraEffectCalculator() {
    const [baseValue, setBaseValue] = React.useState("");
    const [bonusValue, setBonusValue] = React.useState("");

    const num = (v) => {
        const x = Number(String(v).replace(",", "."));
        return Number.isFinite(x) ? x : 0;
    };

    const result = React.useMemo(() => {
        const base = num(baseValue);
        const bonus = num(bonusValue);

        const raw = base * (100 + ((bonus * 60) / (bonus + 25))) / 100;

        return Number.isFinite(raw) ? Math.floor(raw) : 0;
    }, [baseValue, bonusValue]);

    const fmt = (x) => {
        const r = Math.round(x * 100) / 100;
        return String(r);
    };

    const reset = () => {
        setBaseValue("");
        setBonusValue("");
    };

    return (<div className="infoPanel">
        <div className="infoHeader">
            <div className="infoTitle">光环效果计算器</div>

            <div className="filtersResetPanel">
                <button
                    type="button"
                    className="btn secondary"
                    onClick={reset}
                >
                    重置
                </button>
            </div>
        </div>

        <div className="meta">
            计算考虑递减收益后的最终光环效果。
        </div>

        <div className="hr"/>

        <div className="calcGrid">

            <div className="calcRow">
                <div className="calcLabel">基础数值</div>
                <input
                    className="calcInput"
                    type="number"
                    value={baseValue}
                    onChange={(e) => setBaseValue(e.target.value)}
                    placeholder="例如：100"
                />
            </div>

            <div className="calcRow">
                <div className="calcLabel">光环效果加成</div>
                <input
                    className="calcInput"
                    type="number"
                    value={bonusValue}
                    onChange={(e) => setBonusValue(e.target.value)}
                    placeholder="例如：50"
                />
            </div>

            <div className="calcOut">
                <div className="calcOutLabel">最终效果</div>
                <div className="calcOutValue">{fmt(result)}</div>
            </div>

            <div className="calcFormula dim">
                X = base × (100 + (bonus × 60)/(bonus + 25)) / 100
            </div>

        </div>
    </div>);
}

function AuraRadiusEffectCalculator() {

    // Radius inputs
    const [radiusBase, setRadiusBase] = React.useState("");
    const [radiusBonus, setRadiusBonus] = React.useState("");

    // Effect inputs
    const [effectBase, setEffectBase] = React.useState("");
    const [effectBonus, setEffectBonus] = React.useState("");

    const num = (v) => {
        const x = Number(String(v).replace(",", "."));
        return Number.isFinite(x) ? x : 0;
    };

    const SUBTILE_TO_YARDS = 2 / 3;          // 0.666666...
    const YARDS_TO_SUBTILES = 1.5; // 1.5

    const calcRadiusYards = React.useMemo(() => {
        // user input (yards)
        const baseYards = num(radiusBase);
        const skill_radius_bonus = num(radiusBonus);

        // convert yards -> subtiles (game internal)
        // IMPORTANT: subtiles are discrete, so we round to int
        const baseSubtiles = Math.round(baseYards * YARDS_TO_SUBTILES);

        // DR bonus term (still in % units)
        const bonusTerm = (skill_radius_bonus * 70) / ((skill_radius_bonus + 18) || 1);

        // apply formula in subtiles
        const xSubtilesRaw = (baseSubtiles * (100 + bonusTerm)) / 100;

        // IMPORTANT: game uses discrete subtiles
        const xSubtiles = Math.round(xSubtilesRaw);

        // convert back to yards for display
        const xYards = xSubtiles * SUBTILE_TO_YARDS;

        return Number.isFinite(xYards) ? xYards : 0;
    }, [radiusBase, radiusBonus]);

    const calcEffect = React.useMemo(() => {
        const base_value = num(effectBase);
        const aura_effect_bonus = num(effectBonus);
        const bonusTerm = (aura_effect_bonus * 60) / (aura_effect_bonus + 25 || 1);
        const Y = (base_value * (100 + bonusTerm)) / 100;
        return Number.isFinite(Y) ? Y : 0;
    }, [effectBase, effectBonus]);

    const fmt = (x) => {
        // keep it readable, but stable
        const r = Math.round(x * 100) / 100;
        return String(r);
    };

    const reset = () => {
        setRadiusBase("");
        setRadiusBonus("");
        setEffectBase("");
        setEffectBonus("");
    };

    return (<div className="infoPanel">
        <div className="infoHeader">
            <div className="infoTitle">光环范围与效果</div>
            <button type="button" className="btn ghost" onClick={reset}>
                Reset
            </button>
        </div>

        <div className="meta">
            输入基础数值与加成数值；计算器将应用该词缀使用的递减收益公式。
        </div>

        <div className="hr"/>

        <div className="calcGrid">
            <div className="calcCard">
                <div className="calcTitle">范围</div>

                <div className="calcRow">
                    <div className="calcLabel">基础数值</div>
                    <input
                        className="calcInput"
                        type="number"
                        inputMode="decimal"
                        value={radiusBase}
                        onChange={(e) => setRadiusBase(e.target.value)}
                        placeholder="例如：10"
                    />
                </div>

                <div className="calcRow">
                    <div className="calcLabel">技能范围加成</div>
                    <input
                        className="calcInput"
                        type="number"
                        inputMode="decimal"
                        value={radiusBonus}
                        onChange={(e) => setRadiusBonus(e.target.value)}
                        placeholder="例如：50"
                    />
                </div>

                <div className="calcOut">
                    <div className="calcOutLabel">范围结果（X）</div>
                    <div className="calcOutValue">{fmt(calcRadiusYards)}</div>
                </div>

                <div className="calcFormula dim">
                    X = base × (100 + ((bonus×70)/(bonus+18))) / 100
                </div>
            </div>

            <div className="calcCard">
                <div className="calcTitle">效果</div>

                <div className="calcRow">
                    <div className="calcLabel">基础数值</div>
                    <input
                        className="calcInput"
                        type="number"
                        inputMode="decimal"
                        value={effectBase}
                        onChange={(e) => setEffectBase(e.target.value)}
                        placeholder="例如：100"
                    />
                </div>

                <div className="calcRow">
                    <div className="calcLabel">光环效果加成</div>
                    <input
                        className="calcInput"
                        type="number"
                        inputMode="decimal"
                        value={effectBonus}
                        onChange={(e) => setEffectBonus(e.target.value)}
                        placeholder="例如：80"
                    />
                </div>

                <div className="calcOut">
                    <div className="calcOutLabel">效果结果（Y）</div>
                    <div className="calcOutValue">{fmt(calcEffect)}</div>
                </div>

                <div className="calcFormula dim">
                    Y = base × (100 + ((bonus×60)/(bonus+25))) / 100
                </div>
            </div>
        </div>
    </div>);
}

function HelpPanel() {
    return (<div className="helpPanel">
        <div className="helpTitle">帮助</div>

        <div className="helpBody">
            <p><b>导航</b></p>
            <ul>
                <li><b>← / →</b> 切换标签页</li>
                <li><b>↑ / ↓</b> 在物品列表中移动选中项</li>
                <li><b>Ctrl/Cmd + F</b> 快捷键 - 聚焦搜索框</li>
                <li><b>Esc</b> 取消聚焦搜索框（当搜索框处于聚焦状态时）</li>
            </ul>

            <p><b>搜索</b></p>
            <ul>
                <li>使用引号进行精确短语搜索：<code>"快速施法"</code></li>
                <li>在 <b>暗金装备</b>、<b>符文之语</b>、<b>圣化</b> 和 <b>词缀</b> 标签页中，搜索也会匹配
                    属性内容。
                </li>
            </ul>

            <p><b>界面</b></p>
            <ul>
                <li>标签下方的点状下划线表示悬停时包含有用的提示。</li>
                <li>标签下方的虚线下划线表示它链接到本站的某个条目，点击后会跳转过去。
                </li>
                <li>点击页脚右侧的版本号可查看本资料库的更新日志
                </li>
                <li>暗金装备名称旁的橙色星号表示该物品是流放圣域（Sanctuary of Exile）新增的</li>
            </ul>
        </div>
    </div>);
}

function FateCardTooltip({card}) {
    if (!card) return <div className="emptyState">选择一张命运卡牌。</div>;

    return (
        <>
            <div className="tipTitle">{n(card.name)}</div>

            <div className="hr"/>

            <div className="uniqueHeader">描述</div>

            {String(card.description || "")
                .replace(/\r\n/g, "\n")
                .trim()
                .split("\n")
                .map((line, i) => {
                    const text = line.trim();

                    if (!text) {
                        return <div key={i} style={{height: 8}}/>;
                    }

                    return (
                        <div key={i} className="runeModLine">
                            {text}
                        </div>
                    );
                })}

            <div className="hr"/>

            {lineKV("代码：", n(card.code))}
            {lineKV("所需数量：", n(card.requiredAmount))}
        </>
    );
}

function WeaponTooltip({w, onGoCode, onGoUnique}) {
    if (!w) return <div className="emptyState">请选择物品。</div>;
    const title = n(w?.displayName) || n(w?.name) || "Unknown Item";
    const hasRequirements = (has(w?.requiredStrength) || has(w?.requiredDexterity) || has(w?.requiredLevel) && w?.requiredLevel != 0 && w?.requiredDexterity != 0 && w?.requiredStrength != 0);

    const tierEntries = [{
        tierLabel: "普通", name: n(w?.normalItemDisplayName), code: n(w?.normalTierCode),
    }, {
        tierLabel: "扩展", name: n(w?.exceptionalItemDisplayName), code: n(w?.exceptionalTierCode),
    }, {
        tierLabel: "精英", name: n(w?.eliteItemDisplayName), code: n(w?.eliteTierCode),
    },];

    return (<>
        <div className="tipTitle">{title}</div>
        <div className="tipSubtitle">{weaponTypeLabel(w)}</div>
        <div className="hr"/>

        {weaponDmgLines(w).map((d) => (<React.Fragment key={d.k}>{lineKV(d.k + ":", d.v)}</React.Fragment>))}

        {has(w?.speed) && lineKV("武器速度修正：", fmtSigned(w?.speed) || n(w?.speed))}

        {n(w?.noDurability) === "1" ? (<div
            className="line dim">不可破坏</div>) : (has(w?.durability) && lineKV("耐久：", n(w?.durability)))}

        {has(w?.maxSockets) && lineKV("最大孔数：", n(w?.maxSockets))}

        {hasRequirements ? (<>
            <div className="hr"/>
            <div className="dropHeader">需求</div>
            {nz(w?.requiredLevel) && lineKV("需求等级：", n(w?.requiredLevel), "req")}
            {(nz(w?.requiredStrength) || nz(w?.requiredDexterity))}
            {nz(w?.requiredStrength) && lineKV("需求力量：", n(w?.requiredStrength), "req")}
            {nz(w?.requiredDexterity) && lineKV("需求敏捷：", n(w?.requiredDexterity), "req")}
        </>) : null}

        <div className="hr"/>
        <div className="dropHeader">附加物品信息</div>
        {has(w?.itemTier) && lineKV("物品阶位：", n(w?.itemTier), "")}
        {has(w?.level) && lineKV("品质等级：", n(w?.level), "", TOOLTIPS_TEXT_MAP["qualityLevel"])}
        {lineKV("代码：", n(w?.code), "", TOOLTIPS_TEXT_MAP["code"])}
        <TierLinks entries={tierEntries} onGo={onGoCode}/>
        <UniquesPanel uniques={w?.uniques} onGoUnique={onGoUnique}/>
    </>);
}

function ArmorTooltip({a, onGoCode, onGoUnique}) {
    if (!a) return <div className="emptyState">请选择物品。</div>;
    const title = n(a?.displayName) || n(a?.name) || "Unknown Item";
    const def = armorDefenseLine(a);
    const hasRequirements = (has(a?.requiredStrength) && a?.requiredStrength > 0 && has(a?.requiredLevel) && a?.requiredLevel > 0) || (has(a?.requiredStrength) && a?.requiredStrength > 0);

    const tierEntries = [{
        tierLabel: "普通", name: n(a?.normalItemDisplayName), code: n(a?.normalTierCode),
    }, {
        tierLabel: "扩展", name: n(a?.exceptionalItemDisplayName), code: n(a?.exceptionalTierCode),
    }, {
        tierLabel: "精英", name: n(a?.eliteItemDisplayName), code: n(a?.eliteTierCode),
    },];

    return (<>
        <div className="tipTitle">{title}</div>
        <div className="tipSubtitle">{armorTypeLabel(a)}</div>
        <div className="hr"/>

        {has(def) && lineKV("防御：", def)}
        {nz(a?.block) && lineKV("格挡几率：", `${n(a?.block)}%`)}
        {nz(a?.maxSockets) && lineKV("最大孔数：", n(a?.maxSockets))}
        {has(a?.durability) && lineKV("耐久：", n(a?.durability))}

        {hasRequirements ? (<>
            <div className="hr"/>
            <div className="dropHeader">需求</div>
            {nz(a?.requiredLevel) && lineKV("需求等级：", n(a?.requiredLevel), "req")}
            {nz(a?.requiredStrength) && lineKV("需求力量：", n(a?.requiredStrength), "req")}
        </>) : null}

        <div className="hr"/>
        <div className="dropHeader">附加物品信息</div>
        {has(a?.itemTier) && lineKV("物品阶位：", n(a?.itemTier), "dim")}
        {has(a?.level) && lineKV("品质等级：", n(a?.level), "", TOOLTIPS_TEXT_MAP["qualityLevel"])}
        {lineKV("代码：", n(a?.code), "dim", TOOLTIPS_TEXT_MAP["code"])}
        <TierLinks label="阶位：" entries={tierEntries} onGo={onGoCode}/>
        <UniquesPanel uniques={a?.uniques} onGoUnique={onGoUnique}/>
    </>);
}

function RunewordTooltip({rw, onGoSacred, onLink}) {
    if (!rw) return <div className="emptyState">请选择物品。</div>;

    const title = n(rw?.displayName) || n(rw?.runewordName) || "符文之语";
    const hasRequirements = rw?.requiredlevel > 0;

    const runes = [n(rw?.firstRuneDisplayName), n(rw?.secondRuneDisplayName), n(rw?.thirdRuneDisplayName), n(rw?.fourthRuneDisplayName), n(rw?.fifthRuneDisplayName), n(rw?.sixthRuneDisplayName),].filter(Boolean);

    const types = runewordAllTypes(rw);
    const mods = Array.isArray(rw?.displayProperties) ? rw.displayProperties.filter((x) => x != null && String(x).trim() !== "") : [];

    const rwSacreds = Array.isArray(rw?.sacreds) ? rw.sacreds : [];

    return (<>
        <div className="tipTitle">{title}</div>
        {types.length ? (<div className="tipSubtitle">{types.join(" / ")}</div>) : null}

        <div className="hr"/>
        {runes.length ? (<div className="runesDisplay">
            <Tip text={String(TOOLTIPS_TEXT_MAP["runes"])}>
                {runes.map(runeLabel).join(" · ")}
            </Tip>
        </div>) : null}

        <div className="hr"/>
        <div className="uniqueHeader">属性</div>
        {mods.length ? (mods.flatMap((m, i) => {
            const raw = String(m ?? "");
            const normalized = raw.replace(/\\n/g, "\n");
            const lines = normalized
                .split("\n")
                .map((l) => l.trim())
                .filter(Boolean);

            return lines.map((line, j) => {
                const cls = classForPropertyLine(line);
                const key = `${i}-${j}`;
                return (<div key={key} className={"runeModLine " + cls}>
                    {renderInlineMarkdown(line, onLink)}
                </div>);
            });
        })) : (<div className="line dim">未列出属性。</div>)}

        {hasRequirements ? (<>
            <div className="hr"/>
            <div className="dropHeader">需求</div>
            {nz(rw?.requiredlevel) && lineKV("需求等级：", n(rw?.requiredlevel), "req")}
        </>) : null}

        {rwSacreds.length ? (<>
            <div className="hr"/>
            <div className="dropHeader">圣化</div>
            {rwSacreds.map((s, idx) => {
                const name = sacredNameZh(n(s?.sacredName));
                const typesText = Array.isArray(s?.itemTypes) ? s.itemTypes.map((t) => typeZh(n(t))).filter(Boolean).join(" / ") : "";
                if (!name) return null;

                return (<div key={`${idx}::${name}`} className="line goToLink">
                    {onGoSacred ? (<a
                        href="#"
                        className="d2link"
                        onClick={(ev) => {
                            ev.preventDefault();
                            onGoSacred(name, Array.isArray(s?.itemTypes) ? s.itemTypes : []);
                        }}
                        title={`跳转到圣化：${name}`}
                    >
                        {name} {typesText ? `(${typesText})` : ""}
                    </a>) : (<span className="d2linkText">{name}</span>)}
                </div>);
            })}
        </>) : null}
    </>);
}

function useIsMobile(maxWidth = 980) {
    const [isMobile, setIsMobile] = React.useState(typeof window !== "undefined" ? window.innerWidth <= maxWidth : false);

    React.useEffect(() => {
        const handler = () => setIsMobile(window.innerWidth <= maxWidth);
        window.addEventListener("resize", handler);
        return () => window.removeEventListener("resize", handler);
    }, [maxWidth]);

    return isMobile;
}

function CorruptionsTable({items}) {
    const PAGE_SIZE = 50;
    const [page, setPage] = React.useState(1);

    React.useEffect(() => {
        setPage(1);
    }, [items]);

    const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
    const safePage = Math.min(page, totalPages);

    const pageItems = React.useMemo(() => {
        const start = (safePage - 1) * PAGE_SIZE;
        return items.slice(start, start + PAGE_SIZE);
    }, [items, safePage]);

    return (
        <div className="affixTableWrapper">
            <div className="affixPager">
                <div>
                    <div className="helpTitle">腐化</div>
                    <div>
                        显示第 {(safePage - 1) * PAGE_SIZE + 1}-{Math.min(safePage * PAGE_SIZE, items.length)} 条，共 {items.length} 条
                    </div>
                </div>

                <div className="affixPagerRight">
                    <button
                        type="button"
                        className="btn affixPagerBtn"
                        disabled={safePage <= 1}
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                    >
                        ‹ 上一页
                    </button>

                    <span className="affixPagerInfo">
                        第 {safePage} / {totalPages} 页
                    </span>

                    <button
                        type="button"
                        className="btn affixPagerBtn"
                        disabled={safePage >= totalPages}
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    >
                        下一页 ›
                    </button>
                </div>
            </div>

            <div className="affixTableScroll">
                <table className="affixTable corruptionsTable">
                    <thead>
                    <tr>
                        <th>物品</th>
                        <th>腐化</th>
                        <th>几率</th>
                    </tr>
                    </thead>

                    <tbody>
                    {pageItems.map((it, idx) => (
                        <tr key={`${safePage}-${idx}-${n(it?.displayName)}-${n(it?.chance)}`}>
                            <td>{n(it?.displayName)}</td>
                            <td className="affixAttr">
                                {Array.isArray(it?.corruptionProperties) && it.corruptionProperties.length
                                    ? it.corruptionProperties.join("\n")
                                    : "—"}
                            </td>
                            <td className="corruptionChance">{n(it?.chance)}%</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function AffixesPanel({data, loading, error, sort, onChangeSort}) {
    const [page, setPage] = React.useState(0);
    const isMobile = useIsMobile(895);
    const pageSize = 50;

    // Local state

    // Normalised data coming from global filters/search
    const all = React.useMemo(() => (Array.isArray(data) ? data : []), [data]);

    // Whenever the underlying data changes (global filters / search),
    // reset to page 0 so we don't end up on an invalid page.
    React.useEffect(() => {
        setPage(0);
    }, [data]);

    const sortKey = sort?.key || "attrs";
    const sortDir = sort?.dir || "asc";

    const sorted = React.useMemo(() => {
        const arr = [...all];
        if (!sortKey) return arr;

        // Special case: Attributes column
        if (sortKey === "attrs") {
            arr.sort((a, b) => {
                const aa = affixPrimaryPropertyAndMax(a);
                const bb = affixPrimaryPropertyAndMax(b);

                // 1) group by property
                const propCmp = aa.property.localeCompare(bb.property);
                if (propCmp !== 0) {
                    return sortDir === "asc" ? propCmp : -propCmp;
                }

                // 2) within same property, sort by max
                const diff = aa.max - bb.max;
                return sortDir === "asc" ? diff : -diff;
            });
            return arr;
        }

        // All other columns use the generic logic
        const getValue = (it) => {
            switch (sortKey) {
                case "name":
                    return n(it?.name);
                case "types":
                    return (it?.displayItemTypeNames || []).join(", ");
                case "excluded":
                    return (it?.displayExcludedItemTypeNames || []).join(", ");
                case "class":
                    return n(it?.classDisplayName);
                case "rare":
                    return Number(it?.rare || 0);
                case "maxLevel":
                    return Number(it?.maxLevel || 0);
                case "reqLevel":
                    return Number(it?.requiredLevel || 0);
                case "freq":
                    return Number(it?.frequency || 0);
                default:
                    return "";
            }
        };

        arr.sort((a, b) => {
            const va = getValue(a);
            const vb = getValue(b);

            const bothNumbers = typeof va === "number" && !Number.isNaN(va) && typeof vb === "number" && !Number.isNaN(vb);

            if (bothNumbers) {
                return sortDir === "asc" ? va - vb : vb - va;
            }

            return sortDir === "asc" ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
        });

        return arr;
    }, [all, sortKey, sortDir]);

    const handleSort = (key) => {
        onChangeSort((prev) => {
            if (prev && prev.key === key) {
                return {key, dir: prev.dir === "asc" ? "desc" : "asc"};
            }
            return {key, dir: "asc"};
        });
    };

    const sortArrowFor = (key) => {
        if (sortKey !== key) return null;
        return <span className="sortArrow">{sortDir === "asc" ? "▲" : "▼"}</span>;
    };

    // --- Loading / empty / mobile -------------------------------------------

    if (loading) {
        return (<div className="infoPanel">
            <div className="infoHeader">
                <div className="infoTitle">词缀</div>
            </div>
            <div className="meta">词缀加载中…</div>
        </div>);
    }

    if (error) {
        return (<div className="infoPanel">
            <div className="infoHeader">
                <div className="infoTitle">词缀</div>
            </div>
            <div className="meta">
                词缀加载失败：{String(error.message || error)}
            </div>
        </div>);
    }

    if (isMobile) {
        return (<div className="infoPanel">
            <div className="infoHeader">
                <div className="infoTitle">词缀</div>
            </div>
            <div
                className="emptyState"
                style={{padding: "16px", textAlign: "center"}}
            >
                词缀表格无法在移动端查看。
                <br/>
                请使用屏幕更大的设备。
            </div>
        </div>);
    }

    const total = sorted.length;
    if (!total) {
        return (<div className="infoPanel">
            <div className="infoHeader">
                <div className="infoTitle">词缀</div>
            </div>
            <div className="emptyState">没有符合筛选条件的词缀。</div>
        </div>);
    }

    // --- Pagination (on *sorted* data) ---------------------------------------

    const pageCount = Math.max(1, Math.ceil(total / pageSize));
    const safePage = Math.min(page, pageCount - 1);
    const start = safePage * pageSize;
    const end = start + pageSize;
    const current = sorted.slice(start, end);

    const goPrev = () => setPage((p) => Math.max(0, p - 1));
    const goNext = () => setPage((p) => Math.min(pageCount - 1, p + 1));

    // --- Render table --------------------------------------------------------

    return (<div className="infoPanel">
        <div className="infoHeader">
            <div className="infoTitle">词缀</div>
        </div>

        <div className="affixTableWrapper">
            {/* Pager above table */}
            <div className="affixPager">
                <div className="affixPagerLeft">
            <span>
              显示第 {start + 1}–{Math.min(end, total)} 条，共 {total} 条
            </span>
                </div>
                <div className="affixPagerRight">
                    <button
                        type="button"
                        className="btn ghost affixPagerBtn"
                        onClick={goPrev}
                        disabled={safePage === 0}
                    >
                        ‹ 上一页
                    </button>
                    <span className="affixPagerInfo">
              第 {safePage + 1} / {pageCount} 页
            </span>
                    <button
                        type="button"
                        className="btn ghost affixPagerBtn"
                        onClick={goNext}
                        disabled={safePage === pageCount - 1}
                    >
                        下一页 ›
                    </button>
                </div>
            </div>

            {/* Scrollable table */}
            <div className="affixTableScroll">
                <table className="affixTable">
                    <thead>
                    <tr>
                        <th
                            className="sortable"
                            onClick={() => handleSort("name")}
                        >
                  <span className="thLabel">
                    名称 {sortArrowFor("name")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("attrs")}
                        >
                  <span className="thLabel">
                    属性 {sortArrowFor("attrs")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("level")}
                        >
                  <span className="thLabel">
                      <Tip text={String(TOOLTIPS_TEXT_MAP["affixLevel"])}>词缀等级</Tip> {sortArrowFor("level")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("rare")}
                        >
                  <span className="thLabel">
                      <Tip text={String(TOOLTIPS_TEXT_MAP["affixRares"])}>稀有 {sortArrowFor("rare")}</Tip>
                  </span>

                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("freq")}
                        >
                  <span className="thLabel">
                      <Tip text={String(TOOLTIPS_TEXT_MAP["affixFrequency"])}>频率</Tip> {sortArrowFor("freq")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("maxLevel")}
                        >
                  <span className="thLabel">
                      <Tip text={String(TOOLTIPS_TEXT_MAP["affixMaxLevel"])}>最大等级</Tip> {sortArrowFor("maxLevel")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("types")}
                        >
                  <span className="thLabel">
                    物品类型 {sortArrowFor("types")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("excluded")}
                        >
                  <span className="thLabel">
                    排除的物品类型 {sortArrowFor("excluded")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("class")}
                        >
                  <span className="thLabel">
                    职业 {sortArrowFor("class")}
                  </span>
                        </th>

                        <th
                            className="sortable"
                            onClick={() => handleSort("reqLevel")}
                        >
                  <span className="thLabel">
                    需求等级 {sortArrowFor("reqLevel")}
                  </span>
                        </th>
                    </tr>
                    </thead>

                    <tbody>
                    {current.map((it, idx) => (<tr key={`${safePage}-${idx}-${it.id || it.name}`}>
                        <td>{n(it?.name)}</td>
                        <td>{affixDisplayString(it)}</td>
                        <td>{has(it?.level) ? it.level : ""}</td>
                        <td>{it?.rare ? "是" : "否"}</td>
                        <td>{has(it?.frequency) ? it.frequency : ""}</td>
                        <td>{has(it?.maxLevel) ? it.maxLevel : ""}</td>
                        <td>
                            {(it?.displayItemTypeNames || []).join(", ")}
                        </td>
                        <td>
                            {(it?.displayExcludedItemTypeNames || []).join(", ")}
                        </td>
                        <td>{n(it?.classDisplayName)}</td>
                        <td>
                            {has(it?.requiredLevel) ? it.requiredLevel : ""}
                        </td>
                    </tr>))}
                    </tbody>
                </table>
            </div>
        </div>
    </div>);
}

function UniqueTooltip({u, openDropCalculator, onLink}) {
    if (!u) return <div className="emptyState">请选择物品。</div>;

    const title = n(u?.displayName) || "Unknown Unique";

    const base = uniqueBase(u);
    const baseName = n(base?.displayName) || n(base?.name) || "";

    const mods = visibleProperties(
        Array.isArray(u?.displayProperties)
            ? u.displayProperties.filter((x) => x != null && String(x).trim() !== "")
            : []
    );

    const dropSource = u?.dropSource;
    const dropRate = u?.dropRate;
    const occurrenceChance = u?.occurrenceChance;
    const occurrenceChanceCurrency = u?.occurrenceChanceCurrency;

    const hasDropSource = dropSource !== null && dropSource !== undefined && String(dropSource).trim() !== "";
    const hasDropRate = dropRate !== null && dropRate !== undefined && String(dropRate).trim() !== "";
    const hasOccurrenceChance = occurrenceChance !== null && occurrenceChance !== undefined && String(occurrenceChance).trim() !== "";
    const hasOccurrenceChanceCurrency = occurrenceChanceCurrency !== null && occurrenceChanceCurrency !== undefined && String(occurrenceChanceCurrency).trim() !== "";
    const hasDropInfo = hasDropSource || hasDropRate || hasOccurrenceChance || hasOccurrenceChanceCurrency;

    const itemType = getItemTypeForUnique(u);
    const requiredLevel = getRequiredLevelForUnique(u, itemType);
    const requiredDexterity = getRequiredDexterityForUnique(u, itemType);
    const requiredStrength = getRequiredStrengthForUnique(u, itemType);
    const hasRequirements = (requiredLevel > 0 && requiredStrength > 0) || (requiredLevel > 0 && requiredDexterity > 0) || (requiredLevel > 0 && requiredDexterity > 0 && requiredStrength > 0);

    const mythicOrbIndexes = new Set([
        "拿各的戒指",
        "马纳德的治疗",
        "乌鸦之霜",
        "矮人之星",
        "腐肉之风",
        "诺科兰遗物",
        "阿特玛的圣甲虫",
        "艾利屈之眼",
        "新月",
        "萨拉森的机会",
        "玛希姆奥克的橡木古董",
        "猫眼",
    ]);

    const divineOrbIndexes = new Set([
        "乔丹之石",
        "布尔凯索的婚戒",
        "自然的和平",
        "约束之环",
        "幽魂之环",
        "死亡仪态",
        "兄弟会召唤",
        "巴尔隘口",
        "巴尔的喘息",
        "巴尔之握",
        "旭日东升",
        "大君之怒",
        "马拉的万花筒",
        "炽天使圣歌",
        "金属网格",
        "命运的抗争",
        "星魂",
    ]);

    const creationOrb = mythicOrbIndexes.has(u?.index)
        ? "神话宝珠"
        : divineOrbIndexes.has(u?.index)
            ? "神授宝珠"
            : (u?.itemTier === "普通" || u?.itemTier === "扩展")
                ? "神话宝珠"
                : "神授宝珠";

    return (<>
        <div className="tipUniqueTitle">{title}</div>
        <div className="tipSubtitle">
            {baseName}
        </div>

        {u?.carryOne === "1" ? (<div className="carryOne">
            你的背包和仓库中只能携带一件！
        </div>) : null}

        {has(u?.weaponBase) ? (<>
            <div className="hr"/>
            {has(u?.displayOneHandDamage) && lineKV("单手伤害：", n(u?.displayOneHandDamage), "")}
            {has(u?.displayTwoHandDamage) && lineKV("双手伤害：", n(u?.displayTwoHandDamage), "")}
        </>) : null}

        {has(u?.armorBase) ? (<>
            <div className="hr"/>
            {has(u?.displayDefense) && lineKV("防御：", n(u?.displayDefense), "")}
        </>) : null}

        <div className="hr"/>
        <div className="uniqueHeader">暗金属性</div>

        {mods.length ? (mods.flatMap((m, idx) => {
            const raw = String(m ?? "");
            // support both "\n" and actual newlines
            const normalized = raw.replace(/\\n/g, "\n");
            const lines = normalized
                .split("\n")
                .map((l) => l.trim())
                .filter(Boolean);

            return lines.map((line, j) => {
                const cls = classForPropertyLine(line);
                const key = `${idx}-${j}`;

                return (<div key={key} className={"uniqueMod " + cls}>
                    {renderInlineMarkdown(line, onLink)}
                </div>);
            });
        })) : (<div className="line dim">暂无词缀信息。</div>)}

        {hasDropInfo && !u?.hellforged ? (<>
            <div className="hr"/>
            <div className="dropHeader">掉落信息</div>
            {hasDropSource && lineKV("掉落来源：", String(dropSource), "")}
            {hasDropRate && lineKV("掉落率：", String(dropRate), "")}
            {hasOccurrenceChance && lineKV("出现几率：", String(occurrenceChance), "")}
        </>) : null}

        {hasRequirements ? (<>
            <div className="hr"/>
            <div className="dropHeader">需求</div>
            {nz(requiredLevel) && lineKV("需求等级：", n(requiredLevel), "req")}
            {nz(requiredStrength) && lineKV("需求力量：", n(requiredStrength), "req")}
            {nz(requiredDexterity) && lineKV("需求敏捷：", n(requiredDexterity), "req")}
        </>) : null}

        {u?.showCanBeCreatedWith === true && !u?.hellforged ? (<>
            <div className="hr"/>
            <div className="dropHeader">制作</div>
            {hasOccurrenceChanceCurrency && occurrenceChance !== occurrenceChanceCurrency && lineKV("通货出现几率：", String(occurrenceChanceCurrency), "")}
            <br/>
            <div className="line dim">
                你可以用其基底物品配合{" "}
                <span className="highlight">{creationOrb}</span> 制作这件暗金装备。
            </div>
        </>) : null}

        {u?.hellforged ? (<>
            <div className="hr"/>
            <div className="dropHeader">制作</div>
            <div className="line dim">
                你可以使用特殊的炼狱熔炉配方制作这件暗金装备。请查看上方「魔方配方」标签页。
            </div>
        </>) : null}

        {!u?.hellforged ? (<>
            <div
                className="tooltip-link"
                onClick={() => openDropCalculator(n(u?.displayName) || n(u?.index))}
            >
                查看掉落率
            </div>
        </>) : null}
    </>);
}

function StaticDataPanel({data, loading, error, search, onLink, damnation = false, emptyLabel}) {
    const [openMap, setOpenMap] = React.useState({});

    const all = Array.isArray(data) ? data : [];

    const filtered = React.useMemo(() => {
        const q = (search || "").trim().toLowerCase();

        const modeOk = (r) => {
            const modes = r?.modes;
            if (!modes) return true;
            const list = Array.isArray(modes) ? modes : [modes];
            return (damnation ? list.includes("damnation") : list.includes("standard")) || list.includes("both");
        };

        const base = all.filter(modeOk);
        if (!q) return base;

        return base.filter((r) => {
            const title = (n(r?.title) || "").toLowerCase();

            const textArr = Array.isArray(r?.text) ? r.text : [r?.text];
            const textJoined = textArr
                .filter(Boolean)
                .join("\n")
                .toLowerCase();

            return title.includes(q) || textJoined.includes(q);
        });
    }, [all, search, damnation]);

    const toggle = (id) => {
        setOpenMap((m) => {
            const current = m[id] ?? true;
            return {...m, [id]: !current};
        });
    };

    if (loading) {
        return (
            <div className="helpPanel">
                <div className="helpBody">数据加载中…</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="helpPanel">
                <div className="helpBody">
                    数据加载失败：{" "}
                    {String(error.message || error)}
                </div>
            </div>
        );
    }

    if (!filtered.length) {
        return (
            <div className="helpPanel">
                <div className="helpBody">
                    <div className="emptyState">{emptyLabel || "没有符合搜索条件的魔方配方。"}</div>
                </div>
            </div>
        );
    }

    return (<>
        {filtered.map((r, idx) => {
            const id = r.id || `${r.type || "recipe"}-${idx}`;
            const isOpen = openMap[id] ?? true;
            const title = n(r.title) || `配方 ${idx + 1}`;
            const kind = n(r.type);

            return (<div key={id} className="infoPanel" style={{marginBottom: 10}}>
                <div className="infoHeader">
                    <div className="infoTitle" style={{fontSize: 18}}>
                        {title}
                        {kind && (<span
                            style={{
                                fontSize: 14,
                                marginLeft: 8,
                                color: "var(--muted)",
                                textTransform: "none",
                                letterSpacing: 0,
                                fontWeight: 400,
                            }}
                        >
                    · {kind}
                  </span>)}
                    </div>

                    <button
                        type="button"
                        className="infoToggle"
                        onClick={() => toggle(id)}
                    >
                        {isOpen ? "隐藏" : "显示"}
                    </button>
                </div>

                {isOpen && (<div className="infoBody cubeInfoBody">
                    <Markdown text={r.text} onLink={onLink}/>
                </div>)}
            </div>);
        })}
    </>);
}

function TabsBar({
                     tab,
                     setTab,
                     damnationMode,
                     toggleDamnationMode,
                 }) {
    // 全部标签页直接平铺展示，窄屏时由 CSS 自动换行（自适应）
    const allKeys = Object.keys(TABS);

    return (
        <div className="tabsPanel">
            <div className="tabsLeft">
                <div className="tabs">
                    {allKeys.map((key) => (
                        <div
                            key={key}
                            className={"tab" + (tab === key ? " active" : "")}
                            onClick={() => setTab(key)}
                            role="button"
                            tabIndex={0}
                        >
                            {renderTabTitle(key)}
                        </div>
                    ))}
                </div>
            </div>

            <div className="tabsRight">
                <label className="toggleWrap topBarToggle">
                    <span className="toggleLabel">毁灭</span>
                    <div className="toggle">
                        <input
                            type="checkbox"
                            checked={damnationMode}
                            onChange={(e) => toggleDamnationMode(e.target.checked)}
                        />
                        <span className="toggleSlider"/>
                    </div>
                </label>
            </div>
        </div>
    );
}


export default function App() {
    const [damnationMode, setDamnationMode] = React.useState(
        localStorage.getItem("damnation") === "true"
    );
    const weapons = useJson("Weapons.json", damnationMode);
    const armors = useJson("Armors.json", damnationMode);
    const uniques = useJson("Uniques.json", damnationMode);
    const runewords = useJson("Runewords.json", damnationMode);
    const sacreds = useJson("Sacreds.json", damnationMode);
    const cube = useJson("Cube.json", damnationMode);
    const ascendancies = useJson("Ascendancies.json", damnationMode);
    const mapping = useJson("Mapping.json", damnationMode);
    const standard = useJson("Standard.json", damnationMode);
    const siteUpdates = useJson("SiteUpdates.json", damnationMode);
    const affixes = useJson("Affixes.json", damnationMode);
    const skills = useJson("Skills.json", damnationMode);
    const damnation = useJson("Damnation.json", damnationMode);
    const corruptions = useJson("Corruptions.json", damnationMode);
    const fateCards = useJson("FateCards.json", damnationMode);
    const kiln = useJson("Kiln.json", damnationMode);

    const INFO_OPEN_STORAGE_KEY = "the-archivist-v1";
    const searchInputRef = React.useRef(null);
    const skipAutoIndexRef = React.useRef(false);
    const cubeSearchInputRef = React.useRef(null);
    const ascendanciesSearchInputRef = React.useRef(null);
    const kilnSearchInputRef = React.useRef(null);
    const mappingSearchInputRef = React.useRef(null);
    const skillsSearchInputRef = React.useRef(null);
    const changesSearchInputRef = React.useRef(null);
    const skipFilterResetRef = React.useRef(false);
    const [pendingLinkTarget, setPendingLinkTarget] = useState(null);
    const [showTopButton, setShowTopButton] = useState(false);

    const [tab, setTab] = useState("weapons");
    const [dropCalculatorRequest, setDropCalculatorRequest] = useState(null);

    const openDropCalculator = (itemName) => {
        setDropCalculatorRequest({
            item: itemName
        });

        setTab("dropcalc");
    };

    const toggleDamnationMode = (checked) => {
        setDamnationMode(checked);
        localStorage.setItem("damnation", checked ? "true" : "false");
    };

    const [affixSort, setAffixSort] = useState({
        key: "attrs",   // default column
        dir: "asc",     // or "desc" if you prefer
    });

    const [infoOpenByTab, setInfoOpenByTab] = useState(() => ({
        weapons: true, armors: true, uniques: true, runewords: true, sacreds: true,
    }));

    const info = INFO_BY_TAB[tab] || {title: "关于", text: ""};
    const infoOpen = !!infoOpenByTab[tab];

    const dataset = tab === "weapons" ? weapons : tab === "armors" ? armors : tab === "uniques" ?
        uniques : tab === "runewords" ? runewords : tab === "sacreds" ? sacreds : tab === "affixes" ?
            affixes : tab === "skills" ? skills : tab === "corruptions" ? corruptions : tab === "fatecards" ?
                fateCards : weapons; // fallback

    useEffect(() => {
        const onScroll = () => {
            setShowTopButton(window.scrollY > 400);
        };

        window.addEventListener("scroll", onScroll, {passive: true});
        onScroll();

        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    function goToTop() {
        window.scrollTo({top: 0, behavior: "smooth"});
    }

    function toggleRuneFilter(rune) {
        setSelectedRunes((prev) =>
            prev.includes(rune)
                ? prev.filter((x) => x !== rune)
                : [...prev, rune]
        );
    }

    function sacredRunes(s) {
        return sacredIngredients(s).filter((x) =>
            ALL_RUNES.includes(n(x))
        );
    }

    useEffect(() => {
        if (tab !== "cube") {
            setCubeSearch("");
        }
    }, [tab]);

    useEffect(() => {
        if (tab !== "changes") {
            setChangesSearch("");
        }
    }, [tab]);

    useEffect(() => {
        if (tab !== "skills") {
            setSkillsSearch("");
        }
    }, [tab]);

    useEffect(() => {
        try {
            const raw = window.localStorage.getItem(INFO_OPEN_STORAGE_KEY);
            if (!raw) return;

            const parsed = JSON.parse(raw);
            if (parsed && typeof parsed === "object") {
                setInfoOpenByTab((prev) => ({
                    ...prev, ...parsed,
                }));
            }
        } catch (e) {
            console.warn("Failed to read info panel state from storage", e);
        }
    }, []);

    const [search, setSearch] = useState("");
    const [typeValue, setTypeValue] = useState("");
    const [tierValue, setTierValue] = useState("");
    const [socketsValue, setSocketsValue] = useState("");
    const [cubeSearch, setCubeSearch] = useState("");
    const [kilnSearch, setKilnSearch] = useState("");
    const [ascendanciesSearch, setAscendanciesSearch] = useState("");
    const [mappingSearch, setMappingSearch] = useState("");
    const [changesSearch, setChangesSearch] = useState("");
    const [skillsSearch, setSkillsSearch] = useState("");
    const [uberValue, setUberValue] = useState(false);
    const [hellforgedValue, setHellforgedValue] = useState(false);
    const [pendingUniqueCode, setPendingUniqueCode] = useState("");
    const [pendingSacredMatch, setPendingSacredMatch] = useState(null);
    const [highlightOnly, setHighlightOnly] = useState(false);
    const [affixTypeValue, setAffixTypeValue] = useState("");
    const [runeCountValue, setRuneCountValue] = useState("");
    const [selectedRunes, setSelectedRunes] = useState([]);
    const [showRuneFilterBar, setShowRuneFilterBar] = useState(false);

    const items = dataset.data;

    const handleVersionClick = () => {
        setTab("changelog");
    };

    const handleMarkdownAppLink = React.useCallback(({tab: targetTab, name}) => {
        const t = (targetTab || "").toLowerCase();
        const label = (name || "").trim();
        const hasName = !!label;
        const needle = label.toLowerCase();

        // --- Cube Recipes tab ---
        if (t === "cube") {
            setTab("cube");
            if (hasName) {
                setCubeSearch(needle);
                if (cubeSearchInputRef.current) {
                    cubeSearchInputRef.current.focus();
                    cubeSearchInputRef.current.select();
                }
            }
            // if no name → just jump to tab, keep existing cubeSearch as-is
            return;
        }

        // --- SoE changes tab ---
        if (t === "changes") {
            setTab("changes");
            if (hasName) {
                setChangesSearch(needle);
                if (changesSearchInputRef.current) {
                    changesSearchInputRef.current.focus();
                    changesSearchInputRef.current.select();
                }
            }
            return;
        }

        // --- Skills tab ---
        if (t === "skills") {
            setTab("skills");
            if (hasName) {
                setSkillsSearch(needle);
                if (skillsSearchInputRef.current) {
                    skillsSearchInputRef.current.focus();
                    skillsSearchInputRef.current.select();
                }
            }
            // if no name → just jump to tab, keep existing skillsSearch as-is
            return;
        }

        // If there's no name part, just jump to the tab and let normal
        // "tab change" behavior reset filters etc.
        if (!hasName) {
            setTab(t);
            return;
        }

        // Name present → full "go-to-item" behavior
        skipFilterResetRef.current = true;
        skipAutoIndexRef.current = true;

        setTab(t);
        setSearch(needle);
        setPendingLinkTarget({tab: t, name: needle});
    }, []);


    const typeOptions = useMemo(() => {
        if (!items.length) return [];

        if (tab === "weapons") return Array.from(new Set(items.map(weaponTypeForFilter).filter(Boolean))).sort();

        if (tab === "armors") return Array.from(new Set(items.map(armorTypeForFilter).filter(Boolean))).sort();

        if (tab === "uniques") return Array.from(new Set(items.map(uniqueBaseTypeLabel).filter(Boolean))).sort();

        if (tab === "runewords") {
            const all = items.flatMap(runewordAllTypes);
            return Array.from(new Set(all)).sort();
        }

        if (tab === "affixes") {
            const all = items.flatMap(affixTypes);
            return Array.from(new Set(all)).sort();
        }

        if (tab === "corruptions") {
            return [...new Set(items.map((it) => n(it?.displayName)).filter(Boolean))].sort();
        }

        const all = items.flatMap(sacredTypes);
        return Array.from(new Set(all)).sort();
    }, [items, tab]);

    const tierOptions = useMemo(() => {
        const tiers = Array.from(new Set(items.map((it) => n(it?.itemTier)).filter(Boolean)));
        return tiers.sort((a, b) => {
            const an = Number(a), bn = Number(b);
            if (!Number.isNaN(an) && !Number.isNaN(bn)) return an - bn;
            return a.localeCompare(b);
        });
    }, [items]);

    useEffect(() => {
        // If we just switched tabs via an internal Markdown app: link,
        // skip resetting filters once.
        if (skipFilterResetRef.current) {
            skipFilterResetRef.current = false;
            return;
        }

        setSearch("");
        setTypeValue("");
        setTierValue("");
        setSocketsValue("");
        setUberValue(false);
        setHellforgedValue(false);
        setHighlightOnly(false);
        setAffixTypeValue("");
        setRuneCountValue("");
        setSelectedRunes([]);

        setActiveIndex(0);
    }, [tab]);

    const filtered = useMemo(() => {
        const {phrases, terms} = parseSearchQuery(search);

        // 1) Apply all existing filters first
        const base = items.filter((it) => {
            const name = (n(it?.displayName) || n(it?.runewordName) || n(it?.name)).toLowerCase();

            const searchText = buildSearchTextForItem(tab, it);

            for (const p of phrases) {
                if (!searchText.includes(p)) return false;
            }

            for (const t of terms) {
                if (!searchText.includes(t)) return false;
            }

            if (tierValue && n(it?.itemTier) !== tierValue) return false;

            if (tab === "weapons") {
                if (typeValue && weaponTypeForFilter(it) !== typeValue) return false;
                if (socketsValue && Number(it?.maxSockets) !== Number(socketsValue)) return false;

                if (highlightOnly && !isHighlightedItem(it)) {
                    return false;
                }
            }

            if (tab === "armors") {
                if (typeValue && armorTypeForFilter(it) !== typeValue) return false;
                if (socketsValue && Number(it?.maxSockets) !== Number(socketsValue)) return false;

                if (highlightOnly && !isHighlightedItem(it)) {
                    return false;
                }
            }

            if (tab === "uniques") {
                if (typeValue && uniqueBaseTypeLabel(it) !== typeValue) return false;

                if (uberValue && !isUberUnique(it)) {
                    return false;
                }

                if (hellforgedValue && !isHellforged(it)) {
                    return false;
                }

                if (highlightOnly && !isHighlightedItem(it)) {
                    return false;
                }
            }

            if (tab === "runewords") {
                if (typeValue) {
                    const types = runewordAllTypes(it);
                    if (!types.includes(typeValue)) return false;
                }

                if (highlightOnly && !isHighlightedItem(it)) {
                    return false;
                }

                if (runeCountValue) {
                    if (runewordRuneCount(it) !== Number(runeCountValue)) return false;
                }

                if (selectedRunes.length) {
                    const itemRunes = runewordRunes(it).map((r) => r.toLowerCase());

                    const hasAllSelectedRunes = selectedRunes.every((r) => itemRunes.includes(r.toLowerCase()));

                    if (!hasAllSelectedRunes) return false;
                }
            }

            if (tab === "sacreds") {
                if (typeValue) {
                    const types = sacredTypes(it);
                    if (!types.includes(typeValue)) return false;
                }

                if (selectedRunes.length) {
                    const itemRunes = sacredRunes(it).map((r) => r.toLowerCase());

                    const hasAllSelectedRunes = selectedRunes.every((r) =>
                        itemRunes.includes(r.toLowerCase())
                    );

                    if (!hasAllSelectedRunes) return false;
                }
            }

            if (tab === "affixes") {
                if (typeValue) {
                    const types = affixTypes(it);
                    if (!types.includes(typeValue)) return false;
                }

                if (affixTypeValue === "Suffix") {
                    if (!it?.suffix) return false;
                } else if (affixTypeValue === "Prefix") {
                    if (it?.suffix) return false;
                }
            }

            if (tab === "corruptions") {
                if (typeValue && n(it?.displayName) !== typeValue) {
                    return false;
                }
            }

            if (tab === "fatecards") {
                if (typeValue && n(it?.displayName) !== typeValue) {
                    return false;
                }
            }

            return true;
        });

        // 2) Extra sort for Affixes tab: sort by item type, then by name
        if (tab === "affixes") {
            const typeFilterNorm = typeValue ? typeValue.toLowerCase() : "";

            const sorted = [...base].sort((a, b) => {
                // Build a textual key from all item types (e.g. "Amulets, Rings")
                const aTypes = affixTypes(a);
                const bTypes = affixTypes(b);

                const aKeyAll = aTypes.join(", ").toLowerCase();
                const bKeyAll = bTypes.join(", ").toLowerCase();

                // If a specific type is selected, you could prioritize it here,
                // but since the global filter already ensures it’s present,
                // we just sort alphabetically by the combined type string.
                const typeCmp = aKeyAll.localeCompare(bKeyAll);
                if (typeCmp !== 0) return typeCmp;

                // Tie-break by name for stable ordering
                const aName = (n(a?.name) || n(a?.displayName) || "").toLowerCase();
                const bName = (n(b?.name) || n(b?.displayName) || "").toLowerCase();

                return aName.localeCompare(bName);
            });

            return sorted;
        }

        // 3) Other tabs: just return filtered list as before
        return base;
    }, [items, tab, search, tierValue, typeValue, socketsValue, uberValue, hellforgedValue, highlightOnly, affixTypeValue, runeCountValue, selectedRunes]);

    useEffect(() => {
        if (!pendingLinkTarget) return;
        if (tab !== pendingLinkTarget.tab) return;
        if (dataset.loading) return;

        const targetName = pendingLinkTarget.name;

        const idx = filtered.findIndex((it) => {
            const nm = (n(it?.displayName) || n(it?.runewordName) || n(it?.name)).toLowerCase();

            return nm === targetName;
        });

        if (idx >= 0) {
            setActiveIndex(idx);
        } else if (filtered.length) {
            setActiveIndex(0);
        }

        setPendingLinkTarget(null);
    }, [pendingLinkTarget, tab, dataset.loading, filtered]);

    const [activeIndex, setActiveIndex] = useState(0);

    useEffect(() => {
        if (skipAutoIndexRef.current) {

            skipAutoIndexRef.current = false;
            return;
        }

        setActiveIndex(0);
    }, [tab, search, tierValue, typeValue, socketsValue, uberValue, highlightOnly]);

    useEffect(() => {
        if (!pendingUniqueCode) return;
        if (tab !== "uniques") return;
        if (dataset.loading) return;

        const idx = dataset.data.findIndex((it) => n(it?.code) === pendingUniqueCode);
        if (idx >= 0) setActiveIndex(idx);

        setPendingUniqueCode("");
    }, [pendingUniqueCode, tab, dataset.loading, dataset.data]);

    useEffect(() => {
        if (!pendingSacredMatch) return;
        if (tab !== "sacreds") return;
        if (sacreds.loading) return;

        const {name, types} = pendingSacredMatch;

        const all = sacreds.data;
        const idx = all.findIndex((s) => {
            const sName = n(s?.displayName).toLowerCase();
            if (name && sName !== name) return false;

            const sTypes = sacredTypes(s).map((t) => t.toLowerCase());
            for (const t of types) {
                if (!sTypes.includes(t)) return false;
            }
            return true;
        });

        if (idx >= 0) setActiveIndex(idx);

        setPendingSacredMatch(null);
    }, [pendingSacredMatch, tab, sacreds.loading, sacreds.data, setActiveIndex]);

    const activeItem = filtered[activeIndex] ?? null;

    function jumpToSacred(sacredName, itemTypes) {
        const name = n(sacredName);
        const types = Array.isArray(itemTypes) ? itemTypes.map((t) => typeZh(n(t)).toLowerCase()).filter(Boolean) : [];

        if (!name && !types.length) return;

        skipAutoIndexRef.current = true;

        setTab("sacreds");

        setSearch("");
        setTypeValue("");
        setTierValue("");
        setSocketsValue("");
        setUberValue(false);
        setHellforgedValue(false);
        setHighlightOnly(false);

        setPendingSacredMatch({
            name: name.toLowerCase(), types,
        });
    }

    function jumpToCode(code) {
        const c = n(code);
        if (!c) return;

        skipAutoIndexRef.current = true;

        setSearch("");
        setTypeValue("");
        setTierValue("");
        setSocketsValue("");
        setUberValue(false);
        setHellforgedValue(false);
        setHighlightOnly(false);

        const all = dataset.data;
        const idx = all.findIndex((it) => n(it?.code) === c);
        if (idx >= 0) setActiveIndex(idx);
    }

    function jumpToUnique(code) {
        const c = n(code);
        if (!c) return;

        skipAutoIndexRef.current = true;

        setTab("uniques");

        setSearch("");
        setTypeValue("");
        setTierValue("");
        setSocketsValue("");
        setUberValue(false);
        setHellforgedValue(false);
        setHighlightOnly(false);
        setPendingUniqueCode(c);
    }

    useEffect(() => {
        function onKeyDown(e) {

            if (e.key === "Escape") {
                if (tab === "cube") {
                    cubeSearchInputRef.current?.blur();
                } else if (tab === "changes") {
                    changesSearchInputRef.current?.blur();
                } else {
                    searchInputRef.current?.blur();
                }
            }

            if (e.ctrlKey && e.key === "f") {
                e.preventDefault();
                if (tab === "cube") {
                    if (cubeSearchInputRef.current) {
                        cubeSearchInputRef.current.focus();
                        cubeSearchInputRef.current.select();
                    }
                } else if (tab === "changes") {
                    if (changesSearchInputRef.current) {
                        changesSearchInputRef.current.focus();
                        changesSearchInputRef.current.select();
                    }
                } else {
                    if (searchInputRef.current) {
                        searchInputRef.current.focus();
                        searchInputRef.current.select();
                    }
                }
            }

            const tag = e.target?.tagName;
            if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;

            if (e.key === "ArrowDown") {
                e.preventDefault();
                setActiveIndex((i) => Math.min(i + 1, Math.max(filtered.length - 1, 0)));
                return;
            }

            if (e.key === "ArrowUp") {
                e.preventDefault();
                setActiveIndex((i) => Math.max(i - 1, 0));
                return;
            }
        }

        window.addEventListener("keydown", onKeyDown);
        return () => window.removeEventListener("keydown", onKeyDown);
    }, [tab, filtered.length]);


    const subLabel = useMemo(() => {
        if (tab === "weapons") return (it) => weaponTypeLabel(it);
        if (tab === "armors") return (it) => armorTypeLabel(it);
        if (tab === "uniques") {
            return (it) => {
                const bt = uniqueBaseTypeLabelPretty(it) || uniqueBaseTypeLabel(it);
                const base = uniqueBase(it);
                const bn = n(base?.displayName) || n(base?.name);
                return bn ? `${bt}` : bt;
            };
        }
        if (tab === "sacreds") {
            return (it) => {
                const types = sacredTypes(it);
                return types.length ? types.join(" / ") : "圣化";
            };
        }

        if (tab === "fatecards") {
            return () => {
                return "命运卡牌";
            };
        }

        return (it) => {
            const types = runewordAllTypes(it);
            return types.length ? types.join(" / ") : "符文之语";
        };
    }, [tab]);

    const tinyLabel = useMemo(() => {
        if (tab === "weapons") {
            return (it) => {
                const parts = [];
                const dmg = weaponDmgLines(it);
                if (dmg.length) parts.push(`${dmg[0].k.replace(" 伤害", "")}：${dmg[0].v}`);
                if (nz(it?.requiredLevel)) parts.push(`需求等级 ${n(it?.requiredLevel)}`);
                if (nz(it?.requiredStrength)) parts.push(`力量 ${n(it?.requiredStrength)}`);
                if (nz(it?.requiredDexterity)) parts.push(`敏捷 ${n(it?.requiredDexterity)}`);
                if (nz(it?.maxSockets)) parts.push(`孔数 ${n(it?.maxSockets)}`);
                if (has(it?.itemTier)) parts.push(`阶位 ${n(it?.itemTier)}`);
                return parts.join(" • ");
            };
        }

        if (tab === "armors") {
            return (it) => {
                const parts = [];
                const def = armorDefenseLine(it);
                if (has(def)) parts.push(`防御：${def}`);
                if (nz(it?.block)) parts.push(`格挡 ${n(it?.block)}%`);
                if (nz(it?.maxSockets)) parts.push(`孔数 ${n(it?.maxSockets)}`);
                if (nz(it?.requiredLevel)) parts.push(`需求等级 ${n(it?.requiredLevel)}`);
                if (nz(it?.requiredStrength)) parts.push(`力量 ${n(it?.requiredStrength)}`);
                if (has(it?.itemTier)) parts.push(`阶位 ${n(it?.itemTier)}`);
                return parts.join(" • ");
            };
        }

        if (tab === "runewords") {
            return (it) => {
                const runes = [n(it?.firstRune), n(it?.secondRune), n(it?.thirdRune), n(it?.fourthRune), n(it?.fifthRune), n(it?.sixthRune),].filter(Boolean);

                const count = runes.length ? `${runes.length} 个符文` : "";
                const props = Array.isArray(it?.displayProperties) ? it.displayProperties.filter(Boolean).length : 0;
                return [count, props ? `${props} 条属性` : ""].filter(Boolean).join(" • ");
            };
        }

        if (tab === "sacreds") {
            return (it) => {
                const ing = sacredIngredients(it);
                const map = it?.propertiesByItemType && typeof it.propertiesByItemType === "object" ? it.propertiesByItemType : {};
                const typeCount = Object.keys(map).length;
                return [ing.length ? `${ing.length} 个材料` : "", typeCount ? `${typeCount} 种类型变体` : "",].filter(Boolean).join(" • ");
            };
        }

        return (it) => {
            const parts = [];
            if (nz(it?.requiredLevel)) parts.push(`需求等级 ${n(it?.requiredLevel)}`);
            if (has(it?.level)) parts.push(`品质等级 ${n(it?.level)}`);
            if (has(it?.itemTier)) parts.push(`阶位 ${n(it?.itemTier)}`);
            return parts.join(" • ");
        };
    }, [tab]);

    const countLabel = dataset.loading ? "加载中…" : dataset.error ? `错误：${dataset.error.message}` : `${filtered.length} 件物品`;
    const showSockets = tab === "weapons" || tab === "armors";
    const typePlaceholder = tab === "uniques" ? "全部基底类型" : (tab === "runewords" || tab === "sacreds") ? "全部物品类型" : "全部类型";

    return (<div className="appRoot">
        <div className="wrap">
            <TabsBar tab={tab} setTab={setTab} damnationMode={damnationMode} toggleDamnationMode={toggleDamnationMode}/>

            {tab === "help" ? (<HelpPanel/>) : tab === "calculators" ? (<>
                    <div className="calcWide">
                        <div className="panels">
                            <AuraEffectCalculator/>
                            <CurseEffectCalculator/>
                        </div>
                    </div>
                </>
            ) : tab === "dropcalc" ? (
                <DropCalculatorPanel
                    request={dropCalculatorRequest}
                    clearRequest={() => setDropCalculatorRequest(null)}
                    damnationMode={damnationMode}
                />
            ) : tab === "kiln" ? (<>
                <div className="filtersStack">
                    <div className="filtersPanel">
                        <input
                            type="text"
                            ref={kilnSearchInputRef}
                            value={kilnSearch}
                            onChange={(e) => setKilnSearch(e.target.value)}
                            className="searchBar"
                            placeholder="搜索…"
                        />
                    </div>
                </div>
                <StaticDataPanel
                    data={kiln.data}
                    loading={kiln.loading}
                    error={kiln.error}
                    search={kilnSearch}
                    onLink={handleMarkdownAppLink}
                />
            </>) : tab === "cube" ? (<>
                <div className="filtersStack">
                    <div className="filtersPanel">
                        <input
                            type="text"
                            ref={cubeSearchInputRef}
                            value={cubeSearch}
                            onChange={(e) => setCubeSearch(e.target.value)}
                            className="searchBar"
                            placeholder="搜索魔方配方…"
                        />
                    </div>
                </div>
                <StaticDataPanel
                    data={cube.data}
                    loading={cube.loading}
                    error={cube.error}
                    search={cubeSearch}
                    onLink={handleMarkdownAppLink}
                    damnation={damnationMode}
                />
            </>) : tab === "ascendancies" ? (<>
                <div className="filtersStack">
                    <div className="filtersPanel">
                        <input
                            type="text"
                            ref={ascendanciesSearchInputRef}
                            value={ascendanciesSearch}
                            onChange={(e) => setAscendanciesSearch(e.target.value)}
                            className="searchBar"
                            placeholder="搜索…"
                        />
                    </div>
                </div>
                <StaticDataPanel
                    data={ascendancies.data}
                    loading={ascendancies.loading}
                    error={ascendancies.error}
                    search={ascendanciesSearch}
                    onLink={handleMarkdownAppLink}
                />
            </>) : tab === "mapping" ? (<>
                <div className="filtersStack">
                    <div className="filtersPanel">
                        <input
                            type="text"
                            ref={mappingSearchInputRef}
                            value={mappingSearch}
                            onChange={(e) => setMappingSearch(e.target.value)}
                            className="searchBar"
                            placeholder="搜索…"
                        />
                    </div>
                </div>
                <StaticDataPanel
                    data={mapping.data}
                    loading={mapping.loading}
                    error={mapping.error}
                    search={mappingSearch}
                    onLink={handleMarkdownAppLink}
                />
            </>) : tab === "corruptions" ? (<>
                <div className="filtersStack">
                    <FiltersBar
                        search={search}
                        setSearch={setSearch}
                        typeValue={typeValue}
                        setTypeValue={setTypeValue}
                        tierValue={tierValue}
                        setTierValue={setTierValue}
                        socketsValue={socketsValue}
                        setSocketsValue={setSocketsValue}
                        uberValue={uberValue}
                        setUberValue={setUberValue}
                        hellforgedValue={hellforgedValue}
                        setHellforgedValue={setHellforgedValue}
                        types={typeOptions}
                        tiers={tierOptions}
                        showSockets={showSockets}
                        showUber={tab === "uniques"}
                        typePlaceholder={typePlaceholder}
                        searchInputRef={searchInputRef}
                        showTier={tab !== "runewords" && tab !== "sacreds" && tab !== "affixes" && tab !== "corruptions" && tab !== "fatecards"}
                        showHighlight={tab === "uniques" || tab === "runewords" || tab === "weapons" || tab === "armors"}
                        highlightOnly={highlightOnly}
                        setHighlightOnly={setHighlightOnly}
                        showAffixType={tab === "affixes"}
                        affixTypeValue={affixTypeValue}
                        setAffixTypeValue={setAffixTypeValue}
                        showHellforged={tab === "uniques"}
                    />
                </div>
                <div className="affixPanel corruptionsPanel">
                    <CorruptionsTable items={filtered}/>
                </div>
            </>) : tab === "skills" ? (<>
                <div className="filtersStack">
                    <div className="filtersPanel">
                        <input
                            type="text"
                            ref={skillsSearchInputRef}
                            value={skillsSearch}
                            onChange={(e) => setSkillsSearch(e.target.value)}
                            className="searchBar"
                            placeholder="搜索技能…"
                        />
                    </div>
                </div>
                <StaticDataPanel
                    data={skills.data}
                    loading={skills.loading}
                    error={skills.error}
                    search={skillsSearch}
                    onLink={handleMarkdownAppLink}
                />
            </>) : tab === "builds" ? (
                <BuildsPanel/>
            ) : tab === "affixes" ? (<>
                <div className="filtersStack">
                    <FiltersBar
                        search={search}
                        setSearch={setSearch}
                        typeValue={typeValue}
                        setTypeValue={setTypeValue}
                        tierValue={tierValue}
                        setTierValue={setTierValue}
                        socketsValue={socketsValue}
                        setSocketsValue={setSocketsValue}
                        uberValue={uberValue}
                        setUberValue={setUberValue}
                        hellforgedValue={hellforgedValue}
                        setHellforgedValue={setHellforgedValue}
                        types={typeOptions}
                        tiers={tierOptions}
                        showSockets={showSockets}
                        showUber={tab === "uniques"}
                        typePlaceholder={typePlaceholder}
                        searchInputRef={searchInputRef}
                        showTier={tab !== "runewords" && tab !== "sacreds" && tab !== "affixes" && tab !== "fatecards"}
                        showHighlight={tab === "uniques" || tab === "runewords" || tab === "weapons" || tab === "armors"}
                        highlightOnly={highlightOnly}
                        setHighlightOnly={setHighlightOnly}
                        showAffixType={tab === "affixes"}
                        affixTypeValue={affixTypeValue}
                        setAffixTypeValue={setAffixTypeValue}
                        showHellforged={tab === "uniques"}
                    />
                    <InfoPanel
                        title={info.title}
                        markdownText={info.text}
                        isOpen={infoOpen}
                        onLink={handleMarkdownAppLink}
                        onToggle={() => setInfoOpenByTab((prev) => {
                            const next = {...prev, [tab]: !prev[tab]};
                            try {
                                window.localStorage.setItem(INFO_OPEN_STORAGE_KEY, JSON.stringify(next));
                            } catch (e) {
                                console.warn("Failed to save info panel state", e);
                            }
                            return next;
                        })}
                    />
                </div>
                <AffixesPanel
                    data={filtered}
                    loading={affixes.loading}
                    error={affixes.error}
                    sort={affixSort}
                    onChangeSort={setAffixSort}
                />
            </>) : tab === "damnation" ? (<>
                <StaticDataPanel
                    data={damnation.data}
                    loading={damnation.loading}
                    error={damnation.error}
                    onLink={handleMarkdownAppLink}
                />
            </>) : tab === "changes" ? (<>
                <div className="filtersStack">
                    <div className="filtersPanel">
                        <input
                            type="text"
                            ref={changesSearchInputRef}
                            value={changesSearch}
                            onChange={(e) => setChangesSearch(e.target.value)}
                            className="searchBar"
                            placeholder="搜索流放圣域变更…"
                        />
                    </div>
                </div>
                <StaticDataPanel
                    data={standard.data}
                    loading={standard.loading}
                    error={standard.error}
                    search={changesSearch}
                    onLink={handleMarkdownAppLink}
                />
            </>) : tab === "changelog" ? (<>
                <StaticDataPanel
                    data={siteUpdates.data}
                    loading={siteUpdates.loading}
                    error={siteUpdates.error}
                    emptyLabel="暂无更新记录。"
                />
            </>) : (<>
                <div className="filtersStack">
                    <FiltersBar
                        search={search}
                        setSearch={setSearch}
                        typeValue={typeValue}
                        setTypeValue={setTypeValue}
                        tierValue={tierValue}
                        setTierValue={setTierValue}
                        socketsValue={socketsValue}
                        setSocketsValue={setSocketsValue}
                        uberValue={uberValue}
                        setUberValue={setUberValue}
                        hellforgedValue={hellforgedValue}
                        setHellforgedValue={setHellforgedValue}
                        types={typeOptions}
                        tiers={tierOptions}
                        showSockets={showSockets}
                        showUber={tab === "uniques"}
                        showHellforged={tab === "uniques"}
                        typePlaceholder={typePlaceholder}
                        searchInputRef={searchInputRef}
                        showType={tab !== "fatecards"}
                        showTier={tab !== "runewords" && tab !== "sacreds" && tab !== "fatecards"}
                        showHighlight={tab === "uniques" || tab === "runewords" || tab === "weapons" || tab === "armors"}
                        highlightOnly={highlightOnly}
                        setHighlightOnly={setHighlightOnly}
                        showRuneCount={tab === "runewords"}
                        runeCountValue={runeCountValue}
                        setRuneCountValue={setRuneCountValue}
                    />
                    {(tab === "runewords" || tab === "sacreds") && (
                        <div className="runeFilterPanel">
                            <div className="runeFilterHeader">
                                <div className="runeFilterTitle">
                                    符文筛选
                                    {selectedRunes.length ? ` (${selectedRunes.length})` : ""}
                                </div>

                                <div className="runeFilterActions">
                                    {selectedRunes.length > 0 && (
                                        <button
                                            type="button"
                                            className="btn runeFilterClear"
                                            onClick={() => setSelectedRunes([])}
                                        >
                                            清除
                                        </button>
                                    )}

                                    <button
                                        type="button"
                                        className="infoToggle"
                                        onClick={() => setShowRuneFilterBar((v) => !v)}
                                    >
                                        {showRuneFilterBar ? "隐藏" : "显示"}
                                    </button>
                                </div>
                            </div>

                            {showRuneFilterBar && (
                                <div className="runeGrid">
                                    {ALL_RUNES.map((rune) => {
                                        const active = selectedRunes.includes(rune);

                                        return (
                                            <button
                                                key={rune}
                                                type="button"
                                                className={`runeChip${active ? " active" : ""}`}
                                                onClick={() => toggleRuneFilter(rune)}
                                            >
                                                <img src={RuneIcon} alt="" className="runeChipIcon"/>
                                                <span>{runeChipLabel(rune)}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                    <InfoPanel
                        title={info.title}
                        markdownText={info.text}
                        isOpen={infoOpen}
                        onLink={handleMarkdownAppLink}
                        onToggle={() => setInfoOpenByTab((prev) => {
                            const next = {...prev, [tab]: !prev[tab]};
                            try {
                                window.localStorage.setItem(INFO_OPEN_STORAGE_KEY, JSON.stringify(next));
                            } catch (e) {
                                console.warn("Failed to save info panel state", e);
                            }
                            return next;
                        })}
                    />
                </div>

                <ListPanel
                    tab={tab}
                    title={renderTabTitle(tab)}
                    countLabel={countLabel}
                    items={filtered}
                    activeIndex={activeIndex}
                    setActiveIndex={setActiveIndex}
                    subLabel={subLabel}
                    tinyLabel={tinyLabel}
                />

                <TooltipShell>
                    {tab === "weapons" && (<WeaponTooltip
                        w={activeItem}
                        onGoCode={jumpToCode}
                        onGoUnique={jumpToUnique}
                    />)}

                    {tab === "runewords" && <RunewordTooltip rw={activeItem} onGoSacred={jumpToSacred}
                                                             onLink={handleMarkdownAppLink}/>}

                    {tab === "armors" && (<ArmorTooltip
                        a={activeItem}
                        onGoCode={jumpToCode}
                        onGoUnique={jumpToUnique}
                    />)}
                    {tab === "uniques" && <UniqueTooltip u={activeItem} onLink={handleMarkdownAppLink}
                                                         openDropCalculator={openDropCalculator}/>}
                    {tab === "sacreds" && <SacredTooltip s={activeItem} onLink={handleMarkdownAppLink}/>}
                    {tab === "fatecards" && (<FateCardTooltip card={activeItem}/>
                    )}
                </TooltipShell>
            </>)}
        </div>

        <footer className="footer">
            <div className="footerInner">
                    <span className="footerLeft">作者 <a className="footerGitLink" target="_blank"
                                                       href="https://github.com/Lukaszpg">MindH1ve</a></span>

                <a
                    className="footerRight"
                    href={LATEST_RELEASE}
                    target="_blank"
                    style={{cursor: "pointer"}}
                >模组版本：v{GAME_VERSION}</a>

                <span
                    className="footerRight"
                    onClick={handleVersionClick}
                    style={{cursor: "pointer"}}
                >资料库版本：v{APP_VERSION}</span>
            </div>
        </footer>

        {showTopButton && (
            <button
                type="button"
                className="goTopBtn"
                onClick={goToTop}
                aria-label="返回顶部"
                title="返回顶部"
            >
                ↑
            </button>
        )}
    </div>);
}