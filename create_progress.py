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
    tableTop = "{{Wikidata:WikiProject WLM/Mapping tables/Template:Status-head}}\n"
    tableContent = ""
    for table in tables:
        tableContent += "{{Wikidata:WikiProject WLM/Mapping tables/Template:Status\n"
        for header in tableHeaders:
            if header == "dataset":
                shortName = wlmhelpers.shortenTablename(table[0])
                tableContent += "| {} = [[Wikidata:WikiProject_WLM/Mapping_tables/{}|{}]]\n".format(
                    header, shortName, shortName)
            elif header == "rows":
                tableContent += "| {} = {}\n".format(header, table[1])
            else:
                tableContent += "| {} = \n".format(header)
        tableContent += "}}\n"
    wholeTable = tableTop + tableContent
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