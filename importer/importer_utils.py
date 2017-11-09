#!/usr/bin/python
# -*- coding: utf-8  -*-
import json
import csv
import re
import os
import mwparserfromhell as wparser
import string
import pywikibot
import datetime
import requests
import pymysql
import random
from urllib.parse import quote
from wikidataStuff.WikidataStuff import WikidataStuff as wds

site_cache = {}


def remove_empty_dicts_from_list(list_of_dicts):
    return [i for i in list_of_dicts if i]


def save_to_file(filename, content, silent=False):
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(content)
        if not silent:
            print("SAVED FILE " + filename)


def json_to_file(filename, json_content, silent=False):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(json_content, f, sort_keys=True,
                  indent=4,
                  ensure_ascii=False,
                  default=datetime_convert)
        if not silent:
            print("SAVED FILE " + filename)


def create_dir(out_path):
    """
    Create a directory if it doesn't exist.

    @param out_path: directory to create
    """
    if not out_path:
        raise ValueError('Cannot a create directory without a name.')
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    elif os.path.isfile(out_path):
        raise ValueError(
            'Cannot create the directory "{}" as a file with that name '
            'already exists.'.format(out_path))


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
    except pymysql.ProgrammingError:
        return False


def load_json(filename):
    try:
        with open(filename, encoding="utf-8") as f:
            try:
                return json.load(f)
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError:
        print("File {} does not exist.".format(filename))


def datetime_convert(dt_object):
    if isinstance(dt_object, datetime.datetime):
        return dt_object.__str__()


def remove_multiple_spaces(text):
    return re.sub(' +', ' ', text)


def remove_markup(text):
    remove_br = re.compile('<br.*?>\W*', re.I)
    text = remove_br.sub(' ', text)
    text = " ".join(text.split())
    if "[" in text or "''" in text:
        text = wparser.parse(text)
        text = text.strip_code()
    return remove_multiple_spaces(text.strip())


def contains_digit(text):
    return any(x.isdigit() for x in text)


def get_external_links(wikitext):
    """Retrieve external url's from wikitext."""
    urls = []
    links = wparser.parse(wikitext).filter_external_links()
    if len(links) > 0:
        for link in links:
            urls.append(link.url)
    return urls


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
                if (any(substring in part for substring in patterns) and
                        contains_digit(part)):
                    interesting_part = part.strip()
        else:
            if (any(substring in address for substring in patterns) and
                    contains_digit(address)):
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


def get_unique_wikilinks(text):
    results = []
    wikilinks = get_wikilinks(text)
    for wikilink in wikilinks:
        if wikilink not in results:
            results.append(wikilink)
    return results


def count_wikilinks(text):
    return len(get_wikilinks(text))


def q_from_wikipedia(language, page_title):
    """
    Get the ID of the WD item linked to a wp page.

    If the page exists, has no item and is in the article
    namespace, create an item for it.
    """
    # various cleanup
    if page_title.startswith("[[") and page_title.endswith("]]"):
        internal_links = get_wikilinks(page_title)
        if not internal_links:
            return
        page_title = internal_links[0].title

    if isinstance(page_title, str):
        # get_wikilinks()[0].title does not return a str
        page_title = page_title.replace('\n', ' ')

    if not page_title:
        return

    wp_site = pywikibot.Site(language, "wikipedia")
    page = pywikibot.Page(wp_site, page_title)
    summary = "Creating item for {} on {}wp."
    summary = summary.format(page_title, language)
    wd_repo = create_site_instance("wikidata", "wikidata")
    wdstuff = wds(wd_repo, edit_summary=summary, no_wdss=True)
    if page.exists():
        if page.isRedirectPage():
            page = page.getRedirectTarget()
        if page.isDisambig():
            return
        try:
            item = pywikibot.ItemPage.fromPage(page)
        except pywikibot.NoPage:
            if page.namespace() != 0:  # main namespace
                return
            item = wdstuff.make_new_item_from_page(page, summary)
        return item.getID()


def q_from_first_wikilink(language, text):
    try:
        wikilink = get_wikilinks(text)[0]
        return q_from_wikipedia(language, wikilink.title)
    except IndexError:
        return


def get_matching_items_from_dict(value, dict_name):
    """
    Return all items in a dict for which the label matches the provided value.

    @param value: the value to match
    @param dict_name: the dict to look in
    """
    matches = [dict_name[x]["items"]
               for x in dict_name if x.lower() == value]
    if len(matches) == 0:
        return []
    else:
        return matches[0]


