from os import path
import json
import mwparserfromhell as wparser
import pywikibot
import re
import wikidataStuff.helpers as helpers
from importer_utils import *
import pytest

MAPPING_DIR = "mappings"
ADM0 = load_json(path.join(MAPPING_DIR, "adm0.json"))
PROPS = load_json(path.join(MAPPING_DIR, "props_general.json"))


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


def is_legit_house_number(text):
    number_regex = re.compile(
        '\d{1,3}\s?([A-Z]{1})?((-|–)\d{1,3})?\s?([A-Z]{1})?')
    m = number_regex.match(text)
    if m:
        return True
    else:
        return False


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


def get_street_address(address, language):
    print(address)
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
                    " torg", "torget", " plats", "platsen", " gränd"]
        if "," in address:
            address_split = address.split(",", re.IGNORECASE)
            for part in address_split:
                if any(substring in part for substring in patterns) and contains_digit(part):
                    interesting_part = part.strip()
        else:
            if any(substring in address for substring in patterns) and contains_digit(address):
                interesting_part = address
        if len(interesting_part) > 1:
            interesting_part_split = interesting_part.split(" ")
            for part in interesting_part_split:
                if contains_digit(part) and is_legit_house_number(part):
                    legit_address = interesting_part.rstrip(',.-')
        return legit_address


def test_get_street_address_1():
    assert get_street_address("Bruksvägen 23", "sv") == "Bruksvägen 23"


def test_get_street_address_2():
    assert get_street_address(
        "Vilhelm Mobergs gata 4", "sv") == "Vilhelm Mobergs gata 4"


def test_get_street_address_3():
    assert get_street_address("Spånhult", "sv") == None


def test_get_street_address_4():
    assert get_street_address(
        "Virserums station, Södra Järnvägsgatan 20", "sv") == "Södra Järnvägsgatan 20"


def test_get_street_address_5():
    assert get_street_address(
        "Kyrkogatan 34, Dackestop", "sv") == "Kyrkogatan 34"


def test_get_street_address_6():
    assert get_street_address(
        "Odlaregatan, Svalöv (Gamla 9:an).", "sv") == None


def test_get_street_address_7():
    assert get_street_address(
        "Bröderna Nilssons väg 14, Onslunda, 273 95 Tomelilla", "sv") == "Bröderna Nilssons väg 14"


def test_get_street_address_8():
    assert get_street_address(
        "Norra Finnskoga Hembygdsgård , Höljes, Solrosvägen 2,", "sv") == "Solrosvägen 2"


def get_wikilinks(text):
    parsed = wparser.parse(text)
    return parsed.filter_wikilinks()


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


class Monument(object):

    def print_wd(self):
        print(
            json.dumps(self.wd_item,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False)
        )

    def set_country(self):
        country = [item["item"]
                   for item in ADM0 if item["code"].lower() == self.adm0]
        self.wd_item["statements"][PROPS["country"]] = country

    def set_is(self, mapping):
        default_is = mapping.file_content["default_is"]
        self.wd_item["statements"][PROPS["is"]] = [default_is["item"]]

    def set_labels(self):
        self.wd_item["labels"] = {self.lang: remove_markup(self.name)}

    def set_heritage(self, mapping):
        heritage = mapping.file_content["heritage"]
        self.wd_item["statements"][PROPS["heritage_status"]] = helpers.listify(
            heritage["item"])

    def set_coords(self):
        if self.lat and self.lon:
            self.wd_item["statements"][PROPS["coordinates"]] = helpers.listify(
                (self.lat, self.lon))

    def set_image(self):
        if self.image:
            self.wd_item["statements"][PROPS["image"]] = self.image

    def set_commonscat(self):
        if self.commonscat:
            self.wd_item["statements"][PROPS["commonscat"]] = self.commonscat

    def set_street_address(self):
        """
        NOTE: P:located at street address says "Include building number through to post code"
        In most cases, there's no post code in the data!
        In practice though, it's often omitted....
        Compare with located on street (P669) and its qualifier street number (P670).
        """
        if self.address:
            self.wd_item["statements"][
                PROPS["located_street"]] = get_street_address(
                    self.address, self.lang)

    def exists(self, mapping):
        self.wd_item["wd-item"] = None
        if self.monument_article:
            wd_item = q_from_wikipedia(self.lang, self.monument_article)
            self.wd_item["wd-item"] = wd_item

    def construct_wd_item(self, mapping, data_files=None):
        self.wd_item = {}
        self.wd_item["statements"] = {}
        self.set_labels()
        self.set_country()
        self.set_is(mapping)
        self.set_heritage(mapping)
        self.set_coords()
        self.set_image()
        self.set_commonscat()
        self.set_street_address()
        # self.exists(mapping)

    def __init__(self, db_row_dict, mapping, data_files):
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.construct_wd_item(mapping)
        self.data_files = data_files

    def get_fields(self):
        return sorted(list(self.__dict__.keys()))


