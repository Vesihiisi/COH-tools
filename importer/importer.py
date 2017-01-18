from Monument import *
from Uploader import *
from Logger import *
from os import path
import argparse
import pymysql
from importer_utils import *

SHORT = 10
MAPPING_DIR = "mappings"
MONUMENTS_ALL = "monuments_all"


class Mapping(object):

    def load_mapping_file(self, countryname, languagename):
        filename = path.join(
            MAPPING_DIR, "{}_({}).json".format(countryname, languagename))
        return load_json(filename)

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

                   "monuments_xk_(sq)": {"class": XkSq, "data_files": {}},

                   "monuments_za_(en)": {"class": ZaEn, "data_files": {}},

                   "monuments_ro_(ro)": {"class": RoRo, "data_files": {}},

                   "monuments_dk-bygninger_(da)": {"class": DkBygningDa,
                                                   "data_files": {}},
                   "monuments_pl_(pl)": {"class": PlPl,
                                         "data_files": {"settlements": "poland_settlements.json"}},
                   "monuments_dk-fortidsminder_(da)": {"class": DkFortidsDa,
                                                       "data_files": {
                                                           "types": "dk-fortidsminder_(da)_types.json"
                                                       }},
                   "monuments_no_(no)": {"class": NoNo,
                                         "data_files": {}},
                   "monuments_se-bbr_(sv)": {"class": SeBbrSv,
                                             "data_files": {}},
                   "monuments_ee_(et)": {"class": EeEt,
                                         "data_files": {}},
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
        file_dict[key] = load_json(path.join(MAPPING_DIR, file_dict[key]))
    return file_dict


def get_items(connection, country, language, short=False, upload=False):
    if upload:
        logger = Logger()
    specific_table_name = get_specific_table_name(country, language)
    if not table_exists(connection, specific_table_name):
        print("Table does not exist.")
        return
    mapping = Mapping(country, language)
    query = make_query(specific_table_name)
    if short:
        query += " LIMIT " + str(SHORT)
    if specific_table_name in SPECIFIC_TABLES.keys():
        class_to_use = SPECIFIC_TABLES[specific_table_name]["class"]
        data_files = load_data_files(
            SPECIFIC_TABLES[specific_table_name]["data_files"])
    else:
        class_to_use = Monument
        data_files = None
    print_row_count(specific_table_name, connection)
    database_rows = select_query(query, connection)
    for row in database_rows:
        monument = class_to_use(row, mapping, data_files)
        if upload:
            uploader = Uploader(monument, log=logger)
            uploader.upload()
            print("--------------------------------------------------")


def main(arguments):
    connection = create_connection(arguments)
    country = arguments.country
    language = arguments.language
    short = arguments.short
    upload = arguments.upload
    get_items(connection, country, language, short, upload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--language", default="sv")
    parser.add_argument("--country", default="se-ship")
    parser.add_argument("--short", action='store_true')
    parser.add_argument("--upload", action='store_true')
    args = parser.parse_args()
    main(args)
