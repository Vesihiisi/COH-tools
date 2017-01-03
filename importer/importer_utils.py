import json


def get_specific_table_name(countryname, languagename):
    return "monuments_{}_({})".format(countryname, languagename)


def get_number_of_rows(connection, tablename):
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM `" + tablename + "`"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]


def table_exists(connection, tablename):
    try:
        if get_number_of_rows(connection, tablename) > 0:
            return True
    except pymysql.ProgrammingError as e:
        return False


def load_json(filename):
    try:
        with open(filename) as f:
            try:
                return json.load(f)
            except ValueError:
                print("Failed to decode file {}.".format(filename))
    except OSError as e:
        print("File {} does not exist.".format(filename))
