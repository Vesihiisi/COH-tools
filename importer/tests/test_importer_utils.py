import string
import unittest
import importer_utils as utils


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


class TestWikiCode(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
