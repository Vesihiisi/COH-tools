from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class SvEs(Monument):

    def set_heritage_id(self):
        wlm = self.mapping["table_name"].upper()
        self.add_statement("wlm_id", "{}-{}".format(wlm, self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monumento_enlace")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("id")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_coords()
        self.set_is()
        self.set_country()
        self.set_coords()
        self.set_heritage()
        self.set_heritage_id()

        self.set_image()
        self.set_commonscat()

        # self.update_labels()
        # self.update_descriptions()
        # self.set_adm_location()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("sv", "es", SvEs)
    dataset.data_files = {}
    importer.main(args, dataset)
