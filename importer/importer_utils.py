import json
import re
import mwparserfromhell as wparser
import string
import pywikibot
import datetime
import requests


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


def get_number_of_rows(connection, tablename):
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM `" + tablename + "`"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]


def table_exists(connection, tablename):
    try:
        if get_number_of_rows(connection, tablename) > 0:
            return True
    except pymysql.ProgrammingError as e:
        return False


def load_json(filename):
    try:
        with open(filename) as f:
            try:
                return json.load(f)
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError as e:
        print("File {} does not exist.".format(filename))


def datetime_convert(dt_object):
    if isinstance(dt_object, datetime.datetime):
        return dt_object.__str__()


def remove_markup(text):
    remove_br = re.compile('<br.*?>\W*', re.I)
    text = remove_br.sub(' ', text)
    text = " ".join(text.split())
    if "[" in text:
        text = wparser.parse(text)
        text = text.strip_code()
    return text.strip()


def contains_digit(text):
    return any(x.isdigit() for x in text)


def is_legit_house_number(text):
    number_regex = re.compile(
        '\d{1,3}\s?([A-Z]{1})?((-|–)\d{1,3})?\s?([A-Z]{1})?')
    m = number_regex.match(text)
    if m:
        return True
    else:
        return False


def get_street_address(address, language):
    address = remove_markup(address)
    if language == "sv":
        # Try to see if it's a legit-ish street address
        # numbers like 3, 3A, 2-4
        # oh, and sometimes it's not a _street_ name: "Norra Kik 7"
        # street names can consist of several words: "Nils Ahlins gata 19"
        # how about: "Östra skolan, Bergaliden 24"
        # "Västanåvägen 12-6, Näsum"
        # If there's a comma, order can vary
        #####
        # regex should match: 12, 3, 43-45, 34b, 43B, 25 a, 43B-43E
        legit_address = None
        interesting_part = ""
        patterns = ["gatan", "vägen", " väg", " gata",
                    " torg", "torget", " plats", "platsen", " gränd",
                    "kajen", "promenaden", "liden", "stigen"]
        if "," in address:
            address_split = address.split(",", re.IGNORECASE)
            for part in address_split:
                if (any(substring in part for substring in patterns)
                        and contains_digit(part)):
                    interesting_part = part.strip()
        else:
            if (any(substring in address for substring in patterns)
                    and contains_digit(address)):
                interesting_part = address
        if len(interesting_part) > 1:
            interesting_part_split = interesting_part.split(" ")
            for part in interesting_part_split:
                if contains_digit(part) and is_legit_house_number(part):
                    legit_address = interesting_part.rstrip(',.-')
        return legit_address


def get_wikilinks(text):
    parsed = wparser.parse(text)
    return parsed.filter_wikilinks()


def count_wikilinks(text):
    return len(get_wikilinks(text))


def q_from_wikipedia(language, page_title):
    site = pywikibot.Site(language, "wikipedia")
    page = pywikibot.Page(site, page_title)
    if page.exists():
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        try:
            item = pywikibot.ItemPage.fromPage(page)
            return item.getID()
        except pywikibot.NoPage:
            print("Failed to get page for {} - {}."
                  "It probably does not exist.".format(
                      language, page_title)
                  )
            return


def q_from_first_wikilink(language, text):
    try:
        wikilink = get_wikilinks(text)[0]
        return q_from_wikipedia(language, wikilink.title)
    except IndexError:
        return


def legit_year(text):
    year = None
    if text and text.isdigit():
        if int(text) >= 1 and int(text) <= 2020:
            year = int(text)
    return year


def legit_year_range(text):
    year_range = None
    if "-" in text and len(text.split("-")) == 2:
        part_one = text.split("-")[0]
        part_two = text.split("-")[1]
        if parse_year(part_one) and parse_year(part_two):
            if (len(part_one) == len(part_two)
                    and int(part_two) > int(part_one)):
                year_range = (int(part_one), int(part_two))
            elif len(part_one) == 4 and len(part_two) == 2:
                full_length_part_two = part_one[:2] + part_two
                if int(full_length_part_two) > int(part_one):
                    year_range = (int(part_one), int(full_length_part_two))
    return year_range


def parse_year(text):
    year = None
    if legit_year(text):
        year = legit_year(text)
    elif ("-") in text:
        year = legit_year_range(text)
    return year


def remove_characters(text, string_of_chars_to_remove):
    translator = str.maketrans(
        {key: None for key in string_of_chars_to_remove})
    return text.translate(translator)


def comma_to_period(text):
    return text.replace(",", ".")


def remove_marks_from_ends(text):
    return text.lstrip(string.punctuation).rstrip(string.punctuation)


def string_to_float(text):
    text_clean = remove_marks_from_ends(text)
    text_clean = comma_to_period(text_clean)
    return float(text_clean)


def parse_ship_dimensions(text):
    dimensions_vocab = {
        "längd": "length",
        "bredd": "width",
        "djup": "draft",
        "brt": "grt"
    }
    dimensions_dict = {}
    dimensions_list = text.split(" ")
    for i, item in enumerate(dimensions_list):
        if contains_digit(item):
            try:
                number_part = string_to_float(comma_to_period(item))
                associated_word = remove_marks_from_ends(
                    dimensions_list[i - 1].lower())
                word_part = dimensions_vocab[associated_word]
                dimensions_dict[word_part] = number_part
            except (ValueError, KeyError):
                continue
    return dimensions_dict


def get_http_code(url):
    r = requests.get(url)
    return r.status_code


def get_bbr_link(text):
    """
    raa/bbr/21300000003265
    """
    base_url = "http://kulturarvsdata.se/raa/"
    url_bbr = base_url + "bbr/" + text
    url_bbra = base_url + "bbra/" + text
    if get_http_code(url_bbra) == 200:
        return "raa/bbra/" + text
    elif get_http_code(url_bbr) == 200:
        return "raa/bbr/" + text