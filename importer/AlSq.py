from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class AlSq(Monument):

    def set_special_is(self):
        if self.has_non_empty_attribute("type"):
            spec_is_raw = self.type.lower()
            is_dict = self.data_files["is"]["mappings"]
            matches = utils.get_matching_items_from_dict(spec_is_raw, is_dict)
            if len(matches) == 1:
                self.substitute_statement("is", matches[0])
            else:
                self.add_to_report("type", self.type, "is")

    def set_location(self):
        """Set Location based on mapping file."""
        self.set_from_dict_match(
            lookup_dict=self.data_files["settlements"],
            dict_label="itemLabel",
            value_label="place",
            prop="location"
        )

    def set_adm_location(self):
        """Set Admin Location based on mapping file."""
        self.set_from_dict_match(
            lookup_dict=self.data_files["municipalities"],
            dict_label="itemLabel",
            value_label="municipality",
            prop="located_adm"
        )

    def update_labels(self):
        albanian = utils.remove_markup(self.name)
        self.add_label("sq", albanian)

    def update_descriptions(self):
        english = "cultural heritage monument of Albania"
        self.add_description("en", english)

    def set_heritage_id(self):
        wlm = "{}-{}".format(self.mapping["table_name"].upper(), self.idno)
        self.add_statement("wlm_id", wlm)
        self.add_disambiguator(self.idno)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("idno")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_heritage_id()
        self.set_heritage()
        self.set_is()
        self.set_special_is()
        self.set_adm_location()
        self.set_location()
        self.set_coords()
        self.set_image()
        self.update_descriptions()
        self.update_labels()
        # there's no commonscat in dataset
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("al", "sq", AlSq)
    dataset.data_files = {"settlements": "albania_settlements.json",
                          "municipalities": "albania_municipalities.json"}
    dataset.lookup_downloads = {"is": "al_(sq)/type"}
    importer.main(args, dataset)
