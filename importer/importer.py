from Uploader import *
from Logger import *
import LookupTable as Lt
from os import path
import argparse
import pymysql
import wikidataStuff.wdqsLookup as lookup
import importer_utils as utils

DEFAULT_SHORT = 10
MAPPING_DIR = "mappings"
REPORTING_DIR = "reports"
PREVIEW_DIR = "previews"
MONUMENTS_ALL = "monuments_all"


class Mapping(object):

    def __init__(self, dataset):
        self.dataset = dataset
        self.file_content = self.load_mapping_file()

    def load_mapping_file(self):
        filename = path.join(MAPPING_DIR, self.dataset.mapping_file)
        return utils.load_json(filename)

    def get_unique_prop(self):
        if ("unique" in self.file_content and
                self.file_content["unique"]["property"] != ""):
            return self.file_content["unique"]["property"]


def make_query(specific_table, offset):
    """
    Generate a query to retrieve data from database.

    :param specific_table: Name of table to retrieve data from.
    :param offset: Optional offset to start from.
    """
    query = 'select DISTINCT * from `{}`'.format(specific_table)
    if isinstance(offset, int):
        unlimited = "18446744073709551615"
        # workaround for MySQL requiring a limit when using offset
        query += " LIMIT {}, {};".format(str(offset), unlimited)
    return query


def make_count_query(specific_table):
    return ("SELECT COUNT(*) FROM `{}`").format(specific_table)


def create_connection(arguments):
    """Create a connection to the SQL database using arguments."""
    return pymysql.connect(
        host=arguments["host"],
        user=arguments["user"],
        password=arguments["password"],
        db=arguments["db"],
        charset="utf8")


def get_row_count(tablename, connection):
    count_query = make_count_query(tablename)
    return select_query(count_query, connection)[0]['COUNT(*)']


def print_row_count(tablename, connection):
    rowcount = get_row_count(tablename, connection)
    print(("TABLE {} HAS {} ROWS.").format(tablename, rowcount))


def select_query(query, connection):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def get_wd_items_using_prop(prop):
    items = {}
    print("WILL NOW DOWNLOAD WD ITEMS THAT USE " + prop)
    query = (
        "SELECT DISTINCT ?item ?value "
        "WHERE { ?item wdt:%s ?value }" % prop
    )
    data = lookup.make_simple_wdqs_query(query, verbose=False)
    for x in data:
        key = lookup.sanitize_wdqs_result(x['item'])
        value = x['value']
        items[value] = key
    print("FOUND {} WD ITEMS WITH PROP {}".format(len(items), prop))
    return items


def get_subclasses(q_item):
    """
    Get Q-ids of all the items that are subclasses of the specified one.

    The query fetches both items where P279 = q_item
    and indirect ones (subclass of subclass...).
    """
    results = []
    query = "SELECT DISTINCT ?item WHERE {?item wdt:P279* wd:" + q_item + ".}"
    data = lookup.make_simple_wdqs_query(query, verbose=False)
    for x in data:
        results.append(lookup.sanitize_wdqs_result(x['item']))
    return results


def make_filenames(tablename, timestamp):
    """Construct the problem and preview filenames."""
    filenames = {}
    utils.create_dir(REPORTING_DIR)
    filenames['reports'] = path.join(
        REPORTING_DIR, "report_{0}_{1}.json".format(tablename, timestamp))
    filenames['skipped'] = path.join(
        REPORTING_DIR, "skipped_{0}_{1}.json".format(tablename, timestamp))

    utils.create_dir(PREVIEW_DIR)
    filenames['examples'] = path.join(
        PREVIEW_DIR, "examples_{0}_{1}.wiki".format(tablename, timestamp))
    filenames['matches'] = path.join(
        PREVIEW_DIR, "matches_{0}_{1}.wiki".format(tablename, timestamp))
    return filenames


def load_data_files(dataset):
    """Load offline data files as specified in the dataset."""
    file_dict = dataset.data_files
    for key in file_dict.keys():
        json_path = path.join(MAPPING_DIR, file_dict[key])
        file_dict[key] = utils.load_json(json_path)
        print("Loaded offline data file: {}".format(json_path))
    return file_dict


