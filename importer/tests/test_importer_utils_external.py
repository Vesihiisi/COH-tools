from importer_utils import *


def test_get_http_code_1():
    assert get_http_code(
        "http://kulturarvsdata.se/raa/bbr/21300000003265") == 200


def test_get_http_code_2():
    assert get_http_code(
        "http://kulturarvsdata.se/raa/bbra/21300000003265") == 404


def test_get_bbr_link_1():
    assert get_bbr_link("21320000019150") == "raa/bbra/21320000019150"


def test_get_bbr_link_2():
    assert get_bbr_link("21300000003265") == "raa/bbr/21300000003265"
