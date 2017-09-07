#!/usr/bin/python
# -*- coding: utf-8  -*-
import pywikibot
import string
import unittest
import importer.importer_utils as utils


class TestWLMStuff(unittest.TestCase):

    def test_get_specific_table_name(self):
        dataset = "se-arbetsl"
        lang = "sv"
        output = "monuments_se-arbetsl_(sv)"
        self.assertEqual(utils.get_specific_table_name(dataset, lang), output)

    def test_create_wlm_url(self):
        dataset = "se-ship"
        lang = "sv"
        id_no = "SFC 9698"
        output = ("https://tools.wmflabs.org/heritage/api/api.php"
                  "?action=search&format=json&srcountry=se-ship"
                  "&srlanguage=sv&srid=SFC%209698")
        self.assertEqual(utils.create_wlm_url(dataset, lang, id_no), output)


class TestDictionaryMethods(unittest.TestCase):

    def setUp(self):
        self.lookup_table = {
            'Foo': {'items': ['Q7777'], 'count': '222'},
            'Foo and cat': {'items': ['Q8888', 'Q1234'], 'count': '111'}
        }
        self.query_results_table_with_default_key = [
            {"item": "Foo", "iso_code": "222"},
            {"item": "cat", "iso_code": "mjau"}
        ]
        self.query_results_table_with_non_default_key = [
            {"name": "Aaa", "iso_code": "55"},
            {"name": "Ggg", "iso_code": "00"}
        ]

    def test_get_item_from_dict_by_key_one_default(self):
        dic = self.query_results_table_with_default_key
        search_term = "mjau"
        key_field = "iso_code"
        output = ["cat"]
        matches = utils.get_item_from_dict_by_key(
            dict_name=dic, search_term=search_term, search_in=key_field)
        self.assertEqual(matches, output)

    def test_get_item_from_dict_by_key_one_non_default(self):
        dic = self.query_results_table_with_non_default_key
        search_term = "55"
        key_field = "iso_code"
        value_field = "name"
        output = ["Aaa"]
        matches = utils.get_item_from_dict_by_key(
            dict_name=dic, search_term=search_term, search_in=key_field,
            return_content_of=value_field)
        self.assertEqual(matches, output)

    def test_get_item_from_dict_by_key_none(self):
        search_term = "999",
        key_field = "iso_code"
        output = []
        dic = self.query_results_table_with_default_key
        matches = utils.get_item_from_dict_by_key(
            dict_name=dic, search_term=search_term, search_in=key_field)
        self.assertEqual(matches, output)

    def test_get_matching_items_from_dict_one(self):
        search_term = "foo"
        output = ['Q7777']
        self.assertEqual(utils.get_matching_items_from_dict(
            search_term, self.lookup_table), output)

    def test_get_matching_items_from_dict_two(self):
        search_term = "foo and cat"
        output = ['Q8888', 'Q1234']
        self.assertEqual(utils.get_matching_items_from_dict(
            search_term, self.lookup_table), output)

    def test_get_matching_items_from_dict_none(self):
        search_term = "bbb"
        output = []
        self.assertEqual(utils.get_matching_items_from_dict(
            search_term, self.lookup_table), output)


