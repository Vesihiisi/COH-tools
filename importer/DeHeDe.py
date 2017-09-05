from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class DeHeDe(Monument):

    def set_location(self):
        if self.has_non_empty_attribute("ortsteil"):
            location_q = utils.q_from_wikipedia("de", self.ortsteil)
            if location_q:
                self.add_statement("location", location_q)

    def set_adm_location(self):
        city_q = utils.q_from_wikipedia("de", self.stadt)
        self.add_statement("located_adm", city_q)

    def update_descriptions(self):
        placename = None
        germany = {
            "de": "Deutschland",
            "en": "Germany",
            "sv": "Tyskland"
        }
        templates = {
            "en": "Kulturdenkmal in {}",
            "de": "Kulturdenkmal in {}",
            "sv": "kulturminnesmärke i {}"
        }
        for lg in templates:
            country = germany[lg]
            if self.has_non_empty_attribute("stadt"):
                placename = utils.get_rid_of_brackets(self.stadt)
                placename = "{}, {}".format(placename, country)
            else:
                placename = country
            desc = templates[lg].format(placename)
            self.add_description(lg, desc)

    def update_labels(self):
        if self.has_non_empty_attribute("bezeichnung"):
            german = utils.remove_markup(self.bezeichnung)
        elif self.has_non_empty_attribute("adresse"):
            german = utils.remove_markup(self.adresse)
        self.add_label("de", german)

    def set_heritage_id(self):
        self.add_statement("denkXweb", str(self.nummer))

    def set_street_address(self):
        street_with_no = utils.remove_markup(self.adresse)
        town = utils.get_rid_of_brackets(self.stadt)
        address = "{}, {}".format(street_with_no, town)
        self.add_statement("located_street", address)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("de", "artikel")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("nummer")
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_source()
        self.set_registrant_url()
        self.set_image("bild")
        self.set_commonscat()
        self.set_country()
        self.set_adm_location()
        self.set_location()
        self.set_coords()
        self.set_heritage()
        self.set_heritage_id()
        self.set_street_address()
        self.update_labels()
        self.update_descriptions()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("de-he", "de", DeHeDe)
    importer.main(args, dataset)
