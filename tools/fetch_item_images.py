# -*- coding: utf-8 -*-
"""下载物品贴图到 public/item-images/。

贴图名来自 `tools/build_item_images.py` 生成的 `public/data/ItemImages.json`。
默认从国服官方档案站（bd.wdjwxh.com）的 `/item-images/<name>.png` 获取 —— 这些 PNG 是
游戏客户端库存贴图（DC6）的转换结果，与本 wiki 记录的是同一款游戏。

用法:
    python3 tools/fetch_item_images.py                  # 只补缺失
    python3 tools/fetch_item_images.py --all            # 重新下载全部
    python3 tools/fetch_item_images.py --base-url https://example.com/item-images
    python3 tools/fetch_item_images.py --proxy http://127.0.0.1:7897
    python3 tools/fetch_item_images.py --check          # 只检查缺失，不下载
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP = os.path.join(ROOT, "public", "data", "ItemImages.json")
DEST = os.path.join(ROOT, "public", "item-images")
DEFAULT_BASE = "https://bd.wdjwxh.com/item-images"


def opener(proxy):
    if proxy:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return urllib.request.build_opener()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "")
    ap.add_argument("--all", action="store_true", help="重新下载全部（默认只补缺失）")
    ap.add_argument("--check", action="store_true", help="只报告缺失，不下载")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    data = json.load(open(MAP, encoding="utf-8"))
    names = sorted({v for rec in data["images"].values() for v in rec.values()})
    os.makedirs(DEST, exist_ok=True)

    missing = [n for n in names if args.all or not os.path.exists(os.path.join(DEST, f"{n}.png"))]
    have = len(names) - len(missing)
    print(f"需要 {len(names)} 张 · 已有 {have} 张 · 待下载 {len(missing)} 张")

    if args.check or not missing:
        if missing:
            print("缺失清单（前 40）:", ", ".join(missing[:40]))
        return 0

    op = opener(args.proxy)

    def try_get(url):
        with op.open(url, timeout=args.timeout) as r:
            return r.read()

    ok, failed = 0, []
    for i, nm in enumerate(missing, 1):
        # 源站文件名大小写不统一（游戏表里是 invrEl，站上是 invrel），逐个候选回退；
        # 落盘一律用**游戏表里的原名**，前端无需做大小写处理。
        candidates = [nm]
        if nm.lower() != nm:
            candidates.append(nm.lower())
        blob = None
        last_err = None
        for cand in candidates:
            try:
                blob = try_get(f"{args.base_url}/{urllib.parse.quote(cand)}.png")
                if not blob:
                    raise ValueError("空响应")
                break
            except (urllib.error.HTTPError, urllib.error.URLError, ValueError, TimeoutError) as e:
                last_err = e
                blob = None
        if blob is None:
            failed.append((nm, str(last_err)))
        else:
            with open(os.path.join(DEST, f"{nm}.png"), "wb") as f:
                f.write(blob)
            ok += 1
        if i % 50 == 0 or i == len(missing):
            print(f"  进度 {i}/{len(missing)} · 成功 {ok} · 失败 {len(failed)}")

    print(f"完成：成功 {ok}，失败 {len(failed)}")
    if failed:
        print("失败清单（前 40）:")
        for nm, err in failed[:40]:
            print(f"  {nm}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
