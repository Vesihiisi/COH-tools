import pymysql
import json
from os import path


def selectQuery(query, connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def tableExists(connection, tablename):
    try:
        if not tableIsEmpty(connection, tablename):
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
            if not tableIsEmpty(connection, tablename):
                countryTables.append(
                    (tablename, getNumberOfRows(connection, tablename)))
    return countryTables


def getRowStats(connection):
    tables = getNonEmptyCountryTables(connection)
    for tablename in tables:
        rows = getNumberOfRows(connection, tablename)
        print(tablename, rows)


def shortenTablename(tablename):
    tablenameArr = tablename.split("_")[1:]
    return "_".join(tablenameArr)


def saveToFile(filename, content):
    with open(filename, "w", encoding="utf-8") as out:
        out.write(content)
        print("Saved file: {}".format(filename))


def saveToJson(filename, content):
    with open(filename, 'w', encoding="utf-8") as fp:
        json.dump(content, fp, indent=4, ensure_ascii=False)
        print("Saved file: {}".format(filename))


def getLanguage(tablename):
    return tablename.split('(', 1)[1].split(')')[0]


def load_json(filename):
    try:
        with open(filename, encoding="utf-8") as f:
            try:
                return json.load(f)
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError as e:
        print("File {} does not exist.".format(filename))


def on_forge():
    """Check if running in the Toolforge environment."""
    return path.isfile(path.expanduser("~") + "/replica.my.cnf")


def get_db_credentials():
    """Get credentials to access the SQL db on Toolforge."""
    credentials = {}
    credentials_path = path.expanduser("~") + "/replica.my.cnf"
    with open(credentials_path, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("user"):
            credentials["user"] = line.partition("=")[-1].strip()
        elif line.startswith("password"):
            credentials["password"] = line.partition("=")[-1].strip()
    return credentials


def create_connection(arguments):
    """Create a connection to the SQL database using arguments."""
    arguments = vars(arguments)
    if on_forge():
        arguments["host"] = "tools-db"
        arguments["db"] = "s51138__heritage_p"
        credentials = get_db_credentials()
        arguments["user"] = credentials["user"]
        arguments["password"] = credentials["password"]

    return pymysql.connect(
        host=arguments["host"],
        user=arguments["user"],
        password=arguments["password"],
        db=arguments["db"],
        charset="utf8")
