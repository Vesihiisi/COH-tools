import argparse
import pymysql
import json
from os import path
import wlmhelpers
import wikidataStuff
import wikidataStuff.helpers as helpers
from wikidataStuff.WikidataStuff import WikidataStuff as WD

MAPPING_DIR = "mappings/"
MONUMENTS_ALL = "monuments_all"


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


class Mapping(object):

    def join_id(self):
        return self.file_content["_id"]

    def load_mapping_file(self, countryname, languagename):
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

    def __init__(self, countryname, languagename):
        self.file_content = self.load_mapping_file(countryname, languagename)


class Monument(object):

    def __init__(self, db_row_dict):
        for k, v in db_row_dict.items():
            if not k.startswith("m_spec."):
                setattr(self, k, v)

    def get_fields(self):
        return sorted(list(self.__dict__.keys()))


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


def get_items(connection, country, language):
    mapping = Mapping(country, language)
    query = make_query(country,
                       language,
                       get_specific_table_name(country, language),
                       mapping.join_id())
    results = []
    for n, i in enumerate(wlmhelpers.selectQuery(query, connection)):
        results.append(Monument(i))
    return results


def main(arguments):
    connection = create_connection(arguments)
    country = arguments.country
    language = arguments.language
    #results = get_items(connection, country, language)
    #print("Fetched {} items from {}".format(
    #    len(results), get_specific_table_name(country, language)))


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
