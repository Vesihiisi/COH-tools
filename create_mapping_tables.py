import pymysql
import argparse


def showTables(connection):
    cursor = connection.cursor()
    cursor.execute("show tables")
    return cursor.fetchall()


def getNumberOfRows(connection, tablename):
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM `" + tablename + "`"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]


def tableIsEmpty(connection, tablename):
    numberOfRows = getNumberOfRows(connection, tablename)
    return numberOfRows == 0


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

def addTablenameToList(tablename, filename):
    tablenameArr = tablename.split("_")[1:]
    tablenameShort = "_".join(tablenameArr)
    template = "* [[Wikidata:WikiProject_WLM/Mapping_tables/{}|{}]]".format(tablenameShort, tablenameShort)
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
        if isinstance(content, str) and "[[" in content:
            content = "<nowiki>" + content + "</nowiki>"
    except IndexError:
        content = ""
    return content

TABLE_NAMES = "_tablenames.txt"

def main(arguments):
    connection = pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db)
    allTables = showTables(connection)
    open(TABLE_NAMES, 'w').close()
    for table in allTables:
        tablename = table[0]
        if tablename.startswith("monuments_") and tablename != "monuments_all":
            if tableIsEmpty(connection, tablename) == False:
                addTablenameToList(tablename, TABLE_NAMES)
                headerList = getTableHeaders(connection, tablename)
                headersWithContent = []
                for header in headerList:
                    content = getExampleValueFromColumn(connection, header, tablename)
                    headersWithContent.append((header, content))
                wikiTable = tableHeadersToWikitable(headersWithContent)
                saveToFile("{}.txt".format(tablename), wikiTable)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    args = parser.parse_args()
    main(args)
