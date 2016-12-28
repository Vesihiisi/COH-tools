import argparse
import sqlalchemy
import wlmhelpers


def run(stmt):
    return stmt.execute()


def main(arguments):
    db = sqlalchemy.create_engine('mysql://{}:{}@{}/{}'.format(
        arguments.user,
        arguments.password,
        arguments.host,
        arguments.db), encoding='utf8')
    db.echo = False
    metadata = sqlalchemy.MetaData(db)
    try:
        monuments = sqlalchemy.Table(arguments.table, metadata, autoload=True)
        allMonuments = run(monuments.select())
        for v in allMonuments:
            for column, value in v.items():
                print('{0}: {1}'.format(column, value))
    except sqlalchemy.exc.SQLAlchemyError as exc:
        print("{} does not exist.".format(arguments.table))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--db", default="wlm")
    parser.add_argument("--table", required=True)
    args = parser.parse_args()
    main(args)
