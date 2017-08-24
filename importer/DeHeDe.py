from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class DeHeDe(Monument):

    def set_adm_location(self):
        city_q = utils.q_from_wikipedia("de", self.stadt)
        self.add_statement("located_adm", city_q)

    def update_labels(self):
        german = utils.remove_markup(self.bezeichnung)
        self.add_label("de", german)

    def set_heritage_id(self):
        self.add_statement("denkXweb", str(self.nummer))

    def set_street_address(self):
        street_with_no = utils.remove_markup(self.adresse)
        town = self.stadt
        address = "{}, {}".format(street_with_no, town)
        self.add_statement("located_street", address)

    def set_monuments_all_id(self):
        self.monuments_all_id = str(self.nummer)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_source()
        self.set_registrant_url()
        self.set_image("bild")
        self.set_commonscat()
        self.set_country()
        self.set_adm_location()
        self.set_coords(("lat", "lon"))
        self.set_heritage()
        self.set_heritage_id()
        self.set_street_address()
        self.update_labels()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("de-he", "de", DeHeDe)
    dataset.data_files = {}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
