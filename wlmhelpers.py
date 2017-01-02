import pymysql
import json


def selectQuery(query, connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def tableExists(connection, tablename):
    try:
        if tableIsEmpty(connection, tablename) == False:
            return True
    except pymysql.ProgrammingError as e:
        return False


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
        print("Saved file: {}".format(filename))


def getLanguage(tablename):
    return tablename.split('(', 1)[1].split(')')[0]


def load_json(filename):
    try:
        with open(filename) as f:
            try:
                return json.load(f)
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError as e:
        print("File {} does not exist.".format(filename))