class TestStringMethods(unittest.TestCase):

    def test_contains_digit(self):
        self.assertTrue(utils.contains_digit("fna3fs"))
        self.assertFalse(utils.contains_digit("foo"))

    def test_get_number_from_string_succeed(self):
        text = "12 byggnader"
        self.assertEqual(utils.get_number_from_string(text), 12)

    def test_get_number_from_string_none(self):
        text = "just text!"
        self.assertIsNone(utils.get_number_from_string(text))

    def test_remove_multiple_spaces(self):
        text = "text  with      a lot   of spaces"
        output = "text with a lot of spaces"
        self.assertEqual(utils.remove_multiple_spaces(text), output)

    def test_get_last_char(self):
        self.assertEqual(utils.get_last_char("foobar"), "r")

    def test_is_vowel_simple(self):
        self.assertTrue(utils.is_vowel("a"))

    def test_is_vowel_accented(self):
        self.assertTrue(utils.is_vowel("é"))

    def test_is_vowel_diacritic(self):
        self.assertTrue(utils.is_vowel("Ø"))

    def test_is_vowel_consonant(self):
        self.assertFalse(utils.is_vowel("g"))

    def test_last_char_is_vowel_pass(self):
        self.assertTrue(utils.last_char_is_vowel("foo"))

    def test_last_char_is_vowel_fail(self):
        self.assertFalse(utils.last_char_is_vowel("bar"))

    def test_first_char_is_number_true(self):
        self.assertTrue(utils.first_char_is_number("2 foo"))

    def test_first_char_is_number_false(self):
        self.assertFalse(utils.first_char_is_number("f2oo"))

    def test_get_rid_of_brackets_succeed(self):
        text = "Kulla Gunnarstorps mölla (Kulla Gunnarstorp 1:21)"
        output = "Kulla Gunnarstorps mölla"
        self.assertEqual(utils.get_rid_of_brackets(text), output)

    def test_get_rid_of_brackets_none(self):
        text = "Kulla Gunnarstorps mölla"
        output = "Kulla Gunnarstorps mölla"
        self.assertEqual(utils.get_rid_of_brackets(text), output)

    def test_get_text_inside_brackets_succeed(self):
        text = "Kulla Gunnarstorps mölla (Kulla Gunnarstorp 1:21)"
        output = "Kulla Gunnarstorp 1:21"
        self.assertEqual(utils.get_text_inside_brackets(text), output)

    def test_get_text_inside_brackets_nested_one(self):
        text = "outsidetext (foo (cat))"
        output = "foo (cat)"
        self.assertEqual(utils.get_text_inside_brackets(text), output)

    def test_get_text_inside_brackets_nested_two(self):
        text = "text (foo (bar (cat))) around"
        output = "foo (bar (cat))"
        self.assertEqual(utils.get_text_inside_brackets(text), output)

    def test_get_text_inside_brackets_twice(self):
        text = "pre (foo) mid (bar) post"
        self.assertRaises(ValueError, utils.get_text_inside_brackets, text)

    def test_get_text_inside_brackets_broken_1(self):
        text = "pre (foo"
        self.assertRaises(ValueError, utils.get_text_inside_brackets, text)

    def test_get_text_inside_brackets_broken_2(self):
        text = "foo )bar( cat"
        self.assertRaises(ValueError, utils.get_text_inside_brackets, text)

    def test_get_text_inside_brackets_broken_3(self):
        text = "foo) bar (cat)"
        self.assertRaises(ValueError, utils.get_text_inside_brackets, text)

    def test_get_text_inside_brackets_broken_4(self):
        text = "foo (bar))"
        self.assertRaises(ValueError, utils.get_text_inside_brackets, text)

    def test_get_text_inside_brackets_none(self):
        text = "just text no brackets"
        output = "just text no brackets"
        self.assertEqual(utils.get_text_inside_brackets(text), output)

    def test_comma_to_period(self):
        self.assertEqual(utils.comma_to_period("42,22"), "42.22")

    def test_remove_characters_selected(self):
        text = "foo-.fdaf.f2,3"
        chars = ".,"
        output = "foo-fdaff23"
        self.assertEqual(utils.remove_characters(text, chars), output)

    def test_remove_characters_punctuation(self):
        text = ('string with "punctuation" inside of it! '
                'Does this work? I hope so.')
        chars = string.punctuation
        output = ("string with punctuation inside of it "
                  "Does this work I hope so")
        self.assertEqual(utils.remove_characters(text, chars), output)

    def test_remove_marks_from_ends_period(self):
        self.assertEqual(utils.remove_marks_from_ends(".43.22."), "43.22")

    def test_remove_marks_from_ends_colon(self):
        self.assertEqual(utils.remove_marks_from_ends("foo:"), "foo")

    def test_string_to_float_1(self):
        self.assertEqual(utils.string_to_float("32.11"), 32.11)

    def test_string_to_float_2(self):
        self.assertEqual(utils.string_to_float("32,11"), 32.11)

    def test_string_to_float_3(self):
        self.assertEqual(utils.string_to_float("32,11."), 32.11)

    def test_get_longest_string_one(self):
        in_list = ["aaa", "aaaa"]
        output = "aaaa"
        self.assertEqual(utils.get_longest_string(in_list), output)

    def test_get_longest_string_multiple(self):
        in_list = ["aaa", "aaaa", "aaaaa", "bbbbb"]
        output = ["aaaaa", "bbbbb"]
        self.assertEqual(utils.get_longest_string(in_list), output)

    def test_get_longest_match_short(self):
        options = ["bro", "järnvägsbro", "kyrka"]
        raw_data = "götaälvsbron"
        output = "bro"
        self.assertEqual(utils.get_longest_match(raw_data, options), output)

    def test_get_longest_match_long(self):
        options = ["bro", "järnvägsbro", "kyrka"]
        raw_data = "stora järnvägsbron"
        output = "järnvägsbro"
        self.assertEqual(utils.get_longest_match(raw_data, options), output)

    def test_get_longest_match_none(self):
        options = ["bro", "järnvägsbro", "kyrka"]
        raw_data = "skogskapellet"
        self.assertIsNone(utils.get_longest_match(raw_data, options))


