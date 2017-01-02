from os import path
from wikidataStuff.WikidataStuff import WikidataStuff as WD
import argparse
import json
import mwparserfromhell as wparser
import pymysql
import pywikibot
import wikidataStuff
import wikidataStuff.helpers as helpers
import wlmhelpers

SHORT = 10
MAPPING_DIR = "mappings/"
MONUMENTS_ALL = "monuments_all"
ADM0 = wlmhelpers.load_json(MAPPING_DIR + "adm0.json")
PROPS = wlmhelpers.load_json(MAPPING_DIR + "props_general.json")


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


class Mapping(object):

    def join_id(self):
        return self.file_content["_id"]

    def load_mapping_file(self, countryname, languagename):
        filename = path.relpath(
            MAPPING_DIR + "{}_({}).json".format(countryname, languagename))
        return wlmhelpers.load_json(filename)

    def __init__(self, countryname, languagename):
        self.file_content = self.load_mapping_file(countryname, languagename)


class Monument(object):

    def set_country(self):
        country = [item["item"]
                   for item in ADM0 if item["code"].lower() == self.adm0]
        self.wd_item["country"] = {PROPS["country"]: country}

    def set_is(self, mapping):
        default_is = mapping.file_content["default_is"]
        self.wd_item["is"] = {PROPS["is"]: [default_is["item"]]}

    def set_labels(self):
        if "[" in self.name:
            text = wparser.parse(self.name)
            name = text.strip_code()
        else:
            name = self.name
        self.wd_item["label"] = {self.lang: name.strip()}

    def set_heritage(self, mapping):
        heritage = mapping.file_content["heritage"]
        self.wd_item["heritage"] = {
            PROPS["heritage_status"]: helpers.listify(heritage["item"])}

    def set_coords(self):
        if self.lat and self.lon:
            self.wd_item["coordinates"] = {
                PROPS["coordinates"]: (self.lat, self.lon)}
        else:
            self.wd_item["coordinates"] = None

    def set_image(self):
        if self.image:
            self.wd_item["image"] = {PROPS["image"]: self.image}
        else:
            self.wd_item["image"] = None

    def set_commonscat(self):
        if self.commonscat:
            self.wd_item["commonscat"] = {PROPS["commonscat"]: self.commonscat}
        else:
            self.wd_item["commonscat"] = None

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

    def construct_wd_item(self, mapping):
        self.wd_item = {}
        self.set_labels()
        self.set_country()
        self.set_is(mapping)
        self.set_heritage(mapping)
        self.set_coords()
        self.set_image()
        self.set_commonscat()
        self.exists(mapping)

    def __init__(self, db_row_dict, mapping):
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k.replace("-", "_"), v)
        self.construct_wd_item(mapping)

    def get_fields(self):
        return sorted(list(self.__dict__.keys()))


class SeFornminSv(Monument):

    def update_labels(self):
        if len(self.namn) == 0:
            self.wd_item["label"]["sv"] = self.raa_nr

    def set_raa(self):
        self.wd_item["raa-nr"] = {PROPS["raa-nr"]: [self.raa_nr]}

    def set_adm_location(self):
        municip_dict = wlmhelpers.load_json(
            MAPPING_DIR + "sweden_municipalities_en.json")
        pattern = self.adm2.lower() + " municipality"
        try:
            municipality = [x["municipality"] for x in municip_dict if x[
                "municipality"].lower() == pattern][0]
            ## TODO: Check if target item is valid municipality ##
            self.wd_item["located_adm"] = {
                PROPS["located_adm"]: [municipality]}
        except IndexError:
            print("Could not parse municipality: {}.".format(self.adm2))
            return

    def update_wd_item(self):
        self.update_labels()
        self.set_raa()
        self.set_adm_location()

    def __init__(self, db_row_dict, mapping):
        Monument.__init__(self, db_row_dict, mapping)
        self.update_wd_item()


def make_query(country, language, specific_table, join_id):
    return ('select *  from {} as m_all JOIN `{}` '
            'as m_spec on m_all.id = m_spec.{} '
            'WHERE m_all.country="{}" and m_all.lang="{}"'
            ).format(MONUMENTS_ALL, specific_table, join_id, country, language)


def create_connection(arguments):
    return pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")


SPECIFIC_TABLES = {"monuments_se-fornmin_(sv)": SeFornminSv}


def get_items(connection, country, language, short=False):
    specific_table_name = get_specific_table_name(country, language)
    if not wlmhelpers.tableExists(connection, specific_table_name):
        print("Table does not exist.")
        return
    mapping = Mapping(country, language)
    query = make_query(country,
                       language,
                       specific_table_name,
                       mapping.join_id())
    if short:
        query += " LIMIT " + str(SHORT)
    if specific_table_name in SPECIFIC_TABLES.keys():
        results = [SPECIFIC_TABLES[specific_table_name](
            table_row, mapping) for table_row in wlmhelpers.selectQuery(query, connection)]
    else:
        results = [Monument(table_row, mapping)
                   for table_row in wlmhelpers.selectQuery(query, connection)]
    print("Fetched {} items from {}".format(
        len(results), get_specific_table_name(country, language)))
    return results


def main(arguments):
    connection = create_connection(arguments)
    country = arguments.country
    language = arguments.language
    results = get_items(connection, country, language, arguments.short)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--language", default="sv")
    parser.add_argument("--country", default="se-ship")
    parser.add_argument("--short", action='store_true')
    args = parser.parse_args()
    main(args)
