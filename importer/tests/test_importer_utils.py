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
    assert parse_ship_dimensions("Längd: 18,55 Bredd: 4,06 Djup: Brt: 37,78") == {"length": 18.55,
                                                                                  "width": 4.06,
                                                                                  "grt": 37.78}


def test_parse_ship_dimensions_2():
    assert parse_ship_dimensions("Längd: 17.5 Bredd: 5.8 Djup: 2.50 Brt: 47") == {"length": 17.5,
                                                                                  "width": 5.8,
                                                                                  "draft": 2.50,
                                                                                  "grt": 47}


def test_parse_ship_dimensions_3():
    assert parse_ship_dimensions("Längd:  Bredd:  Djup:  Brt:") == {}


def test_parse_ship_dimensions_4():
    assert parse_ship_dimensions("Längd: 14,76. Bredd: 4,83 Djup: Brt: 22") == {"length": 14.76,
                                                                                "width": 4.83,
                                                                                "grt": 22}


def test_comma_to_period_1():
    assert comma_to_period("43,12") == "43.12"


def test_remove_marks_from_ends_1():
    assert remove_marks_from_ends(".43.22.") == "43.22"


def test_remove_marks_from_ends_2():
    assert remove_marks_from_ends("length:") == "length"


def test_string_to_float_1():
    assert string_to_float("32.12") == 32.12


def test_string_to_float_2():
    assert string_to_float("32,12") == 32.12


def test_string_to_float_3():
    assert string_to_float("32,12.") == 32.12


def test_string_to_float_3():
    assert string_to_float(",32,12.") == 32.12


def test_count_wikilinks_1():
    assert count_wikilinks("just text") == 0


def test_count_wikilinks_2():
    assert count_wikilinks("[[Movikens masugn|Moviken]]") == 1


def test_count_wikilinks_3():
    assert count_wikilinks("[[Tranås]] and also [[Svanesund]]") == 2


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


def test_get_rid_of_brackets_1():
    assert get_rid_of_brackets(
        "Kulla Gunnarstorps mölla (Kulla Gunnarstorp 1:21)") == "Kulla Gunnarstorps mölla"


def test_get_rid_of_brackets_2():
    assert get_rid_of_brackets(
        "Kulla Gunnarstorps mölla") == "Kulla Gunnarstorps mölla"


def test_get_text_inside_brackets_1():
    assert get_text_inside_brackets(
        "Kulla Gunnarstorps mölla (Kulla Gunnarstorp 1:21)") == "Kulla Gunnarstorp 1:21"


def test_get_text_inside_brackets_2():
    assert get_text_inside_brackets(
        "just text no brackets") == "just text no brackets"


def test_get_number_from_string_1():
    assert get_number_from_string("12 byggnader") == 12


def test_get_number_from_string_2():
    assert get_number_from_string("just text!") == None


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


def test_string_is_q_item_1():
    assert string_is_q_item("Q1641992") == True


def test_string_is_q_item_2():
    assert string_is_q_item("some string") == False


def test_string_is_q_item_3():
    assert string_is_q_item("Q34234vsf") == False