class TestDatetimeMethods(unittest.TestCase):

    def test_parse_year_full(self):
        self.assertEqual(utils.parse_year("1888"), 1888)

    def test_parse_year_full_range(self):
        self.assertEqual(utils.parse_year("1991-2008"), (1991, 2008))

    def test_parse_year_short_range(self):
        self.assertEqual(utils.parse_year("1987-88"), (1987, 1988))

    def test_parse_year_invalid(self):
        self.assertIsNone(utils.parse_year("43432424"))
        self.assertIsNone(utils.parse_year("1999-foo"))
        self.assertIsNone(utils.parse_year("1999-1899"))
        self.assertIsNone(utils.parse_year("1999-2000-2003"))

    def test_date_to_dict_1(self):
        text = "1999-12-09"
        template = "%Y-%m-%d"
        output = {"year": 1999, "month": 12, "day": 9}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_date_to_dict_2(self):
        text = "09-12-1999"
        template = "%d-%m-%Y"
        output = {"year": 1999, "month": 12, "day": 9}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_date_to_dict_3(self):
        text = "12-1999"
        template = "%m-%Y"
        output = {"year": 1999, "month": 12}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_date_to_dict_4(self):
        text = "1999"
        template = "%Y"
        output = {"year": 1999}
        self.assertEqual(utils.date_to_dict(text, template), output)

    def test_dict_to_iso_date_full(self):
        date_dict = {"year": 1999, "month": 10, "day": 19}
        output = "1999-10-19"
        self.assertEqual(utils.dict_to_iso_date(date_dict), output)

    def test_dict_to_iso_date_year(self):
        date_dict = {"year": 1999}
        output = "1999"
        self.assertEqual(utils.dict_to_iso_date(date_dict), output)

    def test_dict_to_iso_date_year_month(self):
        date_dict = {"year": 1999, "month": 10}
        output = "1999-10"
        self.assertEqual(utils.dict_to_iso_date(date_dict), output)


