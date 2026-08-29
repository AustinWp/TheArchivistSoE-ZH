# -*- coding: utf-8 -*-
"""圣化宝珠页面数据重建（以官方 CubeMain 创建配方为唯一来源）。

- 输入/底材/名称：来自 standard-mode CubeMain.txt 的 86 条创建配方行
- 名称：官方串表（圣化宝珠·X）；同名不同部位加括号区分（如 圣化宝珠·梦境（头盔））
- 属性（propertiesByItemType / itemTypesDisplayNames）：沿用旧 Sacreds.json（已中文化），按符文+底材精确对齐后保留

用法: python3 tools/rebuild_sacreds.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

RUNE = {'r01': 'El', 'r02': 'Eld', 'r03': 'Tir', 'r04': 'Nef', 'r05': 'Eth', 'r06': 'Ith',
        'r07': 'Tal', 'r08': 'Ral', 'r09': 'Ort', 'r10': 'Thul', 'r11': 'Amn', 'r12': 'Sol',
        'r13': 'Shael', 'r14': 'Dol', 'r15': 'Hel', 'r16': 'Io', 'r17': 'Lum', 'r18': 'Ko',
        'r19': 'Fal', 'r20': 'Lem', 'r21': 'Pul', 'r22': 'Um', 'r23': 'Mal', 'r24': 'Ist',
        'r25': 'Gul', 'r26': 'Vex', 'r27': 'Ohm', 'r28': 'Lo', 'r29': 'Sur', 'r30': 'Ber',
        'r31': 'Jah', 'r32': 'Cham', 'r33': 'Zod'}
SLOTZH = {'helm': '头盔', 'tors': '护甲', 'shld': '任意盾牌', 'weap': '武器'}
SECTIONS = ['SACRED ORBS - HELMS', 'SACRED ORB - BOOTS', 'SACRED ORBS - CHESTS',
            'SACRED ORBS - SHIELDS', 'SACRED ORBS - WEAPONS', 'SACRED ORB - QUIVERS']


def main():
    zh = json.load(open(os.path.join(ROOT, 'public', 'data', 'official_zh.json'), encoding='utf-8'))['names']
    recs = json.load(open(os.path.join(HERE, 'generated', 'cube_recipes.json'), encoding='utf-8'))['recipes']['standard']
    old = json.load(open(os.path.join(ROOT, 'public', 'data', 'Sacreds.json'), encoding='utf-8'))

    # 官方 86 条：sr code -> {runes, slot, zh_name}
    rows = []
    for r in recs:
        if r['section'] not in SECTIONS:
            continue
        runes, slot = [], None
        for i in r['inputs']:
            if i['code'] == 'sror':
                continue
            if i['code'] in SLOTZH:
                slot = SLOTZH[i['code']]
            elif i['code'][:3] in RUNE:
                runes.append((RUNE[i['code'][:3]], i['qty']))
        sr = r['output']['code']
        rows.append({'sr': sr, 'runes': tuple(runes), 'slot': slot,
                     'zh': zh.get(sr, '').replace('圣化宝珠·', '') or sr})

    # 官方名重复（多部位）时加部位区分
    from collections import Counter
    cnt = Counter(x['zh'] for x in rows)
    for x in rows:
        x['name'] = f"圣化宝珠·{x['zh']}"
        if cnt[x['zh']] > 1:
            x['name'] += f"（{x['slot']}）" if x['slot'] else ""

    # 旧数据按（符文序列, 底材）建立索引，保留属性
    def old_key(s):
        runes, slot = [], None
        for k in ('firstInputDisplayName', 'secondInputDisplayName', 'thirdInputDisplayName',
                  'fourthInputDisplayName', 'fifthInputDisplayName', 'sixthInputDisplayName'):
            v = s.get(k)
            if not v:
                continue
            if v in ('头盔', '护甲', '任意盾牌', '武器', '任意盔甲'):
                slot = v
            else:
                runes.append((v, s.get(k.replace('DisplayName', 'Quantity'))))
        return tuple(runes), slot

    old_by_key = {}
    orphan = []
    for s in old:
        k = old_key(s)
        if k in old_by_key:
            orphan.append((k, s['displayName']))
        else:
            old_by_key[k] = s

    out = []
    unmatched = []
    for x in rows:
        hit = old_by_key.get((x['runes'], x['slot']))
        if hit is None:
            # 底材未标注或顺序变化时兜底：只按符文
            hits = [(k, v) for (k, slot), v in old_by_key.items() if k == x['runes']]
            hit = hits[0][1] if len(hits) == 1 else None
        if hit is None:
            unmatched.append((x['sr'], x['name'], x['runes'], x['slot']))
            out.append({
                'displayName': x['name'],
                'itemTypesDisplayNames': [x['slot']] if x['slot'] else [],
                'propertiesByItemType': {},
            })
        else:
            out.append({
                'displayName': x['name'],
                'itemTypesDisplayNames': hit.get('itemTypesDisplayNames') or ([x['slot']] if x['slot'] else []),
                'propertiesByItemType': hit.get('propertiesByItemType') or {},
            })
        item = out[-1]
        inputs = list(x['runes'])
        if x['slot']:
            inputs.append((x['slot'], 1))
        for idx, (nm, q) in enumerate(inputs[:6], start=1):
            item[f'{["first", "second", "third", "fourth", "fifth", "sixth"][idx-1]}InputDisplayName'] = nm
            item[f'{["first", "second", "third", "fourth", "fifth", "sixth"][idx-1]}InputQuantity'] = q

    json.dump(out, open(os.path.join(ROOT, 'public', 'data', 'Sacreds.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print(f"重建 {len(out)} 条；未能对齐旧属性的条目：{len(unmatched)}")
    for u in unmatched:
        print('  UNMATCHED', u[0], u[1], u[2], u[3])
    if orphan:
        print(f"旧数据重复键丢弃 {len(orphan)} 条：", orphan[:5])


if __name__ == '__main__':
    main()