def load_data(dataset):
    """
    Get data files necessary for mappings.

    Loads both offline files and online ones specified in the dataset.
    """
    data_files = load_data_files(dataset)
    data_files["_static"] = load_static_data()
    if dataset.subclass_downloads:
        for sub_title, sub_item in dataset.subclass_downloads.items():
            data_files[sub_title] = get_subclasses(sub_item)
            print("Loaded online data: {}".format(sub_title))
    if dataset.lookup_downloads:
        for l_title, l_path in dataset.lookup_downloads.items():
            lookup_table = Lt.LookupTable(l_path)
            lookup_json = lookup_table.convert_page_to_json_table()
            data_files[l_title] = lookup_json
            print("Loaded online data: {}".format(l_path))
    return data_files


def load_static_data():
    """Get static data files shared by all countries."""
    return {
        "props": utils.load_json(
            path.join(MAPPING_DIR, "props_general.json")),
        "adm0": utils.load_json(path.join(MAPPING_DIR, "adm0.json")),
        "sources": utils.load_json(
            path.join(MAPPING_DIR, "data_sources.json")),
        "common_items": utils.load_json(
            path.join(MAPPING_DIR, "common_items.json"))
    }


def get_items(connection,
              dataset,
              upload,
              short=False,
              offset=None,
              table=False,
              list_matches=False):
    """
    Retrieve data from database and process it.

    :param connection: Connection used to access the database.
    :param dataset: The Database instance to work on.
    :param upload: Whether to upload the processed items.
    :param short: Optional number of randomly selected rows to process.
    :param offset: Optional offset to retrieve rows.
    :param table: Whether to save the results as a wikitable.
    :param list_matches: Whether to save a list of matched items and their
        P31 values for copy/pasting to Wikidata.
    """
    filenames = make_filenames(
        dataset.table_name, utils.get_current_timestamp())
    if upload:
        logger = Logger()
    if not utils.table_exists(connection, dataset.table_name):
        print("Table does not exist.")
        return
    mapping = Mapping(dataset)
    unique_prop = mapping.get_unique_prop()
    if unique_prop is not None:
        existing = get_wd_items_using_prop(unique_prop)
    else:
        existing = None
    query = make_query(dataset.table_name, offset)

    print_row_count(dataset.table_name, connection)
    database_rows = select_query(query, connection)
    if short:
        database_rows = utils.get_random_list_sample(database_rows, short)
        print("USING RANDOM SAMPLE OF " + str(short))

    matched_item_p31s = {}
    problem_reports = []
    skipped_uploads = []

    wikidata_site = utils.create_site_instance("wikidata", "wikidata")
    data_files = load_data(dataset)
    counter = 0
    for row in database_rows:
        if not upload and counter % 100 == 0:
            # visual feedback needed for preview runs
            print(".", end="", flush=True)
        counter += 1
        monument = dataset.monument_class(
            row, mapping, data_files, existing, wikidata_site)
        problem_report = monument.get_report()
        if not monument.upload:
            skipped_uploads.append(monument)
        if table:
            raw_data = "<pre>" + str(row) + "</pre>\n"
            monument_table = monument.print_wd_to_table()
            utils.append_line_to_file(raw_data, filenames['examples'])
            utils.append_line_to_file(monument_table, filenames['examples'])
        if upload:
            live = True if upload == "live" else False
            uploader = Uploader(
                monument,
                repo=wikidata_site,
                log=logger,
                tablename=dataset.country,
                live=live)
            if "Q" in problem_report and problem_report["Q"] == "":
                """
                If the Monument didn't have an associated Qid,
                this means the Uploader has now created a new Item
                for it -- insert that id into the problem report.
                """
                problem_report["Q"] = uploader.wd_item_q

            uploader.upload()
            print("--------------------------------------------------")
        if list_matches:
            match_info = monument.get_matched_item_p31s()
            if match_info:
                for p31 in match_info[0]:
                    if p31 not in matched_item_p31s:
                        matched_item_p31s[p31] = []
                    matched_item_p31s[p31].append(
                        (match_info[1], match_info[2]))
        if problem_report:  # dictionary is not empty
            problem_reports.append(problem_report)
            utils.json_to_file(
                filenames['reports'], problem_reports, silent=True)

    if not upload:
        print("\n")  # linebreak needed in case of visual feedback dots
    if problem_reports:
        print("SAVED PROBLEM REPORTS TO {}".format(filenames['reports']))
    if skipped_uploads:
        skipped_items_output = "\n".join(
            format_skipped_items(skipped_uploads))
        utils.save_to_file(
            filenames['skipped'], skipped_items_output, silent=True)
        print("SAVED {0} SKIPPED UPLOADS TO {1}".format(
            len(skipped_uploads), filenames['skipped']))
    if table:
        print("SAVED TEST RESULTS TO {}".format(filenames['examples']))
    if list_matches:
        matched_items_output = (
            '{| class="wikitable sortable"\n'
            "! matched item {{P|P31}} !! frequency !! wlm-id(s) [max 10] \n")
        matched_items_output += "\n".join(
            format_matched_p31s_rows(matched_item_p31s))
        matched_items_output += "\n|}"
        utils.save_to_file(filenames['matches'], matched_items_output)


