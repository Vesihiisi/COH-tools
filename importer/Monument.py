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
                       ensure_ascii=False)
        )

    def remove_markup(self, string):
        remove_br = re.compile('\W*<br.*?>\W*', re.I)
        string = remove_br.sub(' ', string)
        if "[" in string:
            string = wparser.parse(string)
            string = string.strip_code()
        return string.strip()

    def set_country(self):
        country = [item["item"]
                   for item in ADM0 if item["code"].lower() == self.adm0]
        self.wd_item["statements"][PROPS["country"]] = country

    def set_is(self, mapping):
        default_is = mapping.file_content["default_is"]
        self.wd_item["statements"][PROPS["is"]] = [default_is["item"]]

    def set_labels(self):
        self.wd_item["labels"] = {self.lang: self.remove_markup(self.name)}

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

    def exists(self, mapping):
        self.wd_item["wd-item"] = None
        if self.monument_article:
            site = pywikibot.Site(self.lang, "wikipedia")
            page = pywikibot.Page(site, self.monument_article)
            if page.exists():
                if page.isRedirectPage():
                    page = page.getRedirectTarget()
                try:
                    item = pywikibot.ItemPage.fromPage(page)
                except pywikibot.NoPage:
                    print("Failed to get page for {} - {}."
                          "It probably does not exist.".format(
                              self.lang, self.monument_article))
                    return
                self.wd_item["_itemID"] = item.getID()

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
        self.exists(mapping)

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
            MAPPING_DIR, "sweden_municipalities_en.json"))
        pattern = self.adm2.lower() + " municipality"
        try:
            municipality = [x["item"] for x in municip_dict if x[
                "municipality"].lower() == pattern][0]
            ## TODO: Check if target item is valid municipality ##
            self.wd_item["statements"][
                PROPS["located_adm"]] = helpers.listify(municipality)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_type(self):
        # TODO: import type with lookup_table_to_json
        # This should be done on a global level, when parsing table name
        return

    def set_location(self):
        # TODO: check self.address and map it to P276.
        # This only makes sense if it's a wikilinked item,
        # and also if there's exactly 1 item
        # because stuff like
        # [[Sundsbruk]] - [[Sköns Prästbord]] (Nordväst om [[Sköns kyrka]])
        # NOTE: adm3 always empty for this table
        return

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
        print(self.wd_item["descriptions"])

    def set_adm_location(self):
        municip_dict_en = self.data_files["municipalities_en"]
        pattern = self.adm2.lower() + " municipality"
        municip_dict_sv = self.data_files["municipalities_sv"]
        try:
            municipality = [x["item"] for x in municip_dict_en if x[
                "municipality"].lower() == pattern][0]
            ## TODO: Check if target item is valid municipality ##
            self.wd_item["statements"][
                PROPS["located_adm"]] = helpers.listify(municipality)
            swedish_name = [x["municipality"]
                            for x in municip_dict_sv
                            if x["item"] == municipality][0]
            self.add_location_to_desc(swedish_name)
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def set_type(self):
        # TODO: import type with lookup_table_to_json
        # This should be done on a global level, when parsing table name
        return

    def set_location(self):
        # TODO: this table has both ort and address..
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
