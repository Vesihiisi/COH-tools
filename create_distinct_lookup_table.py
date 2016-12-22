import pymysql
import argparse
import wlmhelpers


def makeQuery(column, tablename):
    return "SELECT {}, COUNT(*) AS count FROM `{}` GROUP BY {} ORDER BY count DESC".format(column, tablename, column)


def createWikitable(distinctsTuple):
    tableTop = "{| class='wikitable sortable'\n! Name\n! Count\n! Item(s)\n! Notes\n"
    tableBottom = "|}\n"
    wikitext = ""
    for item in distinctsTuple:
        if len(item[0]) > 0:
            wikitext += "|- \n| {}\n| {}\n| \n| \n".format(item[0], item[1])
    return tableTop + wikitext + tableBottom


def createFileName(column, tablename):
    return "{}_{}.txt".format(column, tablename)


def main(arguments):
    connection = pymysql.connect(
        host=arguments.host,
        user=arguments.user,
        password=arguments.password,
        db=arguments.db,
        charset="utf8")
    query = makeQuery(arguments.column, arguments.table)
    distincts = wlmhelpers.selectQuery(query, connection)
    wlmhelpers.saveToFile(
        createFileName(arguments.column, arguments.table), createWikitable(distincts))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--column", required=True)
    parser.add_argument("--table", required=True)
    args = parser.parse_args()
    main(args)
