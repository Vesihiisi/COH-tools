from Monument import Monument
import importer_utils as utils


class EeEt(Monument):

    def update_labels(self):
        name = utils.remove_markup(self.nimi)
        self.add_label("et", name)

    def set_no(self):
        register_no = str(self.registrant_url.split("=")[-1])
        self.add_statement("estonian_monument_id", register_no)

    def set_adm_location(self):
        counties = self.data_files["counties"]
        try:
            county_item = [x["item"]
                           for x in counties if x["et"] == self.maakond]
            self.add_statement("located_adm", county_item[0])
        except IndexError:
            return

    def set_monuments_all_id(self):
        """Map which column name in specific table to  ID in monuments_all."""
        self.monuments_all_id = str(self.number)

    def __init__(self, db_row_dict, mapping, data_files, existing, repository):
        Monument.__init__(self, db_row_dict, mapping,
                          data_files, existing, repository)
        self.set_changed()
        self.set_monuments_all_id()
        self.update_labels()
        self.wlm_source = self.create_wlm_source(self.monuments_all_id)
        self.set_commonscat()
        self.set_image("pilt")
        self.set_coords(("lat", "lon"))
        self.set_no()
        self.set_adm_location()
        self.set_wd_item(self.find_matching_wikidata(mapping))
