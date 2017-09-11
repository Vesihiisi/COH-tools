from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class MxEs(Monument):

    def set_heritage_id(self):
        self.add_statement("wlm_id", str(self.id))

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("es", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id(str(self.id))
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_image("imagen")
        self.set_commonscat("monumento_categoria")
        self.set_coords()
        self.set_country()
        self.set_is()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Command line entry point for importer."""
    args = importer.handle_args()
    dataset = Dataset("mx", "ex", MxEs)
    dataset.data_files = {}
    importer.main(args, dataset)
