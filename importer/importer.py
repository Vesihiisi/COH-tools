from CmFr import CmFr
from CzCs import CzCs
from DkBygningDa import DkBygningDa
from DkFortidsDa import DkFortidsDa
from EeEt import EeEt
from HuHu import HuHu
from IeEn import IeEn
from NoNo import NoNo
from PlPl import PlPl
from PtPt import PtPt
from RoRo import RoRo
from SeArbetslSv import SeArbetslSv
from SeBbrSv import SeBbrSv
from SeFornminSv import SeFornminSv
from SeShipSv import SeShipSv
from XkSq import XkSq
from ZaEn import ZaEn
from Uploader import *
from Logger import *
from os import path
import argparse
import pymysql
import wikidataStuff.wdqsLookup as lookup
import importer_utils as utils

DEFAULT_SHORT = 10
MAPPING_DIR = "mappings"
MONUMENTS_ALL = "monuments_all"


class Mapping(object):

    def load_mapping_file(self, countryname, languagename):
        filename = path.join(
            MAPPING_DIR, "{}_({}).json".format(countryname, languagename))
        return utils.load_json(filename)

    def get_unique_prop(self):
        if "unique" in self.file_content and self.file_content["unique"]["property"] != "":
            return self.file_content["unique"]["property"]

    def __init__(self, countryname, languagename):
        self.file_content = self.load_mapping_file(countryname, languagename)


def make_query(specific_table):
    return ('select DISTINCT *  from `{}`').format(specific_table)


def make_count_query(specific_table):
    return ("SELECT COUNT(*) FROM `{}`").format(specific_table)


def create_connection(arguments):
    return pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")


"""
There must be a better way to do this.....
"""
SPECIFIC_TABLES = {"monuments_se-ship_(sv)": {"class": SeShipSv,
                                              "data_files":
                                              {"functions":
                                               "se-ship_(sv)_functions.json"}},
                   "monuments_cz_(cs)": {"class": CzCs, "data_files": {}},
                   "monuments_hu_(hu)": {"class": HuHu, "data_files": {}},
                   "monuments_pt_(pt)": {"class": PtPt, "data_files": {}},
                   "monuments_ro_(ro)": {"class": RoRo, "data_files": {}},
                   "monuments_xk_(sq)": {"class": XkSq, "data_files": {}},
                   "monuments_ie_(en)": {"class": IeEn, "data_files": {"counties": "ireland_counties.json"}},
                   "monuments_za_(en)": {"class": ZaEn, "data_files": {}},
                   "monuments_cm_(fr)": {"class": CmFr, "data_files": {}},
                   "monuments_dk-bygninger_(da)": {"class": DkBygningDa,
                                                   "data_files": {},
                                                   "subclass_downloads": {"settlement": "Q486972"}},
                   "monuments_pl_(pl)": {"class": PlPl,
                                         "data_files": {"settlements": "poland_settlements.json"}},
                   "monuments_dk-fortidsminder_(da)": {"class": DkFortidsDa,
                                                       "data_files": {
                                                           "types": "dk-fortidsminder_(da)_types.json"
                                                       }},
                   "monuments_no_(no)": {"class": NoNo,
                                         "data_files": {}},
                   "monuments_se-bbr_(sv)": {"class": SeBbrSv,
                                             "data_files": {"functions": "se-bbr_(sv)_functions.json",
                                             "settlements": "sweden_settlements.json"}},
                   "monuments_ee_(et)": {"class": EeEt,
                                         "data_files": {"counties": "estonia_counties.json"}},
                   "monuments_se-fornmin_(sv)":
                   {"class": SeFornminSv,
                    "data_files":
                    {"municipalities": "sweden_municipalities.json",
                     "types": "se-fornmin_(sv)_types.json"}},
                   "monuments_se-arbetsl_(sv)":
                   {"class":
                    SeArbetslSv,
                    "data_files":
                    {"municipalities": "sweden_municipalities.json",
                     "types": "se-arbetsl_(sv)_types.json",
                     "settlements": "sweden_settlements.json"}}
                   }


def get_row_count(tablename, connection):
    count_query = make_count_query(tablename)
    return select_query(count_query, connection)[0]['COUNT(*)']


