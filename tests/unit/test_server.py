import logging

import pytest
from mcp.server.fastmcp import FastMCP

from growatt_mcp import __version__, main
from growatt_mcp.tools import TOOL_MODULES


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert f"growatt-mcp {__version__}" in capsys.readouterr().out


def test_missing_token_exits_with_code_2(monkeypatch, capsys):
    monkeypatch.delenv("GROWATT_TOKEN", raising=False)
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert "GROWATT_TOKEN" in capsys.readouterr().err


def test_main_happy_path_runs_app(monkeypatch):
    seen = {}

    def fake_run(self, *args, **kwargs):
        seen["name"] = self.name
        seen["tools"] = len(self._tool_manager.list_tools())

    monkeypatch.setenv("GROWATT_TOKEN", "abc")
    monkeypatch.setenv("GROWATT_READ_ONLY", "1")
    monkeypatch.setattr(FastMCP, "run", fake_run)
    main([])
    assert seen["name"] == f"Growatt Solar v{__version__}"
    assert seen["tools"] == 16, "read-only mode registers only the read tools"
    assert logging.getLogger("httpx").level == logging.WARNING


def test_keyboard_interrupt_is_swallowed(monkeypatch):
    def fake_run(self, *args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setenv("GROWATT_TOKEN", "abc")
    monkeypatch.setattr(FastMCP, "run", fake_run)
    main([])  # must not raise


async def test_app_name_and_instructions(app):
    assert app.name == f"Growatt Solar v{__version__}"
    assert "get_plants" in (app.instructions or "")
    assert "untrusted" in (app.instructions or "")


async def test_lifespan_closes_client(app, client):
    assert not client.is_closed
    async with app.settings.lifespan(app):
        pass
    assert client.is_closed


def test_every_tool_module_has_register():
    for module in TOOL_MODULES:
        assert callable(module.register), module.__name__
