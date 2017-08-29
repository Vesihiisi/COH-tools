from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class GhEn(Monument):

    def set_special_is(self):
        if self.has_non_empty_attribute("original_function"):
            spec_is_raw = self.original_function.lower()
            table = self.data_files["is"]["mappings"]
            lookup = [table[x]["items"]
                      for x in table if x.lower() == spec_is_raw]
            special_is_q = lookup[0][0]
            if len(lookup) == 1:
                self.substitute_statement("is", special_is_q)

    def set_inception(self):
        if self.has_non_empty_attribute("built"):
            if utils.legit_year(self.built):
                year_qualifier = {"time_value": {"year": self.built}}
                self.add_statement(
                    "inception", year_qualifier)

    def set_adm_location(self):
        region_q = utils.q_from_first_wikilink("en", self.region)
        if region_q:
            self.add_statement("located_adm", region_q)

    def set_location(self):
        location_q = utils.q_from_first_wikilink("en", self.location)
        if location_q:
            self.add_statement("location", location_q)

    def set_heritage_id(self):
        self.add_statement("wlm_id", self.id)

    def update_labels(self):
        english = utils.remove_markup(self.name)
        self.add_label("en", english)
        if self.has_non_empty_attribute("alternative_names"):
            self.add_label("en", self.alternative_names)

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = self.id

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_special_is()
        self.set_image()
        self.set_inception()
        self.set_commonscat()
        self.set_coords(("lat", "lon"))
        self.set_heritage()
        self.set_heritage_id()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("gh", "en", GhEn)
    dataset.data_files = {}
    dataset.lookup_downloads = {"is": "gh_(en)/original function"}
    importer.main(args, dataset)
