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

    def set_admin_location(self):
        if self.has_non_empty_attribute("municipality"):
            municip_dict = self.data_files["municipalities"]
            municip = self.municipality
            try:
                municip_match = [x for x in municip_dict
                                 if x["cs"].lower() == municip.lower()][0]
                self.add_statement("located_adm", municip_match)
            except IndexError:
                self.add_to_report(
                    "municipality", self.municipality, "located_adm")

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
        self.set_heritage()
        self.set_admin_location()