class TestWikitext(unittest.TestCase):

    def test_remove_markup_simple(self):
        text = "[[Tegera Arena]], huvudentrén"
        output = "Tegera Arena, huvudentrén"
        self.assertEqual(utils.remove_markup(text), output)

    def test_remove_markup_linebreak_1(self):
        text = "[[Tegera Arena]],<br>huvudentrén"
        output = "Tegera Arena, huvudentrén"
        self.assertEqual(utils.remove_markup(text), output)

    def test_remove_markup_linebreak_2(self):
        text = "[[Tegera Arena]],<br/> huvudentrén"
        output = "Tegera Arena, huvudentrén"
        self.assertEqual(utils.remove_markup(text), output)

    def test_remove_markup_pipe(self):
        text = "[[Tegera Arena|Arenan]], huvudentrén"
        output = "Arenan, huvudentrén"
        self.assertEqual(utils.remove_markup(text), output)

    def test_count_wikilinks_none(self):
        text = "just text"
        self.assertEqual(utils.count_wikilinks(text), 0)

    def test_count_wikilinks_one(self):
        text = "[[Movikens masugn|Moviken]]"
        self.assertEqual(utils.count_wikilinks(text), 1)

    def test_count_wikilinks_two(self):
        text = "[[Tranås]] and also [[Svanesund]]"
        self.assertEqual(utils.count_wikilinks(text), 2)

    def test_string_is_q_item_pass(self):
        self.assertTrue(utils.string_is_q_item("Q1641992"))

    def test_string_is_q_item_fail(self):
        self.assertFalse(utils.string_is_q_item("some string"))

    def test_string_is_q_item_invalid(self):
        self.assertFalse(utils.string_is_q_item("Q34234vsf"))

    def test_wd_template_p(self):
        self.assertEqual(utils.wd_template("P", "17"), "{{P|17}}")

    def test_wd_template_q(self):
        self.assertEqual(utils.wd_template("Q", "Q34"), "{{Q|Q34}}")


class TestLegitHouseNumber(unittest.TestCase):

    def test_is_legit_house_number_1(self):
        text = "32"
        self.assertTrue(utils.is_legit_house_number(text))

    def test_is_legit_house_number_2(self):
        text = "2"
        self.assertTrue(utils.is_legit_house_number(text))

    def test_is_legit_house_number_3(self):
        text = "3b"
        self.assertTrue(utils.is_legit_house_number(text))

    def test_is_legit_house_number_4(self):
        text = "2 B"
        self.assertTrue(utils.is_legit_house_number(text))

    def test_is_legit_house_number_5(self):
        text = "3-5"
        self.assertTrue(utils.is_legit_house_number(text))

    def test_is_legit_house_number_6(self):
        text = "43B-43E"
        self.assertTrue(utils.is_legit_house_number(text))


class TestGetAddress(unittest.TestCase):

    def test_get_street_address_1(self):
        text = "Bruksvägen 23"
        lang = "sv"
        output = "Bruksvägen 23"
        self.assertEqual(utils.get_street_address(text, lang), output)

    def test_get_street_address_2(self):
        text = "Vilhelm Mobergs gata 4"
        lang = "sv"
        output = "Vilhelm Mobergs gata 4"
        self.assertEqual(utils.get_street_address(text, lang), output)

    def test_get_street_address_3(self):
        text = "Spånhult"
        lang = "sv"
        self.assertIsNone(utils.get_street_address(text, lang))

    def test_get_street_address_4(self):
        text = "Virserums station, Södra Järnvägsgatan 20"
        lang = "sv"
        output = "Södra Järnvägsgatan 20"
        self.assertEqual(utils.get_street_address(text, lang), output)

    def test_get_street_address_5(self):
        text = "Kyrkogatan 34, Dackestop"
        lang = "sv"
        output = "Kyrkogatan 34"
        self.assertEqual(utils.get_street_address(text, lang), output)

    def test_get_street_address_6(self):
        text = "Odlaregatan, Svalöv (Gamla 9:an)."
        lang = "sv"
        self.assertIsNone(utils.get_street_address(text, lang))

    def test_get_street_address_7(self):
        text = "Bröderna Nilssons väg 14, Onslunda, 273 95 Tomelilla"
        lang = "sv"
        output = "Bröderna Nilssons väg 14"
        self.assertEqual(utils.get_street_address(text, lang), output)

    def test_get_street_address_8(self):
        text = "Norra Finnskoga Hembygdsgård , Höljes, Solrosvägen 2,"
        lang = "sv"
        output = "Solrosvägen 2"
        self.assertEqual(utils.get_street_address(text, lang), output)

    def test_get_street_address_9(self):
        text = ("Svaneholms slott ligger i Skurup i Skåne, "
                "fyra mil öster om Malmö, vid väg E65.")
        lang = "sv"
        self.assertIsNone(utils.get_street_address(text, lang))


