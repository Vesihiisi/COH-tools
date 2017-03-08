import unittest
import importer_utils as utils


class TestStringMethods(unittest.TestCase):

    def test_contains_digit(self):
        self.assertTrue(utils.contains_digit("fna3fs"))
        self.assertFalse(utils.contains_digit("foo"))

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


class TestRemoveMarkup(unittest.TestCase):

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
