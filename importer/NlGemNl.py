from Monument import Monument
import importer_utils as utils


class NlGemNl(Monument):

    def set_monuments_all_id(self):
        """Map which column in table to ID in monuments_all."""
        self.monuments_all_id = "{}/{}".format(self.gemcode, self.objnr)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_country()
        self.print_wd()
