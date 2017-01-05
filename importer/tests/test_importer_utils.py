from importer_utils import *


def test_contains_digit_1():
    assert contains_digit("fna3fs") == True


def test_contains_digit_2():
    assert contains_digit("fnas") == False


def test_remove_markup_1():
    assert remove_markup(
        "[[Tegera Arena]], huvudentrén") == "Tegera Arena, huvudentrén"


def test_remove_markup_2():
    assert remove_markup(
        "[[Tegera Arena]],<br>huvudentrén") == "Tegera Arena, huvudentrén"


def test_remove_markup_3():
    assert remove_markup(
        "[[Tegera Arena]],<br/> huvudentrén") == "Tegera Arena, huvudentrén"


def test_is_legit_house_number_1():
    assert is_legit_house_number("32") == True


def test_is_legit_house_number_2():
    assert is_legit_house_number("2") == True


def test_is_legit_house_number_3():
    assert is_legit_house_number("3b") == True


def test_is_legit_house_number_4():
    assert is_legit_house_number("3 B") == True


def test_is_legit_house_number_5():
    assert is_legit_house_number("3-5") == True


def test_is_legit_house_number_6():
    assert is_legit_house_number("43B-43E") == True


def test_get_street_address_1():
    assert get_street_address("Bruksvägen 23", "sv") == "Bruksvägen 23"


def test_get_street_address_2():
    assert get_street_address(
        "Vilhelm Mobergs gata 4", "sv") == "Vilhelm Mobergs gata 4"


def test_get_street_address_3():
    assert get_street_address("Spånhult", "sv") == None


def test_get_street_address_4():
    assert get_street_address(
        ("Virserums station, Södra "
            "Järnvägsgatan 20"), "sv") == "Södra Järnvägsgatan 20"


def test_get_street_address_5():
    assert get_street_address(
        "Kyrkogatan 34, Dackestop", "sv") == "Kyrkogatan 34"


def test_get_street_address_6():
    assert get_street_address(
        "Odlaregatan, Svalöv (Gamla 9:an).", "sv") == None


def test_get_street_address_7():
    assert get_street_address(
        ("Bröderna Nilssons väg 14, Onslunda, "
            "273 95 Tomelilla"), "sv") == "Bröderna Nilssons väg 14"


def test_get_street_address_8():
    assert get_street_address(
        ("Norra Finnskoga Hembygdsgård , "
            "Höljes, Solrosvägen 2,"), "sv") == "Solrosvägen 2"


def test_get_street_address_9():
    assert get_street_address(
        ("Svaneholms slott ligger i Skurup i Skåne, "
            "fyra mil öster om Malmö, vid väg E65."), "sv") == None


def test_get_specific_table_name_1():
    assert get_specific_table_name(
        "se-arbetsl", "sv") == "monuments_se-arbetsl_(sv)"


def test_parse_year_1():
    assert parse_year("1987") == 1987


def test_parse_year_2():
    assert parse_year("1987-88") == (1987, 1988)


def test_parse_year_3():
    assert parse_year("24235423") == None


def test_parse_year_4():
    assert parse_year("1999-2008") == (1999, 2008)


def test_parse_year_5():
    assert parse_year("1999-foo") == None


def test_parse_year_6():
    assert parse_year("1999-1899") == None


def test_parse_year_6():
    assert parse_year("1999-2000-2003") == None


def test_remove_characters_1():
    assert remove_characters("foo-.fdaf.f2,3", ".,") == "foo-fdaff23"


def test_remove_characters_2():
    assert remove_characters(('string with "punctuation" inside of it! '
                              'Does this work? I hope so.'),
                             string.punctuation) == ("string with punctuation "
                                                     "inside of it Does this "
                                                     "work I hope so")


def test_parse_ship_dimensions_1():
    assert parse_ship_dimensions("Längd: 18,55 Bredd: 4,06 Djup: Brt: 37,78") == {"L": 18.55,
                                                                                 "W": 4.06,
                                                                                 "D": None,
                                                                                 "BRT": 37.78}


def test_parse_ship_dimensions_2():
    assert parse_ship_dimensions("Längd: 17.5 Bredd: 5.8 Djup: 2.50 Brt: 47") == {"L": 17.5,
                                                                                 "W": 5.8,
                                                                                 "D": 2.50,
                                                                                 "BRT": 47}


def test_parse_ship_dimensions_3():
    assert parse_ship_dimensions("Längd:  Bredd:  Djup:  Brt:") == {"L": None,
                                                                   "W": None,
                                                                   "D": None,
                                                                   "BRT": None}


def test_parse_ship_dimensions_4():
    assert parse_ship_dimensions("Längd: 14,76. Bredd: 4,83 Djup: Brt: 22") == {"L": 14.76,
                                                                               "W": 4.83,
                                                                               "D": None,
                                                                               "BRT": 22}
