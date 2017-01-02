import argparse
import pywikibot as pwb
import mwparserfromhell as mwp
import json
import wlmhelpers

BASE_URL = "Wikidata:WikiProject WLM/Mapping tables/"


def filter_tr(node):
    return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'tr'


def filter_td(node):
    return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'td'


def createFilename(tablename):
    tablename = tablename.replace(" ", "_").replace("/", "_")
    return "{}.json".format(tablename)


def fetch_page(tablename):
    site = pwb.Site("wikidata", "wikidata")
    page = pwb.Page(site, BASE_URL + tablename)
    return page


def get_page_metadata(page):
    timestamp = page.editTime().isoformat()
    permalink = page.permalink()
    return {'permalink': permalink, 'timestamp': timestamp}


def table_to_json(tablename):
    lookupDict = {}
    lookupDict["mappings"] = {}
    page = fetch_page(tablename)
    lookupDict["@meta"] = get_page_metadata(page)
    parsed = mwp.parse(page.get())
    table = parsed.filter_tags(matches=lambda node: node.tag == "table")
    rows = table[0].contents.filter(recursive=False, matches=filter_tr)
    for row in rows:
        cells = row.contents.filter(recursive=False, matches=filter_td)
        parsedWdItems = mwp.parse(cells[2].contents).filter_templates()
        if len(parsedWdItems) > 0:
            dictKey = cells[0].contents.title().strip()
            for index, item in enumerate(parsedWdItems):
                itemID = item.params[0].title()
                if itemID[0] != "Q":
                    itemID = "Q" + itemID
                parsedWdItems[index] = itemID
            lookupDict["mappings"][dictKey] = {
                "items": parsedWdItems,
                "count": cells[1].contents.title().strip()}
    return lookupDict


def main(args):
    wlmhelpers.saveToJson(createFilename(args.name), table_to_json(args.name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    main(args)