class TestShipDimensions(unittest.TestCase):

    def test_parse_ship_dimensions_1(self):
        text = "Längd: 18,55 Bredd: 4,06 Djup: Brt: 37,78"
        output = {"length": 18.55, "width": 4.06, "grt": 37.78}
        self.assertEqual(utils.parse_ship_dimensions(text), output)

    def test_parse_ship_dimensions_2(self):
        text = "Längd: 17.5 Bredd: 5.8 Djup: 2.50 Brt: 47"
        output = {"length": 17.5, "width": 5.8, "draft": 2.50, "grt": 47}
        self.assertEqual(utils.parse_ship_dimensions(text), output)

    def test_parse_ship_dimensions_3(self):
        text = "Längd:  Bredd:  Djup:  Brt:"
        output = {}
        self.assertEqual(utils.parse_ship_dimensions(text), output)

    def test_parse_ship_dimensions_4(self):
        text = "Längd: 14,76. Bredd: 4,83 Djup: Brt: 22"
        output = {"length": 14.76, "width": 4.83, "grt": 22}
        self.assertEqual(utils.parse_ship_dimensions(text), output)


class TestCoordinates(unittest.TestCase):

    def test_tuple_is_coords_pass(self):
        self.assertTrue(utils.tuple_is_coords((-56.16, -14.86667)))
        self.assertTrue(utils.tuple_is_coords((56.16566667, 14.86541667)))

    def test_tuple_is_coords_fail(self):
        self.assertFalse(utils.tuple_is_coords((56.16566667)))
        self.assertFalse(utils.tuple_is_coords((56.16566667, 14.86541667, 14)))
        self.assertFalse(utils.tuple_is_coords(("56.16566667", 14.86541667)))


class TestMisc(unittest.TestCase):

    def test_remove_empty_dicts_from_list(self):
        dic_list = [{"foo": 1}, {}, {}, {"bar": "cat"}]
        output = [{"foo": 1}, {"bar": "cat"}]
        self.assertEqual(utils.remove_empty_dicts_from_list(dic_list), output)

    def test_is_valid_url(self):
        url = ("http://pywikibot.readthedocs.io/en/latest/_modules/"
               "pywikibot/page/?highlight=WbQuantity")
        self.assertTrue(utils.is_valid_url(url))


class TestCommons(unittest.TestCase):

    def test_file_is_on_commons_pass(self):
        self.assertTrue(utils.file_is_on_commons("Loojangu värvid 2.jpg"))

    def test_file_is_on_commons_fail(self):
        self.assertFalse(utils.file_is_on_commons("adgffhgadftgfhsfgdg"))

    def test_commonscat_exists_pass(self):
        self.assertTrue(
            utils.commonscat_exists("Libraries in Germany by city"))

    def test_commonscat_exists_fail(self):
        self.assertFalse(utils.commonscat_exists("adgafgtaffrsdf"))


class TestWikidata(unittest.TestCase):

    def setUp(self):
        self.wikidata_site = utils.create_site_instance("wikidata", "wikidata")

    def test_get_value_of_property_page(self):
        runestone = "Q7899135"
        country = "P17"
        sweden = ["Q34"]
        self.assertEqual(
            utils.get_value_of_property(runestone, country, self.wikidata_site),
            sweden)

    def test_get_value_of_property_string(self):
        se_heritage = "P1260"
        runestone = "Q7899135"
        result = ["raa/fmi/10028200010001"]
        self.assertEqual(
            utils.get_value_of_property(runestone, se_heritage, self.wikidata_site),
            result)

    def test_get_P31_one(self):
        """
        August Strindberg -> human
        """
        self.assertEqual(utils.get_P31("Q7724", self.wikidata_site), ["Q5"])

    def test_get_P31_two(self):
        """
        Felis manul -> [taxon, synonym]
        """
        self.assertEqual(utils.get_P31("Q24006022", self.wikidata_site), ["Q16521", "Q1040689"])

    def test_get_P31_none(self):
        """
        model organism -> [] (it's only a subclass)
        """
        self.assertEqual(utils.get_P31("Q213907", self.wikidata_site), [])

    def test_is_whitelisted_P31_pass(self):
        """
        Solberg, Kungälvs kommun -> småort
        """
        self.assertTrue(utils.is_whitelisted_P31("Q2263578", self.wikidata_site, ["Q14839548"]))

    def test_is_whitelisted_P31_fail(self):
        """
        Solberg, Kungälvs kommun -> [city, tätort]
        """
        self.assertFalse(
            utils.is_whitelisted_P31("Q2263578", self.wikidata_site, ["Q515", "Q12813115"]))


