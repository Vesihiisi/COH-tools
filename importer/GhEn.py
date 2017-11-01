from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class GhEn(Monument):

    def set_special_is(self):
        if self.has_non_empty_attribute("original_function"):
            spec_is_raw = self.original_function.lower()
            is_dict = self.data_files["is"]["mappings"]
            matches = utils.get_matching_items_from_dict(spec_is_raw, is_dict)
            if len(matches) == 1:
                self.substitute_statement("is", matches[0])
            else:
                self.add_to_report(
                    "original_function", self.original_function, "is")

    def set_inception(self):
        if self.has_non_empty_attribute("built"):
            if utils.legit_year(self.built):
                year_qualifier = {"time_value": {"year": self.built}}
                self.add_statement(
                    "inception", year_qualifier)
            else:
                self.add_to_report(
                    "built", self.built, "inception")

    def set_adm_location(self):
        self.set_from_dict_match(
            lookup_dict=self.data_files["regions"],
            dict_label="iso",
            value_label="region_iso",
            prop="located_adm"
        )

    def set_location(self):
        location_q = utils.q_from_first_wikilink("en", self.location)
        if location_q:
            self.add_statement("location", location_q)
        else:
            self.add_to_report("location", self.location, "location")

    def set_heritage_id(self):
        if not self.id.startswith('GH-'):
            self.upload = False
            return
        self.add_statement("wlm_id", self.id)

    def update_labels(self):
        english = utils.remove_markup(self.name)
        self.add_label("en", english)
        if self.has_non_empty_attribute("alternative_names"):
            for alias in self.alternative_names.split(','):
                self.add_label("en", alias.strip())

    def update_descriptions(self):
        desc = "material cultural heritage site in Ghana"
        self.add_description("en", desc)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_is()
        self.set_special_is()
        self.set_image()
        self.set_inception()
        self.set_commonscat()
        self.set_coords()
        self.set_heritage()
        self.set_heritage_id()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("gh", "en", GhEn)
    dataset.data_files = {
        "regions": "ghana_regions.json"  # http://tinyurl.com/y9ye4kfg
    }
    dataset.lookup_downloads = {"is": "gh_(en)/original function"}
    importer.main(args, dataset)
