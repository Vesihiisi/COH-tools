from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class CnEn(Monument):

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("en", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("designation")
        self.set_changed()
        self.set_wlm_source()
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("cn", "en", CnEn)
    dataset.data_files = {}
    importer.main(args, dataset)
