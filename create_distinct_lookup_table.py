"""
Example usage
python3 create_distinct_lookup_table.py --column liik --table "monuments_ee_(et)" --user foo
"""

import pymysql
import argparse
import wlmhelpers
import pywikibot as pwb
import mwparserfromhell as mwp


def makeQuery(column, tablename):
    return "SELECT {}, COUNT(*) AS count FROM `{}` GROUP BY {} ORDER BY count DESC".format(column, tablename, column)


def wdItemTemplate(wditemID):
    return "{{" + wditemID[0] + "|" + wditemID + "}}"


def createWikitable(language, distinctsTuple, column):
    tableTop = "{| class='wikitable sortable'\n! Name\n! Count\n! Item(s)\n! Notes\n"
    tableBottom = "|}\n"
    wikitext = ""
    site = pwb.Site(language, "wikipedia")
    for item in distinctsTuple:
        wdItems = []
        count = item["count"]
        value = item[column]
        parsed_value = mwp.parse(value)
        wikilinks = parsed_value.filter_wikilinks()
        for wl in wikilinks:
            page = pwb.Page(site, wl.title)
            try:
                wdItem = pwb.ItemPage.fromPage(page)
                wdItemTemplated = wdItemTemplate(wdItem.getID())
                wdItems.append(wdItemTemplated)
            except pwb.exceptions.NoPage:
                pass
        if len(wdItems) == 0:
            wdItemsString = ""
        else:
            wdItemsString = " ".join(wdItems)
        print(wdItemsString)
        wikitext += "|- \n| {}\n| {}\n| {}\n| \n".format(
            value, count, wdItemsString)
    return tableTop + wikitext + tableBottom


def createFileName(column, tablename):
    return "{}_{}.txt".format(column, tablename)


def main(arguments):
    connection = pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")
    language = wlmhelpers.getLanguage(arguments.table)
    query = makeQuery(arguments.column, arguments.table)
    distincts = wlmhelpers.selectQuery(query, connection)
    filename = createFileName(arguments.column, arguments.table)
    wikitable = createWikitable(language, distincts, arguments.column)
    wlmhelpers.saveToFile(filename, wikitable)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--column", required=True)
    parser.add_argument("--table", required=True)
    args = parser.parse_args()
    main(args)
