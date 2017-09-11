import dateparser
from Monument import Monument, Dataset
import importer_utils as utils
import importer as importer


class XkSq(Monument):

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("sq", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id("idno")
        self.set_registrant_url()
        self.set_changed()
        self.set_wlm_source()
        self.set_heritage_id()
        self.set_heritage()
        self.set_wd_item(self.find_matching_wikidata(mapping))


if __name__ == "__main__":
    """Point of entrance for importer."""
    args = importer.handle_args()
    dataset = Dataset("xk", "sq", XkSq)
    importer.main(args, dataset)
