from os import path
import json
import mwparserfromhell as wparser
import pywikibot
import re
import wikidataStuff.helpers as helpers
from importer_utils import *

MAPPING_DIR = "mappings"
ADM0 = load_json(path.join(MAPPING_DIR, "adm0.json"))
PROPS = load_json(path.join(MAPPING_DIR, "props_general.json"))


class Monument(object):

    def print_wd(self):
        print(
            json.dumps(self.wd_item,
                       sort_keys=True,
                       indent=4,
                       ensure_ascii=False,
                       default=datetime_convert)
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

    def set_registrant_url(self):
        if self.registrant_url:
            self.wd_item["registrant_url"] = self.registrant_url

    def set_street_address(self):
        """
        NOTE: P:located at street address says "Include building number through to post code"
        In most cases, there's no post code in the data!
        In practice though, it's often omitted....
        Compare with located on street (P669) and its qualifier street number (P670).
        """
        if self.address:
            processed_address = get_street_address(self.address, self.lang)
            if processed_address is not None:
                self.wd_item["statements"][
                    PROPS["located_street"]] = processed_address

    def exists(self, mapping):
        self.wd_item["wd-item"] = None
        if self.monument_article:
            wd_item = q_from_wikipedia(self.lang, self.monument_article)
            self.wd_item["wd-item"] = wd_item

    def set_changed(self):
        if self.changed:
            self.wd_item["changed"] = self.changed

    def set_source(self):
        if self.source:
            self.wd_item["source"] = self.source

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
        self.set_registrant_url()
        self.set_changed()
        self.set_source()
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

    def set_id(self):
        if self.id:
            self.wd_item["statements"][PROPS["arbetsam"]] = self.id

    def update_wd_item(self):
        self.update_labels()
        self.set_descriptions()
        self.set_id()
        self.set_adm_location()
        self.set_type()
        self.set_location()

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()


class SeShipSv(Monument):
    """
    TODO
    * handle material (from lookup table)
    * handle function (from lookup table)
    """

    def update_labels(self):
        return

    def set_shipyard(self):
        if self.varv:
            possible_varv = self.varv
            if "<br>" in possible_varv:
                possible_varv = self.varv.split("<br>")[0]
            if "[[" in possible_varv:
                varv = q_from_first_wikilink("sv", possible_varv)
                self.wd_item["statements"][PROPS["manufacturer"]] = varv

    def set_manufacture_year(self):
        if self.byggar:
            byggar = parse_year(remove_characters(self.byggar, ".,"))
            self.wd_item["statements"][PROPS["inception"]] = byggar

    def set_dimensions(self):
        if self.dimensioner:
            dimensions_processed = parse_ship_dimensions(self.dimensioner)
            for dimension in dimensions_processed:
                if dimension in PROPS:
                    value = dimensions_processed[dimension]
                    self.wd_item["statements"][PROPS[dimension]] = value

    def set_homeport(self):
        if self.hemmahamn and count_wikilinks(self.hemmahamn) == 1:
            home_port = q_from_first_wikilink("sv", self.hemmahamn)
            self.wd_item["statements"][PROPS["home_port"]] = home_port

    def set_call_sign(self):
        if self.signal:
            self.wd_item["statements"][PROPS["call_sign"]] == self.signal

    def update_wd_item(self):
        self.update_labels()
        self.set_manufacture_year()
        self.set_shipyard()
        self.set_homeport()
        self.set_dimensions()
        self.set_call_sign()

    def __init__(self, db_row_dict, mapping, data_files=None):
        Monument.__init__(self, db_row_dict, mapping, data_files)
        self.update_wd_item()
