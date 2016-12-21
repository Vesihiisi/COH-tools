import pymysql
import argparse
import wlmhelpers

tableHeaders = ["dataset", "rows", "tables", "implicit",
                "monuments_all", "specific",
                "new properties", "lookup", "licence", "test run",
                "uploaded", "comments"]

OUTPUT_FILE = "status.txt"


def createPage(connection):
    tables = wlmhelpers.getNonEmptyCountryTables(connection)
    tableTop = "{| class='wikitable sortable'\n"
    tableBottom = "|}\n"
    tableContent = ""
    for header in tableHeaders:
        tableTop += "! {}\n".format(header)
    for table in tables:
        tableContent += "|- \n"
        for header in tableHeaders:
            if header == "dataset":
                shortName = wlmhelpers.shortenTablename(table[0])
                tableContent += "| [[Wikidata:WikiProject_WLM/Mapping_tables/{}|{}]]\n".format(
                    shortName, shortName)
            elif header == "rows":
                tableContent += "| {}\n".format(table[1])
            else:
                tableContent += "| \n"
    wholeTable = tableTop + tableContent + tableBottom
    wlmhelpers.saveToFile(OUTPUT_FILE, wholeTable)


def main(arguments):
    connection = pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")
    createPage(connection)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    args = parser.parse_args()
    main(args)
