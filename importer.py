import argparse
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import wlmhelpers
import json
from os import path

Base = declarative_base()

MAPPING_DIR = "mappings/"


def run(stmt):
    return stmt.execute()


def get_monuments_in_country(countryname, languagename, all_monuments):
    return run(all_monuments.select(sqlalchemy.and_(
        all_monuments.c.country == countryname,
        all_monuments.c.lang == languagename)
    ))


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


def load_mapping_file(countryname, languagename):
    filename = path.relpath(MAPPING_DIR + "{}_({}).json".format(countryname, languagename))
    try:
        with open(filename) as f:
            data = json.load(f)
        return data
    except OSError as e:
        print("File {} does not exist.".format(filename))


def main(arguments):
    db = sqlalchemy.create_engine('mysql://{}:{}@{}/{}?charset=utf8'.format(
        arguments.user,
        arguments.password,
        arguments.host,
        arguments.db), encoding='utf8')
    db.echo = False
    try:
        metadata = sqlalchemy.MetaData(db)
        all_monuments = sqlalchemy.Table(
            "monuments_all", metadata, autoload=True)
        associated_table = get_specific_table_name(
            arguments.country, arguments.language)
        monuments_country = get_monuments_in_country(
            arguments.country, arguments.language, all_monuments)
        mapping_file = load_mapping_file(arguments.country, arguments.language)

    except sqlalchemy.exc.SQLAlchemyError as exc:
        print("{} does not exist.".format(arguments.table))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--table")
    parser.add_argument("--language", default="sv")
    parser.add_argument("--country", default="se-ship")
    args = parser.parse_args()
    main(args)
