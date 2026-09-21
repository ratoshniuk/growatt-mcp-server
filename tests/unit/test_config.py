import pytest

from growatt_mcp.config import DEFAULT_BASE_URL, REGIONS, ConfigError, load_settings


def test_token_required():
    with pytest.raises(ConfigError, match="GROWATT_TOKEN"):
        load_settings({})
    with pytest.raises(ConfigError, match="GROWATT_TOKEN"):
        load_settings({"GROWATT_TOKEN": "   "})


def test_defaults():
    s = load_settings({"GROWATT_TOKEN": "abc"})
    assert s.token == "abc"
    assert s.base_url == DEFAULT_BASE_URL
    assert s.timeout == 30.0


@pytest.mark.parametrize("region", sorted(REGIONS))
def test_region_selects_host(region):
    s = load_settings({"GROWATT_TOKEN": "abc", "GROWATT_REGION": region.upper()})
    assert s.base_url == REGIONS[region]


def test_unknown_region_rejected():
    with pytest.raises(ConfigError, match="GROWATT_REGION"):
        load_settings({"GROWATT_TOKEN": "abc", "GROWATT_REGION": "mars"})


def test_base_url_overrides_region_and_strips_slash():
    s = load_settings({"GROWATT_TOKEN": "abc", "GROWATT_REGION": "cn", "GROWATT_BASE_URL": "https://x.test/"})
    assert s.base_url == "https://x.test"


@pytest.mark.parametrize("value", ["abc", "0", "-5"])
def test_bad_timeout_rejected(value):
    with pytest.raises(ConfigError, match="GROWATT_TIMEOUT"):
        load_settings({"GROWATT_TOKEN": "abc", "GROWATT_TIMEOUT": value})


def test_timeout_parsed():
    assert load_settings({"GROWATT_TOKEN": "abc", "GROWATT_TIMEOUT": "7.5"}).timeout == 7.5