class TestWikipedia(unittest.TestCase):

    def setUp(self):
        self.wikidata_site = utils.create_site_instance("wikidata", "wikidata")

    def test_q_from_wikipedia_succeed(self):
        self.assertEqual(
            utils.q_from_wikipedia("sv", "Norrala socken"), "Q10602691")

    def test_q_from_wikipedia_none(self):
        self.assertIsNone(utils.q_from_wikipedia("sv", "Användare:Vesihiisi"))
        self.assertIsNone(
            utils.q_from_wikipedia("sv", "This page does not exist"))

    def test_q_from_wikipedia_disambig(self):
        wiki_page = utils.q_from_wikipedia("fi", "1 (täsmennyssivu)")
        self.assertIsNone(wiki_page)

    def test_q_from_first_wikilink(self):
        text = ("'''Norrala socken'''"
                " ligger i [[Hälsingland]], ingår sedan 1971 i "
                "[[Söderhamns kommun]] och motsvarar från 2016 "
                "[[Norrala distrikt]].")
        self.assertEqual(utils.q_from_first_wikilink("sv", text), "Q206564")

    def test_wp_page_exists_pass(self):
        self.assertTrue(utils.wp_page_exists("sv", "Långtora socken"))

    def test_wp_page_exists(self):
        self.assertFalse(utils.wp_page_exists("sv", "datfyasqwewrq"))


class TestSocken(unittest.TestCase):

    def test_socken_to_q_1(self):
        self.assertEqual(utils.socken_to_q("Holm", "Medelpad"), "Q10525331")

    def test_socken_to_q_2(self):
        self.assertEqual(utils.socken_to_q("Holm", "Uppland"), "Q10525332")

    def test_socken_to_q_3(self):
        self.assertEqual(utils.socken_to_q("Långtora", "Uppland"), "Q10572689")

    def test_socken_to_q_4(self):
        self.assertEqual(
            utils.socken_to_q("Linde", "Västmanland"), "Q10562482")

    def test_socken_to_q_5(self):
        self.assertEqual(utils.socken_to_q("Löts", "Öland"), "Q10572936")

    def test_socken_to_q_6(self):
        self.assertEqual(utils.socken_to_q("Egby", "Öland"), "Q10480210")

    def test_socken_to_q_7(self):
        self.assertEqual(utils.socken_to_q("Backa", "Bohuslän"), "Q10424141")

    def test_socken_to_q_8(self):
        self.assertEqual(
            utils.socken_to_q("Solberga", "Bohuslän"),  "Q2788890")


class TestBbr(unittest.TestCase):

    def test_get_http_code_good(self):
        url = "http://kulturarvsdata.se/raa/bbr/21300000003265"
        self.assertEqual(utils.get_http_code(url), 200)

    def test_get_http_code_bad(self):
        url = "http://kulturarvsdata.se/raa/bbra/21300000003265"
        self.assertEqual(utils.get_http_code(url), 404)

    def test_get_bbr_link(self):
        self.assertEqual(
            utils.get_bbr_link("21320000019150"), "raa/bbra/21320000019150")
        self.assertEqual(
            utils.get_bbr_link("21300000003265"), "raa/bbr/21300000003265")


if __name__ == '__main__':
    unittest.main()
