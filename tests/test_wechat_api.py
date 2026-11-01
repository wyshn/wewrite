import pytest

from wewrite.toolkit import wechat_api


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_delete_draft_success(monkeypatch):
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        captured["json"] = kwargs.get("json")
        return _FakeResponse({"errcode": 0, "errmsg": "ok"})

    monkeypatch.setattr(wechat_api.requests, "post", fake_post)

    wechat_api.delete_draft("token-1", "media-1")

    assert captured["url"].endswith("/cgi-bin/draft/delete")
    assert captured["params"] == {"access_token": "token-1"}
    assert captured["json"] == {"media_id": "media-1"}


def test_delete_draft_error(monkeypatch):
    monkeypatch.setattr(
        wechat_api.requests,
        "post",
        lambda *args, **kwargs: _FakeResponse({"errcode": 40007, "errmsg": "invalid media_id"}),
    )

    with pytest.raises(ValueError, match="40007"):
        wechat_api.delete_draft("token-1", "missing")
