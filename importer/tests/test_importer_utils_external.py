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


def test_socken_to_q_1():
    assert socken_to_q("Holm", "Medelpad") == "Q10525331"


def test_socken_to_q_2():
    assert socken_to_q("Holm", "Uppland") == "Q10525332"


def test_socken_to_q_3():
    assert socken_to_q("Långtora", "Uppland") == "Q10572689"


def test_socken_to_q_4():
    assert socken_to_q("Linde", "Västmanland") == "Q10562482"


def test_socken_to_q_5():
    assert socken_to_q("Löts", "Öland") == "Q10572936"


def test_socken_to_q_6():
    assert socken_to_q("Egby", "Öland") == "Q10480210"


def test_socken_to_q_7():
    assert socken_to_q("Backa", "Bohuslän") == "Q10424141"


def test_socken_to_q_8():
    assert socken_to_q("Solberga", "Bohuslän") == "Q2788890"


def test_file_is_on_commons_1():
    assert file_is_on_commons("Loojangu värvid 2.jpg") == True


def test_file_is_on_commons_2():
    assert file_is_on_commons("adgffhgadftgfhsfgdg") == False


def test_commonscat_exists_1():
    assert commonscat_exists("Libraries in Germany by city") == True


def test_commonscat_exists_2():
    assert commonscat_exists("adgafgtaffrsdf") == False


def test_q_from_wikipedia_1():
    assert q_from_wikipedia("sv", "Norrala socken") == "Q10602691"


def test_q_from_wikipedia_2():
    assert q_from_wikipedia("sv", "Användare:Vesihiisi") == None


def test_q_from_wikipedia_2():
    assert q_from_wikipedia("sv", "This page does not exist") == None


def test_q_from_first_wikilink_1():
    assert q_from_first_wikilink("sv", ("'''Norrala socken'''"
                                        " ligger i [[Hälsingland]], ingår sedan 1971 i "
                                        "[[Söderhamns kommun]] och motsvarar från 2016 "
                                        "[[Norrala distrikt]].")) == "Q206564"