def get_item_from_dict_by_key(dict_name,
                              search_term,
                              search_in,
                              return_content_of="item"):
    """
    Return all items in a dict with a certain field match.

    It will normally return the content of the field
    'item' which is expected to contain a Q-item.
    It is, however, possible to overwrite the name
    of the field whose contents should be returned.

    @param dict_name: the dictionary to look in
    @pram search_term: the value to match
    @param search_in: the field in which to look for matching value
    @param return_content_of: the field whose content to return
    """
    results = []
    matches = [x for x in dict_name if x[search_in] == search_term]
    if len(matches) == 0:
        return []
    else:
        for match in matches:
            results.append(match[return_content_of])
        return results


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
            if (len(part_one) == len(part_two) and
                    int(part_two) > int(part_one)):
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


def get_longest_string(in_list):
    """
    Get the longest string(s) in a list.

    :param in_list: list of strings
    :return: single string if there's only one with the max length,
             or a list of strings if there are several.
    """
    if len(in_list) == 0:
        return None
    max_length = max(len(x) for x in in_list)
    matches = [x for x in in_list if len(x) == max_length]
    if len(matches) == 1:
        return matches[0]
    else:
        return matches


def get_longest_match(word, keywords):
    """
    Given a list of keywords, get longest keyword that overlaps with input.

    A naive attempt to match words in languages that use
    compound nouns written together. Given a string and a list of
    keywords, return the longest of these keywords that's
    contained in the input string. That way, if the keyword list
    contains both a simple word ("bro") and its compound ("järnvägsbro"),
    we only get the more specific one:
        * "götaälvsbron" -> "bro"
        * "en stor järnvägsbro" -> "järnvägsbro"
    """
    matches = []
    for k in keywords:
        if k in word:
            matches.append(k)
    return get_longest_string(matches)


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


def is_vowel(char):
    vowels = "auoiyéeöåäáæø"
    if char.lower() in vowels:
        return True
    else:
        return False


def get_last_char(text):
    return text[-1]


def last_char_is_vowel(text):
    return is_vowel(get_last_char(text))


def first_char_is_number(text):
    """Check if string starts with a number."""
    return text[0].isdigit()


def socken_to_q(socken, landskap):
    if last_char_is_vowel(socken) or get_last_char(socken) == "s":
        socken_name = socken + " socken"
    else:
        socken_name = socken + "s socken"
    socken_and_landskap = socken_name + ", " + landskap
    if wp_page_exists("sv", socken_and_landskap):
        return q_from_wikipedia("sv", socken_and_landskap)
    elif wp_page_exists("sv", socken_name):
        return q_from_wikipedia("sv", socken_name)


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


def get_rid_of_brackets(text):
    if "(" in text:
        return re.sub('\(.*?\)', '', text).strip()
    else:
        return text


def get_text_inside_brackets(text):
    """
    Get the content of the first encountered occurence of round brackets.

    Handles nested brackets by getting the content of
    the first level:
        foo (cat) → cat
        text (foo (bar (cat))) around → foo (bar (cat))

    Does not handle multiple instances of brackets on the same level.
        text (foo) text (bar) → ValueError

    Does not handle mismatched brackets.
        foo (bar → ValueError
    """
    if "(" in text:
        first_bracket_index = text.find('(')
        last_bracket_index = text[first_bracket_index:].rfind(')')
        if last_bracket_index < 0 or text[:first_bracket_index].rfind(')') > 0:
            raise ValueError("Unmatched brackets encountered.")
        last_bracket_index += first_bracket_index
        result = text[first_bracket_index + 1:last_bracket_index]
        if (result.find(')') > 0 and
                (result.find('(') > result.find(')') or
                    result.find('(') < 0)):
            raise ValueError("Unmatched brackets encountered.")
        return result
    else:
        return text


def get_number_from_string(text):
    try:
        result = int(''.join(part for part in text if part.isdigit()))
    except ValueError:
        result = None
    return result


def string_is_q_item(text):
    pattern = re.compile("^Q[0-9]+$", re.I)
    try:
        m = pattern.match(text)
    except TypeError:
        return False
    if m:
        return True
    else:
        return False


def string_is_p_item(text):
    pattern = re.compile("^P[0-9]+$", re.I)
    try:
        m = pattern.match(text)
    except TypeError:
        return False
    if m:
        return True
    else:
        return False


def tuple_is_coords(sometuple):
    result = False
    if isinstance(sometuple, tuple) and len(sometuple) == 2:
        if all(isinstance(x, float) for x in sometuple):
            result = True
    return result


def file_is_on_commons(text):
    text = text.replace(" ", "_")
    site = create_site_instance("commons", "commons")
    page = pywikibot.Page(site, "File:" + text)
    return page.exists()


def commonscat_exists(text):
    text = text.replace(" ", "_")
    site = create_site_instance("commons", "commons")
    page = pywikibot.Page(site, "Category:" + text)
    return page.exists()


def wp_page_exists(language, title):
    site = create_site_instance(language, "wikipedia")
    page = pywikibot.Page(site, title)
    if page.exists():
        return True
    else:
        return False


