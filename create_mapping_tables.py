import pymysql
import argparse
import wlmhelpers


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


def saveToFile(filename, content):
    with open(filename, "w") as out:
        out.write(content)
        print("Saved file: {}".format(filename))


def addToFile(filename, content):
    with open(filename, "a") as out:
        out.write(content + "\n")


def fileToString(filename):
    return open(filename, 'r').read()


def shortenTablename(tablename):
    tablenameArr = tablename.split("_")[1:]
    return "_".join(tablenameArr)


def addTablenameToList(tablename, filename):
    tablenameShort = shortenTablename(tablename)
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

TABLE_NAMES = "_tablenames.txt"
TEMPLATE = "_template.txt"


def main(arguments):
    connection = pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")
    open(TABLE_NAMES, 'w').close()
    countryTables = wlmhelpers.getNonEmptyCountryTables(connection)
    for tablename in countryTables:
        addTablenameToList(tablename, TABLE_NAMES)
        headerList = getTableHeaders(connection, tablename)
        headersWithContent = []
        for header in headerList:
            content = getExampleValueFromColumn(
                connection, header, tablename)
            headersWithContent.append((header, content))
        wikiTable = tableHeadersToWikitable(headersWithContent)
        wikiPage = insertWikitableIntoTemplate(
            shortenTablename(tablename), wikiTable, TEMPLATE)
        saveToFile("{}.txt".format(tablename), wikiPage)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    args = parser.parse_args()
    main(args)
