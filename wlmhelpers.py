import pymysql
import json

def selectQuery(query, connection):
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getNumberOfRows(connection, tablename):
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM `" + tablename + "`"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]


def showTables(connection):
    cursor = connection.cursor()
    cursor.execute("show tables")
    return cursor.fetchall()


def tableIsEmpty(connection, tablename):
    numberOfRows = getNumberOfRows(connection, tablename)
    return numberOfRows == 0


def getNonEmptyCountryTables(connection):
    countryTables = []
    allTables = showTables(connection)
    for table in allTables:
        tablename = table[0]
        if tablename.startswith("monuments_") and tablename != "monuments_all":
            if tableIsEmpty(connection, tablename) == False:
                countryTables.append(
                    (tablename, getNumberOfRows(connection, tablename)))
    return countryTables


def getRowStats():
    tables = getNonEmptyCountryTables(connection)
    for tablename in tables:
        rows = getNumberOfRows(connection, tablename)
        print(tablename, rows)


def shortenTablename(tablename):
    tablenameArr = tablename.split("_")[1:]
    return "_".join(tablenameArr)


def saveToFile(filename, content):
    with open(filename, "w") as out:
        out.write(content)
        print("Saved file: {}".format(filename))


def saveToJson(filename, content):
    with open(filename, 'w') as fp:
        json.dump(content, fp, indent=4, ensure_ascii=False)


def getLanguage(tablename):
    return tablename.split('(', 1)[1].split(')')[0]
