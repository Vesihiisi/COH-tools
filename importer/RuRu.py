from Monument import Monument
import importer_utils as utils


class RuRu(Monument):

    def set_heritage_id(self):
        self.add_statement("kulturnoe-nasledie", self.id)

    def set_monuments_all_id(self):
        self.monuments_all_id = self.id

    def exists_with_monument_article(self, language):
        return super().exists_with_monument_article("ru", "monument_article")

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.set_is()
        self.set_heritage()
        self.set_image()
        self.set_commonscat()
        self.set_heritage_id()
        self.set_coords(("lat", "lon"))
        self.set_wd_item(self.find_matching_wikidata(mapping))
