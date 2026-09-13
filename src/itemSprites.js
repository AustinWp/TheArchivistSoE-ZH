// 物品贴图索引：由 App 在渲染期写入（见 App.jsx 里 setItemSpriteMap 的调用），
// 供各处把物品 code 转成贴图 URL。抽成独立模块是为了让构筑面板等其他组件也能用。

let ITEM_SPRITE_MAP = {};

export function setItemSpriteMap(map) {
    ITEM_SPRITE_MAP = map && typeof map === "object" ? map : {};
}

export function itemSpriteUrl(code, kind) {
    const key = String(code ?? "").trim().toLowerCase();
    if (!key) return null;

    const rec = ITEM_SPRITE_MAP[key];
    if (!rec) return null;

    const name = (kind && rec[kind]) || rec.b;
    if (!name) return null;

    return `${import.meta.env.BASE_URL}item-images/${name}.png`;
}
