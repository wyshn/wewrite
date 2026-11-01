import io
import json
import shlex
import sys
from pathlib import Path

import pytest
from PIL import Image

from wewrite.toolkit import image_gen


def _png_bytes(size=(2946, 1252), color="navy"):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


def test_cover_is_fitted_to_900x383():
    img = Image.open(io.BytesIO(_png_bytes()))
    out = image_gen._apply_wechat_fit(img, "cover")
    assert out.size == (900, 383)


def test_article_width_is_900():
    img = Image.open(io.BytesIO(_png_bytes((1920, 1080))))
    out = image_gen._apply_wechat_fit(img, "article")
    assert out.size == (900, 506)


def test_explicit_size_is_not_refit():
    img = Image.open(io.BytesIO(_png_bytes((1920, 816))))
    assert image_gen._apply_wechat_fit(img, "1920x816").size == (1920, 816)


def test_cover_aspect_maps_to_21_9():
    assert image_gen._size_to_aspect("1920x816") == "21:9"


def test_normalize_cover_under_1mb():
    out = image_gen._normalize_image(_png_bytes(), "/tmp/cover.jpg", preset="cover")
    img = Image.open(io.BytesIO(out))
    assert img.size == (900, 383)
    assert len(out) < 1024 * 1024


def test_parse_cli_json_with_log_lines():
    text = 'download image 1 URL: https://example.com/a.png\n{"gen_status":"success"}'
    assert image_gen._parse_cli_json(text) == {"gen_status": "success"}


def test_dreamina_entry_does_not_require_api_key():
    provider = image_gen._build_provider_from_entry(
        {"provider": "dreamina", "binary": "/bin/echo"}
    )
    assert isinstance(provider, image_gen.DreaminaProvider)


def _fake_cli(tmp_path: Path, submit_payload: dict) -> Path:
    script = tmp_path / "fake_cli.py"
    script.write_text(
        "import json, sys\n"
        "from pathlib import Path\n"
        "from PIL import Image\n"
        f"submit = {submit_payload!r}\n"
        "args = sys.argv[1:]\n"
        "Path(__file__).with_name('argv.log').open('a', encoding='utf-8').write(json.dumps(args) + '\\n')\n"
        "if args[0] == 'text2image' or args[0] == 'image2image':\n"
        "    print(json.dumps(submit))\n"
        "elif args[0] == 'query_result':\n"
        "    d = next(a.split('=', 1)[1] for a in args if a.startswith('--download_dir='))\n"
        "    p = Path(d) / 'out.png'\n"
        "    Image.new('RGB', (1920, 816), 'navy').save(p)\n"
        "    print(json.dumps({'gen_status': 'success', 'result_json': {'images': [{'path': str(p)}]}}))\n",
        encoding="utf-8",
    )
    binary = tmp_path / "dreamina"
    binary.write_text(
        f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(script))} \"$@\"\n",
        encoding="utf-8",
    )
    binary.chmod(0o755)
    return binary


def test_dreamina_generate_reads_downloaded_file(tmp_path):
    binary = _fake_cli(tmp_path, {"submit_id": "sid-1", "gen_status": "success"})
    provider = image_gen.DreaminaProvider(binary=str(binary), poll=1, timeout=5)
    raw = provider.generate("a cover", "1920x816")
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")


def test_dreamina_refs_use_image2image(tmp_path):
    binary = _fake_cli(tmp_path, {"submit_id": "sid-2", "gen_status": "success"})
    ref = tmp_path / "ref.png"
    Image.new("RGB", (64, 64), "red").save(ref)

    provider = image_gen.DreaminaProvider(binary=str(binary), poll=1, timeout=5)
    provider.generate("edit this", "1920x816", refs=[str(ref)])

    lines = [
        json.loads(line)
        for line in (tmp_path / "argv.log").read_text(encoding="utf-8").splitlines()
    ]
    submit = next(args for args in lines if args[0] == "image2image")
    assert f"--images={ref}" in submit


def test_missing_ref_is_rejected():
    with pytest.raises(ValueError, match="参考图不存在"):
        image_gen._normalize_refs(["/definitely/missing.png"])


def test_batch_passes_refs_to_generate_image(tmp_path, monkeypatch):
    seen = {}

    def fake_generate(prompt, output, size="cover", config=None, refs=None):
        seen["refs"] = refs
        Path(output).write_bytes(b"x")
        return output

    monkeypatch.setattr(image_gen, "generate_image", fake_generate)
    result = image_gen.generate_batch(
        [{"prompt": "p", "output": str(tmp_path / "o.png"), "size": "cover", "refs": ["a.png"]}],
        config={"image": {}},
    )

    assert result[0]["ok"] is True
    assert seen["refs"] == ["a.png"]


def test_cli_forwards_refs(monkeypatch, tmp_path):
    seen = {}

    def fake_generate(prompt, output, size="cover", config=None, refs=None):
        seen["refs"] = refs
        return output

    monkeypatch.setattr(image_gen, "_load_config", lambda: {"image": {}})
    monkeypatch.setattr(image_gen, "generate_image", fake_generate)
    monkeypatch.setattr(sys, "argv", [
        "image-gen",
        "--prompt", "改成水彩",
        "--output", str(tmp_path / "o.png"),
        "--refs", "a.png", "b.png",
    ])

    image_gen.main()

    assert seen["refs"] == ["a.png", "b.png"]


def test_dreamina_failure_is_raised(tmp_path):
    binary = _fake_cli(tmp_path, {"gen_status": "fail", "fail_reason": "bad size"})
    provider = image_gen.DreaminaProvider(binary=str(binary), poll=1, timeout=5)
    with pytest.raises(ValueError, match="bad size"):
        provider.generate("a cover", "1920x816")
