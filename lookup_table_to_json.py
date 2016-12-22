import argparse
import pywikibot as pwb
import mwparserfromhell as mwp
import json

BASE_URL = "Wikidata:WikiProject WLM/Mapping tables/"


def filter_tr(node):
    return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'tr'

def filter_td(node):
    return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'td'


def main(args):
    lookupDict = {}
    tablename = args.name
    site = pwb.Site("wikidata", "wikidata")
    rawText = pwb.Page(site, BASE_URL + tablename).get()
    parsed = mwp.parse(rawText)
    table = parsed.get(0)
    rows = table.contents.filter(recursive=False, matches=filter_tr)
    for row in rows:
        cells = row.contents.filter(recursive=False, matches=filter_td)
        parsedWdItems = mwp.parse(cells[2].contents).filter_templates()
        if len(parsedWdItems) > 0:
            dictKey = cells[0].contents.title().strip()
            for index, item in enumerate(parsedWdItems):
                parsedWdItems[index] = item.params[0].title()
            lookupDict[dictKey] = parsedWdItems
    with open('result.json', 'w') as fp:
        json.dump(lookupDict, fp, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    main(args)
