import pymysql


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
                countryTables.append(tablename)
    return countryTables
