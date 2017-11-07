#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-contained-ish module for Bosnia/Herzegovina.

Since this data does not come from WLM,
this module contains its own little
importer that parses the csv data
(in several files in a subdirectory called
upon with --datadir).
"""
import argparse
import os
import dateparser

import wikidataStuff.wdqsLookup as lookup

from Monument import Monument
from Uploader import Uploader
import importer_utils as utils

MAPPINGS_DIR = "mappings"
REPORTING_DIR = "reports"
PREVIEW_DIR = "previews"


class BosniaMonument(Monument):

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        """
        Initialize the data object.

        Like Monument.py but with some simplifications
        re: attribute setting
        """
        self.raw_data = db_row_dict
        self.props = data_files["_static"]["props"]
        self.adm0 = data_files["_static"]["adm0"]
        self.sources = data_files["_static"]["sources"]
        self.common_items = data_files["_static"]["common_items"]
        for k, v in db_row_dict.items():
            setattr(self, k.lower().strip().replace(" ", "_"), v)
        self.data_files = data_files
        self.existing = existing
        self.construct_wd_item(mapping)
        self.repo = repository
        self.problem_report = {}

    def create_source(self):
        source_item = "Q42750314"
        last_edit = "2017-09-08"
        timestamp = utils.date_to_dict(last_edit, "%Y-%m-%d")
        prop_stated = self.props["stated_in"]
        prop_date = self.props["retrieved"]
        self.source = {"source": {"prop": prop_stated, "value": source_item},
                       "retrieved": {"prop": prop_date,
                                     "value": timestamp}, }

    def set_country(self):
        self.add_statement("country", "Q225", refs=self.source)

    def set_is(self):
        """
        Set P31.

        Try to get a specific one via mapping file.
        Otherwise default of cultural property.
        """
        default = self.mapping["default_is"]["item"]
        type_dict = self.data_files["_static"]["bosnia_types"]
        type_raw = self.object_type.strip()
        type_match = utils.get_item_from_dict_by_key(
            dict_name=type_dict,
            search_in="itemLabel",
            search_term=type_raw)
        if len(type_match) == 1:
            to_add = type_match[0]
        else:
            to_add = default

        self.add_statement("is", to_add, refs=self.source, if_empty=True)

    def clean_url(self):
        """
        Prettify reference url.

        The URL's look like
        http://aplikacija.kons.gov.ba/kons/public/nacionalnispomenici/show/3729?return=&search=idgrad:undefined:46|
        which is messy so the mess after ? gets removed. Same result!
        """
        if self.has_non_empty_attribute("url"):
            if self.url.startswith("http"):
                return self.url.split("?")[0]

    def set_heritage(self):
        """
        Set heritage.

        National Monument of Bosnia and Herzegovina (Q12637954)
        with facultative start date and
        'described at url'.
        """
        heritage = self.mapping["heritage"]["item"]
        url = self.clean_url()
        date_parsed = dateparser.parse(self.designated)
        quals = {}
        if date_parsed:
            date_dict = utils.datetime_object_to_dict(date_parsed)
            quals["start_time"] = utils.package_time(date_dict)
        if url:
            quals["described_at_url"] = url

        self.add_statement("heritage_status", heritage,
                           quals=quals, refs=self.source)

    def set_adm_location(self):
        """
        Set administrative location.

        Since the mapping file covers all that's in the
        source data, there's not trying / reporting to do.
        """
        municip_dict = self.data_files["_static"]["bosnia_adm"]
        municip_raw = self.municipality.strip()
        municip_match = utils.get_item_from_dict_by_key(dict_name=municip_dict,
                                                        search_term=municip_raw,
                                                        search_in="itemLabel")
        self.add_statement("located_adm", municip_match[0], refs=self.source)

    def set_street_address(self):
        addr_raw = self.address.strip()
        if addr_raw != "N/A" and not addr_raw.startswith("http"):
            # yes this is needed
            self.add_statement("located_street", addr_raw, refs=self.source)

    def update_labels(self):
        labels = {
            "en": self.english_name,
            "bs": self.short_name
        }
        for lang in labels:
            self.add_label(lang, labels[lang])
        self.add_alias("bs", self.official_name)  # 2 bs labels

    def update_descriptions(self):
        """
        Set description in bs.

        Use object_type, decapitalized.
        """
        bs_desc = self.object_type[0].lower() + self.object_type[1:]
        self.add_description("bs", bs_desc)

    def set_coords(self):
        """
        Set coordinates.

        Try to parse the non-split text value...
        """
        coords_raw = self.coordinates.replace("°", "")
        if "N/A" not in coords_raw and "x" not in coords_raw:
            if "N" in coords_raw and "E" in coords_raw:
                split_parts = coords_raw.split("N")
                try:
                    coord_tuple = (float(split_parts[0].strip()),
                                   float(split_parts[1].strip()[:-1].strip()))
                    self.add_statement(
                        "coordinates", coord_tuple, refs=self.source)
                except ValueError:
                    print("Nope coords: {}".format(self.coordinates))
                    self.add_to_report("coordinates",
                                       self.coordinates,
                                       "coordinates")

    def set_heritage_id(self):
        url = self.clean_url()
        if url:
            id_no = url.rsplit('/', 1)[-1]
            wlm_prefix = self.mapping["country_code"].upper()
            wlm_id = "{}-{}".format(wlm_prefix, id_no)
            self.add_statement("wlm_id", wlm_id, refs=False)
        else:
            self.upload = False

    def get_matching_existing(self):
        wlm = self.get_statement_values("wlm_id")
        if wlm and wlm[0] in self.existing:
            return self.existing.get(wlm[0])

    def construct_wd_item(self, mapping, data_files=None):
        """
        Create the empty structure of the data object.

        Like Monument.py but simplify mapping loading.
        """
        self.wd_item = {}
        self.wd_item["upload"] = True
        self.wd_item["statements"] = {}
        self.wd_item["labels"] = {}
        self.wd_item["aliases"] = {}
        self.wd_item["descriptions"] = {}
        self.wd_item["disambiguators"] = {}
        self.wd_item["wd-item"] = None
        self.mapping = mapping
        self.create_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_adm_location()
        self.set_coords()
        self.set_is()
        self.set_street_address()
        self.update_descriptions()
        self.update_labels()
        self.set_wd_item(self.get_matching_existing())


def generate_filenames(tablename, timestamp):
    """Construct the problem and preview filenames."""
    filenames = {}
    utils.create_dir(REPORTING_DIR)
    filenames['reports'] = os.path.join(
        REPORTING_DIR, "report_{0}_{1}.json".format(tablename, timestamp))

    utils.create_dir(PREVIEW_DIR)
    filenames['examples'] = os.path.join(
        PREVIEW_DIR, "examples_{0}_{1}.wiki".format(tablename, timestamp))
    filenames['matches'] = os.path.join(
        PREVIEW_DIR, "matches_{0}_{1}.wiki".format(tablename, timestamp))
    return filenames


def load_source_data(directory):
    """Load multiple source files from directory."""
    source_data = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            rows = utils.get_data_from_csv_file(os.path.join(path, name))
            for row in rows:
                source_data.append(row)
    print("Loaded {} files, {} data rows.".format(len(files),
                                                  len(source_data)))
    return source_data


def get_wd_items_using_prop(prop):
    """
    Get WD items that already have some value of a unique ID.

    Even if there are none before we start working,
    it's still useful to have in case an upload is interrupted
    and has to be restarted, or if we later want to enhance
    some items. When matching, these should take predecence
    over any hardcoded matching files.

    The output is a dictionary of ID's and items
    that looks like this:
    {'4420': 'Q28936211', '2041': 'Q28933898'}
    """
    items = {}
    print("WILL NOW DOWNLOAD WD ITEMS THAT USE " + prop)
    query = "SELECT DISTINCT ?item ?value  WHERE {?item p:" + \
        prop + "?statement. OPTIONAL { ?item wdt:" + prop + " ?value. }}"
    data = lookup.make_simple_wdqs_query(query, verbose=False)
    for x in data:
        key = lookup.sanitize_wdqs_result(x['item'])
        value = x['value']
        items[value] = key
    print("FOUND {} WD ITEMS WITH PROP {}".format(len(items), prop))
    return items


def load_mapping_files():
    """Load the files with mappings of various values."""
    mapping_files = {}
    mapping_files["_static"] = {}
    files_to_get = ["ba_(bs).json", "bosnia_adm.json", "bosnia_types.json"]
    for filename in files_to_get:
        filename_base = os.path.splitext(filename)[0]
        file_content = utils.load_json(
            os.path.join(MAPPINGS_DIR, filename))
        mapping_files["_static"][filename_base] = file_content
    mapping_files["_static"]["common_items"] = utils.load_json(os.path.join(
        MAPPINGS_DIR, "common_items.json"))
    mapping_files["_static"]["sources"] = utils.load_json(os.path.join(
        MAPPINGS_DIR, "sources.json"))
    mapping_files["_static"]["adm0"] = utils.load_json(
        os.path.join(MAPPINGS_DIR, "adm0.json"))
    mapping_files["_static"]["props"] = utils.load_json(os.path.join(
        MAPPINGS_DIR, "props_general.json"))
    return mapping_files


def main(arguments):
    """Process the arguments and fetch data according to them."""
    arguments = vars(arguments)
    filenames = generate_filenames("Bosnia", utils.get_current_timestamp())
    repo = utils.create_site_instance("wikidata", "wikidata")
    source_data = load_source_data(arguments["datadir"])
    data_files = load_mapping_files()
    mapping = data_files["_static"]["ba_(bs)"]
    existing = get_wd_items_using_prop(
        data_files["_static"]["ba_(bs)"]["unique"]["property"])
    if arguments["offset"]:
        print("Using offset: {}.".format(str(arguments["offset"])))
        source_data = source_data[arguments["offset"]:]
    if arguments["short"]:
        print("Using limit: {}.".format(str(arguments["short"])))
        source_data = source_data[:arguments["short"]]
    for row in source_data:
        monument = BosniaMonument(row, mapping, data_files, existing, repo)
        if arguments["table"]:
            raw_data = "<pre>" + str(row) + "</pre>\n"
            monument_table = monument.print_wd_to_table()
            utils.append_line_to_file(raw_data, filenames['examples'])
            utils.append_line_to_file(monument_table, filenames['examples'])
        if arguments["upload"]:
            live = True if arguments["upload"] == "live" else False
            uploader = Uploader(monument,
                                repo=repo,
                                live=live,
                                tablename="ba")
            uploader.upload()


if __name__ == "__main__":
    arguments = {}
    parser = argparse.ArgumentParser()
    parser.add_argument("--datadir", required=True)
    parser.add_argument("--upload", action='store')
    parser.add_argument("--table", action='store_true')
    parser.add_argument("--offset",
                        nargs='?',
                        type=int,
                        action='store')
    parser.add_argument("--short",
                        nargs='?',
                        type=int,
                        action='store')
    args = parser.parse_args()
    main(args)
