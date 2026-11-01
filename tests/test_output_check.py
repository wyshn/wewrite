import os
from pathlib import Path

from PIL import Image

from wewrite.commands import output_check


def _make_output(path: Path, ref: str = "images/figure.png",
                 noise_image: bool = False) -> Path:
    path.mkdir()
    (path / "article.md").write_text("测试内容。" * 100, encoding="utf-8")
    (path / "preview.html").write_text(
        "<!DOCTYPE html><html><body>ok</body></html>", encoding="utf-8"
    )
    Image.new("RGB", (900, 383), "navy").save(path / "cover.png")
    (path / "images").mkdir()
    if noise_image:
        raw = os.urandom(1200 * 1200 * 3)
        Image.frombytes("RGB", (1200, 1200), raw).save(path / "images" / "figure.png")
    else:
        Image.new("RGB", (100, 100), "red").save(path / "images" / "figure.png")
    (path / "article-illustrated.md").write_text(
        f"# T\n\n![图]({ref})\n\n" + "正文。" * 100, encoding="utf-8"
    )
    return path


def test_valid_output_passes(tmp_path):
    result = output_check.check_dir(_make_output(tmp_path / "ok"))
    assert result["ok"] is True
    assert result["errors"] == []


def test_missing_preview_fails(tmp_path):
    path = _make_output(tmp_path / "bad")
    (path / "preview.html").unlink()
    result = output_check.check_dir(path)
    assert result["ok"] is False
    assert any("preview.html" in error for error in result["errors"])


def test_absolute_and_project_image_refs_fail(tmp_path):
    absolute = output_check.check_dir(_make_output(tmp_path / "abs", ref="/tmp/a.png"))
    assert absolute["ok"] is False
    assert any("相对路径" in error for error in absolute["errors"])

    project = output_check.check_dir(
        _make_output(tmp_path / "project", ref="ai-daily-report/a.png")
    )
    assert project["ok"] is False
    assert any("ai-daily-report" in error for error in project["errors"])


def test_oversized_body_image_fails(tmp_path):
    result = output_check.check_dir(_make_output(tmp_path / "big", noise_image=True))
    assert result["ok"] is False
    assert any("超过" in error for error in result["errors"])
