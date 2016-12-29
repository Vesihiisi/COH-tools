import argparse
import pymysql
import json
from os import path
import wlmhelpers

MAPPING_DIR = "mappings/"
MONUMENTS_ALL = "monuments_all"


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


def load_mapping_file(countryname, languagename):
    filename = path.relpath(
        MAPPING_DIR + "{}_({}).json".format(countryname, languagename))
    try:
        with open(filename) as f:
            try:
                data = json.load(f)
                return data
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError as e:
        print("File {} does not exist.".format(filename))


def make_query(country, language, specific_table, join_id):
    return ('select *  from {} as m_all JOIN `{}` '
            'as m_spec on m_all.id = m_spec.{} '
            'WHERE m_all.country="{}" and m_all.lang="{}"'
            ).format(MONUMENTS_ALL, specific_table, join_id, country, language)


def main(arguments):
    connection = pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")
    country = arguments.country
    language = arguments.language
    mapping_file = load_mapping_file(country, language)
    query = make_query(country,
                       language,
                       get_specific_table_name(country, language),
                       mapping_file["_id"])
    results = wlmhelpers.selectQuery(query, connection)
    print("Fetched {} items from {}".format(len(results), get_specific_table_name(country, language)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--language", default="sv")
    parser.add_argument("--country", default="se-ship")
    args = parser.parse_args()
    main(args)
