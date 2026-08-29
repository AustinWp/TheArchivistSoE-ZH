// ============================================================================
// 核心 BD 构筑（Builds）面板
// 按职业整理的核心 BD 构筑库：职业选择 → 构筑卡片 → 构筑详情（分节渲染）
// 数据来源：public/data/Builds.json
// ============================================================================
import React, {useEffect, useState} from "react";

import BowIcon from "./icons/bow.svg";
import ClawsIcon from "./icons/claws.svg";
import AxeIcon from "./icons/axe.svg";
import HelmetIcon from "./icons/helmet.svg";
import WandIcon from "./icons/wand.svg";
import ScepterIcon from "./icons/scepter.svg";
import SorceressOrbIcon from "./icons/orb.svg";

// 职业图标映射（沿用站内武器/护甲图标）
const CLASS_ICON_MAP = {
    bow: BowIcon,
    claws: ClawsIcon,
    axe: AxeIcon,
    pelt: HelmetIcon,
    wand: WandIcon,
    scepter: ScepterIcon,
    orb: SorceressOrbIcon,
};

const IMG_BASE = `${import.meta.env.BASE_URL}data/builds/`;

// ---- 行内简易 Markdown：**加粗**、`代码` ----
function InlineMd({text}) {
    const parts = String(text ?? "").split(/(\*\*[^*]+\*\*|`[^`]*`)/g);
    return (
        <>
            {parts.map((part, i) => {
                if (part.startsWith("**") && part.endsWith("**")) {
                    return <strong key={i} className="bdStrong">{part.slice(2, -2)}</strong>;
                }
                if (part.startsWith("`") && part.endsWith("`")) {
                    return <code key={i} className="bdCode">{part.slice(1, -1)}</code>;
                }
                return <React.Fragment key={i}>{part}</React.Fragment>;
            })}
        </>
    );
}

function MultiLine({text}) {
    return String(text ?? "")
        .split("\n")
        .map((line, i, arr) => (
            <React.Fragment key={i}>
                <InlineMd text={line}/>
                {i < arr.length - 1 ? <br/> : null}
            </React.Fragment>
        ));
}

// ---- 截图（点击放大） ----
function BuildFigure({item, onOpen}) {
    const src = IMG_BASE + item.src;
    return (
        <figure className="bdFigure">
            <div className="bdFigureImg" onClick={() => onOpen(item)}>
                <img src={src} alt={item.caption || ""} loading="lazy"/>
            </div>
            {item.caption ? <figcaption className="bdFigCaption">{item.caption}</figcaption> : null}
        </figure>
    );
}

// ---- 分块渲染器 ----
function SectionBlock({block, onOpenImage}) {
    switch (block.type) {
        case "h2":
            return <h2 className="bdH2"><span className="bdH2Mark">◆</span>{block.text}</h2>;
        case "sub":
            return <h3 className="bdSub">{block.text}</h3>;
        case "p":
            return <p className="bdP"><InlineMd text={block.text}/></p>;
        case "ul":
            return (
                <ul className="bdUl">
                    {block.items.map((it, i) => (
                        <li key={i} className="bdLi"><span className="bdLiMark">▸</span><span><InlineMd text={it}/></span></li>
                    ))}
                </ul>
            );
        case "note":
            return (
                <div className="bdNote">
                    <div className="bdNoteTag">专家注</div>
                    <div className="bdNoteBody"><MultiLine text={block.text}/></div>
                </div>
            );
        case "warn":
            return (
                <div className="bdWarn">
                    <div className="bdWarnTag">⚠ 注意</div>
                    <div className="bdWarnBody"><MultiLine text={block.text}/></div>
                </div>
            );
        case "kv":
            return (
                <div className="bdKv">
                    {block.rows.map(([k, v], i) => (
                        <div key={i} className="bdKvRow">
                            <div className="bdKvKey"><InlineMd text={k}/></div>
                            <div className="bdKvVal"><MultiLine text={v}/></div>
                        </div>
                    ))}
                </div>
            );
        case "formula":
            return (
                <div className="bdFormula">
                    <div className="bdFormulaTitle">📐 {block.title}</div>
                    <div className="bdFormulaChain">
                        {block.parts.map((p, i) => (
                            <React.Fragment key={i}>
                                {i > 0 ? <span className="bdTimes">×</span> : null}
                                <span className="bdChip">{p}</span>
                            </React.Fragment>
                        ))}
                    </div>
                    <div className="bdFormulaNote">多层乘法叠乘 → 造价越高，收益越陡</div>
                </div>
            );
        case "table":
            return (
                <div className="bdTableWrap">
                    {block.caption ? <div className="bdTableCaption">{block.caption}</div> : null}
                    <table className="bdTable">
                        <thead>
                        <tr>
                            {block.headers.map((h, i) => <th key={i}>{h}</th>)}
                        </tr>
                        </thead>
                        <tbody>
                        {block.rows.map((row, i) => (
                            <tr key={i}>
                                {row.map((cell, j) => (
                                    <td key={j} className={j === 0 ? "bdTdFirst" : ""}>
                                        <InlineMd text={cell}/>
                                    </td>
                                ))}
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            );
        case "img":
            return (
                <BuildFigure
                    item={{src: block.src, caption: block.caption}}
                    onOpen={onOpenImage}
                />
            );
        case "imgs":
            return (
                <div className="bdImgGrid">
                    {block.items.map((it, i) => (
                        <BuildFigure key={i} item={it} onOpen={onOpenImage}/>
                    ))}
                </div>
            );
        case "hl":
            return <div className="bdHl"><InlineMd text={block.text}/></div>;
        default:
            return null;
    }
}

// ---- 构筑详情 ----
function BuildDetail({build, onBack, onOpenImage}) {
    return (
        <div className="bdDetail">
            <button type="button" className="bdBack" onClick={onBack}>← 返回构筑列表</button>

            <div className="bdHead">
                <div className="bdTitleRow">
                    <h1 className="bdTitle">{build.name}</h1>
                    {build.enName ? <div className="bdEnName">{build.enName}</div> : null}
                </div>
                <div className="bdMetaRow">
                    {build.author ? <span className="bdTag bdTagAuthor">攻略：{build.author}</span> : null}
                    {build.version ? <span className="bdTag bdTagVersion">{build.version}</span> : null}
                    {(build.tags || []).map((t, i) => <span key={i} className="bdTag">{t}</span>)}
                </div>
                {build.summary ? <p className="bdSummary">{build.summary}</p> : null}
                {(build.facts || []).length > 0 ? (
                    <div className="bdFacts">
                        {build.facts.map(([k, v], i) => (
                            <div key={i} className="bdFact">
                                <div className="bdFactKey">{k}</div>
                                <div className="bdFactVal"><InlineMd text={v}/></div>
                            </div>
                        ))}
                    </div>
                ) : null}
            </div>

            <div className="bdBody">
                {(build.sections || []).map((block, i) => (
                    <SectionBlock key={i} block={block} onOpenImage={onOpenImage}/>
                ))}
            </div>
        </div>
    );
}

// ---- 主面板 ----
export default function BuildsPanel() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [classId, setClassId] = useState("amazon");
    const [buildId, setBuildId] = useState(null);
    const [lightbox, setLightbox] = useState(null);

    useEffect(() => {
        let cancelled = false;
        fetch(`${import.meta.env.BASE_URL}data/Builds.json`, {cache: "no-store"})
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP ${r.status} ${r.statusText}`);
                return r.json();
            })
            .then((json) => {
                if (cancelled) return;
                setData(json);
                setLoading(false);
            })
            .catch((e) => {
                if (cancelled) return;
                setError(e instanceof Error ? e : new Error(String(e)));
                setLoading(false);
            });
        return () => {
            cancelled = true;
        };
    }, []);

    const classes = data?.classes || [];
    const cls = classes.find((c) => c.id === classId) || classes[0] || null;
    const build = cls ? (cls.builds || []).find((b) => b.id === buildId) : null;

    // 切换职业时回到职业概览
    function selectClass(id) {
        setClassId(id);
        setBuildId(null);
    }

    if (loading) {
        return <div className="bdState">正在加载构筑数据…</div>;
    }
    if (error) {
        return <div className="bdState bdStateError">构筑数据加载失败：{error.message}</div>;
    }
    if (!classes.length) {
        return <div className="bdState">暂无构筑数据。</div>;
    }

    return (
        <div className="buildsPanel">
            <div className="bdHeader">
                <div className="bdHeaderTitle">核心 BD 构筑</div>
                <div className="bdHeaderSub">分职业整理的核心构筑库 · 数据来自玩家社区攻略（持续收录中）</div>
            </div>

            {/* 职业选择条 */}
            <div className="bdClassBar">
                {classes.map((c) => {
                    const Icon = CLASS_ICON_MAP[c.icon] || BowIcon;
                    const count = (c.builds || []).length;
                    return (
                        <button
                            key={c.id}
                            type="button"
                            className={"bdClassChip" + (c.id === classId ? " active" : "")}
                            onClick={() => selectClass(c.id)}
                        >
                            <img src={Icon} alt="" className="bdClassIcon"/>
                            <span className="bdClassName">{c.name}</span>
                            <span className="bdClassCount">{count}</span>
                        </button>
                    );
                })}
            </div>

            {build ? (
                <BuildDetail
                    build={build}
                    onBack={() => setBuildId(null)}
                    onOpenImage={setLightbox}
                />
            ) : (
                <div className="bdListArea">
                    <div className="bdListHeading">
                        <span className="bdListTitle">{cls ? cls.name : ""} · 构筑列表</span>
                        <span className="bdListHint">{cls?.enName || ""}</span>
                    </div>
                    {(cls?.builds || []).length === 0 ? (
                        <div className="bdEmpty">
                            <div className="bdEmptyIcon">◈</div>
                            <div className="bdEmptyText">「{cls?.name || ""}」的构筑正在整理中，敬请期待。</div>
                        </div>
                    ) : (
                        <div className="bdCardGrid">
                            {(cls?.builds || []).map((b) => (
                                <button
                                    key={b.id}
                                    type="button"
                                    className="bdCard"
                                    onClick={() => setBuildId(b.id)}
                                >
                                    <div className="bdCardTop">
                                        <span className="bdCardName">{b.name}</span>
                                        {b.enName ? <span className="bdCardEn">{b.enName}</span> : null}
                                    </div>
                                    <div className="bdCardTags">
                                        {(b.tags || []).map((t, i) => <span key={i} className="bdTag bdTagSmall">{t}</span>)}
                                    </div>
                                    <p className="bdCardSummary">{b.summary}</p>
                                    <div className="bdCardFoot">
                                        <span className="bdCardAuthor">✍ {b.author || "佚名"}</span>
                                        <span className="bdCardGo">查看构筑 →</span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* 截图放大灯箱 */}
            {lightbox ? (
                <div className="bdLightbox" onClick={() => setLightbox(null)}>
                    <div className="bdLightboxInner" onClick={(e) => e.stopPropagation()}>
                        <img src={IMG_BASE + lightbox.src} alt={lightbox.caption || ""}/>
                        {lightbox.caption ? <div className="bdLightboxCaption">{lightbox.caption}</div> : null}
                        <button type="button" className="bdLightboxClose" onClick={() => setLightbox(null)}>×</button>
                    </div>
                </div>
            ) : null}
        </div>
    );
}
