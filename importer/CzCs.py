from Monument import Monument
import importer_utils as utils


class CzCs(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.name)
        self.add_label("cs", name)

    def set_no(self):
        code = str(self.id_objektu)
        self.add_statement("czech_monument_id", code)

    def set_monuments_all_id(self):
        self.monuments_all_id = self.id_objektu

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_monuments_all_id()
        self.set_changed()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.update_labels()
        self.set_commonscat()
        self.set_image("image")
        self.set_coords(("lat", "lon"))
        self.set_no()
        self.set_country()
