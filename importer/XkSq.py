from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class XkSq(Monument):

    def set_is(self):
        """
        Set a more detailed value of P31.

        Based on 'category' and lookup table:
        https://www.wikidata.org/wiki/Wikidata:WikiProject_WLM/Mapping_tables/xk_(sq)/category
        If no match, default to default.
        """
        cat_dict = self.data_files["categories"]["mappings"]
        monument_cat = self.category.lower()
        lookup_match = utils.get_matching_items_from_dict(dict_name=cat_dict,
                                                          value=monument_cat)
        if len(lookup_match) == 1:
            self.add_statement("is", lookup_match[0])
        else:
            super().set_is()

    def set_inception(self):
        """Set inception if it's a whole year."""
        if utils.legit_year(self.date_period):
            inc_year = {"time_value": {"year": self.date_period}}
            self.add_statement("inception", inc_year)
        else:
            # this will give a lot of results... :/
            self.add_to_report("date_period", self.date_period, "inception")

    def set_location(self):
        """Set Location if it's matched against valid settlements."""
        if self.has_non_empty_attribute("place"):
            settl_dic = self.data_files["settlements"]
            s_match = utils.get_item_from_dict_by_key(dict_name=settl_dic,
                                                      search_term=self.place,
                                                      search_in="itemLabel")
            if len(s_match) == 1:
                self.add_statement("location", s_match[0])
            else:
                self.add_to_report("place", self.place, "location")

    def set_adm_location(self):
        """Set Admin Location if it's matched against valid values."""
        municip_raw = self.municipality.lower()
        municp_dic = self.data_files["municipalities"]["mappings"]
        municip_matches = utils.get_matching_items_from_dict(
            municip_raw, municp_dic)
        if len(municip_matches) == 1:
            self.add_statement("located_adm", municip_matches[0])
        else:
            self.add_to_report(
                "municipality", self.municipality, "located_adm")

    def set_heritage_id(self):
        self.add_statement("kosovo_monument_id", str(self.idno))
        self.add_disambiguator(str(self.idno))

    def update_labels(self):
        albanian = utils.remove_markup(self.name)
        self.add_label("sq", albanian)

    def update_descriptions(self):
        english = "cultural heritage monument of Kosovo"
        self.add_description("en", english)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("idno")
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_coords()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_heritage()
        self.set_inception()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("xk", "sq", XkSq)
    dataset.data_files = {"settlements": "kosovo_settlements.json"}
    dataset.lookup_downloads = {"municipalities": "xk (sq)/municipalities",
                                "categories": "xk (sq)/category"}
    importer.main(args, dataset)
