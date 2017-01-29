from Monument import Monument
import importer_utils as utils

class RoRo(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.denumire)
        self.add_label("ro", name)

    def set_adm_location(self):
        return

    def set_no(self):
        self.add_statement("romanian_monument_id", self.cod)

    def __init__(self, db_row_dict, mapping, data_files, existing):
        Monument.__init__(self, db_row_dict, mapping, data_files, existing)
        self.update_labels()
        # self.exists("sq")
        self.set_commonscat()
        self.set_image("imagine")
        self.set_coords(("lat", "lon"))
        self.set_adm_location()
        self.set_no()
        # self.set_location()
        self.exists_with_prop(mapping)
        # self.print_wd()


