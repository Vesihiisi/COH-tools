from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CaFr(Monument):

    def set_heritage_id(self):
        self.add_statement("canadian_register", str(self.numero))

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.numero)

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("fr", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_heritage_id()
        self.set_heritage()
        self.set_country()
        self.set_is()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("ca", "fr", CaFr)
    dataset.data_files = {}
    dataset.lookup_downloads = {}
    importer.main(args, dataset)
