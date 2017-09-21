from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class ThTh(Monument):

    def set_wd_from_name(self):
        if utils.count_wikilinks(self.name) == 1:
            self.set_wd_item(utils.q_from_first_wikilink("th", self.name))

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_heritage_id()
        self.set_wd_from_name()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("th", "th", ThTh)
    dataset.data_files = {"provinces": "thailand_provinces.json"}
    importer.main(args, dataset)
