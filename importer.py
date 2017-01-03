from Monument import *
from os import path
from wikidataStuff.WikidataStuff import WikidataStuff as WD
import argparse
import pymysql
import wikidataStuff
import random

SHORT = 10
MAPPING_DIR = "mappings"
MONUMENTS_ALL = "monuments_all"


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


class Mapping(object):

    def join_id(self):
        return self.file_content["_id"]

    def load_mapping_file(self, countryname, languagename):
        filename = path.join(
            MAPPING_DIR, "{}_({}).json".format(countryname, languagename))
        return load_json(filename)

    def __init__(self, countryname, languagename):
        self.file_content = self.load_mapping_file(countryname, languagename)


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


SPECIFIC_TABLES = {"monuments_se-fornmin_(sv)": SeFornminSv,
                   "monuments_se-arbetsl_(sv)": SeArbetslSv}


def select_query(query, connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def get_items(connection, country, language, short=False):
    specific_table_name = get_specific_table_name(country, language)
    if not table_exists(connection, specific_table_name):
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
            table_row, mapping) for table_row
            in select_query(query, connection)]
    else:
        results = [Monument(table_row, mapping)
                   for table_row in select_query(query, connection)]
    print("Fetched {} items from {}".format(
        len(results), get_specific_table_name(country, language)))
    return results


def run_test(monuments):
    sample_item = random.choice(monuments)
    sample_item.print_wd()


def main(arguments):
    connection = create_connection(arguments)
    country = arguments.country
    language = arguments.language
    results = get_items(connection, country, language, arguments.short)
    if arguments.testrun:
        run_test(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--language", default="sv")
    parser.add_argument("--country", default="se-ship")
    parser.add_argument("--short", action='store_true')
    parser.add_argument("--testrun", action='store_true')
    args = parser.parse_args()
    main(args)
