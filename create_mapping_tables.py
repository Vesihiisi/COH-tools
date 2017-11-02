import argparse
import wlmhelpers
import pywikibot


def getTableHeaders(connection, tablename):
    headerList = []
    cursor = connection.cursor()
    query = "DESCRIBE `" + tablename + "`"
    cursor.execute(query)
    result = cursor.fetchall()
    for header in result:
        headerList.append(header[0])
    return headerList


def tableHeadersToWikitable(headersWithContentTuple):
    wikitableTop = "{| class='wikitable'\n! heritage field\n! example value\n! Wikidata property\n! Conversion\n! comment\n"
    wikitableBottom = "|}\n"
    wikitext = ""
    for item in headersWithContentTuple:
        wikitext += "|- \n| {}\n| {}\n| \n| \n|\n".format(item[0], item[1])
    return wikitableTop + wikitext + wikitableBottom


def addToFile(filename, content):
    with open(filename, "a", encoding="utf-8") as out:
        out.write(content + "\n")


def fileToString(filename):
    return open(filename, 'r', encoding="utf-8").read()


def addTablenameToList(tablename, filename):
    tablenameShort = wlmhelpers.shortenTablename(tablename)
    template = "* [[Wikidata:WikiProject_WLM/Mapping_tables/{}|{}]]".format(
        tablenameShort, tablenameShort)
    addToFile(filename, template)
    print("Added table to list: {}".format(tablenameShort))


def getExampleValueFromColumn(connection, column, table):
    cursor = connection.cursor()
    query = "SELECT `" + column + "` FROM `" + \
        table + "` WHERE trim(`" + column + "`) > ''"
    cursor.execute(query)
    result = cursor.fetchall()
    try:
        content = result[1][0]
        if isinstance(content, str):
            if "[" in content or "{{" in content:
                content = "<nowiki>" + content + "</nowiki>"
    except IndexError:
        content = ""
    return content


def insertWikitableIntoTemplate(tabletitle, wikitable, templateFile):
    template = fileToString(templateFile)
    return template % (tabletitle, wikitable)


def createTables(connection):
    open(TABLE_NAMES, 'w', encoding="utf-8").close()
    countryTables = wlmhelpers.getNonEmptyCountryTables(connection)
    for tablename in countryTables:
        tablename = tablename[0]
        addTablenameToList(tablename, TABLE_NAMES)
        headerList = getTableHeaders(connection, tablename)
        headersWithContent = []
        for header in headerList:
            content = getExampleValueFromColumn(
                connection, header, tablename)
            headersWithContent.append((header, content))
        wikiTable = tableHeadersToWikitable(headersWithContent)
        wikiPage = insertWikitableIntoTemplate(
            wlmhelpers.shortenTablename(tablename), wikiTable, TEMPLATE)
        wlmhelpers.saveToFile("{}.txt".format(tablename), wikiPage)

TABLE_NAMES = "_tablenames.txt"
TEMPLATE = "_template.txt"


def main(arguments):
    connection = wlmhelpers.create_connection(arguments)
    createTables(connection)


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
