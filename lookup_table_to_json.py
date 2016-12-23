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


def main(args):
    lookupDict = {}
    lookupDict["mappings"] = {}
    tablename = args.name
    site = pwb.Site("wikidata", "wikidata")
    page = pwb.Page(site, BASE_URL + tablename)
    timestamp = page.editTime().isoformat()
    permalink = page.permalink()
    parsed = mwp.parse(page.get())
    lookupDict["@meta"] = {'permalink': permalink, 'timestamp': timestamp}
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
            lookupDict["mappings"][dictKey] = {"items" : parsedWdItems, "count" : cells[1].contents.title().strip()}
    wlmhelpers.saveToJson(createFilename(tablename), lookupDict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    main(args)
