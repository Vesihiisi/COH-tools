# -*- coding: utf-8 -*-
"""
Class to fetch online lookup table.

Works with tables like this:
https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/se-arbetsl_(sv)/types

Download the table and turn it into a dictionary
that can then be loaded into the Monument object.
"""
import pywikibot as pwb
import mwparserfromhell as mwp

BASE_URL = "Wikidata:WikiProject WLM/Mapping tables/"


class LookupTable(object):
    """A lookup table converted from wikitext."""

    def filter_tr(self, node):
        return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'tr'

    def filter_td(self, node):
        return isinstance(node, mwp.nodes.tag.Tag) and node.tag == 'td'

    def fetch_page(self, tablename):
        """Download lookup table from given path."""
        site = pwb.Site("wikidata", "wikidata")
        page = pwb.Page(site, BASE_URL + tablename)
        return page

    def extract_table_from_page(self, page):
        parsed = mwp.parse(page)
        table = parsed.filter_tags(matches=lambda node: node.tag == "table")
        return table[0]

    def extract_metadata_from_page(self, page):
        """Get permalink and last changed timestamp of wiki page."""
        timestamp = page.editTime().isoformat()
        permalink = page.permalink()
        return {'permalink': permalink, 'timestamp': timestamp}

    def assemble_json_table(self, json_table, metadata):
        lookup_dict = {}
        lookup_dict["metadata"] = metadata
        lookup_dict["mappings"] = json_table
        return lookup_dict

    def table_to_json(self, wikitable):
        """Convert wikitable to json."""
        lookup_dict = {}
        rows = wikitable.contents.filter(
            recursive=False, matches=self.filter_tr)
        for row in rows:
            cells = row.contents.filter(
                recursive=False, matches=self.filter_td)
            parsed_wd_items = mwp.parse(cells[2].contents).filter_templates()
            if len(parsed_wd_items) > 0:
                dict_key = cells[0].contents.title().strip()
                for index, item in enumerate(parsed_wd_items):
                    itemID = item.params[0].title()
                    if itemID[0] != "Q":
                        itemID = "Q" + itemID
                    parsed_wd_items[index] = itemID
                lookup_dict[dict_key] = {
                    "items": parsed_wd_items,
                    "count": cells[1].contents.title().strip()}
        return lookup_dict

    def get_json_table(self):
        """Get the lookup table as json."""
        return self.json_table

    def convert_page_to_json_table(self):
        wikipage = self.fetch_page(self.lookup_path)
        wikitable = self.extract_table_from_page(wikipage.get())
        json_table = self.table_to_json(wikitable)
        metadata = self.extract_metadata_from_page(wikipage)
        return self.assemble_json_table(json_table, metadata)

    def __init__(self, lookup_path):
        self.lookup_path = lookup_path