def format_skipped_items(skipped_items):
    rows = []
    for monument in skipped_items:
        wd_item = monument.wd_item.get("wd-item")
        wlm_id = monument.monuments_all_id
        rows.append("{0} | {1}".format(wd_item, wlm_id))
    return rows


def format_matched_p31s_rows(matched_item_p31s):
    row = "|-\n| {p31} || {freq} || {hits} "
    rows = []
    sorted_items = sorted(matched_item_p31s.items(), key=lambda x: len(x[1]),
                          reverse=True)
    for p31, hits in sorted_items:
        # loop over matches sorted by frequency
        hits = ["[{wlm_url} {id}]".format(wlm_url=url, id=id)
                for url, id in hits]
        hits_text = ", ".join(hits[:10])
        if len(hits) > 10:
            hits_text += ", ..."
        rows.append(row.format(
            p31="{{Q'|%s}}" % p31, freq=len(hits), hits=hits_text))
    return rows


def main(arguments, dataset):
    """Process the arguments and fetch data for the provided dataset."""
    arguments = vars(arguments)
    if on_forge():
        arguments["host"] = "tools-db"
        arguments["db"] = "s51138__heritage_p"
        credentials = get_db_credentials()
        arguments["user"] = credentials["user"]
        arguments["password"] = credentials["password"]
    connection = create_connection(arguments)
    short = arguments["short"]
    offset = arguments["offset"]
    upload = arguments["upload"]
    table = arguments["table"]
    list_matches = arguments["list_matches"]

    get_items(connection, dataset, upload, short, offset, table, list_matches)


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


def on_forge():
    """Check if running in the Toolforge environment."""
    return path.isfile(path.expanduser("~") + "/replica.my.cnf")


def handle_args(*args):
    """
    Parse and handle command line arguments to get data from the database.

    Also supports any pywikibot arguments, these are prefixed by a single "-"
    and the full list can be gotten through "-help".

    Options:
        --host Name of the database host.
        --db Name of the database to connect to.
        --user Username to connect to the database.
        --password Password to connect to the database.
        --upload Whether to upload the processed items. Two options:
            --upload sandbox Upload to the Wikidata sandbox item.
            --upload live Live upload to real Wikidata items.
        --short <int> Only fetch a random sample of <int> items.
        --table Save results of the processing to file as a wikitable.
        --list_matches Save a list of all matching items to a file as wikitext.
    """
    parser = argparse.ArgumentParser()
    if not on_forge():
        parser.add_argument("--host", default="localhost")
        parser.add_argument("--db", default="wlm")
        parser.add_argument("--user", default="root")
        parser.add_argument("--password", default="")
    parser.add_argument("--upload", action='store')
    parser.add_argument("--short",
                        const=DEFAULT_SHORT,
                        nargs='?',
                        type=int,
                        action='store',)
    parser.add_argument("--offset",
                        nargs='?',
                        type=int,
                        action='store',)
    parser.add_argument("--table", action='store_true')
    parser.add_argument("--list_matches", action='store_true')

    # first parse args with pywikibot, send remaining args to local handler
    return parser.parse_args(pywikibot.handle_args(args))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = handle_args()
    main(args)