def is_valid_url(url):
    import re
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    try:
        m = pattern.match(url)
    except TypeError:
        return False
    if m:
        return True
    else:
        return False


def datetime_object_to_dict(datetime_object):
    date_dict = {}
    date_dict["year"] = datetime_object.year
    date_dict["day"] = datetime_object.day
    date_dict["month"] = datetime_object.month
    return date_dict


def datetime_to_dict(date_obj, dateformat):
    """Convert a datetime object to a dict."""
    date_dict = {}
    date_dict["year"] = date_obj.year
    if "%m" in dateformat:
        date_dict["month"] = date_obj.month
    if "%d" in dateformat:
        date_dict["day"] = date_obj.day
    return date_dict


def date_to_dict(datestring, dateformat):
    """Convert a datet string to a dict."""
    date_obj = datetime.datetime.strptime(datestring, dateformat)
    return datetime_to_dict(date_obj, dateformat)


def today_dict():
    """Get today's date as pywikibot-ready dictionary."""
    return datetime_object_to_dict(datetime.date.today())


def dict_to_iso_date(date_dict):
    """
    Convert pywikiboty-style date dictionary
    to ISO string ("2002-10-23").

    @param date_dict: dictionary like
    {"year" : 2002, "month" : 10, "day" : 23}
    """
    iso_date = ""
    if "year" in date_dict:
        iso_date += str(date_dict["year"])
    if "month" in date_dict:
        iso_date += "-" + str(date_dict["month"])
    if "day" in date_dict:
        iso_date += "-" + str(date_dict["day"])
    return iso_date


def append_line_to_file(text, filename):
    with open(filename, 'a', encoding="utf-8") as f:
        f.write(text + "\n")


def dump_list_to_file(some_list, filename):
    f = open(filename, 'w', encoding="utf-8")
    for item in some_list:
        f.write(item + "\n")


def wd_template(template_type, value):
    return "{{" + template_type + "|" + value + "}}"


def get_current_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')


def get_random_list_sample(some_list, amount):
    return random.sample(some_list, amount)


def get_value_of_property(q_number, property_id, site):
    results = []
    item = pywikibot.ItemPage(site, q_number)
    if item.exists() and item.claims.get(property_id):
        for claim in item.claims.get(property_id):
            target = claim.getTarget()
            if isinstance(target, pywikibot.ItemPage):
                target = target.getID()
            results.append(target)
    return results


def get_P31(q_number, site):
    return get_value_of_property(q_number, "P31", site)


def is_whitelisted_P31(q_number, site, allowed_values):
    result = False
    all_P31s = get_P31(q_number, site)
    if all_P31s:
        for P31 in all_P31s:
            if P31 in allowed_values:
                result = True
    else:
        # A great many items do not have any P31 at all,
        # in which case assume it's correct.
        # Otherwise there'd be too many false negatives.
        result = True
    return result


def is_blacklisted_P31(q_number, site, dissalowed_values):
    # Also blacklist any items which contains a P279 (sub-class) statement
    # as these by definition cannot be unique instances
    if len(get_value_of_property(q_number, "P279", site)) > 0:
        return True

    item_P31 = get_P31(q_number, site)
    if len(set(dissalowed_values).intersection(set(item_P31))) > 0:
        # this means one of this item's P31's is in the
        # disallowed list
        return True
    return False


def is_right_country(q_number, site, expected_country):
    """Ensure that the target item has the expected country."""
    item_P17 = get_value_of_property(q_number, "P17", site)
    if not item_P17 or expected_country in item_P17:
        return True
    return False


def create_wlm_url(country, language, id):
    url_base = ("https://tools.wmflabs.org/heritage/api/api.php?"
                "action=search&format=json&srcountry={}&srlang={}&srid={}")

    return url_base.format(
        country, language, quote(id))


def create_site_instance(language, family):
    """Create an instance of a Wiki site (convenience function)."""
    site_key = (language, family)
    site = site_cache.get(site_key)
    if not site:
        site = pywikibot.Site(language, family)
        site_cache[site_key] = site
    return site


def package_quantity(value, unit=None):
    """Package a quantity value in a standardised form."""
    quantity = {"quantity_value": value}
    if unit:
        quantity["unit"] = unit
    return quantity


def package_time(date_dict):
    """Package a time/date statement in a standardised form."""
    return {"time_value": date_dict}


def package_monolingual(text, lang):
    """Package a monolingual statement in a standardised form."""
    return {"monolingual_value": text, "lang": lang}


def get_data_from_csv_file(filename):
    """Load data from csv file into a list."""
    with open(filename, "r") as f_obj:
        reader = csv.DictReader(f_obj, delimiter=',')
        csv_data = list(reader)
    return csv_data
