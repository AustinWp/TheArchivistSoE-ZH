# PD2 流放圣域（Sanctuary of Exile）中文资料库

[The Archivist](https://lukaszpg.github.io/TheArchivistSoE/) 的简体中文复刻版 —— Project Diablo 2《流放圣域（Sanctuary of Exile）》物品资料库。

## 特性

- 完全复刻原站样式（Diablo 风格暗色主题、ExocetBlizzard 字体、物品图标、悬浮提示）
- 全部界面与数据中文化：国服SOL第一赛季 / 武器 / 护甲 / 暗金装备 / 符文之语 / 词缀 / 圣化 / 腐化 / 命运卡牌 / 技能 / 魔方配方 / 飞升 / 地图 / 标准模式 / 毁灭模式 / 炼狱熔炉 / 更新日志
- **国服 S1 赛季页**：收录《PD2-SOE S1 Patch Notes Final》全文，并逐条与国服代码交叉验证（见 `docs/reference/s1-verification.md`）
- **⛔ 国服不支持标记**：国服代码中不存在或未接入的功能 / 公式（如随机狱铸配方、范围公式对狂犬病与火魔圣火不生效等）在页面上以红色徽标标出
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

- 原始来源：游戏模组仓库 [`wdjwxh/PD2-Sanctuary-of-Exile`](https://github.com/wdjwxh/PD2-Sanctuary-of-Exile) 的 `SOECN` 分支（commit `9b24eb72`，2026-09-11，国服 S1 正式服版本；上一基准 `374d8971`）
- 数据流与重生成方法见 [`docs/reference/README.md`](docs/reference/README.md)
- 校验：`python3 tools/verify_cube_claims.py`（41 条事实断言 + 页面表格自检，含国服 S1 拆解分档 / 随机狱铸配方已删除）
- 重生成全部数据：`python3 tools/refresh_data.py`（解析 → 校验 → 生成页面数据 → 构建）
- 待游戏内验证的疑点：`tools/generated/pending_verification.md`（生成物，运行 `python3 tools/parse_cubemain.py` 后生成）
- 国服 S1 更新说明全文：`docs/reference/s1-patch-notes.md`；交叉验证结论：`docs/reference/s1-verification.md`

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
│   ├── refresh_data.py            一键刷新（解析/校验/生成/构建）
│   └── generated/             生成物（gitignore；含报告与对照表）
└── src/                      站点源码
```

## 部署

推送到 GitHub 仓库的 `main` 分支后，`.github/workflows/deploy.yml` 会自动构建并发布到 GitHub Pages。

线上地址：`https://<用户名>.github.io/TheArchivistSoE-ZH/`