def print_row_count(tablename, connection):
    rowcount = get_row_count(tablename, connection)
    print(("TABLE {} HAS {} ROWS.").format(tablename, rowcount))


def select_query(query, connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def load_data_files(file_dict):
    for key in file_dict.keys():
        file_dict[key] = utils.load_json(
            path.join(MAPPING_DIR, file_dict[key]))
    return file_dict


def get_wd_items_using_prop(prop):
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


def get_subclasses(q_item):
    """
    Get Q-ids of all the items that are subclasses of the specified one.

    The query fetches both items where P279 = q_item
    and indirect ones (subclass of subclass...).
    """
    results = []
    query = "SELECT DISTINCT ?item WHERE {?item wdt:P279* wd:" + q_item + ".}"
    data = lookup.make_simple_wdqs_query(query, verbose=False)
    for x in data:
        results.append(lookup.sanitize_wdqs_result(x['item']))
    return results


def get_items(connection,
              country,
              language,
              upload,
              short=False,
              table=False):
    if upload:
        logger = Logger()
    country_language = {"country": country, "language": language}
    specific_table_name = utils.get_specific_table_name(country, language)
    if not utils.table_exists(connection, specific_table_name):
        print("Table does not exist.")
        return
    mapping = Mapping(country, language)
    unique_prop = mapping.get_unique_prop()
    if unique_prop is not None:
        existing = get_wd_items_using_prop(unique_prop)
    else:
        existing = None
    query = make_query(specific_table_name)
    if specific_table_name in SPECIFIC_TABLES:
        specific_table = SPECIFIC_TABLES[specific_table_name]
        class_to_use = specific_table["class"]
        data_files = load_data_files(
            specific_table["data_files"])
        if specific_table.get("subclass_downloads"):
            for subclass_title, subclass_item in specific_table.get("subclass_downloads").items():
                data_files[subclass_title] = get_subclasses(subclass_item)
    else:
        print("No class defined for " + specific_table_name)
        return
    print_row_count(specific_table_name, connection)
    database_rows = select_query(query, connection)
    if short:
        database_rows = utils.get_random_list_sample(database_rows, short)
        print("USING RANDOM SAMPLE OF " + str(short))
    filename = specific_table_name + "_" + utils.get_current_timestamp()
    problem_reports = []
    wikidata_site = utils.create_site_instance("wikidata", "wikidata")
    for row in database_rows:
        monument = class_to_use(row, mapping, data_files, existing, wikidata_site)
        problem_report = monument.get_report()
        if table:
            raw_data = "<pre>" + str(row) + "</pre>\n"
            monument_table = monument.print_wd_to_table()
            utils.append_line_to_file(raw_data, filename)
            utils.append_line_to_file(monument_table, filename)
        if upload:
            live = True if upload == "live" else False
            uploader = Uploader(
                monument,
                repo=wikidata_site,
                log=logger,
                tablename=country,
                live=live)
            if "Q" in problem_report and problem_report["Q"] == "":
                """
                If the Monument didn't have an associated Qid,
                this means the Uploader has now created a new Item
                for it -- insert that id into the problem report.
                """
                problem_report["Q"] = uploader.wd_item_q
            uploader.upload()
            print("--------------------------------------------------")
        problem_reports.append(problem_report)
    non_empty_reports = utils.remove_empty_dicts_from_list(problem_reports)
    utils.json_to_file(
        "report_" + specific_table_name + ".json", non_empty_reports)
    if table:
        print("SAVED TEST RESULTS TO " + filename)


def main(arguments):
    connection = create_connection(arguments)
    country = arguments.country
    language = arguments.language
    short = arguments.short
    upload = arguments.upload
    table = arguments.table
    get_items(connection, country, language, upload, short, table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--language", default="sv")
    parser.add_argument("--country", default="se-ship")
    parser.add_argument("--upload", action='store')
    parser.add_argument("--short",
                        const=DEFAULT_SHORT,
                        nargs='?',
                        type=int,
                        action='store',)
    parser.add_argument("--table", action='store_true')
    args = parser.parse_args()
    print(args)
    main(args)
