import pywikibot as pwb
import mwparserfromhell as mwp

BASE_URL = "Wikidata:WikiProject WLM/Mapping tables/"


class LookupTable(object):

    def filter_tr(self, node):
        return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'tr'

    def filter_td(self, node):
        return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'td'

    def fetch_page(self, tablename):
        site = pwb.Site("wikidata", "wikidata")
        page = pwb.Page(site, BASE_URL + tablename)
        return page

    def get_page_metadata(self, page):
        timestamp = page.editTime().isoformat()
        permalink = page.permalink()
        return {'permalink': permalink, 'timestamp': timestamp}

    def table_to_json(self, tablename):
        print(tablename)
        lookupDict = {}
        lookupDict["mappings"] = {}
        page = self.fetch_page(tablename)
        lookupDict["@meta"] = self.get_page_metadata(page)
        parsed = mwp.parse(page.get())
        table = parsed.filter_tags(matches=lambda node: node.tag == "table")
        rows = table[0].contents.filter(
            recursive=False, matches=self.filter_tr)
        for row in rows:
            cells = row.contents.filter(
                recursive=False, matches=self.filter_td)
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

    def get_json_table(self):
        return self.json_table

    def __init__(self, lookup_path):
        self.json_table = self.table_to_json(lookup_path)
