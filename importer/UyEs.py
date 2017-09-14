from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class UyEs(Monument):

    def set_wd_item_via_name(self):
        if utils.count_wikilinks(self.monumento) == 1:
            monum_q = utils.q_from_first_wikilink("es", self.monumento)
            self.set_wd_item(monum_q)

    def update_labels(self):
        es_name = utils.remove_markup(self.monumento)
        self.add_label("es", es_name)

    def set_heritage_id(self):
        wlm_code = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm_code, self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_heritage_id()
        self.update_labels()
        self.set_wd_item_via_name()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("uy", "es", UyEs)
    dataset.data_files = {}
    importer.main(args, dataset)
