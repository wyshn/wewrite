#!/usr/bin/env python3
"""Validate the WeWrite content output directory contract.

Usage:
    wewrite output-check                 # validate every dir under ~/.wewrite/output
    wewrite output-check <dir> --json    # validate one article directory
"""

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

from .. import paths

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
MAX_BODY_IMAGE_BYTES = 1024 * 1024
REQUIRED_FILES = ("article.md", "preview.html")
FORBIDDEN_FILES = ("config.yaml", ".env", "secrets.json")
IMAGE_REF = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")


def _check_image(path: Path, label: str, errors: list[str], warnings: list[str],
                 limit: int, cover: bool = False) -> tuple[int, int] | None:
    try:
        with Image.open(path) as img:
            img.load()
            width, height = img.size
    except Exception as exc:  # noqa: BLE001 - 报告为校验错误
        errors.append(f"{label}: 无法作为图片打开（{exc}）")
        return None

    size = path.stat().st_size
    if size > limit:
        target = warnings if cover else errors
        target.append(f"{label}: {size / 1024:.0f}KB，超过 {limit / 1024:.0f}KB 上限")

    if cover:
        ratio = width / height if height else 0
        if abs(ratio - 900 / 383) > 0.05:
            warnings.append(f"{label}: 比例 {ratio:.2f}，微信封面建议 2.35:1")
        if (width, height) != (900, 383):
            warnings.append(f"{label}: 尺寸 {width}x{height}，建议 900x383")

    return width, height


def check_dir(path: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_dir():
        return {"path": str(path), "ok": False, "errors": ["目录不存在"], "warnings": []}

    for name in REQUIRED_FILES:
        if not (path / name).is_file():
            errors.append(f"缺少必需文件: {name}")

    for name in FORBIDDEN_FILES:
        if (path / name).exists():
            errors.append(f"产出目录不应包含凭证/配置文件: {name}")
    for pattern in ("*.pem", "*.key"):
        for secret in path.glob(pattern):
            errors.append(f"产出目录不应包含密钥文件: {secret.name}")

    article = path / "article.md"
    if article.is_file():
        text = article.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            errors.append("article.md 为空")
        chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
        if chinese < 200:
            warnings.append(f"article.md 只有 {chinese} 个中文字，可能过短")
        if "ai-daily-report" in text:
            errors.append("article.md 仍引用 ai-daily-report 项目路径")

    preview = path / "preview.html"
    if preview.is_file():
        html = preview.read_text(encoding="utf-8", errors="replace")
        if not html.strip():
            errors.append("preview.html 为空")
        elif "<html" not in html[:500].lower():
            warnings.append("preview.html 不像完整的 HTML 文档")

    cover = next((path / n for n in ("cover.png", "cover.jpg", "cover.jpeg")
                  if (path / n).is_file()), None)
    if cover is None:
        warnings.append("没有 cover.png / cover.jpg")
    else:
        _check_image(cover, cover.name, errors, warnings,
                     limit=1024 * 1024, cover=True)

    images_dir = path / "images"
    if images_dir.is_dir():
        images = [p for p in images_dir.iterdir()
                  if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES]
        if len(images) > 10:
            errors.append(f"images/ 有 {len(images)} 张图，微信正文上限 10 张")
        for image in sorted(images):
            _check_image(image, f"images/{image.name}", errors, warnings,
                         limit=MAX_BODY_IMAGE_BYTES)

    for md_name in ("article.md", "article-illustrated.md"):
        md = path / md_name
        if not md.is_file():
            continue
        content = md.read_text(encoding="utf-8", errors="replace")
        for ref in IMAGE_REF.findall(content):
            if ref.startswith(("http://", "https://", "data:")):
                continue
            if "ai-daily-report" in ref:
                errors.append(f"{md_name}: 图片路径仍指向 ai-daily-report（{ref}）")
                continue
            ref_path = Path(ref)
            if ref_path.is_absolute():
                errors.append(f"{md_name}: 图片必须用相对路径（{ref}）")
            elif ".." in ref_path.parts:
                errors.append(f"{md_name}: 图片路径不能跳出产出目录（{ref}）")
            elif not (path / ref_path).is_file():
                errors.append(f"{md_name}: 图片不存在（{ref}）")

    return {"path": str(path), "ok": not errors, "errors": errors, "warnings": warnings}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="wewrite output-check",
        description="校验内容产出目录：必需文件、图片体积、相对路径与项目耦合",
    )
    parser.add_argument("path", nargs="?", default=None,
                        help="产出目录；默认 ~/.wewrite/output")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args(argv)

    root = Path(args.path).expanduser() if args.path else paths.output_dir()
    if not root.exists():
        print(f"产出目录不存在: {root}", file=sys.stderr)
        sys.exit(1)

    targets = [root] if (root / "article.md").is_file() else sorted(
        d for d in root.iterdir() if d.is_dir()
    )
    if not targets:
        print(f"没有可校验的子目录: {root}", file=sys.stderr)
        sys.exit(1)

    results = [check_dir(target) for target in targets]
    ok = all(item["ok"] for item in results)

    if args.json:
        print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        for item in results:
            mark = "✓" if item["ok"] else "✗"
            print(f"{mark} {item['path']}")
            for warning in item["warnings"]:
                print(f"  ⚠ {warning}")
            for error in item["errors"]:
                print(f"  ✗ {error}")
        print(f"\n{sum(1 for item in results if item['ok'])}/{len(results)} 个目录通过")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