class SeFornminSv(Monument):

    def update_labels(self):
        if len(self.namn) == 0:
            self.wd_item["labels"][self.lang] = self.raa_nr
        else:
            self.wd_item["labels"][self.lang] = self.namn

    def set_descriptions(self):
        DESC_BASE = "fornminne"
        if len(self.typ) > 0:
            self.wd_item["descriptions"] = {"sv": self.typ.lower()}
        else:
            self.wd_item["descriptions"] = {"sv": DESC_BASE}
        self.wd_item["descriptions"]["sv"] += " i " + self.landskap

    def set_raa(self):
        self.wd_item["statements"][
            PROPS["raa-nr"]] = helpers.listify(self.raa_nr)

    def set_adm_location(self):
        municip_dict = load_json(path.join(
            MAPPING_DIR, "sweden_municipalities.json"))
        pattern_en = self.adm2.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern_en][0]
            self.wd_item["statements"][
                PROPS["located_adm"]] = helpers.listify(municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_type(self):
        if self.typ:
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                self.wd_item["statements"]["P31"] = special_type
            except IndexError:
                return

    def set_location(self):
        if self.address:
            if "[[" in self.address:
                wikilinks = get_wikilinks(self.address)
                if len(wikilinks) == 1:
                    target_page = wikilinks[0].title
                    print(self.address)
                    print(target_page)
                    wd_item = q_from_wikipedia(self.lang, target_page)
                    self.wd_item["statements"][PROPS["location"]] = wd_item

    def set_inception(self):
        # TODO
        # This is messy and not super prioritized...
        return

    def update_wd_item(self):
        self.update_labels()
        self.set_descriptions()
        self.set_raa()
        self.set_adm_location()
        self.set_type()
        self.set_location()
        self.set_inception()

    def __init__(self, db_row_dict, mapping, data_files):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()


class SeArbetslSv(Monument):

    def update_labels(self):
        return

    def set_descriptions(self):
        DESC_BASE = "arbetslivsmuseum"
        if len(self.typ) > 0:
            self.wd_item["descriptions"] = {self.lang: self.typ.lower()}
        else:
            self.wd_item["descriptions"] = {self.lang: DESC_BASE}

    def add_location_to_desc(self, municipality):
        self.wd_item["descriptions"][self.lang] += " i " + municipality

    def set_adm_location(self):
        municip_dict = self.data_files["municipalities"]
        pattern = self.adm2.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "en"].lower() == pattern][0]
            self.wd_item["statements"][
                PROPS["located_adm"]] = helpers.listify(municipality)
            swedish_name = [x["sv"]
                            for x in municip_dict
                            if x["item"] == municipality][0]
            self.add_location_to_desc(swedish_name)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_type(self):
        if self.typ:
            table = self.data_files["types"]["mappings"]
            type_to_search_for = self.typ.lower()
            try:
                special_type = [table[x]["items"]
                                for x in table
                                if x.lower() == type_to_search_for][0]
                self.wd_item["statements"]["P31"] = special_type
            except IndexError:
                return
        return

    def set_location(self):
        settlements_dict = self.data_files["settlements"]
        if self.ort:
            try:
                location = [x["item"] for x in settlements_dict if x[
                    "sv"].strip() == remove_markup(self.ort)][0]
                self.wd_item["statements"][
                    PROPS["location"]] = helpers.listify(location)
            except IndexError:
                #print("Could not find ort: " + self.ort)
                return

    def update_wd_item(self):
        self.update_labels()
        self.set_descriptions()
        self.set_adm_location()
        self.set_type()
        self.set_location()

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()
