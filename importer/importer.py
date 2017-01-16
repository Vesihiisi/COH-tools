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
    """
    For a table to be processed, it requires a basic mapping file,
    named just like the table (eg. se-ship_(sv).json)
    At the very least, it should contain the name of the column
    in the _specific_ table should be mapped against the "id" column
    in monuments_all().
    That's because the column does not have to be called "id"
    in the specific table.
    Such as:
    "_id": "signal"
    """

    def join_id(self):
        DEFAULT_ID = "id"
        joins = {}
        if self.country != "dk-bygninger":
            joins["all_id"] = DEFAULT_ID
            joins["join_id"] = self.file_content["_id"]
        else:
            joins["all_id"] = "name"
            joins["join_id"] = "sagsnavn"
        joins["country_code"] = self.file_content["country_code"]
        return joins

    def load_mapping_file(self, countryname, languagename):
        filename = path.join(
            MAPPING_DIR, "{}_({}).json".format(countryname, languagename))
        return load_json(filename)

    def __init__(self, countryname, languagename):
        self.file_content = self.load_mapping_file(countryname, languagename)
        self.country = countryname
        self.joins = self.join_id()


def make_query(country_code, language, specific_table, join_id, all_id="id"):
    """
    you know what. MONUMENTS_ALL IS NOT EVEN NECESSARY
    IT WILL SOLVE THIS WHOLE JOINING PROBLEM IF YOU GET RID OF IT
    THERE IS LITERALLY NOTHING UNIQUE IN IT
    SERIOUSLY
    WHY
    bUT: parent class Monument() relies on consistent attributes to assign
    simple values (name, image, adm2)
    idea: make methods in Monument() take params to indicate where to search
    for the values, like add_image("bilde")
    """
    query = ('select DISTINCT *  from `{}` as m_all JOIN `{}` '
             'as m_spec on m_all.{} = m_spec.{} '
             'WHERE m_all.adm0="{}" and m_all.lang="{}"'
             ).format(MONUMENTS_ALL, specific_table, all_id, join_id, country_code, language)
    print(query)
    return query


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
                                              "data_files": {}},
                   "monuments_dk-bygninger_(da)": {"class": DkBygningDa,
                                                 "data_files": {}},
                   "monuments_se-bbr_(sv)": {"class": SeBbrSv,
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


def select_query(query, connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def load_data_files(file_dict):
    for key in file_dict.keys():
        file_dict[key] = load_json(path.join(MAPPING_DIR, file_dict[key]))
    return file_dict


def get_items(connection, country, language, short=False):
    specific_table_name = get_specific_table_name(country, language)
    if not table_exists(connection, specific_table_name):
        print("Table does not exist.")
        return
    mapping = Mapping(country, language)
    country_code = mapping.joins["country_code"]
    all_id = mapping.joins["all_id"]
    join_id = mapping.joins["join_id"]
    query = make_query(country_code,
                       language,
                       specific_table_name,
                       join_id,
                       all_id)
    if short:
        query += " LIMIT " + str(SHORT)
    if specific_table_name in SPECIFIC_TABLES.keys():
        class_to_use = SPECIFIC_TABLES[specific_table_name]["class"]
        data_files = load_data_files(
            SPECIFIC_TABLES[specific_table_name]["data_files"])
    else:
        class_to_use = Monument
        data_files = None
    print(class_to_use)
    database_rows = select_query(query, connection)
    print(len(database_rows))
    results = [class_to_use(table_row, mapping, data_files)
               for table_row in database_rows]
    print("Fetched {} items from {}".format(
        len(results), get_specific_table_name(country, language)))
    return results


def upload(monuments):
    logger = Logger()
    for sample_item in monuments:
        uploader = Uploader(sample_item, log=logger)
        uploader.upload()


def main(arguments):
    connection = create_connection(arguments)
    country = arguments.country
    language = arguments.language
    results = get_items(connection, country, language, arguments.short)
    if arguments.upload:
        upload(results)


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
