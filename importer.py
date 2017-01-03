from Monument import *
from os import path
from wikidataStuff.WikidataStuff import WikidataStuff as WD
import argparse
import pymysql
import wikidataStuff
import wlmhelpers


SHORT = 10
MAPPING_DIR = "mappings"
MONUMENTS_ALL = "monuments_all"


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


class Mapping(object):

    def join_id(self):
        return self.file_content["_id"]

    def load_mapping_file(self, countryname, languagename):
        filename = path.join(
            MAPPING_DIR, "{}_({}).json".format(countryname, languagename))
        return wlmhelpers.load_json(filename)

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
            table_row, mapping) for table_row
            in wlmhelpers.selectQuery(query, connection)]
    else:
        results = [Monument(table_row, mapping)
                   for table_row in wlmhelpers.selectQuery(query, connection)]
    print("Fetched {} items from {}".format(
        len(results), get_specific_table_name(country, language)))
    return results


def run_test(monuments):
    sample_item = monuments[9]
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
