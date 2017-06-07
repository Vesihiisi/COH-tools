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
        """
        Download lookup table from given path.

        :param tablename: name of the lookup table without
                          full path, eg. "se-fornmin (sv)/types"
        :return: Pywikibot page object where the table is located
        """
        site = pwb.Site("wikidata", "wikidata")
        return pwb.Page(site, BASE_URL + tablename)

    def extract_table_from_page(self, page):
        """
        Get wikitable from page.

        :param page: Pywikibot Page object containing table
        :return: wikitable
        :rtype: Mediawikiparser Tag object
        """
        parsed = mwp.parse(page)
        table = parsed.filter_tags(matches=lambda node: node.tag == "table")
        return table[0]

    def extract_metadata_from_page(self, page):
        """Get permalink and last changed timestamp of wiki page."""
        timestamp = page.editTime().isoformat()
        permalink = page.permalink()
        return {'permalink': permalink, 'timestamp': timestamp}

    def assemble_json_table(self, json_table, metadata):
        """
        Put lookup dictionary and metadata together.

        :param json_table: lookup dictionary
        :param metadata: metadata dictionary
        :return: full mapping dictionary
        """
        lookup_dict = {}
        lookup_dict["metadata"] = metadata
        lookup_dict["mappings"] = json_table
        return lookup_dict

    def table_to_json(self, wikitable):
        """
        Convert wikitable to json.

        :param wikitable: lookup wikitable
        :type wikitable: Mediawikiparser Tag
        :return: lookup dictionary
        """
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
                    item_id = item.params[0].title()
                    if not item_id.startswith("Q"):
                        item_id = "Q" + item_id
                    parsed_wd_items[index] = item_id
                lookup_dict[dict_key] = {
                    "items": parsed_wd_items,
                    "count": cells[1].contents.title().strip()}
        return lookup_dict

    def convert_page_to_json_table(self):
        """Convert a lookup table from self.path to json representation."""
        wikipage = self.fetch_page(self.lookup_path)
        wikitable = self.extract_table_from_page(wikipage.get())
        json_table = self.table_to_json(wikitable)
        metadata = self.extract_metadata_from_page(wikipage)
        return self.assemble_json_table(json_table, metadata)

    def __init__(self, lookup_path):
        """
        Initialize LookupTable object.

        :param lookup_path: name of the lookup table without
                            full path, eg. "se-fornmin (sv)/types"
        """
        self.lookup_path = lookup_path
