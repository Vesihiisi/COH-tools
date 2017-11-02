import pywikibot
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
    connection = wlmhelpers.create_connection(arguments)
    createPage(connection)


def handle_args(*args):
    """
    Parse and handle command line arguments to get data from the database.

    Also supports any pywikibot arguments, these are prefixed by a single "-"
    and the full list can be gotten through "-help".
    """
    parser = argparse.ArgumentParser()
    if not wlmhelpers.on_forge():
        parser.add_argument("--host", default="localhost")
        parser.add_argument("--db", default="wlm")
        parser.add_argument("--user", default="root")
        parser.add_argument("--password", default="")

    # first parse args with pywikibot, send remaining args to local handler
    return parser.parse_args(pywikibot.handle_args(args))


if __name__ == "__main__":
    parsed_args = handle_args()
    main(parsed_args)
