import pytest

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


async def test_app_name_and_instructions(app):
    assert app.name == f"Growatt Solar v{__version__}"
    assert "get_plants" in (app.instructions or "")


def test_every_tool_module_has_register():
    for module in TOOL_MODULES:
        assert callable(module.register), module.__name__
